# Tobacco Situation Monitor V0.1 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a two-week, hourly-running OSINT pipeline that monitors public tobacco case updates nationwide and outputs reviewable, scored intelligence records.

**Architecture:** Implement a rule-driven pipeline in small increments: source registry, scheduled fetch, parse/clean, dedupe, classify/score, review workflow, and dashboard APIs. Prioritize reliability, traceability, and manual override over model complexity.

**Tech Stack:** Python (crawler/parser pipeline), SQLite (or Cloudflare D1-compatible schema), FastAPI (dashboard APIs), pytest (tests), cron/scheduler.

---

### Task 1: Project bootstrap and baseline structure

**Files:**
- Create: `tobacco-situation-monitor/src/tsm/__init__.py`
- Create: `tobacco-situation-monitor/src/tsm/config.py`
- Create: `tobacco-situation-monitor/src/tsm/main.py`
- Create: `tobacco-situation-monitor/tests/test_smoke.py`
- Modify: `tobacco-situation-monitor/README.md`

**Step 1: Write the failing test**

```python
from tsm.main import app

def test_app_object_exists():
    assert app is not None
```

**Step 2: Run test to verify it fails**

Run: `cd tobacco-situation-monitor && pytest tests/test_smoke.py::test_app_object_exists -v`  
Expected: FAIL with import/module error

**Step 3: Write minimal implementation**

```python
# src/tsm/main.py
from fastapi import FastAPI
app = FastAPI(title="TSM")
```

**Step 4: Run test to verify it passes**

Run: `cd tobacco-situation-monitor && pytest tests/test_smoke.py::test_app_object_exists -v`  
Expected: PASS

**Step 5: Commit**

```bash
git -C tobacco-situation-monitor add src/tsm tests/test_smoke.py README.md
git -C tobacco-situation-monitor commit -m "chore: bootstrap tsm app skeleton"
```

---

### Task 2: Database schema migration for V0.1 tables

**Files:**
- Create: `tobacco-situation-monitor/db/migrations/001_init.sql`
- Create: `tobacco-situation-monitor/tests/test_schema.py`
- Create: `tobacco-situation-monitor/src/tsm/db.py`

**Step 1: Write the failing test**

```python
def test_required_tables_exist(conn):
    expected = {"sources", "raw_articles", "case_intels", "alerts", "review_logs"}
    found = set(list_tables(conn))
    assert expected.issubset(found)
```

**Step 2: Run test to verify it fails**

Run: `cd tobacco-situation-monitor && pytest tests/test_schema.py::test_required_tables_exist -v`  
Expected: FAIL because tables not created

**Step 3: Write minimal implementation**

```sql
CREATE TABLE sources (...);
CREATE TABLE raw_articles (...);
CREATE TABLE case_intels (...);
CREATE TABLE alerts (...);
CREATE TABLE review_logs (...);
```

**Step 4: Run test to verify it passes**

Run: `cd tobacco-situation-monitor && pytest tests/test_schema.py::test_required_tables_exist -v`  
Expected: PASS

**Step 5: Commit**

```bash
git -C tobacco-situation-monitor add db/migrations/001_init.sql src/tsm/db.py tests/test_schema.py
git -C tobacco-situation-monitor commit -m "feat: add v0.1 database schema"
```

---

### Task 3: Source registry CRUD (minimal)

**Files:**
- Create: `tobacco-situation-monitor/src/tsm/services/source_manager.py`
- Create: `tobacco-situation-monitor/src/tsm/api/sources.py`
- Create: `tobacco-situation-monitor/tests/test_sources_api.py`
- Modify: `tobacco-situation-monitor/src/tsm/main.py`

**Step 1: Write the failing test**

```python
def test_create_source(client):
    resp = client.post("/api/sources", json={"name": "Fujian Tobacco", "list_url": "https://example.com/list"})
    assert resp.status_code == 201
```

**Step 2: Run test to verify it fails**

Run: `cd tobacco-situation-monitor && pytest tests/test_sources_api.py::test_create_source -v`  
Expected: FAIL with 404

**Step 3: Write minimal implementation**

```python
@router.post("/api/sources", status_code=201)
def create_source(payload: SourceCreate):
    return service.create(payload)
```

**Step 4: Run test to verify it passes**

Run: `cd tobacco-situation-monitor && pytest tests/test_sources_api.py::test_create_source -v`  
Expected: PASS

