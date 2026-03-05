"""Rule-based classification rules for tobacco-related cases.

This module defines keyword-based rules for identifying and classifying
tobacco-related cases from article text.
"""

from dataclasses import dataclass
from typing import Dict, List

# Case type definitions with associated keywords
CASE_TYPE_RULES: Dict[str, List[str]] = {
    "counterfeit": [
        "假冒",
        "假烟",
        "伪劣",
        "仿冒",
        "山寨烟",
        "假卷烟",
    ],
    "smuggling": [
        "走私",
        "跨境",
        "偷运",
        "走私烟",
        "无证运输",
    ],
    "unlicensed": [
        "无证经营",
        "无证销售",
        "非法经营",
        "无证零售",
    ],
    "tax_evasion": [
        "偷税",
        "逃税",
        "漏税",
        "涉税",
    ],
}

# Keywords that indicate a case-related article
CASE_INDICATORS: List[str] = [
    "案件",
    "查处",
    "查获",
    "涉案",
    "执法",
    "稽查",
    "破获",
    "捣毁",
    "抓获",
    "刑拘",
    "逮捕",
    "判刑",
]


def get_case_type_keywords(case_type: str) -> List[str]:
    """Get keywords for a specific case type."""
    return CASE_TYPE_RULES.get(case_type, [])


def get_all_case_types() -> List[str]:
    """Get all available case types."""
    return list(CASE_TYPE_RULES.keys())