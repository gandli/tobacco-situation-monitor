"""Risk scoring and level mapping for tobacco case intelligence.

This module provides scoring functions to assess risk levels of
tobacco-related cases based on keyword signals.
"""

from dataclasses import dataclass
from typing import List, Tuple

# Risk signal keywords with associated weights
RISK_SIGNALS: dict[str, int] = {
    # High-value signals (25 points each)
    "涉案金额": 25,
    "跨省运输": 25,
    "刑事拘留": 25,
    "逮捕": 25,
    # Medium-value signals (15 points each)
    "查获": 15,
    "假烟": 15,
    "假冒": 15,
    "走私": 15,
    "无证经营": 15,
    # Lower-value signals (10 points each)
    "案件": 10,
    "查处": 10,
    "执法": 10,
}

# Risk level thresholds
LEVEL_THRESHOLDS = {
    "low": 30,
    "medium": 60,
    "high": 80,
}


@dataclass
class RiskScore:
    """Result of risk scoring."""

    score: int
    level: str


def score_intel(keyword_hits: List[str]) -> Tuple[int, str]:
    """Score intelligence based on keyword hits and determine risk level.

    Args:
        keyword_hits: List of matched keywords from the article.

    Returns:
        Tuple of (score, level) where level is 'low', 'medium', or 'high'.
    """
    score = sum(RISK_SIGNALS.get(kw, 0) for kw in keyword_hits)

    # Determine risk level based on thresholds
    if score >= LEVEL_THRESHOLDS["high"]:
        level = "high"
    elif score >= LEVEL_THRESHOLDS["medium"]:
        level = "medium"
    elif score >= LEVEL_THRESHOLDS["low"]:
        level = "low"
    else:
        level = "low"

    return score, level