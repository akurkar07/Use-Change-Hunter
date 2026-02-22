"use client";

import React, { useRef, useEffect, useState } from "react";
import { Property, OpportunityScore } from "@/types";
import { AlertCircle } from "lucide-react";

// Dynamic import for Leaflet to avoid SSR issues
import dynamic from "next/dynamic";

const DynamicMap = dynamic(() => import("./MapContent"), {
  ssr: false,
  loading: () => <MapLoader />,
});

interface MapProps {
  properties?: Property[];
  scores?: Record<string, OpportunityScore>;
  center?: [number, number]; // [lat, lng]
  zoom?: number;
  onPropertyClick?: (propertyId: string) => void;
  isLoading?: boolean;
}

export const Map: React.FC<MapProps> = ({
  properties = [],
  scores = {},
  center = [51.5074, -0.1278], // London
  zoom = 12,
  onPropertyClick,
  isLoading = false,
}) => {
  return (
    <div className="w-full h-full rounded-lg overflow-hidden border border-slate-200">
      {isLoading && <MapLoader />}
      {!isLoading && (
        <DynamicMap
          properties={properties}
          scores={scores}
          center={center}
          zoom={zoom}
          onPropertyClick={onPropertyClick}
        />
      )}
    </div>
  );
};

const MapLoader: React.FC = () => (
  <div className="w-full h-full flex items-center justify-center bg-slate-100">
    <div className="text-center">
      <div className="w-12 h-12 rounded-full border-4 border-slate-300 border-t-primary-600 animate-spin mx-auto mb-3" />
      <p className="text-sm text-slate-600">Loading map...</p>
    </div>
  </div>
);

interface MapContentProps {
  properties: Property[];
  scores: Record<string, OpportunityScore>;
  center: [number, number];
  zoom: number;
  onPropertyClick?: (propertyId: string) => void;
}

const MapContent: React.FC<MapContentProps> = ({
  properties,
  scores,
  center,
  zoom,
  onPropertyClick,
}) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<any>(null);
  const [mapL, setMapL] = useState<typeof import("leaflet")>();
  const markersRef = useRef<Map<string, any>>(new Map());
  const [error, setError] = useState<string>("");

  useEffect(() => {
    // Import Leaflet
    import("leaflet")
      .then((L) => {
        setMapL(L);

        if (map.current) return; // Map already initialized

        if (!mapContainer.current) return;

        // Initialize map
        map.current = L.map(mapContainer.current).setView(center, zoom);

        // Add tile layer
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
          attribution: "© OpenStreetMap contributors",
          maxZoom: 19,
        }).addTo(map.current);
      })
      .catch(() => {
        setError("Failed to load map library");
      });
  }, [center, zoom]);

  // Add markers for properties
  useEffect(() => {
    if (!mapL || !map.current) return;

    // Clear existing markers
    markersRef.current.forEach((marker) => marker.remove());
    markersRef.current.clear();

    // Add new markers
    properties.forEach((property) => {
      if (property.latitude === null || property.longitude === null) return;

      const score = scores[property.id];
      const scoreValue = score?.score_total || 0;

      // Determine color based on score
      let color = "#ef4444"; // red
      if (scoreValue >= 70)
        color = "#22c55e"; // green
      else if (scoreValue >= 50) color = "#eab308"; // yellow

      const marker = mapL
        .circleMarker([property.latitude, property.longitude], {
          radius: 8,
          fillColor: color,
          color: color,
          weight: 2,
          opacity: 0.8,
          fillOpacity: 0.8,
        })
        .bindPopup(
          `
          <div class="text-sm">
            <p class="font-bold">${property.address}</p>
            <p class="text-slate-600 text-xs">${property.postcode}</p>
            ${score ? `<p class="font-semibold text-primary-600">Score: ${Math.round(score.score_total)}</p>` : ""}
          </div>
        `,
          { maxWidth: 250 },
        )
        .on("click", () => {
          if (onPropertyClick) {
            onPropertyClick(property.id);
          }
        })
        .addTo(map.current);

      markersRef.current.set(property.id, marker);
    });
  }, [mapL, properties, scores, onPropertyClick]);

  if (error) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-slate-100">
        <div className="text-center">
          <AlertCircle size={32} className="text-danger-600 mx-auto mb-2" />
          <p className="text-sm text-danger-700">{error}</p>
        </div>
      </div>
    );
  }

  return <div ref={mapContainer} className="w-full h-full" />;
};

export default MapContent;
