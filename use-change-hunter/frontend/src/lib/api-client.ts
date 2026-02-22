import axios, { AxiosInstance, AxiosError } from "axios";
import {
  Property,
  PropertyResponse,
  OpportunityScore,
  Scenario,
  SearchStrategy,
  Precedent,
} from "@/types";

export interface ExportOptions {
  include_precedents?: boolean;
  include_scenarios?: boolean;
  include_scores?: boolean;
}

export interface SearchResponse {
  properties: Property[];
  scores: OpportunityScore[];
  total: number;
}

class ApiClient {
  private client: AxiosInstance;
  private apiBase: string;

  constructor() {
    this.apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

    this.client = axios.create({
      baseURL: this.apiBase,
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        console.error("API Error:", error.response?.status, error.message);
        throw error;
      },
    );
  }

  // Search & Planning
  async searchProperties(params: {
    postcode: string;
    strategy?: SearchStrategy;
    radius?: number;
  }): Promise<SearchResponse> {
    const response = await this.client.post<SearchResponse>("/api/search/", {
      postcode: params.postcode,
      strategy: params.strategy || "extension",
      radius: params.radius || 1000,
    });
    return response.data;
  }

  // Properties
  async createProperty(data: Partial<Property>): Promise<Property> {
    const response = await this.client.post<Property>("/api/properties/", data);
    return response.data;
  }

  async getProperty(propertyId: string): Promise<PropertyResponse> {
    const response = await this.client.get<PropertyResponse>(
      `/api/properties/${propertyId}`,
    );
    return response.data;
  }

  // Scores
  async calculateScore(
    propertyId: string,
    strategy: SearchStrategy = "extension",
  ): Promise<OpportunityScore> {
    const response = await this.client.post<OpportunityScore>(
      `/api/scores/calculate`,
      {
        property_id: propertyId,
        strategy,
      },
    );
    return response.data;
  }

  // Precedents
  async getPrecedents(
    propertyId: string,
    radius: number = 1000,
  ): Promise<Precedent[]> {
    const response = await this.client.get<{ precedents: Precedent[] }>(
      `/api/properties/${propertyId}/precedents`,
      {
        params: { radius },
      },
    );
    return response.data.precedents || [];
  }

  // Scenarios
  async createScenario(
    propertyId: string,
    data: Partial<Scenario>,
  ): Promise<Scenario> {
    const response = await this.client.post<Scenario>(
      `/api/scenarios/`,
      {
        property_id: propertyId,
        ...data,
      },
    );
    return response.data;
  }

  async getScenarios(propertyId: string): Promise<Scenario[]> {
    const response = await this.client.get<{ scenarios: Scenario[] }>(
      `/api/scenarios/`,
      {
        params: { property_id: propertyId },
      },
    );
    return response.data.scenarios || [];
  }

  async updateScenario(
    propertyId: string,
    scenarioId: string,
    data: Partial<Scenario>,
  ): Promise<Scenario> {
    const response = await this.client.put<Scenario>(
      `/api/scenarios/${scenarioId}`,
      {
        property_id: propertyId,
        ...data,
      },
    );
    return response.data;
  }

  async deleteScenario(propertyId: string, scenarioId: string): Promise<void> {
    await this.client.delete(`/api/scenarios/${scenarioId}`, {
      params: { property_id: propertyId },
    });
  }

  // Export
  async exportProperty(
    propertyId: string,
    format: "pdf" | "excel" | "json",
    options: ExportOptions = {},
  ): Promise<{ url: string }> {
    if (format === "json") {
      const response = await this.client.post(`/api/export/`, {
        property_id: propertyId,
        format: "json",
        ...options,
      });
      return response.data;
    }

    const response = await this.client.post(
      `/api/export/`,
      {
        property_id: propertyId,
        format,
        ...options,
      },
      {
        responseType: format === "pdf" || format === "excel" ? "blob" : "json",
      },
    );

    if (format === "pdf" || format === "excel") {
      // Create a blob URL for download
      const blob = response.data as Blob;
      const url = window.URL.createObjectURL(blob);
      return { url };
    }

    return response.data;
  }

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    const response = await this.client.get<{ status: string }>("/health/");
    return response.data;
  }
}

export const api = new ApiClient();
