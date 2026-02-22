"use client";

import React, { useState, ReactNode } from "react";

interface TabsProps {
  value: string;
  onValueChange: (value: string) => void;
  children: ReactNode;
}

export const Tabs: React.FC<TabsProps> = ({
  value,
  onValueChange,
  children,
}) => (
  <div>
    {React.Children.map(children, (child) =>
      React.isValidElement(child)
        ? React.cloneElement(child, {
            activeTab: value,
            onTabChange: onValueChange,
          } as any)
        : child,
    )}
  </div>
);

interface TabsListProps {
  children: ReactNode;
  className?: string;
}

export const TabsList: React.FC<TabsListProps> = ({
  children,
  className = "",
}) => (
  <div
    className={`flex gap-1 border-b border-slate-200 bg-white rounded-t-lg overflow-x-auto ${className}`}
  >
    {children}
  </div>
);

interface TabsTriggerProps {
  value: string;
  children: ReactNode;
  activeTab?: string;
  onTabChange?: (value: string) => void;
}

export const TabsTrigger: React.FC<TabsTriggerProps> = ({
  value,
  children,
  activeTab,
  onTabChange,
}) => (
  <button
    onClick={() => onTabChange?.(value)}
    className={`px-4 py-3 font-medium text-sm whitespace-nowrap border-b-2 transition-colors ${
      activeTab === value
        ? "border-primary-600 text-primary-600"
        : "border-transparent text-slate-600 hover:text-slate-900"
    }`}
  >
    {children}
  </button>
);

interface TabsContentProps {
  value: string;
  children: ReactNode;
  activeTab?: string;
}

export const TabsContent: React.FC<TabsContentProps> = ({
  value,
  children,
  activeTab,
}) => {
  if (activeTab !== value) return null;
  return <div className="bg-white rounded-b-lg p-6">{children}</div>;
};
