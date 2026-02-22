"use client";

import React from "react";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { ScoreBadge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Property, OpportunityScore } from "@/types";
import { MapPin, Zap } from "lucide-react";

interface PropertyCardProps {
  property: Property;
  score?: OpportunityScore;
  onView?: (propertyId: string) => void;
  onExport?: (propertyId: string) => void;
}

export const PropertyCard: React.FC<PropertyCardProps> = ({
  property,
  score,
  onView,
  onExport,
}) => {
  const getStrategyColor = (strategy: string) => {
    const colors: Record<string, string> = {
      extension: "bg-blue-50 text-blue-900 border-blue-200",
      hmo: "bg-purple-50 text-purple-900 border-purple-200",
      office_residential: "bg-amber-50 text-amber-900 border-amber-200",
      retail_mixed: "bg-emerald-50 text-emerald-900 border-emerald-200",
      flats: "bg-pink-50 text-pink-900 border-pink-200",
    };
    return colors[strategy] || "bg-slate-50 text-slate-900 border-slate-200";
  };

  const strategyLabels: Record<string, string> = {
    extension: "Extension",
    hmo: "HMO",
    office_residential: "Office → Residential",
    retail_mixed: "Retail → Mixed-Use",
    flats: "Conversion to Flats",
  };

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader>
        <div className="flex items-start justify-between mb-2">
          <h3 className="text-lg font-bold text-slate-900 flex-1">
            {property.address}
          </h3>
          {score && (
            <ScoreBadge
              score={score.score_total}
              size="md"
              className="flex-shrink-0"
            />
          )}
        </div>
        <p className="text-sm text-slate-600 flex items-center gap-1">
          <MapPin size={14} /> {property.postcode}
        </p>
      </CardHeader>

      <CardBody>
        {/* Property Details */}
        <div className="grid grid-cols-2 gap-4 mb-4 py-3 border-y border-slate-200">
          {property.historic_use && (
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wide">
                Current Use
              </p>
              <p className="text-sm font-medium text-slate-900">
                {property.historic_use}
              </p>
            </div>
          )}
          {property.area_sqm && (
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wide">
                Area
              </p>
              <p className="text-sm font-medium text-slate-900">
                {property.area_sqm.toLocaleString()} m²
              </p>
            </div>
          )}
          {property.listed_status && (
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wide">
                Listed Status
              </p>
              <p className="text-sm font-medium text-slate-900">
                {property.listed_status}
              </p>
            </div>
          )}
          {property.distance_nearest_precedent !== undefined && (
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wide">
                Nearest Precedent
              </p>
              <p className="text-sm font-medium text-slate-900">
                {(property.distance_nearest_precedent / 1000).toFixed(2)}km
              </p>
            </div>
          )}
        </div>

        {/* Opportunity Strategies */}
        {property.opportunity_strategies &&
          property.opportunity_strategies.length > 0 && (
            <div className="mb-4">
              <p className="text-xs text-slate-500 uppercase tracking-wide mb-2">
                Opportunities
              </p>
              <div className="flex flex-wrap gap-2">
                {property.opportunity_strategies.map((strategy) => (
                  <span
                    key={strategy}
                    className={`text-xs font-medium px-2.5 py-1 rounded border ${getStrategyColor(strategy)}`}
                  >
                    {strategyLabels[strategy] || strategy}
                  </span>
                ))}
              </div>
            </div>
          )}

        {/* Score Breakdown */}
        {score && (
          <div className="mb-4 p-3 bg-slate-50 rounded border border-slate-200">
            <div className="flex items-center gap-2 mb-2">
              <Zap size={14} className="text-amber-500" />
              <p className="text-sm font-medium text-slate-900">Quick Stats</p>
            </div>
            <div className="grid grid-cols-3 gap-2 text-xs">
              <div>
                <p className="text-slate-600">Precedents</p>
                <p className="font-bold text-slate-900">
                  {score.score_breakdown?.precedents_found || 0}
                </p>
              </div>
              <div>
                <p className="text-slate-600">Approval Rate</p>
                <p className="font-bold text-slate-900">
                  {score.score_breakdown?.approval_rate
                    ? `${Math.round(score.score_breakdown.approval_rate * 100)}%`
                    : "N/A"}
                </p>
              </div>
              <div>
                <p className="text-slate-600">Risk Score</p>
                <p className="font-bold text-slate-900">
                  {Math.round(score.score_risk)}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-2 pt-2 border-t border-slate-200">
          {onView && (
            <Button
              variant="primary"
              size="sm"
              onClick={() => onView(property.id)}
              className="flex-1"
            >
              View Details
            </Button>
          )}
          {onExport && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => onExport(property.id)}
              className="flex-1"
            >
              Export
            </Button>
          )}
        </div>
      </CardBody>
    </Card>
  );
};

interface PropertyGridProps {
  properties: Property[];
  scores?: Record<string, OpportunityScore>;
  isLoading?: boolean;
  onViewProperty?: (propertyId: string) => void;
  onExportProperty?: (propertyId: string) => void;
}

export const PropertyGrid: React.FC<PropertyGridProps> = ({
  properties,
  scores = {},
  isLoading = false,
  onViewProperty,
  onExportProperty,
}) => {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Array(6)
          .fill(0)
          .map((_, i) => (
            <div key={i} className="h-80 bg-slate-200 rounded animate-pulse" />
          ))}
      </div>
    );
  }

  if (!properties || properties.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-slate-500 text-lg">
          No properties found. Try adjusting your search.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {properties.map((property) => (
        <PropertyCard
          key={property.id}
          property={property}
          score={scores[property.id]}
          onView={onViewProperty}
          onExport={onExportProperty}
        />
      ))}
    </div>
  );
};
