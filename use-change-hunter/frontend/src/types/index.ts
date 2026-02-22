// Scoring and Analysis Types
export interface ScoreBreakdown {
  matched_precedents: number;
  approved_similar: number;
  refused_similar: number;
  recent_approved?: number;
  recent_refused?: number;
  planning_signal?: number;
  refusal_rate?: number;
  density_score?: number;
  [key: string]: any;
}

export interface OpportunityScore {
  id: string;
  property_id: string;
  strategy_type: "opportunity" | "risk" | "development" | "sustainability";
  score_total: number;
  score_risk: number;
  score_confidence: number;
  breakdown: ScoreBreakdown;
  scenario?: Record<string, any>;
  generated_at: string;
}

export interface Precedent {
  reference: string;
  decision: "approved" | "refused" | "withdrawn" | "other";
  proposal: string;
  distance_m: number;
  date_decided?: string;
}

export interface PlanningSearchResponse {
  query: string;
  strategy: string;
  center: {
    lat: number;
    lon: number;
  };
  radius_m: number;
  summary: ScoreBreakdown;
  opportunities: Precedent[];
}

// Property Types
export interface Property {
  id: string;
  address?: string;
  postcode?: string;
  property_type?: string;
  geom?: string;
  created_at: string;
}

export interface PropertyResponse extends Property {
  latest_score?: OpportunityScore;
  scenarios?: Scenario[];
}

// Scenario Types
export interface ScenarioParameters {
  build_cost?: number;
  contingency_pct?: number;
  professional_fees_pct?: number;
  finance_cost?: number;
  buy_price?: number;
  stamp_legal?: number;
  gdv?: number;
  annual_rent_uplift?: number;
  hold_years?: number;
  risk_haircut_pct?: number;
  [key: string]: any;
}

export interface Scenario {
  id: string;
  property_id: string;
  name?: string;
  description?: string;
  scenario_type: string;
  parameters: ScenarioParameters;
  results?: {
    inputs: ScenarioParameters;
    outputs: {
      total_cost: number;
      gross_profit: number;
      risk_adjusted_profit: number;
      roi_pct: number;
      [key: string]: any;
    };
  };
  created_at: string;
  updated_at: string;
}

// Export Types
export interface ExportRequest {
  property_id: string;
  format: "pdf" | "excel" | "json";
}

// Strategy Types
export type SearchStrategy =
  | "extension"
  | "hmo"
  | "office_to_resi"
  | "retail_to_mixed"
  | "flats";

export const STRATEGIES: Record<
  SearchStrategy,
  { label: string; description: string; icon: string }
> = {
  extension: {
    label: "Extension",
    description: "Rear, side-return, loft conversions",
    icon: "🏠",
  },
  hmo: {
    label: "HMO",
    description: "House into multiple occupation",
    icon: "🏢",
  },
  office_to_resi: {
    label: "Office → Residential",
    description: "Office conversion to flats",
    icon: "🏢→🏘️",
  },
  retail_to_mixed: {
    label: "Retail → Mixed-Use",
    description: "Retail with residential above",
    icon: "🛍️",
  },
  flats: {
    label: "Subdivide into Flats",
    description: "House division or apartment creation",
    icon: "🏘️",
  },
};

// API Response Types
export interface ApiResponse<T> {
  data: T;
  error?: string;
  status: number;
}

export interface SearchState {
  query: string;
  strategy: SearchStrategy;
  radius_m: number;
  location?: { lat: number; lon: number };
  loading: boolean;
  error?: string;
  results?: PlanningSearchResponse;
}
