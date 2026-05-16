"""
Permissioned blockchain ledger — models the Hyperledger Fabric channel.
Each block contains: index, timestamp, transactions, previous hash, own hash.
Transactions represent node identity events (register, authenticate, revoke).
"""
import hashlib
import json
import time
import threading
from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class Transaction:
    tx_id:   str
    node_id: str
    action:  str        # register | authenticate | revoke | topology_change
    payload: dict
    ts:      float = field(default_factory=time.time)

    def to_dict(self):
        return asdict(self)


@dataclass
class Block:
    index:         int
    transactions:  list[dict]
    prev_hash:     str
    timestamp:     float = field(default_factory=time.time)
    hash:          str   = ""

    def compute_hash(self) -> str:
        content = json.dumps({
            "index":       self.index,
            "transactions": self.transactions,
            "prev_hash":   self.prev_hash,
            "timestamp":   self.timestamp,
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    def finalise(self):
        self.hash = self.compute_hash()

    def to_dict(self):
        return asdict(self)


class Ledger:
    def __init__(self):
        self._lock   = threading.Lock()
        self._chain: list[Block]        = []
        self._pool:  list[Transaction]  = []
        self._identities: dict[str, dict] = {}
        self._genesis()

    def _genesis(self):
        genesis = Block(index=0, transactions=[], prev_hash="0" * 64)
        genesis.finalise()
        self._chain.append(genesis)

    # --- Identity management (smart-contract-like) ---

    def register_node(self, node_id: str, public_key: str, node_type: str) -> dict:
        with self._lock:
            if node_id in self._identities:
                return {"ok": False, "reason": "already registered"}
            self._identities[node_id] = {
                "node_id":    node_id,
                "public_key": public_key,
                "node_type":  node_type,
                "status":     "active",
                "registered": time.time(),
            }
            tx = Transaction(
                tx_id=self._new_tx_id(),
                node_id=node_id,
                action="register",
                payload={"node_type": node_type, "pk_hash": hashlib.sha256(public_key.encode()).hexdigest()[:16]},
            )
            self._pool.append(tx)
            if len(self._pool) >= 1:
                self._commit_block()
            return {"ok": True, "tx_id": tx.tx_id}

    def authenticate_node(self, node_id: str) -> dict:
        with self._lock:
            identity = self._identities.get(node_id)
            if not identity:
                return {"ok": False, "reason": "unknown node"}
            if identity["status"] != "active":
                return {"ok": False, "reason": f"node is {identity['status']}"}
            tx = Transaction(
                tx_id=self._new_tx_id(),
                node_id=node_id,
                action="authenticate",
                payload={"ts": time.time()},
            )
            self._pool.append(tx)
            if len(self._pool) >= 3:
                self._commit_block()
            return {"ok": True, "tx_id": tx.tx_id, "identity": identity}

    def revoke_node(self, node_id: str) -> dict:
        with self._lock:
            if node_id not in self._identities:
                return {"ok": False, "reason": "unknown node"}
            self._identities[node_id]["status"] = "revoked"
            tx = Transaction(
                tx_id=self._new_tx_id(),
                node_id=node_id,
                action="revoke",
                payload={},
            )
            self._pool.append(tx)
            self._commit_block()
            return {"ok": True, "tx_id": tx.tx_id}

    def record_topology_change(self, event: dict) -> dict:
        with self._lock:
            tx = Transaction(
                tx_id=self._new_tx_id(),
                node_id=event.get("node", "system"),
                action="topology_change",
                payload=event,
            )
            self._pool.append(tx)
            if len(self._pool) >= 3:
                self._commit_block()
            return {"ok": True, "tx_id": tx.tx_id}

    # --- Internal ---

    def _new_tx_id(self) -> str:
        return hashlib.sha256(f"{time.time_ns()}".encode()).hexdigest()[:16]

    def _commit_block(self):
        prev = self._chain[-1]
        block = Block(
            index=len(self._chain),
            transactions=[tx.to_dict() for tx in self._pool],
            prev_hash=prev.hash,
        )
        block.finalise()
        self._chain.append(block)
        self._pool.clear()

    # --- Queries ---

    def chain_summary(self) -> dict:
        return {
            "blocks":      len(self._chain),
            "identities":  len(self._identities),
            "active_nodes": sum(1 for v in self._identities.values() if v["status"] == "active"),
            "last_block":  self._chain[-1].to_dict() if self._chain else None,
        }

    def get_chain(self, limit: int = 10) -> list[dict]:
        return [b.to_dict() for b in self._chain[-limit:]]

    def get_identity(self, node_id: str) -> dict | None:
        return self._identities.get(node_id)

    def is_valid(self) -> bool:
        for i in range(1, len(self._chain)):
            cur  = self._chain[i]
            prev = self._chain[i - 1]
            if cur.prev_hash != prev.hash:
                return False
            if cur.hash != cur.compute_hash():
                return False
        return True
