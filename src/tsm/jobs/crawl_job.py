"""Crawl job entry point.

This module provides the main crawl pipeline that:
1. Fetches list pages from configured sources
2. Extracts article links
3. Parses article content
4. Deduplicates articles
5. Classifies and scores articles
6. Detects violation patterns (V0.2)
7. Extracts entities and regions
8. Generates alerts
9. Persists intelligence records
"""

import json
import sqlite3
from datetime import datetime, timezone
from typing import Optional

from tsm.config import settings
from tsm.crawler.extract_links import extract_links
from tsm.crawler.fetcher import fetch
from tsm.intel.alert_engine import Alert, AlertEngine, create_default_engine
from tsm.intel.classifier import classify_article
from tsm.intel.entity_extractor import extract_entities
from tsm.intel.region_extractor import extract_region
from tsm.intel.scoring import score_intel
from tsm.intel.violation_detector import (
    analyze_violation_patterns,
    get_pattern_display_name,
    ViolationPattern,
)
from tsm.parser.article_parser import parse_article
from tsm.services.deduper import compute_content_hash, compute_url_hash, detect_duplicate

# Default database path, can be overridden for testing
DB_PATH: str = "tsm.db"

# Alert engine instance
_alert_engine: Optional[AlertEngine] = None


def get_alert_engine() -> AlertEngine:
    """Get or create the alert engine instance."""
    global _alert_engine
    if _alert_engine is None:
        _alert_engine = create_default_engine()
    return _alert_engine


def run_crawl_once(db_path: Optional[str] = None) -> dict:
    """Execute one crawl cycle.

    Returns summary of what was done:
    - sources_crawled: number of sources processed
    - articles_found: total article links discovered
    - articles_added: new articles persisted
    - duplicates_skipped: articles skipped as duplicates
    - intels_created: new intelligence records created
    - alerts_generated: new alerts triggered
    - patterns_detected: violation patterns identified
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
        "alerts_generated": 0,
        "patterns_detected": {},
    }

    # Get alert engine
    alert_engine = get_alert_engine()

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
                        content_text = article.content_clean or ""
                        
                        # Find matched keywords for scoring
                        matched_keywords = [kw for kw in [
                            "涉案金额", "跨省运输", "刑事拘留", "逮捕",
                            "查获", "假烟", "假冒", "走私", "无证经营",
                            "案件", "查处", "执法"
                        ] if kw in content_text]

                        score, level = score_intel(matched_keywords)

                        # Extract region
                        region_info = extract_region(content_text)
                        region = region_info.raw_text if region_info.confidence > 0 else None

                        # Extract entities
                        entities = extract_entities(content_text)

                        # Detect violation patterns (V0.2)
                        violation_analysis = analyze_violation_patterns(content_text)
                        violation_pattern = violation_analysis.primary_pattern.value
                        pattern_confidence = violation_analysis.primary_confidence
                        pattern_evidence = json.dumps(
                            [p.evidence for p in violation_analysis.all_patterns if p.evidence],
                            ensure_ascii=False
                        ) if violation_analysis.all_patterns else None
                        
                        # Track pattern stats
                        pattern_name = get_pattern_display_name(violation_analysis.primary_pattern)
                        summary["patterns_detected"][pattern_name] = \
                            summary["patterns_detected"].get(pattern_name, 0) + 1

                        # Build risk factors string
                        risk_factors_str = ",".join(violation_analysis.risk_factors) if violation_analysis.risk_factors else None
                        
                        # Build geographic hints string
                        geo_hints_str = ",".join(violation_analysis.geographic_hints) if violation_analysis.geographic_hints else None

                        # Try to insert with V0.2 columns, fall back to V0.1 schema
                        try:
                            cursor = conn.execute(
                                """INSERT INTO case_intels
                                   (article_id, is_case_related, case_type, region, risk_score, risk_level,
                                    keywords_matched, status, monetary_amount, monetary_value,
                                    quantity, quantity_value, quantity_unit, suspects, brands,
                                    vehicle_info, violation_pattern, pattern_confidence, pattern_evidence,
                                    risk_factors, geographic_hints, created_at, updated_at)
                                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                (article_id, 1, classification.case_type, region, score, level,
                                 ",".join(matched_keywords) if matched_keywords else None,
                                 "new",
                                 entities.monetary_amount, entities.monetary_value,
                                 entities.quantity, entities.quantity_value, entities.quantity_unit,
                                 ",".join(entities.suspects) if entities.suspects else None,
                                 ",".join(entities.brands) if entities.brands else None,
                                 entities.vehicle_info,
                                 violation_pattern, pattern_confidence, pattern_evidence,
                                 risk_factors_str, geo_hints_str,
                                 now, now)
                            )
                        except sqlite3.OperationalError:
                            # Fall back to V0.1 schema without violation pattern columns
                            cursor = conn.execute(
                                """INSERT INTO case_intels
                                   (article_id, is_case_related, case_type, region, risk_score, risk_level,
                                    keywords_matched, status, created_at, updated_at)
                                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                (article_id, 1, classification.case_type, region, score, level,
                                 ",".join(matched_keywords) if matched_keywords else None,
                                 "new", now, now)
                            )
                        
                        intel_id = cursor.lastrowid
                        summary["intels_created"] += 1

                        # Evaluate alerts
                        intel_dict = {
                            "id": intel_id,
                            "case_type": classification.case_type,
                            "risk_level": level,
                            "risk_score": score,
                            "region": region,
                            "keywords_matched": ",".join(matched_keywords) if matched_keywords else None,
                        }
                        entities_dict = {
                            "monetary_value": entities.monetary_value,
                            "monetary_amount": entities.monetary_amount,
                            "quantity_value": entities.quantity_value,
                            "quantity": entities.quantity,
                        }
                        
                        alerts = alert_engine.evaluate(intel_dict, entities_dict)
                        
                        # Persist alerts
                        for alert in alerts:
                            try:
                                conn.execute(
                                    """INSERT INTO alerts
                                       (intel_id, alert_type, message, created_at)
                                       VALUES (?, ?, ?, ?)""",
                                    (intel_id, alert.alert_type.value, alert.message, now)
                                )
                                summary["alerts_generated"] += 1
                            except sqlite3.OperationalError:
                                pass  # Skip if alerts table doesn't have expected columns

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