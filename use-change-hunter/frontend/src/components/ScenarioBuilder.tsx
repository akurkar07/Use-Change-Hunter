"use client";

import React, { useState } from "react";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input, Select, TextArea } from "@/components/ui/Input";
import { Scenario, ScenarioBreakdown } from "@/types";
import { TrendingUp, BarChart3, AlertCircle } from "lucide-react";

interface ScenarioBuilderProps {
  initialScenario?: Scenario;
  onSave?: (scenario: Partial<Scenario>) => Promise<void>;
  isLoading?: boolean;
}

export const ScenarioBuilder: React.FC<ScenarioBuilderProps> = ({
  initialScenario,
  onSave,
  isLoading = false,
}) => {
  const [formData, setFormData] = useState<Partial<Scenario>>({
    name: initialScenario?.name || "",
    strategy: initialScenario?.strategy || "extension",
    development_cost: initialScenario?.development_cost || 0,
    holding_period_months: initialScenario?.holding_period_months || 24,
    finance_type: initialScenario?.finance_type || "cash",
    finance_rate: initialScenario?.finance_rate || 0.05,
    assumptions: initialScenario?.assumptions || "",
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [breakdown, setBreakdown] = useState<ScenarioBreakdown | null>(null);

  const handleChange = (field: string, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error for this field when user starts typing
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: "" }));
    }
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.name?.trim()) {
      newErrors.name = "Scenario name is required";
    }
    if (!formData.strategy) {
      newErrors.strategy = "Strategy is required";
    }
    if ((formData.development_cost || 0) < 0) {
      newErrors.development_cost = "Development cost must be positive";
    }
    if ((formData.holding_period_months || 0) < 1) {
      newErrors.holding_period_months =
        "Holding period must be at least 1 month";
    }
    if ((formData.finance_rate || 0) < 0) {
      newErrors.finance_rate = "Finance rate must be positive";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleCalculateBreakdown = () => {
    if (!validateForm()) return;

    // Simulate financial calculations
    const devCost = formData.development_cost || 0;
    const holdingMonths = formData.holding_period_months || 24;
    const financeRate = formData.finance_rate || 0.05;

    // Rough assumptions for demo
    const purchasePrice = 350000; // Mock base value
    const arv = purchasePrice + devCost * 1.3; // Assume 30% value uplift
    const financeAmount = devCost * 0.7; // 70% LTV
    const monthlyInterest = financeAmount * (financeRate / 12) * holdingMonths;
    const otherCosts = devCost * 0.15; // 15% soft costs
    const totalCost = devCost + monthlyInterest + otherCosts;
    const profit = arv - purchasePrice - totalCost;
    const roi = (profit / (purchasePrice + devCost)) * 100;

    setBreakdown({
      estimated_arv: arv,
      estimated_cost: totalCost,
      estimated_profit: profit,
      roi_percent: roi,
      holding_months: holdingMonths,
      financing_cost: monthlyInterest,
    });
  };

  const handleSave = async () => {
    if (!validateForm()) return;
    if (onSave) {
      try {
        await onSave(formData);
      } catch (error) {
        setErrors({ submit: "Failed to save scenario" });
      }
    }
  };

  const strategyLabels: Record<string, string> = {
    extension: "House Extension",
    hmo: "Convert to HMO",
    office_residential: "Office → Residential",
    retail_mixed: "Retail → Mixed-Use",
    flats: "Convert to Flats",
  };

  const financeTypes = [
    { value: "cash", label: "Cash Purchase" },
    { value: "btl_mortgage", label: "BTL Mortgage" },
    { value: "development_loan", label: "Development Loan" },
  ];

  return (
    <div className="space-y-4">
      {/* Input Form */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-bold text-slate-900">
            Scenario Parameters
          </h3>
          <p className="text-sm text-slate-600 mt-1">
            Configure development assumptions
          </p>
        </CardHeader>

        <CardBody className="space-y-4">
          {/* Scenario Name */}
          <div>
            <Input
              label="Scenario Name"
              placeholder="e.g., 'Aggressive Extension Strategy'"
              value={formData.name || ""}
              onChange={(e) => handleChange("name", e.target.value)}
              error={errors.name}
            />
          </div>

          {/* Strategy Selection */}
          <div>
            <Select
              label="Development Strategy"
              value={formData.strategy || ""}
              onChange={(e) => handleChange("strategy", e.target.value)}
              error={errors.strategy}
            >
              {Object.entries(strategyLabels).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </Select>
          </div>

          {/* Development Cost */}
          <div>
            <Input
              label="Development Cost (£)"
              type="number"
              placeholder="50000"
              value={formData.development_cost || ""}
              onChange={(e) =>
                handleChange("development_cost", parseFloat(e.target.value))
              }
              error={errors.development_cost}
            />
            <p className="text-xs text-slate-500 mt-1">
              Estimated cost for all construction and professional fees
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            {/* Holding Period */}
            <div>
              <Input
                label="Holding Period (Months)"
                type="number"
                placeholder="24"
                value={formData.holding_period_months || ""}
                onChange={(e) =>
                  handleChange(
                    "holding_period_months",
                    parseInt(e.target.value),
                  )
                }
                error={errors.holding_period_months}
              />
            </div>

            {/* Finance Type */}
            <div>
              <Select
                label="Financing Type"
                value={formData.finance_type || ""}
                onChange={(e) => handleChange("finance_type", e.target.value)}
              >
                {financeTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </Select>
            </div>
          </div>

          {/* Finance Rate */}
          <div>
            <Input
              label="Annual Finance Rate (%)"
              type="number"
              placeholder="5.0"
              step="0.1"
              value={
                formData.finance_rate
                  ? (formData.finance_rate * 100).toFixed(1)
                  : ""
              }
              onChange={(e) =>
                handleChange("finance_rate", parseFloat(e.target.value) / 100)
              }
              error={errors.finance_rate}
            />
            <p className="text-xs text-slate-500 mt-1">
              Annual interest rate for debt financing
            </p>
          </div>

          {/* Assumptions */}
          <div>
            <TextArea
              label="Additional Assumptions"
              placeholder="e.g., Planning permission granted, No building issues, Market growth 3% annually"
              value={formData.assumptions || ""}
              onChange={(e) => handleChange("assumptions", e.target.value)}
              rows={3}
            />
          </div>

          {/* Error Message */}
          {errors.submit && (
            <div className="p-3 bg-danger-50 border border-danger-200 rounded flex gap-2">
              <AlertCircle
                size={16}
                className="text-danger-600 flex-shrink-0 mt-0.5"
              />
              <p className="text-sm text-danger-700">{errors.submit}</p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-2 pt-2 border-t border-slate-200">
            <Button
              variant="primary"
              onClick={handleCalculateBreakdown}
              disabled={isLoading}
              className="flex-1"
            >
              <BarChart3 size={16} />
              Calculate Breakdown
            </Button>
            {onSave && (
              <Button
                variant="secondary"
                onClick={handleSave}
                disabled={isLoading}
                className="flex-1"
              >
                Save Scenario
              </Button>
            )}
          </div>
        </CardBody>
      </Card>

      {/* Financial Breakdown */}
      {breakdown && (
        <Card className="border-success-200 bg-success-50">
          <CardHeader>
            <h3 className="text-lg font-bold text-success-900 flex items-center gap-2">
              <TrendingUp size={20} /> Financial Breakdown
            </h3>
          </CardHeader>

          <CardBody>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              {/* Purchase + Development */}
              <BreakdownItem
                label="Total Investment"
                value={`£${((formData.development_cost || 0) + 350000).toLocaleString("en-GB", { maximumFractionDigits: 0 })}`}
                subtext="Purchase + Development"
              />

              {/* Estimated ARV */}
              <BreakdownItem
                label="Estimated ARV"
                value={`£${breakdown.estimated_arv.toLocaleString("en-GB", { maximumFractionDigits: 0 })}`}
                subtext="After value uplift"
              />

              {/* Profit */}
              <BreakdownItem
                label="Estimated Profit"
                value={`£${breakdown.estimated_profit.toLocaleString("en-GB", { maximumFractionDigits: 0 })}`}
                subtext={`${breakdown.roi_percent.toFixed(1)}% ROI`}
                highlight={breakdown.roi_percent > 15}
              />
            </div>

            {/* Detailed Breakdown */}
            <div className="space-y-2 text-sm">
              <div className="flex justify-between py-2 border-b border-slate-200">
                <span className="text-slate-700">Development Cost</span>
                <span className="font-medium">
                  £{(formData.development_cost || 0).toLocaleString("en-GB")}
                </span>
              </div>
              <div className="flex justify-between py-2 border-b border-slate-200">
                <span className="text-slate-700">
                  Financing Cost ({breakdown.holding_months} months)
                </span>
                <span className="font-medium">
                  £
                  {breakdown.financing_cost.toLocaleString("en-GB", {
                    maximumFractionDigits: 0,
                  })}
                </span>
              </div>
              <div className="flex justify-between py-2 border-b border-slate-200">
                <span className="text-slate-700">Other Costs (est.)</span>
                <span className="font-medium">
                  £
                  {((formData.development_cost || 0) * 0.15).toLocaleString(
                    "en-GB",
                  )}
                </span>
              </div>
              <div className="flex justify-between py-2 text-success-900 font-bold">
                <span>Net Profit</span>
                <span>
                  £
                  {breakdown.estimated_profit.toLocaleString("en-GB", {
                    maximumFractionDigits: 0,
                  })}
                </span>
              </div>
            </div>

            <p className="text-xs text-slate-600 mt-4 p-2 bg-white rounded">
              ⚠️ This is a rough estimate based on typical market conditions.
              Always consult with a financial advisor before proceeding.
            </p>
          </CardBody>
        </Card>
      )}
    </div>
  );
};

interface BreakdownItemProps {
  label: string;
  value: string;
  subtext?: string;
  highlight?: boolean;
}

const BreakdownItem: React.FC<BreakdownItemProps> = ({
  label,
  value,
  subtext,
  highlight,
}) => (
  <div
    className={`p-4 rounded-lg ${highlight ? "bg-success-100 border border-success-300" : "bg-white border border-success-200"}`}
  >
    <p className="text-xs text-slate-600 uppercase tracking-wide mb-1">
      {label}
    </p>
    <p
      className={`text-xl font-bold ${highlight ? "text-success-900" : "text-slate-900"}`}
    >
      {value}
    </p>
    {subtext && <p className="text-xs text-slate-600 mt-1">{subtext}</p>}
  </div>
);
