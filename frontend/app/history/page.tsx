"use client";

import React, { useEffect, useState } from "react";
import { listAssessments, deleteAssessment, wipeAllAssessments, ApiError, EMERGENCY_FALLBACK_MESSAGE } from "@/lib/api";
import { AssessmentResponse } from "@/types/assessment";
import { UrgencyBadge } from "@/components/UrgencyBadge";
import { History, Trash2, AlertTriangle, ShieldCheck, RefreshCw } from "lucide-react";

export default function HistoryPage() {
  const [assessments, setAssessments] = useState<AssessmentResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [apiError, setApiError] = useState<ApiError | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [isWipingAll, setIsWipingAll] = useState(false);

  const fetchHistory = async () => {
    setIsLoading(true);
    setApiError(null);
    try {
      const data = await listAssessments();
      setAssessments(data);
    } catch (err: unknown) {
      const isApiErr = err && typeof err === "object" && "message" in err;
      const msg = err instanceof Error ? err.message : isApiErr ? String((err as { message: string }).message) : EMERGENCY_FALLBACK_MESSAGE;
      const isEmerg = isApiErr && "isEmergencyFallback" in err ? Boolean((err as { isEmergencyFallback: boolean }).isEmergencyFallback) : true;
      setApiError({
        message: msg,
        isEmergencyFallback: isEmerg,
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleDeleteOne = async (id: string) => {
    if (!confirm("Are you sure you want to permanently delete this assessment record?")) return;
    setDeletingId(id);
    try {
      await deleteAssessment(id);
      setAssessments((prev) => prev.filter((a) => (a.assessment_id || a.id) !== id));
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      alert("Failed to delete assessment: " + msg);
    } finally {
      setDeletingId(null);
    }
  };

  const handleWipeAll = async () => {
    if (
      !confirm(
        "WARNING: This will permanently delete ALL assessment records associated with your account/session. This action cannot be undone. Proceed?"
      )
    ) {
      return;
    }
    setIsWipingAll(true);
    try {
      await wipeAllAssessments();
      setAssessments([]);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      alert("Failed to wipe assessments: " + msg);
    } finally {
      setIsWipingAll(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
        <div className="space-y-1">
          <h1 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <History className="w-6 h-6 text-indigo-600" aria-hidden="true" />
            Triage Assessment History
          </h1>
          <p className="text-xs text-gray-600 max-w-2xl">
            View, inspect, or delete your previous triage evaluations. Under SafeTriage data protection rules,
            guest assessments are automatically purged after 24 hours. You can permanently wipe records at any time.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={fetchHistory}
            disabled={isLoading}
            className="inline-flex items-center px-3 py-1.5 border border-gray-300 rounded-md text-xs font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            aria-label="Refresh assessment list"
          >
            <RefreshCw className={`w-3.5 h-3.5 mr-1 ${isLoading ? "animate-spin" : ""}`} />
            Refresh
          </button>

          {assessments.length > 0 && (
            <button
              onClick={handleWipeAll}
              disabled={isWipingAll}
              className="inline-flex items-center px-3 py-1.5 border border-red-600 rounded-md text-xs font-bold text-red-600 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-red-500 transition"
              aria-label="Wipe all my assessment records"
            >
              <Trash2 className="w-3.5 h-3.5 mr-1" />
              {isWipingAll ? "Wiping..." : "Wipe All Records"}
            </button>
          )}
        </div>
      </div>

      {/* Error state */}
      {apiError && (
        <div role="alert" className="p-4 bg-red-50 border border-red-300 rounded-xl text-red-900 text-sm flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <strong>Error loading history:</strong> {apiError.message}
          </div>
        </div>
      )}

      {/* Loading state */}
      {isLoading && (
        <div className="text-center py-12 text-gray-500 text-sm">
          <RefreshCw className="w-8 h-8 mx-auto animate-spin text-indigo-600 mb-2" />
          Loading your assessment history...
        </div>
      )}

      {/* Empty state */}
      {!isLoading && assessments.length === 0 && !apiError && (
        <div className="bg-white rounded-xl border border-dashed border-gray-300 p-12 text-center text-gray-500 space-y-3">
          <ShieldCheck className="w-12 h-12 text-gray-400 mx-auto" aria-hidden="true" />
          <h2 className="text-base font-semibold text-gray-700">No Assessment Records Found</h2>
          <p className="text-xs text-gray-500 max-w-sm mx-auto">
            You do not have any recorded triage sessions. Run a triage assessment from the home page to see results here.
          </p>
        </div>
      )}

      {/* Records list */}
      {!isLoading && assessments.length > 0 && (
        <div className="space-y-4">
          {assessments.map((asm) => (
            <div
              key={asm.assessment_id}
              className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 space-y-3 hover:border-indigo-300 transition"
            >
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-gray-100 pb-3">
                <div className="flex items-center space-x-3">
                  <UrgencyBadge
                    level={asm.final_urgency}
                    isUncertain={asm.is_uncertain}
                    modelSuggestedUrgency={asm.model_suggested_urgency}
                    modelSuggestionLabel={asm.model_suggestion_label}
                    size="sm"
                  />
                  <span className="text-xs text-gray-500 font-mono">
                    ID: {(asm.assessment_id || asm.id || "unknown").substring(0, 8)}...
                  </span>
                </div>

                <div className="flex items-center space-x-4">
                  {asm.created_at && (
                    <span className="text-xs text-gray-400">
                      {new Date(asm.created_at).toLocaleString()}
                    </span>
                  )}
                  <button
                    onClick={() => handleDeleteOne(asm.assessment_id || asm.id || "")}
                    disabled={deletingId === (asm.assessment_id || asm.id)}
                    className="inline-flex items-center px-2 py-1 text-xs text-red-600 hover:text-red-800 hover:bg-red-50 rounded border border-transparent hover:border-red-200 focus:outline-none focus:ring-2 focus:ring-red-400 transition"
                    aria-label={`Delete assessment ${asm.assessment_id || asm.id}`}
                  >
                    <Trash2 className="w-3.5 h-3.5 mr-1" />
                    {deletingId === (asm.assessment_id || asm.id) ? "Deleting..." : "Delete"}
                  </button>
                </div>
              </div>

              <div className="text-xs text-gray-700 leading-relaxed bg-gray-50/70 p-3 rounded border border-gray-100">
                <strong>Explanation:</strong> {asm.explanation_text}
              </div>

              {asm.triggered_rules && asm.triggered_rules.length > 0 && (
                <div className="text-[11px] text-gray-600 flex flex-wrap gap-2 items-center">
                  <span className="font-semibold text-gray-700">Triggered Rules:</span>
                  {asm.triggered_rules.map((r, i) => (
                    <span key={i} className="px-2 py-0.5 bg-gray-100 border border-gray-200 rounded text-gray-800 font-mono">
                      {r.rule_id} ({r.rule_name})
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
