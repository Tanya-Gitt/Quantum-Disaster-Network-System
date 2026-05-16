import React, { useState } from "react";
import axios from "axios";

const API = process.env.REACT_APP_API_URL || "http://localhost:5000";

const badge = (status) => {
  const colors = { online: "#69f0ae", offline: "#ff5252", standby: "#ffd740", active: "#40c4ff" };
  return (
    <span style={{
      background: colors[status] || "#888",
      color: "#000",
      borderRadius: 4,
      padding: "1px 7px",
      fontSize: 11,
      fontWeight: 700,
    }}>{status}</span>
  );
};

export default function NodePanel({ node, onClose }) {
  const [busy, setBusy] = useState(false);
  const [msg, setMsg]   = useState("");

  if (!node) return null;

  const action = async (endpoint) => {
    setBusy(true);
    try {
      const res = await axios.post(`${API}/api/node/${node.id}/${endpoint}`);
      setMsg(res.data.action === "killed" ? "Node taken offline." : "Node restored online.");
    } catch {
      setMsg("Request failed.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div style={{
      background: "#111827",
      border: "1px solid #1e3a5f",
      borderRadius: 10,
      padding: 16,
      minWidth: 220,
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
        <span style={{ fontWeight: 700, fontSize: 16 }}>Node {node.id}</span>
        <button onClick={onClose} style={{ background: "none", border: "none", color: "#aaa", cursor: "pointer", fontSize: 16 }}>✕</button>
      </div>
      <table style={{ width: "100%", fontSize: 13, borderCollapse: "collapse" }}>
        <tbody>
          <tr><td style={{ color: "#888", paddingBottom: 6 }}>Type</td><td>{node.type}</td></tr>
          <tr><td style={{ color: "#888", paddingBottom: 6 }}>Status</td><td>{badge(node.status)}</td></tr>
          <tr><td style={{ color: "#888", paddingBottom: 6 }}>Load</td><td>{(node.load * 100).toFixed(1)}%</td></tr>
          <tr><td style={{ color: "#888", paddingBottom: 6 }}>Lat/Lon</td><td>{node.lat.toFixed(4)}, {node.lon.toFixed(4)}</td></tr>
        </tbody>
      </table>
      {msg && <p style={{ color: "#ffd740", fontSize: 12, margin: "8px 0 0" }}>{msg}</p>}
      <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
        <button
          disabled={busy || node.status === "offline"}
          onClick={() => action("kill")}
          style={{ flex: 1, background: "#ff1744", color: "#fff", border: "none", borderRadius: 6, padding: "6px 0", cursor: "pointer", fontWeight: 600 }}
        >Simulate Failure</button>
        <button
          disabled={busy || node.status === "online"}
          onClick={() => action("restore")}
          style={{ flex: 1, background: "#00e676", color: "#000", border: "none", borderRadius: 6, padding: "6px 0", cursor: "pointer", fontWeight: 600 }}
        >Restore</button>
      </div>
    </div>
  );
}
