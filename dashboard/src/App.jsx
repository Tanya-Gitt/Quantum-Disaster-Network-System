import React, { useState } from "react";
import { useSocket } from "./hooks/useSocket";
import TopologyMap    from "./components/TopologyMap";
import NodePanel      from "./components/NodePanel";
import SOSPanel       from "./components/SOSPanel";
import MetricsBar     from "./components/MetricsBar";
import BlockchainFeed      from "./components/BlockchainFeed";
import DisasterControls    from "./components/DisasterControls";

const S = {
  app: {
    minHeight: "100vh",
    background: "#0a0e1a",
    color: "#e0e6f0",
    fontFamily: "'Segoe UI', sans-serif",
    display: "flex",
    flexDirection: "column",
  },
  header: {
    background: "#0d1117",
    borderBottom: "1px solid #1e3a5f",
    padding: "12px 24px",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
  },
  title: { fontSize: 18, fontWeight: 700, letterSpacing: 1 },
  dot: (ok) => ({
    width: 10, height: 10, borderRadius: "50%",
    background: ok ? "#69f0ae" : "#ff5252",
    display: "inline-block", marginRight: 6,
  }),
  main: { flex: 1, display: "grid", gridTemplateColumns: "1fr 340px", gap: 0 },
  mapArea: { position: "relative", height: "calc(100vh - 140px)" },
  sidebar: {
    background: "#0d1117",
    borderLeft: "1px solid #1e3a5f",
    padding: 16,
    display: "flex",
    flexDirection: "column",
    gap: 20,
    overflowY: "auto",
    height: "calc(100vh - 140px)",
  },
  section: { borderBottom: "1px solid #1e3a5f", paddingBottom: 16 },
  sectionTitle: { fontSize: 11, color: "#00e5ff", letterSpacing: 2, marginBottom: 10, textTransform: "uppercase" },
  footer: {
    background: "#0d1117",
    borderTop: "1px solid #1e3a5f",
    padding: "6px 24px",
    fontSize: 11,
    color: "#555",
    display: "flex",
    gap: 24,
  },
};

export default function App() {
  const { connected, topology, sosAlerts, blockchainEvents, sendSOS } = useSocket();
  const [selectedNode, setSelectedNode] = useState(null);

  return (
    <div style={S.app}>
      <header style={S.header}>
        <div>
          <span style={S.title}>QDN — Quantum Disaster Network</span>
          <span style={{ marginLeft: 16, fontSize: 12, color: "#888" }}>
            AI-Driven Self-Healing Mesh · Smart India
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", fontSize: 13 }}>
          <span style={S.dot(connected)} />
          {connected ? "Live" : "Connecting…"}
        </div>
      </header>

      <div style={{ padding: "10px 16px", background: "#0a0e1a", borderBottom: "1px solid #1a2a3a" }}>
        <MetricsBar topology={topology} />
      </div>

      <div style={S.main}>
        <div style={S.mapArea}>
          <TopologyMap topology={topology} onNodeClick={setSelectedNode} />
          {selectedNode && (
            <div style={{ position: "absolute", top: 16, right: 16, zIndex: 1000 }}>
              <NodePanel node={selectedNode} onClose={() => setSelectedNode(null)} />
            </div>
          )}
        </div>

        <aside style={S.sidebar}>
          <div style={S.section}>
            <div style={S.sectionTitle}>Emergency Broadcast</div>
            <SOSPanel alerts={sosAlerts} onSend={sendSOS} />
          </div>

          <div style={S.section}>
            <div style={S.sectionTitle}>Node Registry ({topology.nodes?.length ?? 0})</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
              {(topology.nodes || []).map((n) => (
                <div
                  key={n.id}
                  onClick={() => setSelectedNode(n)}
                  style={{
                    display: "flex", justifyContent: "space-between",
                    alignItems: "center", padding: "5px 8px",
                    background: "#111827", borderRadius: 5, cursor: "pointer",
                    border: selectedNode?.id === n.id ? "1px solid #00e5ff" : "1px solid transparent",
                  }}
                >
                  <span style={{ fontSize: 13, fontWeight: 600 }}>{n.id}</span>
                  <span style={{ fontSize: 11, color: "#888" }}>{n.type}</span>
                  <span style={{
                    fontSize: 11, fontWeight: 700,
                    color: n.status === "online" ? "#69f0ae" : n.status === "offline" ? "#ff5252" : "#ffd740",
                  }}>{n.status}</span>
                </div>
              ))}
            </div>
          </div>

          <div style={S.section}>
            <div style={S.sectionTitle}>Disaster Simulator</div>
            <DisasterControls />
          </div>

          <div>
            <div style={S.sectionTitle}>Blockchain Audit Log</div>
            <BlockchainFeed events={blockchainEvents} />
          </div>
        </aside>
      </div>

      <footer style={S.footer}>
        <span>Domain: AI · SDN · PQC · Blockchain · IoT · 6G</span>
        <span>Nodes: {topology.nodes?.length ?? 0}</span>
        <span>Links: {topology.edges?.length ?? 0}</span>
        <span>Cipher: CRYSTALS-Kyber 1024</span>
        <span>Auth: Hyperledger Fabric 2.5</span>
      </footer>
    </div>
  );
}