**Step 5: Commit**

```bash
git -C tobacco-situation-monitor add src/tsm/api/sources.py src/tsm/services/source_manager.py src/tsm/main.py tests/test_sources_api.py
git -C tobacco-situation-monitor commit -m "feat: add source registry api"
```

---

### Task 4: Hourly scheduler + crawl job dispatcher

**Files:**
- Create: `tobacco-situation-monitor/src/tsm/jobs/scheduler.py`
- Create: `tobacco-situation-monitor/src/tsm/jobs/crawl_job.py`
- Create: `tobacco-situation-monitor/tests/test_scheduler.py`

**Step 1: Write the failing test**

```python
def test_scheduler_registers_hourly_job():
    scheduler = build_scheduler()
    jobs = scheduler.get_jobs()
    assert any(j.trigger.interval.total_seconds() == 3600 for j in jobs)
```

**Step 2: Run test to verify it fails**

Run: `cd tobacco-situation-monitor && pytest tests/test_scheduler.py::test_scheduler_registers_hourly_job -v`  
Expected: FAIL no jobs

**Step 3: Write minimal implementation**

```python
scheduler.add_job(run_crawl_once, "interval", hours=1)
```

**Step 4: Run test to verify it passes**

Run: `cd tobacco-situation-monitor && pytest tests/test_scheduler.py::test_scheduler_registers_hourly_job -v`  
Expected: PASS

**Step 5: Commit**

```bash
git -C tobacco-situation-monitor add src/tsm/jobs/scheduler.py src/tsm/jobs/crawl_job.py tests/test_scheduler.py
git -C tobacco-situation-monitor commit -m "feat: add hourly crawl scheduler"
```

---

### Task 5: List-page fetch and candidate link extraction

**Files:**
- Create: `tobacco-situation-monitor/src/tsm/crawler/fetcher.py`
- Create: `tobacco-situation-monitor/src/tsm/crawler/extract_links.py`
- Create: `tobacco-situation-monitor/tests/test_link_extraction.py`

**Step 1: Write the failing test**

```python
def test_extract_links_from_list_html():
    html = '<a href="/news/123.html">案件通报</a>'
    links = extract_links(html, "https://a.gov.cn/list")
    assert links == ["https://a.gov.cn/news/123.html"]
```

**Step 2: Run test to verify it fails**

Run: `cd tobacco-situation-monitor && pytest tests/test_link_extraction.py::test_extract_links_from_list_html -v`  
Expected: FAIL function missing

**Step 3: Write minimal implementation**

```python
def extract_links(html, base_url):
    ...
```

**Step 4: Run test to verify it passes**

Run: `cd tobacco-situation-monitor && pytest tests/test_link_extraction.py::test_extract_links_from_list_html -v`  
Expected: PASS

**Step 5: Commit**

```bash
git -C tobacco-situation-monitor add src/tsm/crawler/fetcher.py src/tsm/crawler/extract_links.py tests/test_link_extraction.py
git -C tobacco-situation-monitor commit -m "feat: extract article links from source list pages"
```

---

### Task 6: Detail-page parse and content cleaning

**Files:**
- Create: `tobacco-situation-monitor/src/tsm/parser/article_parser.py`
- Create: `tobacco-situation-monitor/tests/test_article_parser.py`

**Step 1: Write the failing test**

```python
def test_parse_article_fields():
    html = "<h1>某地查获假烟案</h1><time>2026-03-01</time><div id='content'>正文</div>"
    article = parse_article(html)
    assert article.title == "某地查获假烟案"
    assert "正文" in article.content_clean
```

**Step 2: Run test to verify it fails**

Run: `cd tobacco-situation-monitor && pytest tests/test_article_parser.py::test_parse_article_fields -v`  
Expected: FAIL

**Step 3: Write minimal implementation**

```python
def parse_article(html):
    return Article(title=..., published_at=..., content_clean=...)
```

**Step 4: Run test to verify it passes**

Run: `cd tobacco-situation-monitor && pytest tests/test_article_parser.py::test_parse_article_fields -v`  
Expected: PASS

**Step 5: Commit**

```bash
git -C tobacco-situation-monitor add src/tsm/parser/article_parser.py tests/test_article_parser.py
git -C tobacco-situation-monitor commit -m "feat: parse article title date and body"
```

