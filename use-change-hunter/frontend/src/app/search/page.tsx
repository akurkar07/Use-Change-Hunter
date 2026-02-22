"use client";

import React, { useMemo } from "react";
import { useRouter } from "next/navigation";
import { Map, PropertyGrid, ScoreCard } from "@/components/index";
import { Button } from "@/components/ui/Button";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { ArrowLeft, Sliders, LayoutGrid, Map as MapIcon } from "lucide-react";
import { useSearchStore } from "@/lib/stores/searchStore";
import { usePropertySearch } from "@/lib/hooks";

export default function SearchPage() {
  const router = useRouter();

  // Get state from Zustand store
  const {
    query,
    properties,
    scores,
    selectedPropertyId,
    isLoading,
    viewMode,
    setSelectedProperty,
    setViewMode,
  } = useSearchStore((state) => ({
    query: state.query,
    properties: state.properties,
    scores: state.scores,
    selectedPropertyId: state.selectedPropertyId,
    isLoading: state.isLoading,
    viewMode: state.viewMode || "grid",
    setSelectedProperty: state.setSelectedProperty,
    setViewMode: state.setViewMode || (() => {}),
  }));

  // Fetch search results with React Query
  const { properties: fetchedProperties, scores: fetchedScores, isLoading: queryLoading } =
    usePropertySearch(
      query.postcode,
      query.strategy,
      query.radius
    );

  // Sync React Query results to Zustand store on successful fetch
  React.useEffect(() => {
    if (fetchedProperties.length > 0) {
      useMemo(() => properties, [fetchedProperties]);
    }
  }, [fetchedProperties]);

  const displayProperties = fetchedProperties.length > 0 ? fetchedProperties : properties;
  const displayScores = fetchedScores || scores;

  const selectedPropertyData = selectedPropertyId
    ? displayProperties.find((p) => p.id === selectedPropertyId)
    : null;

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <div className="bg-white border-b border-slate-200 sticky top-16 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between mb-4">
            <button
              onClick={() => router.back()}
              className="flex items-center gap-2 text-slate-600 hover:text-slate-900"
            >
              <ArrowLeft size={20} />
              <span className="font-medium">Back</span>
            </button>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setViewMode?.("grid")}
                className={`p-2 rounded transition-colors ${
                  viewMode === "grid"
                    ? "bg-primary-100 text-primary-600"
                    : "text-slate-600 hover:bg-slate-100"
                }`}
              >
                <LayoutGrid size={20} />
              </button>
              <button
                onClick={() => setViewMode?.("map")}
                className={`p-2 rounded transition-colors ${
                  viewMode === "map"
                    ? "bg-primary-100 text-primary-600"
                    : "text-slate-600 hover:bg-slate-100"
                }`}
              >
                <MapIcon size={20} />
              </button>
              <button className="p-2 rounded hover:bg-slate-100 text-slate-600">
                <Sliders size={20} />
              </button>
            </div>
          </div>

          {/* Search Summary */}
          <div className="flex items-center gap-4">
            <div>
              <p className="text-sm text-slate-600">Current search</p>
              <p className="font-semibold text-slate-900">
                {query.postcode} • {query.strategy} • {query.radius}m radius
              </p>
            </div>
            <div className="ml-auto text-sm text-slate-600">
              {displayProperties.length} properties found
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {viewMode === "grid" ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Properties Grid */}
            <div className="lg:col-span-2">
              <PropertyGrid
                properties={displayProperties}
                scores={displayScores}
                isLoading={queryLoading || isLoading}
                onViewProperty={setSelectedProperty}
                onExportProperty={(id) => {
                  console.log("Export property:", id);
                }}
              />
            </div>

            {/* Side Panel - Selected Property Details */}
            <div className="lg:col-span-1">
              {selectedPropertyData ? (
                <div className="space-y-4 sticky top-32">
                  <Card>
                    <CardHeader>
                      <h3 className="font-bold text-slate-900">
                        Selected Property
                      </h3>
                    </CardHeader>

                    <CardBody className="space-y-6">
                      {/* Address */}
                      <div>
                        <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">
                          Address
                        </p>
                        <p className="font-semibold text-slate-900">
                          {selectedPropertyData.address}
                        </p>
                        <p className="text-sm text-slate-600 mt-1">
                          {selectedPropertyData.postcode}
                        </p>
                      </div>

                      {/* Score if available */}
                      {displayScores[selectedPropertyData.id] && (
                        <ScoreCard score={displayScores[selectedPropertyData.id]} />
                      )}

                      {/* Actions */}
                      <div className="pt-4 border-t border-slate-200 space-y-2">
                        <Button
                          variant="primary"
                          onClick={() =>
                            router.push(`/property/${selectedPropertyData.id}`)
                          }
                          className="w-full"
                        >
                          View Full Details
                        </Button>
                        <Button variant="outline" className="w-full">
                          Export Report
                        </Button>
                      </div>
                    </CardBody>
                  </Card>
                </div>
              ) : (
                <Card>
                  <CardBody className="text-center py-8">
                    <p className="text-slate-500">
                      Select a property to view details
                    </p>
                  </CardBody>
                </Card>
              )}
            </div>
          </div>
        ) : (
          // Map View
          <div className="h-[calc(100vh-200px)] rounded-lg overflow-hidden">
            <Map
              properties={displayProperties}
              scores={displayScores}
              isLoading={queryLoading || isLoading}
              onPropertyClick={setSelectedProperty}
            />
          </div>
        )}
      </div>
    </div>
  );
}
