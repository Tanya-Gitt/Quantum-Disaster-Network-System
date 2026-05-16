import { useEffect, useRef, useState } from "react";
import { io } from "socket.io-client";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:5000";

export function useSocket() {
  const socketRef = useRef(null);
  const [topology, setTopology]       = useState({ nodes: [], edges: [] });
  const [sosAlerts, setSosAlerts]     = useState([]);
  const [aiRouting, setAiRouting]     = useState(null);
  const [pqcStatus, setPqcStatus]     = useState(null);
  const [blockchainEvents, setBlockchainEvents] = useState([]);
  const [connected, setConnected]     = useState(false);

  useEffect(() => {
    const socket = io(API_URL, { transports: ["websocket", "polling"] });
    socketRef.current = socket;

    socket.on("connect",          ()  => setConnected(true));
    socket.on("disconnect",       ()  => setConnected(false));
    socket.on("topology_update",  (d) => setTopology(d));
    socket.on("sos_alert",        (d) => setSosAlerts((prev) => [{ ...d, ts: Date.now() }, ...prev].slice(0, 20)));
    socket.on("ai_routing",       (d) => setAiRouting(d));
    socket.on("pqc_status",       (d) => setPqcStatus(d));
    socket.on("blockchain_event", (d) => setBlockchainEvents((prev) => [{ ...d, ts: Date.now() }, ...prev].slice(0, 50)));

    return () => socket.disconnect();
  }, []);

  const sendSOS = (msg) => {
    socketRef.current?.emit("sos_broadcast", { message: msg, ts: Date.now() });
  };

  return { connected, topology, sosAlerts, aiRouting, pqcStatus, blockchainEvents, sendSOS };
}
