"""Pure-Python Inter-Rater Reliability & Clinical Triage Evaluation Metrics.

Implements:
1. Cohen's Kappa (inter-rater agreement with zero-variance and unequal label support).
2. Wilson Score Confidence Intervals (asymptotically stable binomial proportion CIs).
3. Family-Clustered Bootstrap Confidence Intervals (preserving template family isolation).
4. McNemar's Paired Test (with continuity correction and exact binomial for small samples).
5. Comprehensive Clinical Triage Metrics:
   - Under-triage rate, critical under-triage (L1 missed), under-triage severity
   - Over-triage rate, UNCERTAIN rate (distinct state)
   - L1 sensitivity/specificity, L1+2 sensitivity/specificity
   - Multi-class confusion matrix with explicit UNCERTAIN column
   - Macro/Weighted F1, Per-class Precision/Recall/Specificity
"""

import math
import random
from typing import Any, Callable, Dict, List, Sequence, Set, Tuple


def cohen_kappa(rater1: Sequence[Any], rater2: Sequence[Any]) -> float:
    """Calculate Cohen's kappa coefficient for inter-rater agreement.

    Args:
        rater1: Sequence of categorical ratings from rater 1.
        rater2: Sequence of categorical ratings from rater 2.

    Returns:
        Cohen's kappa coefficient in range [-1.0, 1.0].

    Raises:
        ValueError: If inputs are empty or lengths differ.
    """
    n = len(rater1)
    if n == 0:
        raise ValueError("Cannot calculate Cohen's kappa on empty ratings sequences.")
    if len(rater2) != n:
        raise ValueError(f"Ratings sequences must have equal length: got {n} and {len(rater2)}.")

    # Distinct categories across both raters (handles unequal label sets)
    categories: Set[Any] = set(rater1).union(set(rater2))

    # Observed agreement (p_o)
    agreements = sum(1 for r1, r2 in zip(rater1, rater2) if r1 == r2)
    p_o = agreements / n

    # Marginal counts per category for expected chance agreement (p_e)
    r1_counts: Dict[Any, int] = {cat: 0 for cat in categories}
    r2_counts: Dict[Any, int] = {cat: 0 for cat in categories}

    for r1 in rater1:
        r1_counts[r1] += 1
    for r2 in rater2:
        r2_counts[r2] += 1

    p_e = sum((r1_counts[cat] / n) * (r2_counts[cat] / n) for cat in categories)

    # Zero variance / indeterminate case handling:
    # If both raters assign the exact same single class to every item, p_e == 1.0 and p_o == 1.0.
    # Agreement is complete, so kappa is defined as 1.0.
    if p_e >= 1.0:
        return 1.0 if p_o >= 1.0 else 0.0

    kappa = (p_o - p_e) / (1.0 - p_e)
    return round(kappa, 6)


def wilson_score_interval(successes: int, total: int, confidence: float = 0.95) -> Tuple[float, float]:
    """Calculate the Wilson score confidence interval for a binomial proportion.

    Args:
        successes: Number of successful outcomes (e.g. correct triages or under-triages).
        total: Total number of trials.
        confidence: Desired confidence level (default 0.95).

    Returns:
        Tuple of (lower_bound, upper_bound) in range [0.0, 1.0].
    """
    if total <= 0:
        return (0.0, 0.0)

    # Standard normal quantile: 95% -> 1.959964, 99% -> 2.575829
    z_map = {0.90: 1.644853, 0.95: 1.959964, 0.99: 2.575829}
    z = z_map.get(confidence, 1.959964)

    p = successes / total
    z2 = z * z
    denom = 1.0 + (z2 / total)
    center = (p + (z2 / (2.0 * total))) / denom
    margin = (z / denom) * math.sqrt((p * (1.0 - p) / total) + (z2 / (4.0 * total * total)))

    lower = max(0.0, center - margin)
    upper = min(1.0, center + margin)
    return (round(lower, 4), round(upper, 4))


def mcnemar_test(
    y_true: Sequence[Any],
    y_pred_a: Sequence[Any],
    y_pred_b: Sequence[Any],
) -> Dict[str, float]:
    """Calculate McNemar's paired test for comparing two classifiers against ground truth.

    Args:
        y_true: Sequence of true labels.
        y_pred_a: Sequence of predictions from model A.
        y_pred_b: Sequence of predictions from model B.

    Returns:
        Dict with 'statistic' (chi2), 'p_value', 'discordant_a' (b), 'discordant_b' (c).
    """
    n = len(y_true)
    if len(y_pred_a) != n or len(y_pred_b) != n:
        raise ValueError(f"Lengths must match: true={n}, pred_a={len(y_pred_a)}, pred_b={len(y_pred_b)}")

    # b: A correct, B incorrect
    # c: B correct, A incorrect
    b = 0
    c = 0
    for yt, ya, yb in zip(y_true, y_pred_a, y_pred_b):
        a_correct = (ya == yt)
        b_correct = (yb == yt)
        if a_correct and not b_correct:
            b += 1
        elif b_correct and not a_correct:
            c += 1

    total_discordant = b + c
    if total_discordant == 0:
        return {"statistic": 0.0, "p_value": 1.0, "discordant_a": 0, "discordant_b": 0}

    # Small sample: exact two-sided binomial test
    if total_discordant < 25:
        k = min(b, c)
        p_val = 2.0 * sum(math.comb(total_discordant, i) * (0.5 ** total_discordant) for i in range(k + 1))
        p_val = min(1.0, p_val)
        return {"statistic": float((b - c) ** 2 / total_discordant), "p_value": round(p_val, 6), "discordant_a": b, "discordant_b": c}

    # Asymptotic chi-square with Edwards continuity correction
    chi2 = ((abs(b - c) - 1.0) ** 2) / total_discordant
    # p-value from chi-square distribution with df=1: p = erfc(sqrt(chi2 / 2))
    p_val = math.erfc(math.sqrt(chi2 / 2.0))
    return {"statistic": round(chi2, 4), "p_value": round(p_val, 6), "discordant_a": b, "discordant_b": c}


