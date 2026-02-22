import React from "react";
import clsx from "clsx";

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "success" | "warning" | "danger" | "info";
  size?: "sm" | "md";
}

export const Badge = React.forwardRef<HTMLSpanElement, BadgeProps>(
  (
    { variant = "default", size = "sm", className, children, ...props },
    ref,
  ) => {
    const variants = {
      default: "bg-slate-100 text-slate-800",
      success: "bg-success-100 text-success-700",
      warning: "bg-warning-100 text-warning-700",
      danger: "bg-danger-100 text-danger-700",
      info: "bg-primary-100 text-primary-700",
    };

    const sizes = {
      sm: "px-2.5 py-1 text-xs font-medium",
      md: "px-3 py-1.5 text-sm font-medium",
    };

    return (
      <span
        ref={ref}
        className={clsx(
          "inline-flex items-center rounded-full",
          variants[variant],
          sizes[size],
          className,
        )}
        {...props}
      >
        {children}
      </span>
    );
  },
);

Badge.displayName = "Badge";

// Score Badge Component
interface ScoreBadgeProps extends React.HTMLAttributes<HTMLDiv> {
  score: number;
  label?: string;
  size?: "sm" | "md" | "lg";
}

export const ScoreBadge = React.forwardRef<HTMLDivElement, ScoreBadgeProps>(
  ({ score, label, size = "md", className, ...props }, ref) => {
    const getColor = (value: number) => {
      if (value >= 70) return "success";
      if (value >= 50) return "warning";
      return "danger";
    };

    const sizeClasses = {
      sm: "w-12 h-12 text-lg",
      md: "w-16 h-16 text-2xl",
      lg: "w-20 h-20 text-3xl",
    };

    return (
      <div
        ref={ref}
        className={clsx("flex flex-col items-center justify-center", className)}
        {...props}
      >
        <div
          className={clsx(
            "rounded-full flex items-center justify-center font-bold text-white",
            sizeClasses[size],
            getColor(score) === "success"
              ? "bg-success-500"
              : getColor(score) === "warning"
                ? "bg-warning-500"
                : "bg-danger-500",
          )}
        >
          {score}
        </div>
        {label && (
          <p className="mt-2 text-sm font-medium text-slate-600">{label}</p>
        )}
      </div>
    );
  },
);

ScoreBadge.displayName = "ScoreBadge";
