"use client";

import React from "react";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Precedent } from "@/types";
import { MapPin, Calendar, CheckCircle, X } from "lucide-react";

interface PrecedentsListProps {
  precedents: Precedent[];
  isLoading?: boolean;
}

export const PrecedentsList: React.FC<PrecedentsListProps> = ({
  precedents,
  isLoading = false,
}) => {
  if (isLoading) {
    return (
      <Card>
        <CardBody>
          <div className="space-y-4">
            {Array(3)
              .fill(0)
              .map((_, i) => (
                <div
                  key={i}
                  className="h-20 bg-slate-200 rounded animate-pulse"
                />
              ))}
          </div>
        </CardBody>
      </Card>
    );
  }

  if (!precedents || precedents.length === 0) {
    return (
      <Card>
        <CardBody className="text-center py-8">
          <p className="text-slate-500">No precedents found in this area</p>
        </CardBody>
      </Card>
    );
  }

  const approved = precedents.filter((p) => p.decision === "approved");
  const refused = precedents.filter((p) => p.decision === "refused");

  return (
    <Card>
      <CardHeader>
        <h3 className="text-lg font-bold text-slate-900">
          Planning Precedents
        </h3>
        <p className="text-sm text-slate-600 mt-1">
          {approved.length} Approved · {refused.length} Refused
        </p>
      </CardHeader>

      <CardBody className="space-y-0">
        {/* Approved Section */}
        {approved.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-success-700 mb-3 flex items-center gap-2">
              <CheckCircle size={16} /> Approved ({approved.length})
            </h4>
            <div className="space-y-3 mb-6">
              {approved.map((precedent) => (
                <PrecedentCard
                  key={precedent.reference}
                  precedent={precedent}
                />
              ))}
            </div>
          </div>
        )}

        {/* Refused Section */}
        {refused.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-danger-700 mb-3 flex items-center gap-2">
              <X size={16} /> Refused ({refused.length})
            </h4>
            <div className="space-y-3">
              {refused.map((precedent) => (
                <PrecedentCard
                  key={precedent.reference}
                  precedent={precedent}
                />
              ))}
            </div>
          </div>
        )}
      </CardBody>
    </Card>
  );
};

interface PrecedentCardProps {
  precedent: Precedent;
}

const PrecedentCard: React.FC<PrecedentCardProps> = ({ precedent }) => {
  const decisionStyles = {
    approved: {
      badge: "success",
      icon: <CheckCircle size={16} className="text-success-600" />,
      text: "Approved",
    },
    refused: {
      badge: "danger",
      icon: <X size={16} className="text-danger-600" />,
      text: "Refused",
    },
    withdrawn: {
      badge: "warning",
      icon: <span className="text-warning-600">-</span>,
      text: "Withdrawn",
    },
    other: {
      badge: "default",
      icon: <span className="text-slate-600">?</span>,
      text: "Other",
    },
  };

  const style = decisionStyles[precedent.decision] || decisionStyles.other;

  return (
    <div className="p-4 bg-slate-50 rounded-lg border border-slate-200 hover:border-slate-300 transition-colors">
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 mt-1">{style.icon}</div>

        <div className="flex-1 min-w-0">
          {/* Reference and Badge */}
          <div className="flex items-center gap-2 mb-2">
            <p className="text-sm font-mono text-slate-600">
              {precedent.reference}
            </p>
            <Badge variant={style.badge as any} size="sm">
              {style.text}
            </Badge>
          </div>

          {/* Proposal */}
          <p className="text-sm text-slate-800 mb-2 line-clamp-2">
            {precedent.proposal}
          </p>

          {/* Meta Info */}
          <div className="flex gap-4 text-xs text-slate-500">
            {precedent.distance_m !== undefined && (
              <span className="flex items-center gap-1">
                <MapPin size={12} /> {(precedent.distance_m / 1000).toFixed(2)}
                km away
              </span>
            )}
            {precedent.date_decided && (
              <span className="flex items-center gap-1">
                <Calendar size={12} />{" "}
                {new Date(precedent.date_decided).toLocaleDateString()}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
