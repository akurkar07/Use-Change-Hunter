"use client";

import React, { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/Tabs";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import {
  ScoreCard,
  PrecedentsList,
  ScenarioBuilder,
  ExportDialog,
} from "@/components/index";
import { Property, OpportunityScore, Precedent, Scenario } from "@/types";
import { ArrowLeft, Download, FileText } from "lucide-react";

export default function PropertyDetailPage() {
  const router = useRouter();
  const params = useParams();
  const propertyId = params.id as string;

  const [property, setProperty] = useState<Property | null>(null);
  const [score, setScore] = useState<OpportunityScore | null>(null);
  const [precedents, setPrecedents] = useState<Precedent[]>([]);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showExportDialog, setShowExportDialog] = useState(false);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    const fetchPropertyDetails = async () => {
      setIsLoading(true);
      try {
        // Simulate API calls
        await new Promise((resolve) => setTimeout(resolve, 1000));

        // Mock property data
        const mockProperty: Property = {
          id: propertyId,
          postcode: "SW1A 1AA",
          address: "123 High Street, London",
          latitude: 51.5074,
          longitude: -0.1278,
          area_sqm: 180,
          historic_use: "Residential",
          listed_status: "Not Listed",
          opportunity_strategies: ["extension", "hmo"],
          distance_nearest_precedent: 1200,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };

        const mockScore: OpportunityScore = {
          id: `score-${propertyId}`,
          property_id: propertyId,
          score_total: 78,
          score_risk: 35,
          score_confidence: 82,
          score_breakdown: {
            precedents_found: 12,
            approved: 10,
            refused: 2,
            approval_rate: 0.83,
            nearby_schemes: 4,
          },
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };

        const mockPrecedents: Precedent[] = [
          {
            reference: "21/00123/FUL",
            proposal: "First floor extension with rear dormer",
            decision: "approved",
            date_decided: new Date("2021-06-15").toISOString(),
            distance_m: 450,
            lat: 51.508,
            lng: -0.127,
          },
          {
            reference: "20/00456/FUL",
            proposal: "Two storey side extension",
            decision: "approved",
            date_decided: new Date("2020-09-20").toISOString(),
            distance_m: 680,
            lat: 51.506,
            lng: -0.129,
          },
          {
            reference: "22/00789/FUL",
            proposal: "Conversion to 4 HMO flats",
            decision: "refused",
            date_decided: new Date("2022-03-10").toISOString(),
            distance_m: 920,
            lat: 51.509,
            lng: -0.126,
          },
        ];

        const mockScenarios: Scenario[] = [
          {
            id: "1",
            property_id: propertyId,
            name: "Conservative Extension",
            strategy: "extension",
            development_cost: 65000,
            holding_period_months: 18,
            finance_type: "cash",
            finance_rate: 0,
            assumptions: "Single storey rear extension, no complications",
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
        ];

        setProperty(mockProperty);
        setScore(mockScore);
        setPrecedents(mockPrecedents);
        setScenarios(mockScenarios);
      } catch (error) {
        console.error("Failed to fetch property details:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchPropertyDetails();
  }, [propertyId]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 rounded-full border-4 border-slate-300 border-t-primary-600 animate-spin mx-auto mb-4" />
          <p className="text-slate-600">Loading property details...</p>
        </div>
      </div>
    );
  }

  if (!property || !score) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <Card>
          <CardBody className="text-center py-12">
            <p className="text-slate-600 text-lg">Property not found</p>
            <Button
              variant="primary"
              onClick={() => router.push("/search")}
              className="mt-4"
            >
              Back to Search
            </Button>
          </CardBody>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <div className="bg-white border-b border-slate-200 sticky top-16 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <button
                onClick={() => router.back()}
                className="flex items-center gap-2 text-slate-600 hover:text-slate-900 mb-3"
              >
                <ArrowLeft size={20} />
                <span className="font-medium">Back</span>
              </button>
              <h1 className="text-3xl font-bold text-slate-900 mb-1">
                {property.address}
              </h1>
              <p className="text-slate-600">{property.postcode}</p>
            </div>

            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => setShowExportDialog(true)}
              >
                <Download size={18} />
                Export
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content Area */}
          <div className="lg:col-span-2">
            <Tabs
              value={activeTab}
              onValueChange={setActiveTab}
              className="space-y-6"
            >
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="precedents">Precedents</TabsTrigger>
                <TabsTrigger value="scenarios">Scenarios</TabsTrigger>
                <TabsTrigger value="analysis">Analysis</TabsTrigger>
              </TabsList>

              {/* Overview Tab */}
              <TabsContent value="overview" className="space-y-6">
                {/* Score Card */}
                <ScoreCard score={score} />

                {/* Property Details */}
                <Card>
                  <CardHeader>
                    <h3 className="text-lg font-bold text-slate-900">
                      Property Details
                    </h3>
                  </CardHeader>

                  <CardBody>
                    <div className="grid grid-cols-2 gap-6">
                      <div>
                        <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">
                          Current Use
                        </p>
                        <p className="font-semibold text-slate-900">
                          {property.historic_use}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">
                          Area
                        </p>
                        <p className="font-semibold text-slate-900">
                          {property.area_sqm} m²
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">
                          Listed Status
                        </p>
                        <p className="font-semibold text-slate-900">
                          {property.listed_status}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">
                          Nearest Precedent
                        </p>
                        <p className="font-semibold text-slate-900">
                          {(property.distance_nearest_precedent / 1000).toFixed(
                            2,
                          )}
                          km
                        </p>
                      </div>
                    </div>
                  </CardBody>
                </Card>

                {/* Opportunities */}
                <Card>
                  <CardHeader>
                    <h3 className="text-lg font-bold text-slate-900">
                      Identified Opportunities
                    </h3>
                  </CardHeader>

                  <CardBody>
                    <div className="space-y-3">
                      {property.opportunity_strategies?.map((strategy) => (
                        <div
                          key={strategy}
                          className="p-4 bg-primary-50 border border-primary-200 rounded-lg"
                        >
                          <p className="font-semibold text-primary-900 capitalize">
                            {strategy.replace("_", " → ")}
                          </p>
                          <p className="text-sm text-primary-700 mt-1">
                            Local precedents support this development strategy
                          </p>
                        </div>
                      ))}
                    </div>
                  </CardBody>
                </Card>
              </TabsContent>

              {/* Precedents Tab */}
              <TabsContent value="precedents">
                <PrecedentsList precedents={precedents} />
              </TabsContent>

              {/* Scenarios Tab */}
              <TabsContent value="scenarios" className="space-y-6">
                {scenarios.map((scenario) => (
                  <Card key={scenario.id}>
                    <CardHeader>
                      <h3 className="text-lg font-bold text-slate-900">
                        {scenario.name}
                      </h3>
                    </CardHeader>

                    <CardBody>
                      <div className="grid grid-cols-3 gap-4 mb-4">
                        <div>
                          <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">
                            Development Cost
                          </p>
                          <p className="font-semibold text-slate-900">
                            £{scenario.development_cost?.toLocaleString()}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">
                            Holding Period
                          </p>
                          <p className="font-semibold text-slate-900">
                            {scenario.holding_period_months} months
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">
                            Finance Type
                          </p>
                          <p className="font-semibold text-slate-900 capitalize">
                            {scenario.finance_type?.replace("_", " ")}
                          </p>
                        </div>
                      </div>

                      {scenario.assumptions && (
                        <div className="p-3 bg-slate-50 rounded border border-slate-200 text-sm">
                          <p className="text-slate-600">
                            {scenario.assumptions}
                          </p>
                        </div>
                      )}
                    </CardBody>
                  </Card>
                ))}

                <ScenarioBuilder propertyId={propertyId} />
              </TabsContent>

              {/* Analysis Tab */}
              <TabsContent value="analysis">
                <Card>
                  <CardHeader>
                    <h3 className="text-lg font-bold text-slate-900">
                      Strategic Analysis
                    </h3>
                  </CardHeader>

                  <CardBody className="space-y-6">
                    <div>
                      <h4 className="font-semibold text-slate-900 mb-2">
                        Planning Likelihood
                      </h4>
                      <p className="text-slate-600">
                        Based on {score.score_breakdown?.precedents_found}{" "}
                        nearby precedents, this area has shown{" "}
                        {Math.round(
                          (score.score_breakdown?.approval_rate || 0) * 100,
                        )}
                        % approval rate for similar development proposals.
                      </p>
                    </div>

                    <div className="border-t border-slate-200 pt-6">
                      <h4 className="font-semibold text-slate-900 mb-2">
                        Risk Factors
                      </h4>
                      <ul className="space-y-2 text-sm text-slate-600">
                        <li>
                          • Listed status may restrict external modifications
                        </li>
                        <li>
                          • Local authority currently reviewing new planning
                          policies
                        </li>
                        <li>
                          • Neighboring properties may object to development
                        </li>
                      </ul>
                    </div>

                    <div className="border-t border-slate-200 pt-6">
                      <h4 className="font-semibold text-slate-900 mb-2">
                        Recommendations
                      </h4>
                      <ul className="space-y-2 text-sm text-slate-600">
                        <li>✓ Engage with planning officer early</li>
                        <li>
                          ✓ Review officers' comments on similar applications
                        </li>
                        <li>✓ Consider conservation officer consultation</li>
                      </ul>
                    </div>
                  </CardBody>
                </Card>
              </TabsContent>
            </Tabs>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="sticky top-32 space-y-6">
              {/* Quick Actions */}
              <Card>
                <CardHeader>
                  <h3 className="font-bold text-slate-900">Actions</h3>
                </CardHeader>

                <CardBody className="space-y-2">
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => setShowExportDialog(true)}
                    className="w-full"
                  >
                    <Download size={16} />
                    Export Report
                  </Button>
                  <Button variant="outline" size="sm" className="w-full">
                    Save Property
                  </Button>
                  <Button variant="outline" size="sm" className="w-full">
                    Share with Team
                  </Button>
                </CardBody>
              </Card>

              {/* Key Metrics */}
              <Card>
                <CardHeader>
                  <h3 className="font-bold text-slate-900">Key Metrics</h3>
                </CardHeader>

                <CardBody className="space-y-4">
                  <MetricItem
                    label="Precedents Found"
                    value={score.score_breakdown?.precedents_found || 0}
                  />
                  <MetricItem
                    label="Approval Rate"
                    value={`${Math.round((score.score_breakdown?.approval_rate || 0) * 100)}%`}
                  />
                  <MetricItem
                    label="Nearby Schemes"
                    value={score.score_breakdown?.nearby_schemes || 0}
                  />
                </CardBody>
              </Card>
            </div>
          </div>
        </div>
      </div>

      {/* Export Dialog */}
      {showExportDialog && (
        <ExportDialogWrapper
          property={property}
          onClose={() => setShowExportDialog(false)}
        />
      )}
    </div>
  );
}

