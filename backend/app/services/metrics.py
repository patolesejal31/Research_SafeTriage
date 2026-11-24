"""Pure-Python Inter-Rater Reliability Metrics for Clinical Informatics.

Implements Cohen's Kappa without external numerical dependencies (pure Python).
Handles:
- Perfect agreement (kappa = 1.0)
- Zero variance / constant raters (gracefully handled)
- Unequal label sets (union of categories evaluated)
"""

from typing import Any, Dict, List, Sequence, Set


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
