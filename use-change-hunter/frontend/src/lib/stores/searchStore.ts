'use client';

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { Property, OpportunityScore, Precedent, SearchStrategy } from '@/types';

interface SearchState {
  // Search Query
  query: {
    postcode: string;
    strategy: SearchStrategy;
    radius: number;
  };
  
  // Results
  properties: Property[];
  scores: Record<string, OpportunityScore>;
  precedents: Record<string, Precedent[]>;
  
  // UI State
  selectedPropertyId: string | null;
  viewMode?: 'grid' | 'map';
  isLoading: boolean;
  error: string | null;
  
  // Pagination
  total: number;
  offset: number;
  limit: number;
  
  // Actions
  setQuery: (query: { postcode: string; strategy: SearchStrategy; radius: number }) => void;
  setResults: (properties: Property[], scores: Record<string, OpportunityScore>) => void;
  setSelectedProperty: (propertyId: string | null) => void;
  setViewMode?: (mode: 'grid' | 'map') => void;
  setIsLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setPrecedents: (propertyId: string, precedents: Precedent[]) => void;
  addProperty: (property: Property, score: OpportunityScore) => void;
  clearResults: () => void;
}

export const useSearchStore = create<SearchState>()(
  devtools(
    persist(
      (set, get) => ({
        query: {
          postcode: '',
          strategy: 'extension' as SearchStrategy,
          radius: 1000,
        },
        properties: [],
        scores: {},
        precedents: {},
        selectedPropertyId: null,
        viewMode: 'grid',
        isLoading: false,
        error: null,
        total: 0,
        offset: 0,
        limit: 20,

        setQuery: (query) =>
          set((state) => ({
            query,
            isLoading: true,
            error: null,
          })),

        setResults: (properties, scores) =>
          set({
            properties,
            scores,
            total: properties.length,
            isLoading: false,
          }),

        setSelectedProperty: (propertyId) =>
          set({
            selectedPropertyId: propertyId,
          }),

        setViewMode: (mode) =>
          set({
            viewMode: mode,
          }),

        setIsLoading: (loading) =>
          set({
            isLoading: loading,
          }),

        setError: (error) =>
          set({
            error,
          }),

        setPrecedents: (propertyId, precedents) =>
          set((state) => ({
            precedents: {
              ...state.precedents,
              [propertyId]: precedents,
            },
          })),

        addProperty: (property, score) =>
          set((state) => ({
            properties: [...state.properties, property],
            scores: {
              ...state.scores,
              [property.id]: score,
            },
          })),

        clearResults: () =>
          set({
            properties: [],
            scores: {},
            precedents: {},
            selectedPropertyId: null,
            total: 0,
            offset: 0,
          }),
      }),
      {
        name: 'search-store',
        partialize: (state) => ({
          query: state.query,
          viewMode: state.viewMode,
        }),
      }
    )
  )
);

// Selectors
export const useSearchQuery = () => useSearchStore((state) => state.query);
export const useSearchResults = () => useSearchStore((state) => ({
  properties: state.properties,
  scores: state.scores,
  total: state.total,
}));
export const useSearchLoading = () => useSearchStore((state) => state.isLoading);
export const useSearchError = () => useSearchStore((state) => state.error);
export const useSelectedProperty = () => useSearchStore((state) => state.selectedPropertyId);
