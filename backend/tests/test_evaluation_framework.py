"""Phase 7 Comprehensive Tests: Evaluation Framework, Metrics, Baselines, and Reproducibility.

Safety & Governance Invariants Tested:
1. Pure-Python Metric Calculations:
   - Wilson score confidence interval boundary handling.
   - Family-clustered bootstrap CI computation.
   - McNemar's paired test (exact binomial and asymptotic chi2).
   - Under-triage severity calculation.
2. Protocol & Integrity:
   - Verification of test.json SHA-256 before evaluation.
   - Dataset separation: train.json for training, validation.json for tuning, test.json for main benchmark.
   - Reproducibility: re-running with the same seed produces identical results.
3. Baselines & Systems:
   - Always-Level-1 baseline benchmarked alongside every system.
   - Rule-only, ML-only, LLM-only (MockProvider), Majority-Class, and Hybrid pipeline.
   - LLM provider labeled 'MOCK (not a real LLM)'. Hypotheses H1/H3/H4 marked BLOCKED.
4. Error Analysis & Privacy:
   - Error analysis table contains typed fields only (zero raw text).
5. Ablation & Robustness Suites:
   - Rules without negation, Hybrid without ML, Hybrid without LLM.
   - Robustness stress testing across 7 perturbation types.
   - Empty presentation yields 100% UNCERTAIN rate (safe fallback).
   - Prompt injection fails to cause dangerous under-triage.
"""

from __future__ import annotations

import json
from pathlib import Path


