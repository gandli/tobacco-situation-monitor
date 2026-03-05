"""Test deduplication service."""

import hashlib
import pytest


@pytest.fixture(autouse=True)
def clear_deduper_state():
    """Clear deduper state before each test."""
    from tsm.services.deduper import clear_seen_hashes
    clear_seen_hashes()
    yield
    clear_seen_hashes()


def test_skip_duplicate_content():
    """Test that duplicate content is detected regardless of URL."""
    from tsm.services.deduper import detect_duplicate, compute_content_hash

    # Same content at different URLs should be duplicate
    content = "执法人员查获假冒卷烟案件，涉案金额巨大。"
    content_hash = compute_content_hash(content)

    first = detect_duplicate(url="https://a.gov.cn/news/1.html", content_hash=content_hash)
    second = detect_duplicate(url="https://b.gov.cn/news/2.html", content_hash=content_hash)

    assert first.is_duplicate is False  # First occurrence is not a duplicate
    assert second.is_duplicate is True  # Second occurrence IS a duplicate


def test_url_hash_detection():
    """Test that same URL is detected as duplicate."""
    from tsm.services.deduper import detect_duplicate, compute_url_hash

    url = "https://a.gov.cn/news/1.html"
    url_hash = compute_url_hash(url)

    first = detect_duplicate(url_hash=url_hash, content_hash="hash1")
    second = detect_duplicate(url_hash=url_hash, content_hash="hash2")

    assert first.is_duplicate is False  # First occurrence
    assert second.is_duplicate is True  # Same URL = duplicate


def test_different_content_not_duplicate():
    """Test that different content is not marked as duplicate."""
    from tsm.services.deduper import detect_duplicate, compute_content_hash

    content1 = "案件一：查获假烟"
    content2 = "案件二：查获走私烟"

    hash1 = compute_content_hash(content1)
    hash2 = compute_content_hash(content2)

    first = detect_duplicate(url="https://a.gov.cn/1.html", content_hash=hash1)
    second = detect_duplicate(url="https://a.gov.cn/2.html", content_hash=hash2)

    assert first.is_duplicate is False
    assert second.is_duplicate is False


def test_compute_hashes_are_consistent():
    """Test that hash computation is deterministic."""
    from tsm.services.deduper import compute_url_hash, compute_content_hash

    url = "https://example.com/article"
    content = "案件内容"

    # Same input should produce same hash
    assert compute_url_hash(url) == compute_url_hash(url)
    assert compute_content_hash(content) == compute_content_hash(content)

    # Different input should produce different hash
    assert compute_url_hash(url) != compute_url_hash("https://other.com")
    assert compute_content_hash(content) != compute_content_hash("其他内容")