"""Crawl job entry point.

This module provides the main crawl pipeline that:
1. Fetches list pages from configured sources
2. Extracts article links
3. Parses article content
4. Deduplicates articles
5. Classifies and scores articles
6. Persists intelligence records
"""

import sqlite3
from datetime import datetime, timezone
from typing import Optional

from tsm.config import settings
from tsm.crawler.extract_links import extract_links
from tsm.crawler.fetcher import fetch
from tsm.intel.classifier import classify_article
from tsm.intel.scoring import score_intel
from tsm.parser.article_parser import parse_article
from tsm.services.deduper import compute_content_hash, compute_url_hash, detect_duplicate

# Default database path, can be overridden for testing
DB_PATH: str = "tsm.db"


def run_crawl_once(db_path: Optional[str] = None) -> dict:
    """Execute one crawl cycle.

    Returns summary of what was done:
    - sources_crawled: number of sources processed
    - articles_found: total article links discovered
    - articles_added: new articles persisted
    - duplicates_skipped: articles skipped as duplicates
    - intels_created: new intelligence records created
    """
    db = db_path or DB_PATH
    conn = sqlite3.connect(db)

    # Get all sources
    cursor = conn.execute("SELECT id, name, list_url FROM sources")
    sources = cursor.fetchall()

    summary = {
        "status": "ok",
        "sources_crawled": 0,
        "articles_found": 0,
        "articles_added": 0,
        "duplicates_skipped": 0,
        "intels_created": 0,
    }

    for source_id, source_name, list_url in sources:
        try:
            # Fetch list page
            list_html = fetch(list_url)
            summary["sources_crawled"] += 1

            # Extract article links
            article_links = extract_links(list_html, list_url)
            summary["articles_found"] += len(article_links)

            # Process each article
            for article_url in article_links:
                try:
                    # Fetch article page
                    article_html = fetch(article_url)

                    # Parse article content
                    article = parse_article(article_html)

                    # Compute hashes for deduplication
                    url_hash = compute_url_hash(article_url)
                    content_hash = compute_content_hash(article.content_clean or article.title or "")

                    # Check for duplicates
                    dup_result = detect_duplicate(url_hash=url_hash, content_hash=content_hash)
                    if dup_result.is_duplicate:
                        summary["duplicates_skipped"] += 1
                        continue

                    # Insert raw article
                    now = datetime.now(timezone.utc).isoformat()
                    cursor = conn.execute(
                        """INSERT INTO raw_articles
                           (source_id, url, title, published_at, content_clean, url_hash, content_hash, fetched_at)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (source_id, article_url, article.title, article.published_at,
                         article.content_clean, url_hash, content_hash, now)
                    )
                    article_id = cursor.lastrowid
                    summary["articles_added"] += 1

                    # Classify article
                    classification = classify_article(article.content_clean or "")

                    # Score and create intel record if case-related
                    if classification.is_case_related:
                        # Find matched keywords for scoring
                        content_text = article.content_clean or ""
                        matched_keywords = [kw for kw in [
                            "涉案金额", "跨省运输", "刑事拘留", "逮捕",
                            "查获", "假烟", "假冒", "走私", "无证经营",
                            "案件", "查处", "执法"
                        ] if kw in content_text]

                        score, level = score_intel(matched_keywords)

                        # Insert intel record
                        cursor = conn.execute(
                            """INSERT INTO case_intels
                               (article_id, is_case_related, case_type, risk_score, risk_level,
                                keywords_matched, status, created_at, updated_at)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                            (article_id, 1, classification.case_type, score, level,
                             ",".join(matched_keywords) if matched_keywords else None,
                             "new", now, now)
                        )
                        summary["intels_created"] += 1

                    conn.commit()

                except Exception as e:
                    # Log but continue with next article
                    print(f"Error processing article {article_url}: {e}")
                    continue

            # Update source last_crawled_at
            now = datetime.now(timezone.utc).isoformat()
            conn.execute(
                "UPDATE sources SET last_crawled_at = ?, updated_at = ? WHERE id = ?",
                (now, now, source_id)
            )
            conn.commit()

        except Exception as e:
            print(f"Error crawling source {source_name}: {e}")
            continue

    conn.close()
    return summary