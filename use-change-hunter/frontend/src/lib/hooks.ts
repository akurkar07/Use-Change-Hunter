'use client';

import { useQuery, useMutation, useQueryClient, UseQueryResult, UseMutationResult } from '@tanstack/react-query';
import { api } from './api-client';
import { Property, OpportunityScore, Precedent, Scenario, ExportOptions } from '@/types';

/**
 * Query Keys for React Query cache management
 */
export const searchKeys = {
  all: ['properties'] as const,
  searches: () => [...searchKeys.all, 'searches'] as const,
  search: (postcode: string, strategy: string, radius: number) =>
    [...searchKeys.searches(), { postcode, strategy, radius }] as const,
  property: (id: string) => [...searchKeys.all, 'property', id] as const,
  score: (id: string) => [...searchKeys.all, 'score', id] as const,
  precedents: (id: string) => [...searchKeys.all, 'precedents', id] as const,
  scenarios: (id: string) => [...searchKeys.all, 'scenarios', id] as const,
};

/**
 * Hook: Search for properties
 */
export function useSearchProperties(
  postcode: string,
  strategy: string = 'extension',
  radius: number = 1000,
  enabled: boolean = true
): UseQueryResult<{ properties: Property[]; scores: Record<string, OpportunityScore> }, Error> {
  return useQuery({
    queryKey: searchKeys.search(postcode, strategy, radius),
    queryFn: async () => {
      const response = await api.searchProperties({ postcode, strategy, radius });
      return {
        properties: response.properties,
        scores: response.scores.reduce(
          (acc, score) => ({
            ...acc,
            [score.property_id]: score,
          }),
          {} as Record<string, OpportunityScore>
        ),
      };
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    enabled: enabled && !!postcode,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook: Get property details
 */
export function useProperty(
  propertyId: string,
  enabled: boolean = true
): UseQueryResult<Property, Error> {
  return useQuery({
    queryKey: searchKeys.property(propertyId),
    queryFn: () => api.getProperty(propertyId),
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes
    enabled: enabled && !!propertyId,
  });
}

/**
 * Hook: Get property score
 */
export function usePropertyScore(
  propertyId: string,
  strategy: string = 'extension',
  enabled: boolean = true
): UseQueryResult<OpportunityScore, Error> {
  return useQuery({
    queryKey: searchKeys.score(propertyId),
    queryFn: () => api.calculateScore(propertyId, strategy),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    enabled: enabled && !!propertyId,
  });
}

/**
 * Hook: Get precedents for property
 */
export function usePrecedents(
  propertyId: string,
  radius: number = 1000,
  enabled: boolean = true
): UseQueryResult<Precedent[], Error> {
  return useQuery({
    queryKey: searchKeys.precedents(propertyId),
    queryFn: () => api.getPrecedents(propertyId, radius),
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes
    enabled: enabled && !!propertyId,
  });
}

/**
 * Hook: Get scenarios for property
 */
export function useScenarios(
  propertyId: string,
  enabled: boolean = true
): UseQueryResult<Scenario[], Error> {
  return useQuery({
    queryKey: searchKeys.scenarios(propertyId),
    queryFn: () => api.getScenarios(propertyId),
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes
    enabled: enabled && !!propertyId,
  });
}

/**
 * Hook: Create new scenario
 */
export function useCreateScenario(): UseMutationResult<
  Scenario,
  Error,
  { propertyId: string; data: Partial<Scenario> },
  unknown
> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ propertyId, data }) => api.createScenario(propertyId, data),
    onSuccess: (data) => {
      // Invalidate scenarios query to refetch
      queryClient.invalidateQueries({
        queryKey: searchKeys.scenarios(data.property_id),
      });
    },
  });
}

/**
 * Hook: Export property analysis
 */
export function useExport(): UseMutationResult<
  { url: string },
  Error,
  { propertyId: string; format: 'pdf' | 'excel' | 'json'; options: ExportOptions },
  unknown
> {
  return useMutation({
    mutationFn: ({ propertyId, format, options }) =>
      api.exportProperty(propertyId, format, options),
  });
}

/**
 * Custom hook: Combined search with immediate loading state
 */
export function usePropertySearch(
  postcode: string,
  strategy: string = 'extension',
  radius: number = 1000
) {
  const { data, isLoading, error, isError, isFetching } = useSearchProperties(
    postcode,
    strategy,
    radius,
    !!postcode
  );

  return {
    properties: data?.properties || [],
    scores: data?.scores || {},
    isLoading: isLoading || isFetching,
    error,
    isError,
  };
}
