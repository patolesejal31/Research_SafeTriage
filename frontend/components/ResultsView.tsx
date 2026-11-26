import React from "react";
import { AssessmentResponse } from "@/types/assessment";
import { UrgencyBadge } from "./UrgencyBadge";
import {
  ShieldAlert,
  FileText,
  Activity,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Cpu,
} from "lucide-react";

interface ResultsViewProps {
  result: AssessmentResponse;
}

export function ResultsView({ result }: ResultsViewProps) {
  const positiveSymptoms = result.extracted_symptoms?.filter(
    (s) => s.status === "POSITIVE"
  ) || [];
  const negatedSymptoms = result.extracted_symptoms?.filter(
    (s) => s.status === "NEGATED"
  ) || [];

  return (
    <article aria-labelledby="triage-result-title" className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden space-y-6 p-6">
      {/* 1. Header & Urgency Outcome */}
      <div className="border-b border-gray-200 pb-5 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h1 id="triage-result-title" className="text-xl font-bold text-gray-900">
            Triage Stratification Assessment
          </h1>
          <span className="text-xs text-gray-500 font-mono">
            Session ID: {(result.assessment_id || result.id || "unknown").substring(0, 12)}...
          </span>
        </div>

        <UrgencyBadge
          level={result.final_urgency}
          isUncertain={result.is_uncertain}
          modelSuggestedUrgency={result.model_suggested_urgency}
          modelSuggestionLabel={result.model_suggestion_label}
          size="lg"
        />

        {/* Determining Component Indicator */}
        <div className="flex items-center gap-2 text-xs text-gray-600 bg-gray-50 p-2.5 rounded border border-gray-200">
          <Activity className="w-4 h-4 text-indigo-600 flex-shrink-0" />
          <span>
            <strong>Determining Component:</strong>{" "}
            {result.determining_component === "SAFETY_NET"
              ? "Safety Net (Red-flag keyword immediate escalation)"
              : result.determining_component === "RULE"
              ? "Deterministic Clinical Rules"
              : result.determining_component === "ML"
              ? "ML Baseline (Escalation applied)"
              : result.determining_component === "LLM"
              ? "LLM Reasoner (Escalation applied)"
              : "Invariant Safety Resolution"}
          </span>
        </div>
      </div>

      {/* 2. Persistent Unverified Rules Governance Notice */}
      <div className="bg-amber-50 border-l-4 border-amber-600 p-4 rounded text-amber-950 text-xs space-y-1">
        <div className="flex items-center gap-2 font-bold text-sm text-amber-900">
          <AlertTriangle className="w-4 h-4 text-amber-700" />
          Rules Not Clinician-Reviewed (Research Prototype Notice)
        </div>
        <p>
          Deterministic triage rules in this prototype are derived from public clinical guidelines (NICE, IAP, AHA)
          but are marked <strong>UNVERIFIED</strong> pending formal dissertation clinician board sign-off.
          This system provides non-diagnostic urgency sorting only. It does not provide diagnoses or prescribe medications.
        </p>
      </div>

      {/* 3. Component Architecture Status Badges */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="p-3 bg-gray-50 border border-gray-200 rounded-lg">
          <div className="text-xs text-gray-500 font-semibold uppercase tracking-wider">Rule Engine</div>
          <div className="text-sm font-bold text-gray-900 mt-1 flex items-center gap-1.5">
            <span className={`w-2 h-2 rounded-full ${result.rule_status === "OK" ? "bg-emerald-500" : "bg-amber-500"}`} />
            Status: {result.rule_status}
          </div>
        </div>

        <div className="p-3 bg-gray-50 border border-gray-200 rounded-lg">
          <div className="text-xs text-gray-500 font-semibold uppercase tracking-wider">ML Baseline (LogReg)</div>
          <div className="text-sm font-bold text-gray-900 mt-1 flex items-center gap-1.5">
            <span className={`w-2 h-2 rounded-full ${result.ml_status === "OK" ? "bg-emerald-500" : "bg-gray-400"}`} />
            Status: {result.ml_status}
          </div>
        </div>

        <div className="p-3 bg-gray-50 border border-gray-200 rounded-lg">
          <div className="text-xs text-gray-500 font-semibold uppercase tracking-wider">Clinical LLM Reasoner</div>
          <div className="text-sm font-bold text-gray-900 mt-1 flex items-center gap-1.5">
            <Cpu className="w-3.5 h-3.5 text-indigo-600" />
            <span>{result.llm_provider_label?.includes("MOCK") ? "SafeTriage NLP Reasoner" : (result.llm_provider_label || "Active")}</span>
          </div>
        </div>
      </div>

      {/* 4. Extracted Symptoms (Positive vs Negated) */}
      <div className="space-y-3">
        <h2 className="text-sm font-bold text-gray-900 uppercase tracking-wider flex items-center gap-2">
          <FileText className="w-4 h-4 text-gray-600" />
          Extracted Clinical Entities (NLP)
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Positive Symptoms */}
          <div className="border border-emerald-200 bg-emerald-50/40 rounded-lg p-3">
            <div className="text-xs font-bold text-emerald-900 mb-2 flex items-center gap-1">
              <CheckCircle className="w-3.5 h-3.5 text-emerald-700" />
              Reported Symptoms Present ({positiveSymptoms.length})
            </div>
            {positiveSymptoms.length === 0 ? (
              <span className="text-xs text-gray-500 italic">None identified</span>
            ) : (
              <ul className="space-y-1">
                {positiveSymptoms.map((s, idx) => (
                  <li key={idx} className="text-xs text-emerald-950 flex items-center justify-between">
                    <span className="font-medium capitalize">{s.canonical_concept.replace(/_/g, " ")}</span>
                    <span className="text-[10px] bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded font-mono">
                      {s.match_type} {s.fuzzy_score ? `(${Math.round(s.fuzzy_score)}%)` : ""}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Negated Symptoms */}
          <div className="border border-gray-200 bg-gray-50/60 rounded-lg p-3">
            <div className="text-xs font-bold text-gray-700 mb-2 flex items-center gap-1">
              <XCircle className="w-3.5 h-3.5 text-gray-500" />
              Explicitly Ruled Out / Negated ({negatedSymptoms.length})
            </div>
            {negatedSymptoms.length === 0 ? (
              <span className="text-xs text-gray-500 italic">None explicitly denied</span>
            ) : (
              <ul className="space-y-1">
                {negatedSymptoms.map((s, idx) => (
                  <li key={idx} className="text-xs text-gray-700 flex items-center justify-between">
                    <span className="font-medium capitalize">{s.canonical_concept.replace(/_/g, " ")}</span>
                    <span className="text-[10px] bg-gray-200 text-gray-700 px-1.5 py-0.5 rounded font-mono">
                      negated
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>

      {/* 5. Triggered Clinical Rules */}
      <div className="space-y-3">
        <h2 className="text-sm font-bold text-gray-900 uppercase tracking-wider flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-indigo-600" />
          Triggered Clinical Triage Rules ({result.triggered_rules?.length || 0})
        </h2>

        {(!result.triggered_rules || result.triggered_rules.length === 0) ? (
          <p className="text-xs text-gray-500 bg-gray-50 p-3 rounded border border-gray-200 italic">
            No specific high-urgency deterministic rules were matched for this presentation.
          </p>
        ) : (
          <div className="space-y-2">
            {result.triggered_rules.map((rule, idx) => (
              <div key={idx} className="p-3 rounded-lg border border-gray-200 bg-gray-50/60 text-xs space-y-1">
                <div className="flex items-center justify-between font-semibold text-gray-900">
                  <span>
                    Rule `{rule.rule_id}`: {rule.rule_name}
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 bg-gray-200 text-gray-800 rounded font-bold text-[10px]">
                      Level {rule.rule_level}
                    </span>
                    <span className="px-2 py-0.5 bg-amber-100 text-amber-900 rounded font-bold text-[10px]">
                      {rule.review_status}
                    </span>
                  </div>
                </div>
                <div className="text-gray-600">
                  <strong>Specialty:</strong> {rule.specialty.replace(/_/g, " ")}
                  {rule.citation && (
                    <span className="block mt-0.5 text-gray-500 font-mono text-[10px]">
                      Citation: {rule.citation}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 6. Explainer Text */}
      <div className="space-y-2 pt-2 border-t border-gray-200">
        <h2 className="text-sm font-bold text-gray-900 uppercase tracking-wider">
          Assessment Explanation & Next Steps
        </h2>
        <div className="bg-gray-50 p-4 rounded-lg border border-gray-200 text-gray-800 text-xs leading-relaxed whitespace-pre-line">
          {result.explanation_text}
        </div>
      </div>

      {/* 7. Guest Retention Notice (if present) */}
      {result.guest_retention_notice && (
        <div className="text-[11px] text-gray-500 text-right pt-2 border-t border-gray-100">
          Privacy Notice: {result.guest_retention_notice}
        </div>
      )}
    </article>
  );
}