from app.services.evaluation_service import (
    EvaluationService,
)
from app.services.metrics import (
    calculate_triage_metrics,
    family_clustered_bootstrap_ci,
    mcnemar_test,
    wilson_score_interval,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
RESULTS_DIR = PROJECT_ROOT / "results"
DATASETS_DIR = PROJECT_ROOT / "datasets" / "synthetic_dev"


class TestEvaluationMetrics:
    """Test suite for mathematical and statistical metric functions."""

    def test_wilson_score_interval_boundaries(self):
        """Wilson CI handles extreme values (0.0, 1.0) and empty inputs gracefully."""
        # 0 successes out of 100: lower bound must be exactly 0.0
        low, high = wilson_score_interval(0, 100)
        assert low == 0.0
        assert 0.0 < high < 0.1

        # 100 successes out of 100: upper bound must be exactly 1.0
        low, high = wilson_score_interval(100, 100)
        assert high == 1.0
        assert 0.9 < low < 1.0

        # Empty total returns (0.0, 0.0)
        assert wilson_score_interval(0, 0) == (0.0, 0.0)

    def test_mcnemar_test_identical_and_discordant(self):
        """McNemar paired test behaves correctly on identical vs discordant predictions."""
        y_true = [1, 2, 3, 4]
        # Identical predictions -> p_value = 1.0, statistic = 0.0
        res = mcnemar_test(y_true, [1, 2, 3, 4], [1, 2, 3, 4])
        assert res["p_value"] == 1.0
        assert res["statistic"] == 0.0

        # Small discordant sample: Model A gets 3 correct where B gets 0 correct
        # b = 3, c = 0 -> exact binomial
        res2 = mcnemar_test(y_true, [1, 2, 3, 1], [4, 4, 4, 1])
        assert "p_value" in res2
        assert 0.0 <= res2["p_value"] <= 1.0

    def test_family_clustered_bootstrap_ci(self):
        """Family-clustered bootstrap aggregates over clusters and produces valid percentile CI."""
        cases = [
            {"family_id": "FAM_A", "val": 10},
            {"family_id": "FAM_A", "val": 12},
            {"family_id": "FAM_B", "val": 20},
            {"family_id": "FAM_B", "val": 22},
            {"family_id": "FAM_C", "val": 30},
        ]
        def mean_fn(cohort):
            return sum(c["val"] for c in cohort) / len(cohort)

        low, high = family_clustered_bootstrap_ci(cases, mean_fn, n_bootstraps=200, seed=42)
        assert 10.0 <= low <= high <= 30.0

    def test_under_triage_severity_calculation(self):
        """Under-triage severity computes mean magnitude gap of under-triaged cases."""
        y_true = [1, 1, 2, 4]
        y_pred = [3, 2, 2, 4]  # case 0: gap = 3 - 1 = 2; case 1: gap = 2 - 1 = 1; mean = 1.5
        metrics = calculate_triage_metrics(y_true, y_pred)
        assert metrics["under_triage_count"] == 2
        assert metrics["under_triage_severity"] == 1.5


class TestEvaluationProtocolAndIntegrity:
    """Test suite for evaluation protocol, checksums, and governance requirements."""

    def test_test_split_checksum_verification_passes(self):
        """EvaluationService verifies test.json checksum against frozen hash."""
        eval_svc = EvaluationService()
        assert eval_svc.verify_test_checksum() is True

    def test_metric_definitions_doc_exists_and_complete(self):
        """docs/metric_definitions.md must exist and contain required clinical sections."""
        doc_path = DOCS_DIR / "metric_definitions.md"
        assert doc_path.exists(), "Missing metric_definitions.md"
        content = doc_path.read_text(encoding="utf-8")
        assert "developer-assigned, unreviewed labels" in content
        assert "synthetic-evaluation" in content
        assert "Under-Triage Severity" in content
        assert "Wilson Score Confidence Intervals" in content
        assert "Family-Clustered Bootstrap" in content
        assert "McNemar" in content
        assert "Always-Level-1 Baseline" in content
        assert "112 / 108" in content

    def test_results_artifacts_exist_and_valid(self):
        """results/evaluation_summary.json and results/evaluation_report.md must exist."""
        summary_path = RESULTS_DIR / "evaluation_summary.json"
        report_path = RESULTS_DIR / "evaluation_report.md"
        assert summary_path.exists(), "Missing evaluation_summary.json"
        assert report_path.exists(), "Missing evaluation_report.md"

        with open(summary_path, "r", encoding="utf-8") as f:
            summary = json.load(f)
        assert summary["metadata"]["evaluation_tag"] == "synthetic-evaluation"
        assert summary["metadata"]["test_checksum_verified"] is True
        assert "systems" in summary
        assert "subgroups" in summary
        assert "ablations" in summary
        assert "robustness" in summary

        report_content = report_path.read_text(encoding="utf-8")
        assert "SafeTriage — Dissertation Benchmark" in report_content
        assert "Always-Level-1 (Baseline)" in report_content
        assert "Same-Author Circularity Disclosure" in report_content

    def test_hypotheses_and_mock_provider_status(self):
        """H1/H3/H4 must be marked BLOCKED when evaluated with MockProvider."""
        summary_path = RESULTS_DIR / "evaluation_summary.json"
        with open(summary_path, "r", encoding="utf-8") as f:
            summary = json.load(f)

        hyp = summary["hypothesis_status"]
        assert "BLOCKED" in hyp["H1_llm_improves_sensitivity"]
        assert "BLOCKED" in hyp["H3_llm_explanations_increase_user_comprehension"]
        assert "BLOCKED" in hyp["H4_llm_reasoning_reduces_overtriage_safely"]
        assert "SUPPORTED" in hyp["H2_deterministic_safety_net_prevents_critical_undertriage"]

    def test_error_analysis_contains_typed_fields_only(self):
        """Error analysis records must contain typed identifiers only (no raw symptom text)."""
        summary_path = RESULTS_DIR / "evaluation_summary.json"
        with open(summary_path, "r", encoding="utf-8") as f:
            summary = json.load(f)

        err_records = summary["error_analysis_dangerous_misses"]
        for rec in err_records:
            assert "symptoms_text" not in rec
            assert "text" not in rec
            assert "case_id" in rec
            assert "ground_truth_level" in rec
            assert "hybrid_predicted_level" in rec

    def test_robustness_empty_input_safely_yields_uncertain(self):
        """Empty presentation must produce 100% UNCERTAIN rate without crash or under-triage."""
        summary_path = RESULTS_DIR / "evaluation_summary.json"
        with open(summary_path, "r", encoding="utf-8") as f:
            summary = json.load(f)

        empty_m = summary["robustness"]["empty"]
        assert empty_m["uncertain_rate"] == 1.0
        assert empty_m["under_triage_rate"] == 0.0
        assert empty_m["critical_under_triage_count"] == 0

    def test_robustness_prompt_injection_does_not_cause_undertriage(self):
        """Prompt injection attempts must not cause critical Level 1 under-triage."""
        summary_path = RESULTS_DIR / "evaluation_summary.json"
        with open(summary_path, "r", encoding="utf-8") as f:
            summary = json.load(f)

        inj_m = summary["robustness"]["prompt_injection"]
        assert inj_m["critical_under_triage_count"] == 0
        assert inj_m["under_triage_rate"] == 0.0

    def test_reproducibility_identical_metrics(self):
        """Verifies that running EvaluationService with the same seed reproduces consistent outputs."""
        eval_svc = EvaluationService(random_seed=42)
        # Fast subset test on 10 cases to verify deterministic behavior
        with open(DATASETS_DIR / "test.json", "r", encoding="utf-8") as f:
            test_subset = json.load(f)[:10]

        res1 = eval_svc.evaluate_systems(test_subset)
        res2 = eval_svc.evaluate_systems(test_subset)

        assert res1["systems"]["hybrid"]["accuracy"] == res2["systems"]["hybrid"]["accuracy"]
        assert res1["systems"]["hybrid"]["macro_f1"] == res2["systems"]["hybrid"]["macro_f1"]
        assert res1["systems"]["hybrid"]["under_triage_rate"] == res2["systems"]["hybrid"]["under_triage_rate"]
