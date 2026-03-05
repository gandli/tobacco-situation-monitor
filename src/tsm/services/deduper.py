"""Deduplication service for detecting duplicate articles.

Uses dual-hash strategy:
- URL hash: Detects same article at same URL
- Content hash: Detects same content at different URLs
"""

import hashlib
from dataclasses import dataclass
from typing import Optional


@dataclass
class DuplicateResult:
    """Result of duplicate detection."""

    is_duplicate: bool
    url_hash: str
    content_hash: str
    reason: Optional[str] = None


# In-memory store for testing. In production, this would be a database table.
_seen_url_hashes: set[str] = set()
_seen_content_hashes: set[str] = set()


def compute_url_hash(url: str) -> str:
    """Compute SHA256 hash for URL."""
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def compute_content_hash(content: str) -> str:
    """Compute SHA256 hash for content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def detect_duplicate(
    url: Optional[str] = None,
    content_hash: Optional[str] = None,
    url_hash: Optional[str] = None,
) -> DuplicateResult:
    """Detect if an article is a duplicate.

    Args:
        url: Article URL (will compute url_hash if not provided)
        content_hash: Pre-computed content hash
        url_hash: Pre-computed URL hash (takes precedence over url)

    Returns:
        DuplicateResult with is_duplicate flag and hashes
    """
    # Compute URL hash if not provided
    if url_hash is None and url is not None:
        url_hash = compute_url_hash(url)
    elif url_hash is None:
        url_hash = ""

    # Content hash must be provided
    if content_hash is None:
        content_hash = ""

    # Check URL hash first (same URL = definitely duplicate)
    if url_hash and url_hash in _seen_url_hashes:
        return DuplicateResult(
            is_duplicate=True,
            url_hash=url_hash,
            content_hash=content_hash,
            reason="url_hash_match",
        )

    # Check content hash (same content = duplicate)
    if content_hash and content_hash in _seen_content_hashes:
        return DuplicateResult(
            is_duplicate=True,
            url_hash=url_hash,
            content_hash=content_hash,
            reason="content_hash_match",
        )

    # Not a duplicate - record the hashes for future checks
    if url_hash:
        _seen_url_hashes.add(url_hash)
    if content_hash:
        _seen_content_hashes.add(content_hash)

    return DuplicateResult(
        is_duplicate=False,
        url_hash=url_hash,
        content_hash=content_hash,
        reason=None,
    )


def clear_seen_hashes() -> None:
    """Clear the in-memory hash stores. For testing."""
    _seen_url_hashes.clear()
    _seen_content_hashes.clear()