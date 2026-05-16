import React, { useState } from "react";
import axios from "axios";

const SIM_URL = process.env.REACT_APP_SIM_URL || "http://localhost:5003";

const DISASTERS = [
  { id: "earthquake",  label: "Earthquake",   color: "#ff6d00", icon: "🌍" },
  { id: "flood",       label: "Flood",         color: "#0288d1", icon: "🌊" },
  { id: "cyberattack", label: "Cyberattack",   color: "#aa00ff", icon: "💻" },
  { id: "shutdown",    label: "Shutdown",      color: "#e53935", icon: "📵" },
  { id: "cyclone",     label: "Cyclone",       color: "#00838f", icon: "🌀" },
];

export default function DisasterControls() {
  const [active, setActive]   = useState(null);
  const [result, setResult]   = useState(null);
  const [busy, setBusy]       = useState(false);

  const trigger = async (type) => {
    setBusy(true);
    setActive(type);
    setResult(null);
    try {
      const res = await axios.post(`${SIM_URL}/disaster/${type}`);
      setResult(res.data);
    } catch (e) {
      setResult({ error: "Simulator unreachable — is mesh-sim running?" });
    } finally {
      setBusy(false);
    }
  };

  return (
    <div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginBottom: 10 }}>
        {DISASTERS.map((d) => (
          <button
            key={d.id}
            disabled={busy}
            onClick={() => trigger(d.id)}
            style={{
              background:    active === d.id ? d.color : "#1a1f2e",
              color:         active === d.id ? "#fff" : "#ccc",
              border:        `1px solid ${d.color}`,
              borderRadius:  6,
              padding:       "5px 10px",
              cursor:        "pointer",
              fontSize:      12,
              fontWeight:    active === d.id ? 700 : 400,
            }}
          >
            {d.icon} {d.label}
          </button>
        ))}
      </div>

      {result && !result.error && (
        <div style={{ background: "#0d1117", borderRadius: 6, padding: 8, fontSize: 11 }}>
          <div style={{ color: "#ff6d00", fontWeight: 700 }}>DISASTER TRIGGERED</div>
          <div style={{ color: "#aaa", marginTop: 4 }}>{result.description}</div>
          <div style={{ color: "#ff5252", marginTop: 4 }}>
            Nodes affected: {(result.nodes_killed || []).join(", ")}
          </div>
          <div style={{ color: "#40c4ff" }}>
            Drones deploying: {(result.drones_queued || []).join(", ")}
          </div>
          <div style={{ color: "#69f0ae" }}>
            Auto-recovery ETA: {result.recovery_eta_s}s
          </div>
        </div>
      )}
      {result?.error && (
        <div style={{ color: "#ff5252", fontSize: 11 }}>{result.error}</div>
      )}
    </div>
  );
}