---

### Task 7: Deduplication (URL hash + content hash)

**Files:**
- Create: `tobacco-situation-monitor/src/tsm/services/deduper.py`
- Create: `tobacco-situation-monitor/tests/test_deduper.py`

**Step 1: Write the failing test**

```python
def test_skip_duplicate_content():
    first = upsert_article(url="u1", content="abc")
    second = upsert_article(url="u2", content="abc")
    assert second.is_duplicate is True
```

**Step 2: Run test to verify it fails**

Run: `cd tobacco-situation-monitor && pytest tests/test_deduper.py::test_skip_duplicate_content -v`  
Expected: FAIL

**Step 3: Write minimal implementation**

```python
def detect_duplicate(url, content):
    ...
```

**Step 4: Run test to verify it passes**

Run: `cd tobacco-situation-monitor && pytest tests/test_deduper.py::test_skip_duplicate_content -v`  
Expected: PASS

**Step 5: Commit**

```bash
git -C tobacco-situation-monitor add src/tsm/services/deduper.py tests/test_deduper.py
git -C tobacco-situation-monitor commit -m "feat: add dual-hash deduplication"
```

---

### Task 8: Rule-based case classifier and type tagging

**Files:**
- Create: `tobacco-situation-monitor/src/tsm/intel/rules.py`
- Create: `tobacco-situation-monitor/src/tsm/intel/classifier.py`
- Create: `tobacco-situation-monitor/tests/test_classifier.py`

**Step 1: Write the failing test**

```python
def test_detect_case_related_article():
    text = "近日执法人员查获假冒卷烟案件，涉案金额..."
    intel = classify_article(text)
    assert intel.is_case_related is True
    assert intel.case_type == "counterfeit"
```

**Step 2: Run test to verify it fails**

Run: `cd tobacco-situation-monitor && pytest tests/test_classifier.py::test_detect_case_related_article -v`  
Expected: FAIL

**Step 3: Write minimal implementation**

```python
CASE_RULES = {...}
def classify_article(text):
    ...
```

**Step 4: Run test to verify it passes**

Run: `cd tobacco-situation-monitor && pytest tests/test_classifier.py::test_detect_case_related_article -v`  
Expected: PASS

**Step 5: Commit**

```bash
git -C tobacco-situation-monitor add src/tsm/intel/rules.py src/tsm/intel/classifier.py tests/test_classifier.py
git -C tobacco-situation-monitor commit -m "feat: add rule-based case classification"
```

---

### Task 9: Risk scoring and level mapping

**Files:**
- Create: `tobacco-situation-monitor/src/tsm/intel/scoring.py`
- Create: `tobacco-situation-monitor/tests/test_scoring.py`

**Step 1: Write the failing test**

```python
def test_high_risk_when_multiple_strong_signals():
    score, level = score_intel(["查获", "假烟", "跨省运输", "涉案金额"])
    assert score >= 80
    assert level == "high"
```

**Step 2: Run test to verify it fails**

Run: `cd tobacco-situation-monitor && pytest tests/test_scoring.py::test_high_risk_when_multiple_strong_signals -v`  
Expected: FAIL

**Step 3: Write minimal implementation**

```python
def score_intel(keyword_hits):
    ...
```

**Step 4: Run test to verify it passes**

Run: `cd tobacco-situation-monitor && pytest tests/test_scoring.py::test_high_risk_when_multiple_strong_signals -v`  
Expected: PASS

**Step 5: Commit**

```bash
git -C tobacco-situation-monitor add src/tsm/intel/scoring.py tests/test_scoring.py
git -C tobacco-situation-monitor commit -m "feat: add risk scoring and level mapping"
```

---

### Task 10: Review queue and review API

**Files:**
- Create: `tobacco-situation-monitor/src/tsm/api/review.py`
- Create: `tobacco-situation-monitor/src/tsm/services/review_service.py`
- Create: `tobacco-situation-monitor/tests/test_review_api.py`
- Modify: `tobacco-situation-monitor/src/tsm/main.py`

**Step 1: Write the failing test**

```python
def test_submit_review_action(client, seeded_intel_id):
    resp = client.post(f"/api/intels/{seeded_intel_id}/review", json={"action": "confirm", "comment": "确认有效"})
    assert resp.status_code == 200
```

**Step 2: Run test to verify it fails**

