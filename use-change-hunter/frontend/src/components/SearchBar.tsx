"use client";

import React, { useState } from "react";
import { Input, Select } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { SearchStrategy, STRATEGIES } from "@/types";
import { Search } from "lucide-react";
import { useSearchStore } from "@/lib/stores/searchStore";
import { useSearchProperties } from "@/lib/hooks";

interface SearchBarProps {
  onSearch?: (query: string, strategy: SearchStrategy, radius: number) => void;
}

export const SearchBar: React.FC<SearchBarProps> = ({ onSearch }) => {
  const [query, setQuery] = useState("");
  const [strategy, setStrategy] = useState<SearchStrategy>("extension");
  const [radius, setRadius] = useState(1000);

  // Access Zustand store
  const store = useSearchStore();

  // Use React Query for search
  const { isLoading, error } = useSearchProperties(query, strategy, radius, false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      // Update store with query
      store.setQuery({
        postcode: query,
        strategy,
        radius,
      });

      // Call custom callback if provided
      if (onSearch) {
        onSearch(query, strategy, radius);
      }

      // The store will trigger useSearchProperties to fetch data
      // which will then update the store results
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="md:col-span-2">
          <Input
            type="text"
            placeholder="Enter postcode or address..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            icon={<Search size={18} />}
            disabled={isLoading}
          />
        </div>

        <Select
          value={strategy}
          onChange={(e) => setStrategy(e.target.value as SearchStrategy)}
          options={Object.entries(STRATEGIES).map(([key, { label }]) => ({
            value: key,
            label,
          }))}
          disabled={isLoading}
        />

        <div className="flex gap-2">
          <Select
            value={radius.toString()}
            onChange={(e) => setRadius(parseInt(e.target.value))}
            options={[
              { value: "500", label: "500m" },
              { value: "1000", label: "1km" },
              { value: "2000", label: "2km" },
              { value: "5000", label: "5km" },
            ]}
            disabled={isLoading}
          />

          <Button
            type="submit"
            isLoading={isLoading}
            className="w-full md:w-auto"
          >
            {isLoading ? "Searching..." : "Search"}
          </Button>
        </div>
      </div>
      {error && (
        <div className="mt-2 text-sm text-red-500">
          Error: {error instanceof Error ? error.message : "Search failed"}
        </div>
      )}
    </form>
  );
};