interface PropertyDetailPageProps {
  propertyId?: string;
}

const ScenarioBuilder: React.FC<{ propertyId: string }> = ({ propertyId }) => {
  return (
    <Card>
      <CardHeader>
        <h3 className="text-lg font-bold text-slate-900">Build New Scenario</h3>
      </CardHeader>

      <CardBody>
        <p className="text-slate-600 mb-4">
          Create a custom financial scenario for this property
        </p>
        <Button variant="primary" className="w-full">
          Create Scenario
        </Button>
      </CardBody>
    </Card>
  );
};

interface MetricItemProps {
  label: string;
  value: string | number;
}

const MetricItem: React.FC<MetricItemProps> = ({ label, value }) => (
  <div>
    <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">
      {label}
    </p>
    <p className="text-lg font-bold text-slate-900">{value}</p>
  </div>
);

interface ExportDialogWrapperProps {
  property: Property;
  onClose: () => void;
}

const ExportDialogWrapper: React.FC<ExportDialogWrapperProps> = ({
  property,
  onClose,
}) => (
  <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
    <Card className="w-full max-w-2xl">
      <CardHeader>
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-bold text-slate-900">Export Analysis</h3>
          <button
            onClick={onClose}
            className="text-slate-500 hover:text-slate-700"
          >
            ✕
          </button>
        </div>
      </CardHeader>

      <CardBody>
        <ExportDialog
          propertyAddress={property.address}
          onExport={async () => {
            // Handle export
            onClose();
          }}
        />
      </CardBody>
    </Card>
  </div>
);
