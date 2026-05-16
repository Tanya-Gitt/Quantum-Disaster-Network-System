import React from "react";

function Metric({ label, value, unit, color }) {
  return (
    <div style={{
      background: "#111827", border: "1px solid #1e3a5f",
      borderRadius: 8, padding: "10px 16px", minWidth: 120,
    }}>
      <div style={{ color: "#888", fontSize: 11, marginBottom: 4 }}>{label}</div>
      <div style={{ color: color || "#00e5ff", fontSize: 22, fontWeight: 700 }}>
        {value}<span style={{ fontSize: 12, marginLeft: 3, color: "#aaa" }}>{unit}</span>
      </div>
    </div>
  );
}

export default function MetricsBar({ topology }) {
  const nodes   = topology.nodes || [];
  const online  = nodes.filter((n) => n.status === "online").length;
  const offline = nodes.filter((n) => n.status === "offline").length;
  const drones  = nodes.filter((n) => n.type === "drone" && n.status === "active").length;
  const avgLoad = nodes.length
    ? (nodes.reduce((s, n) => s + n.load, 0) / nodes.length * 100).toFixed(1)
    : 0;

  return (
    <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
      <Metric label="Nodes Online"   value={online}   color="#69f0ae" />
      <Metric label="Nodes Offline"  value={offline}  color={offline > 0 ? "#ff5252" : "#69f0ae"} />
      <Metric label="Active Drones"  value={drones}   color="#40c4ff" />
      <Metric label="Avg Node Load"  value={avgLoad}  unit="%" color="#ffd740" />
      <Metric label="Recovery Target" value="< 2"    unit="s" color="#ea80fc" />
      <Metric label="PQC Cipher"     value="Kyber-1024" color="#80d8ff" />
    </div>
  );
}
