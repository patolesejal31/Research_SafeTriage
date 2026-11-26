"use client";

import React, { useState } from "react";
import { FollowUpAnswer, FollowUpQuestion } from "@/types/assessment";
import { AlertCircle, HelpCircle, ShieldAlert } from "lucide-react";

interface FollowUpSectionProps {
  questions: FollowUpQuestion[];
  skippedQuestions?: FollowUpQuestion[];
  informationIncomplete?: boolean;
  onSubmitAnswers: (answers: FollowUpAnswer[]) => void;
  isLoading?: boolean;
}

export function FollowUpSection({
  questions,
  skippedQuestions = [],
  informationIncomplete = false,
  onSubmitAnswers,
  isLoading = false,
}: FollowUpSectionProps) {
  const [answers, setAnswers] = useState<Record<string, string | number | boolean>>({});

  const handleSelectAnswer = (qId: string, val: string | number | boolean) => {
    setAnswers((prev) => ({ ...prev, [qId]: val }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const formatted: FollowUpAnswer[] = Object.entries(answers).map(([qid, val]) => ({
      question_id: qid,
      answer_value: val,
    }));
    onSubmitAnswers(formatted);
  };

  if (!questions || questions.length === 0) {
    return null;
  }

  // Separate safety-critical from optional
  const safetyCritical = questions.filter((q) => q.safety_critical);
  const optional = questions.filter((q) => !q.safety_critical);

  return (
    <section aria-labelledby="followups-heading" className="bg-white rounded-xl shadow-md border border-gray-200 p-6 space-y-6">
      <div className="border-b border-gray-200 pb-3">
        <h2 id="followups-heading" className="text-lg font-bold text-gray-900 flex items-center gap-2">
          <HelpCircle className="w-5 h-5 text-indigo-600" aria-hidden="true" />
          Clarification Questions (Triage Refinement)
        </h2>
        <p className="text-xs text-gray-600 mt-1">
          Answering these safety questions helps refine urgency stratification. Answers may only escalate urgency, never downgrade.
        </p>
      </div>

      {(informationIncomplete || skippedQuestions.length > 0) && (
        <div role="status" className="p-3 bg-amber-50 border-l-4 border-amber-500 rounded text-amber-900 text-xs flex items-start gap-2">
          <AlertCircle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
          <div>
            <strong>Information Incomplete Notice:</strong> Some questions were omitted due to question caps. Triage level is preserved conservatively and will not be downgraded.
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Safety-Critical Questions Group */}
        {safetyCritical.length > 0 && (
          <div className="space-y-4 bg-red-50/50 p-4 rounded-lg border border-red-200">
            <div className="flex items-center gap-2 text-red-900 font-semibold text-sm">
              <ShieldAlert className="w-4 h-4 text-red-600" />
              <span>Safety-Critical Questions (Always Required)</span>
            </div>
            {safetyCritical.map((q) => (
              <QuestionItem key={q.id} question={q} currentAnswer={answers[q.id]} onSelect={handleSelectAnswer} />
            ))}
          </div>
        )}

        {/* Optional Questions Group (Max 3) */}
        {optional.length > 0 && (
          <div className="space-y-4">
            <div className="text-gray-800 font-semibold text-sm">
              Additional Clinical Clarifications
            </div>
            {optional.map((q) => (
              <QuestionItem key={q.id} question={q} currentAnswer={answers[q.id]} onSelect={handleSelectAnswer} />
            ))}
          </div>
        )}

        <div className="pt-4 flex justify-end">
          <button
            type="submit"
            disabled={isLoading}
            className="px-6 py-2.5 bg-indigo-600 text-white font-medium rounded-lg shadow hover:bg-indigo-700 focus:outline-none focus:ring-4 focus:ring-indigo-200 disabled:opacity-50 transition"
          >
            {isLoading ? "Updating Triage..." : "Submit Answers & Reassess"}
          </button>
        </div>
      </form>
    </section>
  );
}

function QuestionItem({
  question,
  currentAnswer,
  onSelect,
}: {
  question: FollowUpQuestion;
  currentAnswer: string | number | boolean | undefined;
  onSelect: (qId: string, val: string | number | boolean) => void;
}) {
  return (
    <fieldset className="space-y-2">
      <legend className="text-sm font-medium text-gray-900">
        {question.text}
        {question.safety_critical && <span className="text-red-600 ml-1 font-bold">*</span>}
      </legend>

      {question.type === "binary" ? (
        <div className="flex gap-4">
          <label className="inline-flex items-center text-sm text-gray-700 cursor-pointer">
            <input
              type="radio"
              name={`q_${question.id}`}
              value="yes"
              checked={currentAnswer === true || currentAnswer === "yes"}
              onChange={() => onSelect(question.id, true)}
              className="w-4 h-4 text-indigo-600 focus:ring-indigo-500 border-gray-300"
            />
            <span className="ml-2">Yes</span>
          </label>
          <label className="inline-flex items-center text-sm text-gray-700 cursor-pointer">
            <input
              type="radio"
              name={`q_${question.id}`}
              value="no"
              checked={currentAnswer === false || currentAnswer === "no"}
              onChange={() => onSelect(question.id, false)}
              className="w-4 h-4 text-indigo-600 focus:ring-indigo-500 border-gray-300"
            />
            <span className="ml-2">No</span>
          </label>
        </div>
      ) : question.options && question.options.length > 0 ? (
        <div className="flex flex-wrap gap-2">
          {question.options.map((opt) => (
            <label
              key={opt}
              className={`px-3 py-1.5 rounded-md border text-xs font-medium cursor-pointer transition ${
                currentAnswer === opt
                  ? "bg-indigo-50 border-indigo-600 text-indigo-700"
                  : "bg-white border-gray-300 text-gray-700 hover:bg-gray-50"
              }`}
            >
              <input
                type="radio"
                name={`q_${question.id}`}
                value={opt}
                checked={currentAnswer === opt}
                onChange={() => onSelect(question.id, opt)}
                className="sr-only"
              />
              {opt}
            </label>
          ))}
        </div>
      ) : (
        <input
          type={question.free_numeric ? "number" : "text"}
          value={typeof currentAnswer === "boolean" ? "" : (currentAnswer ?? "")}
          onChange={(e) => onSelect(question.id, e.target.value)}
          placeholder="Enter details..."
          className="w-full sm:w-64 px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
        />
      )}
    </fieldset>
  );
}
