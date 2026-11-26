"use client";

import React, { useEffect, useState } from "react";
import { getStoredEvaluationSummary } from "@/lib/api";
import { getStoredUser } from "@/lib/auth";
import { UserProfile } from "@/types/assessment";
import {
  BarChart3,
  ShieldAlert,
  AlertTriangle,
  Lock,
  Cpu,
  GitCommit,
  Hash,
  Database,
  Clock,
  Layers,
} from "lucide-react";
import Link from "next/link";

interface MetricItem {
  accuracy: number;
  macro_f1: number;
  under_triage_rate: number;
  over_triage_rate: number;
  critical_under_triage_count: number;
  uncertain_rate: number;
  macro_f1_bootstrap_ci?: [number, number];
  latency_p95_ms?: number;
}

interface EvaluationPayload {
  metadata: {
    evaluation_tag: string;
    label_caption: string;
    git_commit_hash: string;
    test_checksum: string;
    llm_provider: string;
    n_test_cases: number;
    n_test_families: number;
  };
  hypothesis_status: Record<string, string>;
  same_author_circularity_disclosure: string;
  systems: Record<string, {
    accuracy: number;
    macro_f1: number;
    under_triage_rate: number;
    over_triage_rate: number;
    critical_under_triage_count: number;
    uncertain_rate: number;
    macro_f1_bootstrap_ci: [number, number];
    level1_sensitivity: number;
    level1_2_sensitivity: number;
    latency_p95_ms?: number;
    [key: string]: unknown;
  }>;
  ablations: Record<string, MetricItem>;
  robustness: Record<string, MetricItem>;
}