Run: `cd tobacco-situation-monitor && pytest tests/test_review_api.py::test_submit_review_action -v`  
Expected: FAIL with 404

**Step 3: Write minimal implementation**

```python
@router.post("/api/intels/{intel_id}/review")
def review_intel(intel_id: int, payload: ReviewIn):
    return service.review(intel_id, payload)
```

**Step 4: Run test to verify it passes**

Run: `cd tobacco-situation-monitor && pytest tests/test_review_api.py::test_submit_review_action -v`  
Expected: PASS

**Step 5: Commit**

```bash
git -C tobacco-situation-monitor add src/tsm/api/review.py src/tsm/services/review_service.py src/tsm/main.py tests/test_review_api.py
git -C tobacco-situation-monitor commit -m "feat: add review queue api"
```

---

### Task 11: Dashboard summary and intel query APIs

**Files:**
- Create: `tobacco-situation-monitor/src/tsm/api/intels.py`
- Create: `tobacco-situation-monitor/src/tsm/api/dashboard.py`
- Create: `tobacco-situation-monitor/tests/test_dashboard_api.py`
- Modify: `tobacco-situation-monitor/src/tsm/main.py`

**Step 1: Write the failing test**

```python
def test_dashboard_summary_contains_counts(client):
    resp = client.get("/api/dashboard/summary")
    assert resp.status_code == 200
    assert "today_new" in resp.json()
```

**Step 2: Run test to verify it fails**

Run: `cd tobacco-situation-monitor && pytest tests/test_dashboard_api.py::test_dashboard_summary_contains_counts -v`  
Expected: FAIL

**Step 3: Write minimal implementation**

```python
@router.get("/api/dashboard/summary")
def summary():
    return {"today_new": 0, "high_risk": 0, "by_region": []}
```

**Step 4: Run test to verify it passes**

Run: `cd tobacco-situation-monitor && pytest tests/test_dashboard_api.py::test_dashboard_summary_contains_counts -v`  
Expected: PASS

**Step 5: Commit**

```bash
git -C tobacco-situation-monitor add src/tsm/api/intels.py src/tsm/api/dashboard.py src/tsm/main.py tests/test_dashboard_api.py
git -C tobacco-situation-monitor commit -m "feat: add dashboard and intel query apis"
```

---

### Task 12: End-to-end crawl pipeline test and ops docs

**Files:**
- Create: `tobacco-situation-monitor/tests/test_e2e_pipeline.py`
- Create: `tobacco-situation-monitor/docs/runbook-v01.md`
- Modify: `tobacco-situation-monitor/README.md`

**Step 1: Write the failing test**

```python
def test_pipeline_from_source_to_intel(fake_source, fake_http):
    run_crawl_once()
    intels = list_intels()
    assert len(intels) >= 1
```

**Step 2: Run test to verify it fails**

Run: `cd tobacco-situation-monitor && pytest tests/test_e2e_pipeline.py::test_pipeline_from_source_to_intel -v`  
Expected: FAIL

**Step 3: Write minimal implementation**

```python
def run_crawl_once():
    # fetch -> parse -> dedupe -> classify -> score -> persist
    ...
```

**Step 4: Run test to verify it passes**

Run: `cd tobacco-situation-monitor && pytest tests/test_e2e_pipeline.py::test_pipeline_from_source_to_intel -v`  
Expected: PASS

**Step 5: Commit**

```bash
git -C tobacco-situation-monitor add tests/test_e2e_pipeline.py docs/runbook-v01.md README.md
git -C tobacco-situation-monitor commit -m "test: add e2e pipeline coverage and ops runbook"
```

---

## Verification Gates (must run before claiming completion)

1. `cd tobacco-situation-monitor && pytest -v`  
   Expected: all tests pass
2. `cd tobacco-situation-monitor && ruff check .` (if configured)  
   Expected: no blocking lint errors
3. `cd tobacco-situation-monitor && python -m tsm.main`  
   Expected: service boots without exception
4. Trigger one crawl cycle and verify:
   - `sources.last_crawled_at` updated
   - new rows in `raw_articles`
   - new rows in `case_intels`

---

## Notes for execution discipline

- Keep commits small: one task, one commit.
- Never skip failing-test-first sequence.
- Avoid adding non-essential features (YAGNI).
- Prefer deterministic parser/classifier behavior over clever heuristics.
