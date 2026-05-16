import React, { useState } from "react";

export default function SOSPanel({ alerts, onSend }) {
  const [msg, setMsg] = useState("");

  const send = () => {
    if (msg.trim()) {
      onSend(msg.trim());
      setMsg("");
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
      <div style={{ display: "flex", gap: 8 }}>
        <input
          value={msg}
          onChange={(e) => setMsg(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          placeholder="Broadcast SOS message…"
          style={{
            flex: 1, background: "#1a1f2e", border: "1px solid #ff1744",
            borderRadius: 6, padding: "8px 12px", color: "#fff", fontSize: 13,
          }}
        />
        <button
          onClick={send}
          style={{
            background: "#ff1744", color: "#fff", border: "none",
            borderRadius: 6, padding: "8px 18px", fontWeight: 700,
            cursor: "pointer", letterSpacing: 1,
          }}
        >SOS</button>
      </div>

      <div style={{ maxHeight: 160, overflowY: "auto", display: "flex", flexDirection: "column", gap: 6 }}>
        {alerts.length === 0 && (
          <span style={{ color: "#555", fontSize: 12 }}>No active alerts.</span>
        )}
        {alerts.map((a, i) => (
          <div key={i} style={{
            background: "#1e0a0a", border: "1px solid #ff1744",
            borderRadius: 6, padding: "6px 10px", fontSize: 12,
          }}>
            <span style={{ color: "#ff5252", fontWeight: 700 }}>ALERT</span>{" "}
            <span style={{ color: "#e0e0e0" }}>{a.message || JSON.stringify(a)}</span>
            <span style={{ color: "#555", marginLeft: 8 }}>
              {new Date(a.ts).toLocaleTimeString()}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
