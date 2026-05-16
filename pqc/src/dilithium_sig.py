"""
CRYSTALS-Dilithium3 Digital Signatures.
Uses dilithium-py — a pure-Python reference implementation of FIPS 204 (ML-DSA).
For production, swap with oqs-python (liboqs bindings).
"""
import time
import base64

try:
    from dilithium import Dilithium3
    _BACKEND = "dilithium-py"
except ImportError:
    Dilithium3 = None
    _BACKEND = "fallback-simulated"


def keygen() -> dict:
    t0 = time.perf_counter()
    if Dilithium3:
        pk, sk = Dilithium3.keygen()
        ms = (time.perf_counter() - t0) * 1000
        return {
            "backend":    _BACKEND,
            "algorithm":  "CRYSTALS-Dilithium3",
            "pk_b64":     base64.b64encode(pk).decode(),
            "sk_b64":     base64.b64encode(sk).decode(),
            "pk_bytes":   len(pk),
            "sk_bytes":   len(sk),
            "latency_ms": round(ms, 3),
        }
    import os
    pk, sk = os.urandom(1952), os.urandom(4000)
    ms = (time.perf_counter() - t0) * 1000
    return {"backend": _BACKEND, "algorithm": "CRYSTALS-Dilithium3 (simulated)", "pk_bytes": len(pk), "sk_bytes": len(sk), "latency_ms": round(ms, 3)}


def sign(sk_b64: str, message: str) -> dict:
    t0 = time.perf_counter()
    msg_bytes = message.encode()
    if Dilithium3:
        sk  = base64.b64decode(sk_b64)
        sig = Dilithium3.sign(sk, msg_bytes)
        ms  = (time.perf_counter() - t0) * 1000
        return {"signature_b64": base64.b64encode(sig).decode(), "sig_bytes": len(sig), "latency_ms": round(ms, 3)}
    import os
    sig = os.urandom(3293)
    ms  = (time.perf_counter() - t0) * 1000
    return {"signature_b64": base64.b64encode(sig).decode(), "sig_bytes": len(sig), "latency_ms": round(ms, 3)}


def verify(pk_b64: str, message: str, sig_b64: str) -> dict:
    t0 = time.perf_counter()
    msg_bytes = message.encode()
    if Dilithium3:
        pk  = base64.b64decode(pk_b64)
        sig = base64.b64decode(sig_b64)
        try:
            Dilithium3.verify(pk, msg_bytes, sig)
            valid = True
        except Exception:
            valid = False
        ms = (time.perf_counter() - t0) * 1000
        return {"valid": valid, "latency_ms": round(ms, 3)}
    ms = (time.perf_counter() - t0) * 1000
    return {"valid": True, "latency_ms": round(ms, 3), "note": "simulated"}
