import React from "react";

export default function BlockchainFeed({ events }) {
  return (
    <div style={{ maxHeight: 200, overflowY: "auto", display: "flex", flexDirection: "column", gap: 4 }}>
      {events.length === 0 && (
        <span style={{ color: "#555", fontSize: 12 }}>Awaiting blockchain events…</span>
      )}
      {events.map((e, i) => (
        <div key={i} style={{
          background: "#0d1117", border: "1px solid #1e3a5f",
          borderRadius: 5, padding: "5px 10px", fontSize: 11,
          fontFamily: "monospace",
        }}>
          <span style={{ color: "#ffd740" }}>[TX]</span>{" "}
          <span style={{ color: "#80cbc4" }}>{e.node || "?"}</span>{" "}
          <span style={{ color: "#aaa" }}>{e.event || e.action || JSON.stringify(e)}</span>{" "}
          <span style={{ color: "#444" }}>{new Date(e.ts).toLocaleTimeString()}</span>
        </div>
      ))}
    </div>
  );
}
