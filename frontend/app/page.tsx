"use client";

import React, { useState } from "react";
import {
  submitAssessment,
  submitFollowUps,
  ApiError,
  EMERGENCY_FALLBACK_MESSAGE,
} from "@/lib/api";
import {
  AssessmentResponse,
  FollowUpAnswer,
} from "@/types/assessment";
import { EmergencyModal } from "@/components/EmergencyModal";
import { FollowUpSection } from "@/components/FollowUpSection";
import { ResultsView } from "@/components/ResultsView";
import {
  ShieldAlert,
  Send,
  RotateCcw,
  AlertTriangle,
  Info,
  PhoneCall,
} from "lucide-react";

export default function TriagePage() {
  const [symptomText, setSymptomText] = useState("");
  const [ageYears, setAgeYears] = useState<number | undefined>(undefined);
  const [sex, setSex] = useState<string>("prefer_not_to_say");
  const [optInRawText, setOptInRawText] = useState(false);

  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState<ApiError | null>(null);

  const [currentResult, setCurrentResult] = useState<AssessmentResponse | null>(null);
  const [showEmergencyModal, setShowEmergencyModal] = useState(false);

  const handleSubmitInitial = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!symptomText.trim()) return;

    setIsLoading(true);
    setApiError(null);

    try {
      const resp = await submitAssessment({
        symptoms_text: symptomText.trim(),
        age_years: ageYears,
        sex: sex !== "prefer_not_to_say" ? sex : undefined,
        opt_in_store_raw_symptoms: optInRawText,
      });

      setCurrentResult(resp);

      // CRITICAL SAFETY BEHAVIOR:
      // If Level 1 is returned by Stage A/safety-net, pop EmergencyModal IMMEDIATELY before questions!
      if (resp.final_urgency === 1 || resp.is_level_1_emergency) {
        setShowEmergencyModal(true);
      }
    } catch (err: unknown) {
      const errorObj = err as Partial<ApiError>;
      setApiError(
        errorObj && errorObj.message
          ? (err as ApiError)
          : {
              message: EMERGENCY_FALLBACK_MESSAGE,
              isEmergencyFallback: true,
            }
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleFollowUpSubmit = async (answers: FollowUpAnswer[]) => {
    if (!currentResult) return;

    setIsLoading(true);
    setApiError(null);

    try {
      const resp = await submitFollowUps(currentResult.assessment_id, answers);
      setCurrentResult(resp);

      if (resp.final_urgency === 1 || resp.is_level_1_emergency) {
        setShowEmergencyModal(true);
      }
    } catch (err: unknown) {
      const errorObj = err as Partial<ApiError>;
      setApiError(
        errorObj && errorObj.message
          ? (err as ApiError)
          : {
              message: EMERGENCY_FALLBACK_MESSAGE,
              isEmergencyFallback: true,
            }
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setSymptomText("");
    setAgeYears(undefined);
    setSex("prefer_not_to_say");
    setCurrentResult(null);
    setApiError(null);
    setShowEmergencyModal(false);
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Emergency Modal for Level 1 */}
      <EmergencyModal
        isOpen={showEmergencyModal}
        onClose={() => setShowEmergencyModal(false)}
        reason={currentResult?.triggered_rules?.[0]?.rule_name || "Emergency symptoms flagged"}
      />

      {/* Hero / Instruction Banner */}
      <section aria-labelledby="triage-intro-heading" className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-3">
        <h1 id="triage-intro-heading" className="text-2xl font-extrabold text-gray-900 tracking-tight">
          Preliminary Symptom Triage Assessment
        </h1>
        <p className="text-sm text-gray-700 leading-relaxed max-w-4xl">
          Describe your symptoms in natural language (English, Hinglish, or Marathi transliteration).
          Our hybrid deterministic clinical rule engine, NLP entity extractor, and LLM reasoner will evaluate
          urgency level (Level 1 Emergency to Level 4 Self-Care).
        </p>

        <div className="flex flex-wrap items-center gap-3 pt-2 text-xs text-gray-600">
          <span className="inline-flex items-center text-amber-800 bg-amber-50 px-2.5 py-1 rounded border border-amber-200">
            <ShieldAlert className="w-4 h-4 mr-1 text-amber-600" aria-hidden="true" />
            Non-diagnostic research prototype. Never prescribes medications.
          </span>
          <span className="inline-flex items-center text-gray-600 bg-gray-100 px-2.5 py-1 rounded">
            <Info className="w-3.5 h-3.5 mr-1" aria-hidden="true" />
            Guest session data is automatically purged after 24 hours.
          </span>
        </div>
      </section>

      {/* Error / Service Unreachable Banner (directs to 112 / 108) */}
      {apiError && (
        <div
          role="alert"
          aria-live="assertive"
          className={`p-5 rounded-xl border-2 ${
            apiError.isEmergencyFallback
              ? "bg-red-50 border-red-600 text-red-950"
              : "bg-amber-50 border-amber-500 text-amber-950"
          }`}
        >
          <div className="flex items-start space-x-3">
            <AlertTriangle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" aria-hidden="true" />
            <div className="space-y-2">
              <h2 className="font-bold text-base">
                {apiError.isEmergencyFallback ? "Service Connection Notice" : "Assessment Error"}
              </h2>
              <p className="text-sm leading-relaxed">{apiError.message}</p>
              {apiError.isEmergencyFallback && (
                <div className="pt-2 flex flex-wrap gap-3">
                  <a
                    href="tel:112"
                    className="inline-flex items-center px-4 py-2 bg-red-600 text-white font-bold rounded-lg text-xs shadow hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-600"
                  >
                    <PhoneCall className="w-4 h-4 mr-1.5" /> Call 112 (National)
                  </a>
                  <a
                    href="tel:108"
                    className="inline-flex items-center px-4 py-2 bg-red-700 text-white font-bold rounded-lg text-xs shadow hover:bg-red-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-700"
                  >
                    <PhoneCall className="w-4 h-4 mr-1.5" /> Call 108 (Ambulance)
                  </a>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Main Two-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Intake Form */}
        <div className="lg:col-span-5 space-y-6">
          <section aria-labelledby="intake-form-heading" className="bg-white rounded-xl shadow-md border border-gray-200 p-6 space-y-5">
            <h2 id="intake-form-heading" className="text-lg font-bold text-gray-900 border-b border-gray-200 pb-3">
              Describe Presentation
            </h2>

            <form onSubmit={handleSubmitInitial} className="space-y-5">
              {/* Symptom Input Textarea */}
              <div className="space-y-1.5">
                <label htmlFor="symptoms-input" className="block text-sm font-semibold text-gray-900">
                  What symptoms are you experiencing? <span className="text-red-600">*</span>
                </label>
                <textarea
                  id="symptoms-input"
                  name="symptoms_text"
                  required
                  rows={4}
                  maxLength={2000}
                  value={symptomText}
                  onChange={(e) => setSymptomText(e.target.value)}
                  placeholder="e.g., Severe crushing chest pain radiating to left arm for 30 minutes, profuse sweating, difficulty breathing..."
                  className="w-full p-3 border border-gray-300 rounded-lg text-sm text-gray-900 placeholder-gray-400 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 focus:outline-none resize-y"
                  aria-describedby="symptoms-counter"
                />
                <div id="symptoms-counter" className="flex justify-between text-xs text-gray-500">
                  <span>Be descriptive (onset, location, severity, duration).</span>
                  <span>{symptomText.length} / 2000</span>
                </div>
              </div>

              {/* Demographics Row (Optional) */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1 border-t border-gray-100">
                <div className="space-y-1">
                  <label htmlFor="age-input" className="block text-xs font-semibold text-gray-700">
                    Age (Years) <span className="text-gray-400 font-normal">(Optional)</span>
                  </label>
                  <input
                    id="age-input"
                    type="number"
                    min="0"
                    max="125"
                    step="0.1"
                    value={ageYears !== undefined ? ageYears : ""}
                    onChange={(e) => setAgeYears(e.target.value ? parseFloat(e.target.value) : undefined)}
                    placeholder="e.g., 45"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm text-gray-900 focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  />
                </div>

                <div className="space-y-1">
                  <label htmlFor="sex-select" className="block text-xs font-semibold text-gray-700">
                    Biological Sex <span className="text-gray-400 font-normal">(Optional)</span>
                  </label>
                  <select
                    id="sex-select"
                    value={sex}
                    onChange={(e) => setSex(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm text-gray-900 focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  >
                    <option value="prefer_not_to_say">Prefer not to say</option>
                    <option value="female">Female</option>
                    <option value="male">Male</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>

              {/* Privacy Opt-in Toggle */}
              <div className="pt-2 border-t border-gray-100">
                <label className="flex items-start space-x-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={optInRawText}
                    onChange={(e) => setOptInRawText(e.target.checked)}
                    className="w-4 h-4 mt-0.5 text-indigo-600 rounded border-gray-300 focus:ring-indigo-500"
                  />
                  <span className="text-xs text-gray-700 leading-snug">
                    <strong>Research Privacy Opt-In (Default: OFF):</strong> Allow my raw symptom text to be stored
                    for dissertation model training. If unchecked, only anonymized structured medical codes are saved.
                  </span>
                </label>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-between pt-3">
                {currentResult && (
                  <button
                    type="button"
                    onClick={handleReset}
                    className="inline-flex items-center px-3 py-2 text-xs font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md focus:outline-none focus:ring-2 focus:ring-gray-300 transition"
                  >
                    <RotateCcw className="w-3.5 h-3.5 mr-1" />
                    New Assessment
                  </button>
                )}

                <button
                  type="submit"
                  disabled={isLoading || !symptomText.trim()}
                  className="ml-auto inline-flex items-center px-6 py-2.5 bg-indigo-600 text-white font-bold text-sm rounded-lg shadow hover:bg-indigo-700 focus:outline-none focus:ring-4 focus:ring-indigo-200 disabled:opacity-50 transition"
                >
                  <Send className="w-4 h-4 mr-2" />
                  {isLoading ? "Evaluating Triage..." : "Run Triage Assessment"}
                </button>
              </div>
            </form>
          </section>

          {/* Quick Examples for Testing */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 text-xs space-y-2">
            <span className="font-semibold text-gray-700 block">Click to try sample presentations:</span>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() => setSymptomText("Crushing chest pain radiating to left arm, sweating, nausea for 30 minutes")}
                className="px-2.5 py-1 bg-red-50 text-red-800 rounded border border-red-200 hover:bg-red-100 text-left transition"
              >
                🚨 Level 1: Chest Pain
              </button>
              <button
                type="button"
                onClick={() => setSymptomText("Severe right lower quadrant abdominal pain for 6 hours, vomiting and fever")}
                className="px-2.5 py-1 bg-amber-50 text-amber-800 rounded border border-amber-200 hover:bg-amber-100 text-left transition"
              >
                ⚠️ Level 2: Appendicitis
              </button>
              <button
                type="button"
                onClick={() => setSymptomText("Dry cough and mild sore throat for 3 days, no fever and no shortness of breath")}
                className="px-2.5 py-1 bg-blue-50 text-blue-800 rounded border border-blue-200 hover:bg-blue-100 text-left transition"
              >
                🗓️ Level 3: Mild Cough
              </button>
              <button
                type="button"
                onClick={() => setSymptomText("Minor paper cut on index finger, cleaned and bleeding stopped")}
                className="px-2.5 py-1 bg-emerald-50 text-emerald-800 rounded border border-emerald-200 hover:bg-emerald-100 text-left transition"
              >
                🌿 Level 4: Paper Cut
              </button>
              <button
                type="button"
                onClick={() => setSymptomText("Dard nahi hai par thoda ajeeb lag raha hai, not sure what it is")}
                className="px-2.5 py-1 bg-purple-50 text-purple-800 rounded border border-purple-200 hover:bg-purple-100 text-left transition"
              >
                ❓ UNCERTAIN / Hinglish
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Dynamic Follow-Ups and Results */}
        <div className="lg:col-span-7 space-y-6">
          {/* Follow-up Questions (if returned and not yet Level 1 dismissed) */}
          {currentResult && currentResult.followup_questions && currentResult.followup_questions.length > 0 && (
            <FollowUpSection
              questions={currentResult.followup_questions}
              skippedQuestions={currentResult.skipped_followup_questions}
              informationIncomplete={currentResult.information_incomplete}
              onSubmitAnswers={handleFollowUpSubmit}
              isLoading={isLoading}
            />
          )}

          {/* Results View */}
          {currentResult ? (
            <ResultsView result={currentResult} />
          ) : (
            <div className="bg-white rounded-xl shadow-sm border border-dashed border-gray-300 p-12 text-center text-gray-500 space-y-3">
              <ShieldAlert className="w-12 h-12 text-gray-400 mx-auto" aria-hidden="true" />
              <h2 className="text-base font-semibold text-gray-700">Triage Assessment Standby</h2>
              <p className="text-xs text-gray-500 max-w-sm mx-auto">
                Enter your symptoms on the left and submit. Your preliminary stratification and full transparent
                rule/model justification will appear here.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
