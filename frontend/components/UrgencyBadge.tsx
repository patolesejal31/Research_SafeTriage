import React from "react";
import { AlertOctagon, AlertTriangle, Clock, CheckCircle2, HelpCircle } from "lucide-react";
import { UrgencyLevel } from "@/types/assessment";

interface UrgencyBadgeProps {
  level: UrgencyLevel | "UNCERTAIN" | null;
  isUncertain?: boolean;
  modelSuggestedUrgency?: UrgencyLevel | null;
  modelSuggestionLabel?: string;
  size?: "sm" | "md" | "lg";
  showExplanation?: boolean;
}

export function UrgencyBadge({
  level,
  isUncertain = false,
  modelSuggestedUrgency,
  modelSuggestionLabel,
  size = "md",
  showExplanation = false,
}: UrgencyBadgeProps) {
  if (isUncertain || level === null || level === "UNCERTAIN") {
    return (
      <div className="space-y-2">
        <div
          className={`inline-flex items-center gap-2 rounded-lg font-bold border ${
            size === "lg"
              ? "px-5 py-3 text-lg border-purple-400 bg-purple-100 text-purple-950"
              : "px-3 py-1.5 text-sm border-purple-300 bg-purple-100 text-purple-900"
          }`}
          role="status"
          aria-label="Triage Urgency: UNCERTAIN"
        >
          <HelpCircle className={size === "lg" ? "w-6 h-6 text-purple-700" : "w-4 h-4 text-purple-700"} aria-hidden="true" />
          <span>UNCERTAIN</span>
          <span className="text-xs font-normal text-purple-800">— Needs Direct Clinician Assessment</span>
        </div>
        {(size === "lg" || showExplanation) && (
          <p className="text-sm font-medium text-purple-900 bg-purple-100/60 p-3 rounded-md border border-purple-200">
            Unable to assess safely. If you have severe symptoms, call <strong>112 / 108</strong> or see a clinician immediately.
          </p>
        )}
        {modelSuggestedUrgency && (
          <p className="text-xs text-purple-800 italic">
            Statistical suggestion (informational only; deterministic rule engine was unavailable): Level {modelSuggestedUrgency}
            {modelSuggestionLabel && ` (${modelSuggestionLabel})`}
          </p>
        )}
      </div>
    );
  }

  const configs: Record<
    UrgencyLevel,
    {
      label: string;
      subtext: string;
      bg: string;
      border: string;
      text: string;
      icon: React.ReactNode;
    }
  > = {
    1: {
      label: "Level 1: Emergency",
      subtext: "Immediate emergency medical attention required. Call 112 / 108.",
      bg: "bg-red-50",
      border: "border-red-600",
      text: "text-red-950",
      icon: <AlertOctagon className={size === "lg" ? "w-7 h-7 text-red-600" : "w-5 h-5 text-red-600"} aria-hidden="true" />,
    },
    2: {
      label: "Level 2: Urgent",
      subtext: "Prompt in-person medical evaluation required within hours.",
      bg: "bg-amber-50",
      border: "border-amber-600",
      text: "text-amber-950",
      icon: <AlertTriangle className={size === "lg" ? "w-7 h-7 text-amber-600" : "w-5 h-5 text-amber-600"} aria-hidden="true" />,
    },
    3: {
      label: "Level 3: Routine",
      subtext: "Standard outpatient consultation or scheduled clinical appointment.",
      bg: "bg-blue-50",
      border: "border-blue-500",
      text: "text-blue-950",
      icon: <Clock className={size === "lg" ? "w-7 h-7 text-blue-600" : "w-5 h-5 text-blue-600"} aria-hidden="true" />,
    },
    4: {
      label: "Level 4: Self-Care",
      subtext: "Mild, self-limiting presentation manageable with standard supportive care.",
      bg: "bg-emerald-50",
      border: "border-emerald-600",
      text: "text-emerald-950",
      icon: <CheckCircle2 className={size === "lg" ? "w-7 h-7 text-emerald-600" : "w-5 h-5 text-emerald-600"} aria-hidden="true" />,
    },
  };

  const c = configs[level];

  return (
    <div className="space-y-1">
      <div
        className={`inline-flex items-center gap-2.5 rounded-lg font-bold border-2 ${c.bg} ${c.border} ${c.text} ${
          size === "lg" ? "px-6 py-3.5 text-xl" : "px-3.5 py-1.5 text-sm"
        }`}
        role="status"
        aria-label={`Triage Urgency: ${c.label}`}
      >
        {c.icon}
        <span>{c.label}</span>
      </div>
      {size === "lg" && <p className="text-sm font-medium text-gray-700">{c.subtext}</p>}
    </div>
  );
}