def family_clustered_bootstrap_ci(
    cases: List[Dict[str, Any]],
    metric_fn: Callable[[List[Dict[str, Any]]], float],
    cluster_key: str = "family_id",
    n_bootstraps: int = 1000,
    seed: int = 42,
    alpha: float = 0.05,
) -> Tuple[float, float]:
    """Calculate empirical percentile confidence interval using family-clustered bootstrap.

    Preserves cluster integrity by sampling entire families with replacement rather
    than independent case resampling.

    Args:
        cases: List of case dictionaries containing `cluster_key`.
        metric_fn: Callable taking a resampled list of cases and returning a float metric.
        cluster_key: Key in case dict identifying the cluster (default 'family_id').
        n_bootstraps: Number of bootstrap iterations (default 1000).
        seed: Random seed for deterministic reproducibility.
        alpha: Significance level (default 0.05 for 95% CI).

    Returns:
        Tuple of (lower_percentile, upper_percentile).
    """
    if not cases:
        return (0.0, 0.0)

    # Group cases by family
    family_map: Dict[str, List[Dict[str, Any]]] = {}
    for c in cases:
        fam = c.get(cluster_key, "unknown")
        family_map.setdefault(fam, []).append(c)

    distinct_families = sorted(family_map.keys())
    k = len(distinct_families)
    if k == 0:
        return (0.0, 0.0)

    rng = random.Random(seed)
    boot_estimates: List[float] = []

    for _ in range(n_bootstraps):
        sampled_families = rng.choices(distinct_families, k=k)
        resampled_cohort: List[Dict[str, Any]] = []
        for fam in sampled_families:
            resampled_cohort.extend(family_map[fam])
        estimate = metric_fn(resampled_cohort)
        boot_estimates.append(estimate)

    boot_estimates.sort()
    lower_idx = int((alpha / 2.0) * n_bootstraps)
    upper_idx = int((1.0 - alpha / 2.0) * n_bootstraps)
    lower_idx = max(0, min(lower_idx, n_bootstraps - 1))
    upper_idx = max(0, min(upper_idx, n_bootstraps - 1))

    return (round(boot_estimates[lower_idx], 4), round(boot_estimates[upper_idx], 4))


