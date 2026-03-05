"""Rule-based article classifier for tobacco-related cases.

This module provides a classifier that determines if an article is
case-related and what type of case it describes.
"""

from dataclasses import dataclass
from typing import Optional

from tsm.intel.rules import CASE_INDICATORS, CASE_TYPE_RULES


@dataclass
class ClassificationResult:
    """Result of classifying an article."""

    is_case_related: bool
    case_type: Optional[str] = None
    confidence: float = 0.0


def classify_article(text: str) -> ClassificationResult:
    """Classify article text to determine if it's case-related and what type.

    Args:
        text: The article text to classify.

    Returns:
        ClassificationResult with is_case_related, case_type, and confidence.
    """
    if not text:
        return ClassificationResult(is_case_related=False)

    # Check if article is case-related
    is_case_related = any(indicator in text for indicator in CASE_INDICATORS)

    if not is_case_related:
        return ClassificationResult(is_case_related=False)

    # Determine case type by keyword matching
    best_match: Optional[str] = None
    best_count = 0

    for case_type, keywords in CASE_TYPE_RULES.items():
        match_count = sum(1 for kw in keywords if kw in text)
        if match_count > best_count:
            best_match = case_type
            best_count = match_count

    # Calculate confidence based on number of keyword matches
    confidence = min(1.0, best_count / 2) if best_count > 0 else 0.5

    return ClassificationResult(
        is_case_related=True,
        case_type=best_match,
        confidence=confidence,
    )