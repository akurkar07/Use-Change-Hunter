"use client";

import React from "react";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { ScoreBadge, Badge } from "@/components/ui/Badge";
import { OpportunityScore, ScoreBreakdown } from "@/types";
import { TrendingUp, AlertCircle, Zap } from "lucide-react";

interface ScoreCardProps {
  score: OpportunityScore;
  compact?: boolean;
}

export const ScoreCard: React.FC<ScoreCardProps> = ({
  score,
  compact = false,
}) => {
  const breakdown: ScoreBreakdown = score.breakdown || {};

  const getScoreInterpretation = (value: number) => {
    if (value >= 70) return { text: "Strong Opportunity", color: "success" };
    if (value >= 50) return { text: "Moderate Opportunity", color: "warning" };
    return { text: "Limited Opportunity", color: "danger" };
  };

  const interpretation = getScoreInterpretation(score.score_total);

  if (compact) {
    return (
      <div className="flex items-center gap-4">
        <ScoreBadge score={score.score_total} size="sm" />
        <div>
          <p className="text-sm font-medium text-slate-600">
            Opportunity Score
          </p>
          <p className="text-lg font-bold text-slate-900">
            {interpretation.text}
          </p>
        </div>
      </div>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-bold text-slate-900">
            Opportunity Analysis
          </h3>
          <Badge variant={interpretation.color as any}>
            {score.strategy_type.replace("_", " ").toUpperCase()}
          </Badge>
        </div>
      </CardHeader>

      <CardBody>
        {/* Score Badges */}
        <div className="grid grid-cols-3 gap-4">
          <div className="flex flex-col items-center">
            <ScoreBadge score={score.score_total} size="md" />
            <p className="mt-2 text-xs text-slate-600 text-center">
              Opportunity
            </p>
          </div>
          <div className="flex flex-col items-center">
            <ScoreBadge score={score.score_risk} size="md" />
            <p className="mt-2 text-xs text-slate-600 text-center">Risk</p>
          </div>
          <div className="flex flex-col items-center">
            <ScoreBadge score={score.score_confidence} size="md" />
            <p className="mt-2 text-xs text-slate-600 text-center">
              Confidence
            </p>
          </div>
        </div>

        {/* Interpretation */}
        <div className="mt-6 p-4 bg-primary-50 rounded-lg border border-primary-200">
          <p className="text-sm text-primary-900 flex items-center gap-2">
            <Zap size={16} />
            <strong>{interpretation.text}</strong> - Based on nearby planning
            precedents
          </p>
        </div>

        {/* Breakdown */}
        <div className="mt-6 space-y-3">
          <h4 className="text-sm font-semibold text-slate-900">
            Score Breakdown
          </h4>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="flex justify-between items-center p-3 bg-slate-50 rounded">
              <span className="text-slate-600">Matched Precedents</span>
              <span className="font-bold text-slate-900">
                {breakdown.matched_precedents || 0}
              </span>
            </div>
            <div className="flex justify-between items-center p-3 bg-slate-50 rounded">
              <span className="text-slate-600">Approved Similar</span>
              <span className="font-bold text-success-600">
                {breakdown.approved_similar || 0}
              </span>
            </div>
            <div className="flex justify-between items-center p-3 bg-slate-50 rounded">
              <span className="text-slate-600">Refused Similar</span>
              <span className="font-bold text-danger-600">
                {breakdown.refused_similar || 0}
              </span>
            </div>
            {breakdown.refusal_rate !== undefined && (
              <div className="flex justify-between items-center p-3 bg-slate-50 rounded">
                <span className="text-slate-600">Refusal Rate</span>
                <span className="font-bold text-slate-900">
                  {(breakdown.refusal_rate * 100).toFixed(0)}%
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Risk Alert */}
        {score.score_risk > 60 && (
          <div className="mt-6 p-4 bg-warning-50 rounded-lg border border-warning-200 flex gap-3">
            <AlertCircle
              size={18}
              className="text-warning-600 flex-shrink-0 mt-0.5"
            />
            <div>
              <p className="text-sm font-semibold text-warning-900">
                High Risk
              </p>
              <p className="text-xs text-warning-800 mt-1">
                This area shows higher refusal rates. Verify planning
                feasibility before proceeding.
              </p>
            </div>
          </div>
        )}

        {/* Generated At */}
        <p className="mt-4 text-xs text-slate-500">
          Generated: {new Date(score.generated_at).toLocaleDateString()}
        </p>
      </CardBody>
    </Card>
  );
};
