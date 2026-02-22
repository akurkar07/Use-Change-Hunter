"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { SearchBar } from "@/components/SearchBar";
import { Button } from "@/components/ui/Button";
import { TrendingUp, MapPin, BarChart3, Zap, ArrowRight } from "lucide-react";

export default function Home() {
  const router = useRouter();
  const [isSearching, setIsSearching] = useState(false);

  const handleSearch = async (data: any) => {
    setIsSearching(true);
    try {
      // Redirect to search results with query params
      const params = new URLSearchParams({
        postcode: data.postcode,
        strategy: data.strategy,
        radius: data.radius,
      });
      router.push(`/search?${params.toString()}`);
    } catch (error) {
      console.error("Search failed:", error);
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary-50 via-white to-success-50 py-20">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Badge */}
          <div className="flex justify-center mb-6">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-100 border border-primary-200">
              <Zap size={14} className="text-primary-600" />
              <span className="text-sm font-medium text-primary-900">
                Unlock Hidden Value in Your Properties
              </span>
            </div>
          </div>

          {/* Main Heading */}
          <h1 className="text-5xl md:text-6xl font-bold text-center mb-6 text-slate-900">
            Discover Planning
            <span className="block text-primary-600">Opportunities</span>
          </h1>

          {/* Subheading */}
          <p className="text-xl text-center text-slate-600 mb-12 max-w-3xl mx-auto leading-relaxed">
            Use-Change Hunter analyzes planning precedents to identify
            extensions, HMO conversions, office-to-residential developments, and
            more. Get instant opportunity scores and financial projections for
            any property.
          </p>

          {/* Search Bar */}
          <div className="mb-12">
            <SearchBar onSubmit={handleSearch} isLoading={isSearching} />
          </div>

          {/* Features Quick Links */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <div
                key={index}
                className="p-6 bg-white rounded-lg border border-slate-200 hover:shadow-md transition-shadow"
              >
                <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-primary-100 to-primary-50 flex items-center justify-center mb-4">
                  <feature.icon size={24} className="text-primary-600" />
                </div>
                <h3 className="text-lg font-semibold text-slate-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-sm text-slate-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-white">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-slate-900 mb-4">
              How It Works
            </h2>
            <p className="text-lg text-slate-600">
              Three simple steps to unlock opportunities
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {steps.map((step, index) => (
              <div key={index} className="relative">
                {/* Step Number */}
                <div className="flex items-center gap-4 mb-4">
                  <div className="w-10 h-10 rounded-full bg-primary-600 text-white font-bold flex items-center justify-center flex-shrink-0">
                    {index + 1}
                  </div>
                  <h3 className="text-lg font-semibold text-slate-900">
                    {step.title}
                  </h3>
                </div>

                {/* Description */}
                <div className="ml-14">
                  <p className="text-slate-600 mb-4">{step.description}</p>
                  <div className="p-4 bg-slate-50 rounded border border-slate-200">
                    <code className="text-sm text-slate-700">
                      {step.example}
                    </code>
                  </div>
                </div>

                {/* Arrow to next step */}
                {index < steps.length - 1 && (
                  <div className="absolute top-12 -right-0 hidden md:block transform translate-x-1/2">
                    <ArrowRight className="text-primary-300" size={24} />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 bg-slate-50">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-slate-900 mb-4">
              Why Property Developers Love Us
            </h2>
            <p className="text-lg text-slate-600">
              Save time and identify opportunities faster than ever
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {benefits.map((benefit, index) => (
              <div key={index} className="flex gap-4">
                <div className="flex-shrink-0">
                  <div className="flex items-center justify-center h-10 w-10 rounded-lg bg-success-100">
                    <benefit.icon size={20} className="text-success-600" />
                  </div>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-slate-900 mb-2">
                    {benefit.title}
                  </h3>
                  <p className="text-slate-600">{benefit.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-primary-600 to-primary-700 text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold mb-4">
            Ready to Find Your Next Opportunity?
          </h2>
          <p className="text-xl text-primary-100 mb-8">
            Start analyzing properties today. No credit card required.
          </p>
          <Button
            variant="secondary"
            size="lg"
            onClick={() => router.push("/search")}
          >
            Get Started
            <ArrowRight size={18} />
          </Button>
        </div>
      </section>
    </div>
  );
}

const features = [
  {
    icon: TrendingUp,
    title: "Opportunity Scoring",
    description:
      "Instant scores based on local planning precedents, not black-box algorithms.",
  },
  {
    icon: MapPin,
    title: "Planning Analysis",
    description:
      "See approved and refused applications nearby to understand local planning culture.",
  },
  {
    icon: BarChart3,
    title: "Financial Modeling",
    description:
      "Build scenarios and calculate potential profits with multiple finance options.",
  },
];

const steps = [
  {
    title: "Enter Your Property",
    description: "Simply enter a postcode or address to get started.",
    example: 'e.g., "SW1A 1AA" or "123 High Street, London"',
  },
  {
    title: "Choose Your Strategy",
    description: "Select the type of development you have in mind.",
    example: "Extension, HMO, Office→Residential, etc.",
  },
  {
    title: "Get Your Analysis",
    description: "Receive instant opportunity scores and planning precedents.",
    example: "Score 78/100 with 12 approved precedents nearby",
  },
];

const benefits = [
  {
    icon: TrendingUp,
    title: "Save Hours of Research",
    description:
      "What normally takes days of planning database searches takes seconds.",
  },
  {
    icon: MapPin,
    title: "Data-Driven Decisions",
    description:
      "Base your investment decisions on actual planning precedents, not speculation.",
  },
  {
    icon: BarChart3,
    title: "Financial Projections",
    description:
      "Build detailed scenarios with professional financial models included.",
  },
  {
    icon: Zap,
    title: "Explainable Scores",
    description:
      "Understand exactly why a property scores high or low—no black box.",
  },
];
