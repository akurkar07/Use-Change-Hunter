"use client";

import React, { useState } from "react";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input, Select, TextArea } from "@/components/ui/Input";
import { Download, FileText, AlertCircle, CheckCircle } from "lucide-react";

interface ExportDialogProps {
  propertyAddress?: string;
  onExport: (
    format: "pdf" | "excel" | "json",
    options: ExportOptions,
  ) => Promise<void>;
  isLoading?: boolean;
}

interface ExportOptions {
  includeScoring: boolean;
  includePrecedents: boolean;
  includeScenarios: boolean;
  includeAnalysis: boolean;
  reportName?: string;
}

export const ExportDialog: React.FC<ExportDialogProps> = ({
  propertyAddress,
  onExport,
  isLoading = false,
}) => {
  const [format, setFormat] = useState<"pdf" | "excel" | "json">("pdf");
  const [options, setOptions] = useState<ExportOptions>({
    includeScoring: true,
    includePrecedents: true,
    includeScenarios: true,
    includeAnalysis: true,
    reportName: `Report-${new Date().toISOString().split("T")[0]}`,
  });
  const [status, setStatus] = useState<
    "idle" | "loading" | "success" | "error"
  >("idle");
  const [error, setError] = useState<string>("");

  const handleToggle = (key: keyof Omit<ExportOptions, "reportName">) => {
    setOptions((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const handleExport = async () => {
    try {
      setStatus("loading");
      setError("");
      await onExport(format, options);
      setStatus("success");
      setTimeout(() => setStatus("idle"), 3000);
    } catch (err) {
      setStatus("error");
      setError(err instanceof Error ? err.message : "Export failed");
    }
  };

  const formatLabels: Record<
    string,
    { label: string; description: string; icon: React.ReactNode }
  > = {
    pdf: {
      label: "PDF Report",
      description: "Professional formatted document for printing or sharing",
      icon: <FileText size={16} />,
    },
    excel: {
      label: "Excel Spreadsheet",
      description: "Detailed data with charts and financial models",
      icon: <FileText size={16} />,
    },
    json: {
      label: "JSON Data",
      description: "Raw data export for further analysis",
      icon: <FileText size={16} />,
    },
  };

  const selectedFormat = formatLabels[format];

  return (
    <div className="space-y-4">
      {/* Format Selection */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-bold text-slate-900">Export Format</h3>
        </CardHeader>

        <CardBody className="space-y-3">
          {Object.entries(formatLabels).map(
            ([key, { label, description, icon }]) => (
              <label
                key={key}
                className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                  format === key
                    ? "border-primary-500 bg-primary-50"
                    : "border-slate-200 bg-white hover:border-slate-300"
                }`}
              >
                <input
                  type="radio"
                  name="format"
                  value={key}
                  checked={format === key}
                  onChange={() => setFormat(key as any)}
                  className="sr-only"
                />
                <div className="flex items-start gap-3">
                  <div
                    className={`mt-1 ${format === key ? "text-primary-600" : "text-slate-600"}`}
                  >
                    {icon}
                  </div>
                  <div>
                    <p
                      className={`font-medium ${format === key ? "text-primary-900" : "text-slate-900"}`}
                    >
                      {label}
                    </p>
                    <p className="text-sm text-slate-600 mt-0.5">
                      {description}
                    </p>
                  </div>
                </div>
              </label>
            ),
          )}
        </CardBody>
      </Card>

      {/* Export Options */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-bold text-slate-900">
            Include in Export
          </h3>
        </CardHeader>

        <CardBody className="space-y-4">
          {/* Scoring Section */}
          <CheckboxOption
            checked={options.includeScoring}
            onChange={() => handleToggle("includeScoring")}
            label="Opportunity Scores"
            description="Total, opportunity, risk, and confidence scores"
          />

          {/* Precedents Section */}
          <CheckboxOption
            checked={options.includePrecedents}
            onChange={() => handleToggle("includePrecedents")}
            label="Planning Precedents"
            description="All relevant precedents found in the area"
          />

          {/* Scenarios Section */}
          <CheckboxOption
            checked={options.includeScenarios}
            onChange={() => handleToggle("includeScenarios")}
            label="Financial Scenarios"
            description="Development cost analysis and profit projections"
          />

          {/* Analysis Section */}
          <CheckboxOption
            checked={options.includeAnalysis}
            onChange={() => handleToggle("includeAnalysis")}
            label="Strategic Analysis"
            description="Planning history, constraints, and recommendations"
          />

          {/* Report Name */}
          <div className="pt-4 border-t border-slate-200">
            <Input
              label="Report Name"
              placeholder="e.g., '123 High Street - Analysis'"
              value={options.reportName || ""}
              onChange={(e) =>
                setOptions((prev) => ({ ...prev, reportName: e.target.value }))
              }
            />
            <p className="text-xs text-slate-500 mt-1">
              Used as filename for downloads. Special characters will be
              removed.
            </p>
          </div>
        </CardBody>
      </Card>

      {/* Status Messages */}
      {status === "success" && (
        <div className="p-4 bg-success-50 border border-success-200 rounded flex gap-3">
          <CheckCircle size={20} className="text-success-600 flex-shrink-0" />
          <div>
            <p className="font-medium text-success-900">Export Complete</p>
            <p className="text-sm text-success-800">
              Your file is ready to download.
            </p>
          </div>
        </div>
      )}

      {status === "error" && (
        <div className="p-4 bg-danger-50 border border-danger-200 rounded flex gap-3">
          <AlertCircle size={20} className="text-danger-600 flex-shrink-0" />
          <div>
            <p className="font-medium text-danger-900">Export Failed</p>
            <p className="text-sm text-danger-800">{error}</p>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-2">
        <Button
          variant="primary"
          size="lg"
          onClick={handleExport}
          disabled={isLoading || status === "loading"}
          className="flex-1"
        >
          <Download size={18} />
          Export as {selectedFormat.label}
        </Button>
      </div>

      {/* Info */}
      <p className="text-xs text-slate-600 text-center">
        Exports are generated securely and never stored on our servers.
      </p>
    </div>
  );
};

interface CheckboxOptionProps {
  checked: boolean;
  onChange: () => void;
  label: string;
  description: string;
}

const CheckboxOption: React.FC<CheckboxOptionProps> = ({
  checked,
  onChange,
  label,
  description,
}) => (
  <label className="flex items-start gap-3 cursor-pointer">
    <input
      type="checkbox"
      checked={checked}
      onChange={onChange}
      className="w-5 h-5 mt-0.5 rounded border-slate-300 text-primary-600 focus:ring-primary-500 cursor-pointer"
    />
    <div className="flex-1">
      <p className="font-medium text-slate-900">{label}</p>
      <p className="text-sm text-slate-600 mt-0.5">{description}</p>
    </div>
  </label>
);
