import React, { useEffect, useRef } from "react";
import { MapContainer, TileLayer, CircleMarker, Polyline, Tooltip, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";

const NODE_COLORS = {
  online:  "#00e5ff",
  offline: "#ff1744",
  standby: "#ffd740",
  active:  "#69f0ae",
};

const TYPE_RADIUS = {
  ground: 8,
  drone:  10,
  sdn:    12,
};

function FitBounds({ nodes }) {
  const map = useMap();
  useEffect(() => {
    if (nodes.length > 0) {
      const lats = nodes.map((n) => n.lat);
      const lons = nodes.map((n) => n.lon);
      map.fitBounds([
        [Math.min(...lats) - 0.005, Math.min(...lons) - 0.005],
        [Math.max(...lats) + 0.005, Math.max(...lons) + 0.005],
      ]);
    }
  }, []);  // eslint-disable-line
  return null;
}

export default function TopologyMap({ topology, onNodeClick }) {
  const { nodes, edges } = topology;

  const nodeIndex = {};
  nodes.forEach((n) => (nodeIndex[n.id] = n));

  return (
    <div style={{ height: "100%", width: "100%", borderRadius: 8, overflow: "hidden" }}>
      <MapContainer
        center={[28.610, 77.218]}
        zoom={14}
        style={{ height: "100%", width: "100%" }}
        attributionControl={false}
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution="&copy; CartoDB"
        />
        <FitBounds nodes={nodes} />

        {edges.map((e, i) => {
          const src = nodeIndex[e.source];
          const dst = nodeIndex[e.target];
          if (!src || !dst) return null;
          return (
            <Polyline
              key={i}
              positions={[[src.lat, src.lon], [dst.lat, dst.lon]]}
              pathOptions={{
                color: e.active ? "#00e5ff" : "#333",
                weight: e.active ? 1.5 : 0.5,
                opacity: e.active ? 0.6 : 0.2,
                dashArray: e.active ? null : "4 4",
              }}
            />
          );
        })}

        {nodes.map((n) => (
          <CircleMarker
            key={n.id}
            center={[n.lat, n.lon]}
            radius={TYPE_RADIUS[n.type] || 8}
            pathOptions={{
              color: NODE_COLORS[n.status] || "#888",
              fillColor: NODE_COLORS[n.status] || "#888",
              fillOpacity: 0.85,
              weight: 2,
            }}
            eventHandlers={{ click: () => onNodeClick?.(n) }}
          >
            <Tooltip permanent={n.type === "sdn"} direction="top" offset={[0, -10]}>
              <span style={{ fontSize: 11 }}>
                <strong>{n.id}</strong> [{n.status}] load: {(n.load * 100).toFixed(0)}%
              </span>
            </Tooltip>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  );
}