def calculate_triage_metrics(
    y_true: Sequence[int],
    y_pred: Sequence[Any],
) -> Dict[str, Any]:
    """Compute comprehensive triage performance and safety metrics.

    Args:
        y_true: Ground truth urgency levels (1, 2, 3, 4).
        y_pred: Predicted urgency levels (1, 2, 3, 4, or 'UNCERTAIN' / None).

    Returns:
        Dictionary of calculated metrics, confusion matrix, and safety CIs.
    """
    n = len(y_true)
    if n == 0:
        raise ValueError("Cannot calculate triage metrics on empty dataset.")
    if len(y_pred) != n:
        raise ValueError(f"Lengths must match: true={n}, pred={len(y_pred)}")

    # 1. Separate valid levels from UNCERTAIN / None
    uncertain_count = 0
    valid_pairs: List[Tuple[int, int]] = []
    all_pairs: List[Tuple[int, Any]] = []

    for yt, yp in zip(y_true, y_pred):
        is_unc = (yp is None or yp == "UNCERTAIN" or yp == 0)
        norm_yp = "UNCERTAIN" if is_unc else int(yp)
        all_pairs.append((yt, norm_yp))
        if is_unc:
            uncertain_count += 1
        else:
            valid_pairs.append((yt, norm_yp))

    n_valid = len(valid_pairs)
    uncertain_rate = uncertain_count / n

    # 2. Confusion Matrix: rows 1..4, cols 1..4 + 'UNCERTAIN'
    confusion_matrix: Dict[str, int] = {}
    for yt in [1, 2, 3, 4]:
        for yp_col in [1, 2, 3, 4, "UNCERTAIN"]:
            confusion_matrix[f"true_{yt}_pred_{yp_col}"] = 0

    for yt, yp in all_pairs:
        confusion_matrix[f"true_{yt}_pred_{yp}"] += 1

    # 3. Under-triage & Over-triage on valid predictions
    under_triage_count = 0
    under_triage_severity_sum = 0
    over_triage_count = 0
    correct_count = 0
    critical_under_triage_count = 0  # True L1 predicted as L3 or L4
    total_l1_count = sum(1 for yt in y_true if yt == 1)

    for yt, yp in valid_pairs:
        if yp == yt:
            correct_count += 1
        elif yp > yt:
            # Dangerous under-triage (predicted lower urgency)
            under_triage_count += 1
            under_triage_severity_sum += (yp - yt)
            if yt == 1 and yp in (3, 4):
                critical_under_triage_count += 1
        elif yp < yt:
            # Over-triage (predicted higher urgency)
            over_triage_count += 1

    under_triage_rate = under_triage_count / n_valid if n_valid > 0 else 0.0
    over_triage_rate = over_triage_count / n_valid if n_valid > 0 else 0.0
    under_triage_severity = under_triage_severity_sum / under_triage_count if under_triage_count > 0 else 0.0
    critical_under_triage_rate = critical_under_triage_count / total_l1_count if total_l1_count > 0 else 0.0
    accuracy = correct_count / n_valid if n_valid > 0 else 0.0

    under_triage_ci = wilson_score_interval(under_triage_count, n_valid)
    over_triage_ci = wilson_score_interval(over_triage_count, n_valid)

    # 4. Per-Class Precision, Recall, Specificity, F1
    per_class: Dict[int, Dict[str, float]] = {}
    f1_list: List[float] = []
    weighted_f1_sum = 0.0

    for c in [1, 2, 3, 4]:
        tp = sum(1 for yt, yp in valid_pairs if yt == c and yp == c)
        fp = sum(1 for yt, yp in valid_pairs if yt != c and yp == c)
        fn = sum(1 for yt, yp in valid_pairs if yt == c and yp != c)
        tn = sum(1 for yt, yp in valid_pairs if yt != c and yp != c)

        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        f1 = (2.0 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

        class_prevalence = sum(1 for yt in y_true if yt == c)
        per_class[c] = {
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "specificity": round(spec, 4),
            "f1": round(f1, 4),
            "support": class_prevalence,
        }
        f1_list.append(f1)
        weighted_f1_sum += f1 * class_prevalence

    macro_f1 = sum(f1_list) / 4.0
    weighted_f1 = weighted_f1_sum / n

    # 5. Emergency Sensitivity & Specificity
    # Level 1 Sensitivity (TP / total true L1)
    l1_tp = sum(1 for yt, yp in valid_pairs if yt == 1 and yp == 1)
    l1_sensitivity = l1_tp / total_l1_count if total_l1_count > 0 else 0.0
    l1_fn = total_l1_count - l1_tp
    l1_fp = sum(1 for yt, yp in valid_pairs if yt != 1 and yp == 1)
    l1_tn = sum(1 for yt, yp in valid_pairs if yt != 1 and yp != 1)
    l1_specificity = l1_tn / (l1_tn + l1_fp) if (l1_tn + l1_fp) > 0 else 0.0
    l1_sens_ci = wilson_score_interval(l1_tp, total_l1_count)

    # Level 1+2 Sensitivity (Emergency + Urgent)
    total_l12_count = sum(1 for yt in y_true if yt in (1, 2))
    l12_tp = sum(1 for yt, yp in valid_pairs if yt in (1, 2) and yp in (1, 2))
    l12_sensitivity = l12_tp / total_l12_count if total_l12_count > 0 else 0.0
    l12_fp = sum(1 for yt, yp in valid_pairs if yt not in (1, 2) and yp in (1, 2))
    l12_tn = sum(1 for yt, yp in valid_pairs if yt not in (1, 2) and yp not in (1, 2))
    l12_specificity = l12_tn / (l12_tn + l12_fp) if (l12_tn + l12_fp) > 0 else 0.0
    l12_sens_ci = wilson_score_interval(l12_tp, total_l12_count)

    return {
        "n_total": n,
        "n_valid": n_valid,
        "uncertain_count": uncertain_count,
        "uncertain_rate": round(uncertain_rate, 4),
        "accuracy": round(accuracy, 4),
        "macro_f1": round(macro_f1, 4),
        "weighted_f1": round(weighted_f1, 4),
        "under_triage_count": under_triage_count,
        "under_triage_rate": round(under_triage_rate, 4),
        "under_triage_ci": under_triage_ci,
        "critical_under_triage_count": critical_under_triage_count,
        "critical_under_triage_rate": round(critical_under_triage_rate, 4),
        "under_triage_severity": round(under_triage_severity, 4),
        "over_triage_count": over_triage_count,
        "over_triage_rate": round(over_triage_rate, 4),
        "over_triage_ci": over_triage_ci,
        "l1_sensitivity": round(l1_sensitivity, 4),
        "l1_sensitivity_ci": l1_sens_ci,
        "l1_specificity": round(l1_specificity, 4),
        "l12_sensitivity": round(l12_sensitivity, 4),
        "l12_sensitivity_ci": l12_sens_ci,
        "l12_specificity": round(l12_specificity, 4),
        "per_class": per_class,
        "confusion_matrix": confusion_matrix,
    }
