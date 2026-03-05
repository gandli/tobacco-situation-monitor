"""Test risk scoring and level mapping."""

import pytest


def test_high_risk_when_multiple_strong_signals():
    """Test that multiple strong signals result in high risk score and level."""
    from tsm.intel.scoring import score_intel

    score, level = score_intel(["查获", "假烟", "跨省运输", "涉案金额"])
    assert score >= 80
    assert level == "high"