export default function DashboardPage() {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [data, setData] = useState<EvaluationPayload | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const currentUser = getStoredUser();
    setUser(currentUser);

    // Only fetch if researcher
    if (currentUser?.role === "researcher") {
      getStoredEvaluationSummary()
        .then((res) => {
          setData(res as unknown as EvaluationPayload);
          setIsLoading(false);
        })
        .catch((err) => {
          setError(err.message || "Failed to load stored evaluation summary.");
          setIsLoading(false);
        });
    } else {
      setIsLoading(false);
    }
  }, []);

  // 1. RBAC Guard: Researcher role only
  if (!isLoading && user?.role !== "researcher") {
    return (
      <div className="max-w-2xl mx-auto my-12 bg-white rounded-xl shadow-md border border-gray-200 p-8 text-center space-y-4">
        <div className="w-16 h-16 bg-red-100 text-red-700 rounded-full flex items-center justify-center mx-auto">
          <Lock className="w-8 h-8" />
        </div>
        <h1 className="text-xl font-bold text-gray-900">403 — Researcher Access Required</h1>
        <p className="text-sm text-gray-600 leading-relaxed">
          The SafeTriage Research & Evaluation Dashboard is restricted to authenticated users with the{" "}
          <strong className="text-gray-900 font-mono">researcher</strong> role. Standard user sessions cannot
          access evaluation benchmarks or raw dataset analytics.
        </p>
        <div className="pt-2 flex justify-center gap-4">
          <Link
            href="/login"
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-semibold hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            Login as Researcher
          </Link>
          <Link
            href="/"
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg text-sm font-semibold hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-300"
          >
            Return to Triage
          </Link>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="py-16 text-center text-gray-500 space-y-3">
        <Clock className="w-8 h-8 animate-spin mx-auto text-indigo-600" />
        <p className="text-sm">Loading stored dissertation benchmark results...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-6 bg-red-50 border border-red-300 rounded-xl text-red-950 space-y-2">
        <div className="font-bold text-base flex items-center gap-2 text-red-800">
          <AlertTriangle className="w-5 h-5 text-red-600" />
          Failed to load evaluation results
        </div>
        <p className="text-sm">{error || "No stored evaluation summary found."}</p>
      </div>
    );
  }

  const meta = data.metadata;
  const sys = data.systems;
  const hyp = data.hypothesis_status;
  const abl = data.ablations;
  const rob = data.robustness;

  return (
    <div className="space-y-8 animate-fade-in">
      {/* 1. Header & Governance Metadata Bar */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-gray-200 pb-4">
          <div>
            <h1 className="text-2xl font-black text-gray-900 flex items-center gap-2 tracking-tight">
              <BarChart3 className="w-7 h-7 text-indigo-600" />
              Dissertation Evaluation & Benchmark Dashboard
            </h1>
            <p className="text-xs text-gray-600 mt-1">
              Renders <strong>STORED Phase 7 benchmark outputs</strong>. Metrics are never recomputed on the fly.
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <span className="px-3 py-1 bg-indigo-50 border border-indigo-200 text-indigo-900 font-mono text-xs rounded-full font-bold">
              Tag: {meta.evaluation_tag}
            </span>
            <span className="px-3 py-1 bg-amber-50 border border-amber-200 text-amber-900 font-medium text-xs rounded-full">
              Label: {meta.label_caption}
            </span>
          </div>
        </div>

        {/* Reproducibility metadata cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
          <div className="p-3 bg-gray-50 rounded-lg border border-gray-200 flex items-center space-x-2.5">
            <GitCommit className="w-4 h-4 text-gray-500 flex-shrink-0" />
            <div className="truncate">
              <div className="text-[10px] text-gray-500 font-semibold uppercase">Commit Hash</div>
              <div className="font-mono text-gray-900 truncate" title={meta.git_commit_hash}>
                {meta.git_commit_hash.substring(0, 10)}...
              </div>
            </div>
          </div>

          <div className="p-3 bg-gray-50 rounded-lg border border-gray-200 flex items-center space-x-2.5">
            <Hash className="w-4 h-4 text-gray-500 flex-shrink-0" />
            <div className="truncate">
              <div className="text-[10px] text-gray-500 font-semibold uppercase">Test SHA-256</div>
              <div className="font-mono text-gray-900 truncate" title={meta.test_checksum}>
                {meta.test_checksum.substring(0, 10)}...
              </div>
            </div>
          </div>

          <div className="p-3 bg-gray-50 rounded-lg border border-gray-200 flex items-center space-x-2.5">
            <Cpu className="w-4 h-4 text-gray-500 flex-shrink-0" />
            <div className="truncate">
              <div className="text-[10px] text-gray-500 font-semibold uppercase">LLM Provider</div>
              <div className="font-semibold text-gray-900 truncate">{meta.llm_provider}</div>
            </div>
          </div>

          <div className="p-3 bg-gray-50 rounded-lg border border-gray-200 flex items-center space-x-2.5">
            <Database className="w-4 h-4 text-gray-500 flex-shrink-0" />
            <div className="truncate">
              <div className="text-[10px] text-gray-500 font-semibold uppercase">Dataset Split</div>
              <div className="font-semibold text-gray-900">
                Test: N={meta.n_test_cases} ({meta.n_test_families} families)
              </div>
            </div>
          </div>
        </div>

        {/* Same-author circularity alert */}
        <div className="bg-amber-50 border-l-4 border-amber-600 p-3.5 rounded text-amber-950 text-xs">
          <strong>Methodological Disclosure:</strong> {data.same_author_circularity_disclosure}
        </div>
      </div>

      {/* 2. Hypotheses Status Cards */}
      <section aria-labelledby="hypotheses-heading" className="space-y-3">
        <h2 id="hypotheses-heading" className="text-base font-bold text-gray-900 flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-indigo-600" />
          Dissertation Hypotheses Status
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <HypothesisCard
            id="H1"
            title="LLM improves sensitivity beyond rules"
            status={hyp.H1_llm_improves_sensitivity}
            note="Evaluated with MockProvider. Real provider runs require external API keys."
          />
          <HypothesisCard
            id="H2"
            title="Deterministic safety-net prevents critical under-triage"
            status={hyp.H2_deterministic_safety_net_prevents_critical_undertriage}
            note="0.0% Level 1 cases under-triaged on test cohort."
          />
          <HypothesisCard
            id="H3"
            title="LLM explanations increase comprehension"
            status={hyp.H3_llm_explanations_increase_user_comprehension}
            note="Requires human-subjects clinician and patient comprehension study."
          />
          <HypothesisCard
            id="H4"
            title="LLM clinical reasoning reduces over-triage"
            status={hyp.H4_llm_reasoning_reduces_overtriage_safely}
            note="Evaluated with MockProvider. Real provider runs require external API keys."
          />
        </div>
      </section>

      {/* 3. Main Benchmark Comparison Table */}
      <section aria-labelledby="benchmark-heading" className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-4 overflow-x-auto">
        <h2 id="benchmark-heading" className="text-base font-bold text-gray-900 flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-indigo-600" />
          Main Benchmark Comparison (Always-Level-1 Safety Reference)
        </h2>
        <p className="text-xs text-gray-600">
          Evaluated on <code>test.json</code>. Always-Level-1 represents the maximum-safety zero-undertriage baseline.
        </p>

        <table className="w-full text-left text-xs text-gray-700 border-collapse">
          <thead>
            <tr className="bg-gray-100 text-gray-900 border-b border-gray-300 font-bold">
              <th className="py-2.5 px-3">Metric</th>
              <th className="py-2.5 px-3 text-center bg-red-50 text-red-900">Always-Level-1 (Baseline)</th>
              <th className="py-2.5 px-3 text-center">Majority-Class</th>
              <th className="py-2.5 px-3 text-center">Rule-Only</th>
              <th className="py-2.5 px-3 text-center">ML-Only</th>
              <th className="py-2.5 px-3 text-center">LLM-Only (MOCK)</th>
              <th className="py-2.5 px-3 text-center bg-indigo-50 text-indigo-900">SafeTriage Hybrid</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 font-mono">
            <tr>
              <td className="py-2 px-3 font-sans font-semibold text-gray-900">Accuracy</td>
              <td className="py-2 px-3 text-center bg-red-50/40">{sys.always_level_1.accuracy.toFixed(3)}</td>
              <td className="py-2 px-3 text-center">{sys.majority_class.accuracy.toFixed(3)}</td>
              <td className="py-2 px-3 text-center">{sys.rule_only.accuracy.toFixed(3)}</td>
              <td className="py-2 px-3 text-center">{sys.ml_only.accuracy.toFixed(3)}</td>
              <td className="py-2 px-3 text-center">{sys.llm_only.accuracy.toFixed(3)}</td>
              <td className="py-2 px-3 text-center bg-indigo-50/60 font-bold text-indigo-900">{sys.hybrid.accuracy.toFixed(3)}</td>
            </tr>
            <tr>
              <td className="py-2 px-3 font-sans font-semibold text-gray-900">Macro F1 (95% Clustered CI)</td>
              <td className="py-2 px-3 text-center bg-red-50/40">{sys.always_level_1.macro_f1.toFixed(3)}</td>
              <td className="py-2 px-3 text-center">
                {sys.majority_class.macro_f1.toFixed(3)} [{sys.majority_class.macro_f1_bootstrap_ci[0]}, {sys.majority_class.macro_f1_bootstrap_ci[1]}]
              </td>
              <td className="py-2 px-3 text-center">
                {sys.rule_only.macro_f1.toFixed(3)} [{sys.rule_only.macro_f1_bootstrap_ci[0]}, {sys.rule_only.macro_f1_bootstrap_ci[1]}]
              </td>
              <td className="py-2 px-3 text-center">
                {sys.ml_only.macro_f1.toFixed(3)} [{sys.ml_only.macro_f1_bootstrap_ci[0]}, {sys.ml_only.macro_f1_bootstrap_ci[1]}]
              </td>
              <td className="py-2 px-3 text-center">
                {sys.llm_only.macro_f1.toFixed(3)} [{sys.llm_only.macro_f1_bootstrap_ci[0]}, {sys.llm_only.macro_f1_bootstrap_ci[1]}]
              </td>
              <td className="py-2 px-3 text-center bg-indigo-50/60 font-bold text-indigo-900">
                {sys.hybrid.macro_f1.toFixed(3)} [{sys.hybrid.macro_f1_bootstrap_ci[0]}, {sys.hybrid.macro_f1_bootstrap_ci[1]}]
              </td>
            </tr>
            <tr className="bg-red-50/20">
              <td className="py-2 px-3 font-sans font-bold text-red-950">Under-Triage Rate</td>
              <td className="py-2 px-3 text-center bg-red-50/40 font-bold">{sys.always_level_1.under_triage_rate.toFixed(3)}</td>
              <td className="py-2 px-3 text-center">{sys.majority_class.under_triage_rate.toFixed(3)}</td>
              <td className="py-2 px-3 text-center">{sys.rule_only.under_triage_rate.toFixed(3)}</td>
              <td className="py-2 px-3 text-center">{sys.ml_only.under_triage_rate.toFixed(3)}</td>
              <td className="py-2 px-3 text-center">{sys.llm_only.under_triage_rate.toFixed(3)}</td>
              <td className="py-2 px-3 text-center bg-indigo-50/60 font-bold text-emerald-700">{sys.hybrid.under_triage_rate.toFixed(3)}</td>
            </tr>
            <tr>
              <td className="py-2 px-3 font-sans font-bold text-red-900">Critical L1 Misses</td>
              <td className="py-2 px-3 text-center bg-red-50/40">0</td>
              <td className="py-2 px-3 text-center">{sys.majority_class.critical_under_triage_count}</td>
              <td className="py-2 px-3 text-center">{sys.rule_only.critical_under_triage_count}</td>
              <td className="py-2 px-3 text-center">{sys.ml_only.critical_under_triage_count}</td>
              <td className="py-2 px-3 text-center">{sys.llm_only.critical_under_triage_count}</td>
              <td className="py-2 px-3 text-center bg-indigo-50/60 font-bold text-emerald-700">{sys.hybrid.critical_under_triage_count}</td>
            </tr>
            <tr>
              <td className="py-2 px-3 font-sans font-semibold text-gray-900">Over-Triage Rate</td>
              <td className="py-2 px-3 text-center bg-red-50/40">{sys.always_level_1.over_triage_rate.toFixed(3)}</td>
              <td className="py-2 px-3 text-center">{sys.majority_class.over_triage_rate.toFixed(3)}</td>
              <td className="py-2 px-3 text-center">{sys.rule_only.over_triage_rate.toFixed(3)}</td>
              <td className="py-2 px-3 text-center">{sys.ml_only.over_triage_rate.toFixed(3)}</td>
              <td className="py-2 px-3 text-center">{sys.llm_only.over_triage_rate.toFixed(3)}</td>
              <td className="py-2 px-3 text-center bg-indigo-50/60">{sys.hybrid.over_triage_rate.toFixed(3)}</td>
            </tr>
            <tr>
              <td className="py-2 px-3 font-sans font-semibold text-gray-900">UNCERTAIN Rate</td>
              <td className="py-2 px-3 text-center bg-red-50/40">{sys.always_level_1.uncertain_rate.toFixed(3)}</td>
              <td className="py-2 px-3 text-center">{sys.majority_class.uncertain_rate.toFixed(3)}</td>
              <td className="py-2 px-3 text-center">{sys.rule_only.uncertain_rate.toFixed(3)}</td>
              <td className="py-2 px-3 text-center">{sys.ml_only.uncertain_rate.toFixed(3)}</td>
              <td className="py-2 px-3 text-center">{sys.llm_only.uncertain_rate.toFixed(3)}</td>
              <td className="py-2 px-3 text-center bg-indigo-50/60">{sys.hybrid.uncertain_rate.toFixed(3)}</td>
            </tr>
            <tr>
              <td className="py-2 px-3 font-sans font-semibold text-gray-900">Latency (p95 ms)</td>
              <td className="py-2 px-3 text-center bg-red-50/40">0.0</td>
              <td className="py-2 px-3 text-center">0.0</td>
              <td className="py-2 px-3 text-center">{sys.rule_only.latency_p95_ms} ms</td>
              <td className="py-2 px-3 text-center">{sys.ml_only.latency_p95_ms} ms</td>
              <td className="py-2 px-3 text-center">{sys.llm_only.latency_p95_ms} ms</td>
              <td className="py-2 px-3 text-center bg-indigo-50/60 font-semibold">{sys.hybrid.latency_p95_ms} ms</td>
            </tr>
          </tbody>
        </table>
      </section>

      {/* 4. Ablations & Robustness Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Ablations */}
        <section aria-labelledby="ablations-heading" className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-3">
          <h2 id="ablations-heading" className="text-base font-bold text-gray-900 flex items-center gap-2">
            <Layers className="w-5 h-5 text-indigo-600" />
            Architectural Ablations
          </h2>
          <div className="space-y-2">
            {Object.entries(abl).map(([k, v]: [string, MetricItem]) => (
              <div key={k} className="p-3 bg-gray-50 border border-gray-200 rounded-lg text-xs flex justify-between items-center">
                <div>
                  <span className="font-mono font-bold text-gray-900 block">{k}</span>
                  <span className="text-gray-500">Under-triage: {v.under_triage_rate.toFixed(3)} | Over-triage: {v.over_triage_rate.toFixed(3)}</span>
                </div>
                <div className="text-right font-mono">
                  <span className="block font-bold text-gray-900">F1: {v.macro_f1.toFixed(3)}</span>
                  <span className="text-[10px] text-gray-500">Acc: {v.accuracy.toFixed(3)}</span>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Robustness */}
        <section aria-labelledby="robustness-heading" className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-3">
          <h2 id="robustness-heading" className="text-base font-bold text-gray-900 flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-indigo-600" />
            Robustness Stress Testing (7 Perturbations)
          </h2>
          <div className="space-y-2">
            {Object.entries(rob).map(([k, v]: [string, MetricItem]) => (
              <div key={k} className="p-3 bg-gray-50 border border-gray-200 rounded-lg text-xs flex justify-between items-center">
                <div>
                  <span className="font-mono font-bold text-gray-900 block capitalize">{k.replace(/_/g, " ")}</span>
                  <span className="text-gray-500">
                    L1 Misses: <strong className={v.critical_under_triage_count > 0 ? "text-red-600" : "text-emerald-700"}>{v.critical_under_triage_count}</strong> | UNCERTAIN: {(v.uncertain_rate * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="text-right font-mono">
                  <span className="block font-bold text-gray-900">Acc: {v.accuracy.toFixed(3)}</span>
                  <span className="text-[10px] text-gray-500">Under: {v.under_triage_rate.toFixed(3)}</span>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

function HypothesisCard({
  id,
  title,
  status,
  note,
}: {
  id: string;
  title: string;
  status: string;
  note: string;
}) {
  const isBlocked = status.includes("BLOCKED");
  const isSupported = status.includes("SUPPORTED");

  return (
    <div className={`p-4 rounded-xl border ${isBlocked ? "bg-gray-50 border-gray-200" : "bg-emerald-50/50 border-emerald-200"}`}>
      <div className="flex items-center justify-between text-xs font-bold mb-1">
        <span className="text-gray-700 font-mono">{id}</span>
        <span
          className={`px-2 py-0.5 rounded text-[10px] uppercase tracking-wider font-bold ${
            isBlocked
              ? "bg-gray-200 text-gray-800"
              : isSupported
              ? "bg-emerald-100 text-emerald-900"
              : "bg-red-100 text-red-900"
          }`}
        >
          {isBlocked ? "BLOCKED" : isSupported ? "SUPPORTED" : "REFUTED"}
        </span>
      </div>
      <div className="font-semibold text-sm text-gray-900 mb-1">{title}</div>
      <p className="text-xs text-gray-500 leading-snug">{note}</p>
    </div>
  );
}
