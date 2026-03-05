"""Test rule-based case classification."""

import pytest


def test_detect_case_related_article():
    """Test that case-related articles are correctly identified and classified."""
    from tsm.intel.classifier import classify_article

    text = "近日执法人员查获假冒卷烟案件，涉案金额..."
    intel = classify_article(text)

    assert intel.is_case_related is True
    assert intel.case_type == "counterfeit"