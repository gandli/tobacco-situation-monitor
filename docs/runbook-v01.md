# TSM V0.1 Operations Runbook

## Overview

This runbook covers operational procedures for the Tobacco Situation Monitor V0.1 OSINT pipeline.

## Quick Reference

### Start the Service

```bash
cd tobacco-situation-monitor
source .venv/bin/activate
uvicorn tsm.main:app --reload --port 8000
```

### Run a Manual Crawl

```python
from tsm.jobs.crawl_job import run_crawl_once
result = run_crawl_once()
print(result)
```

### Run Tests

```bash
pytest -v
```

## Database Operations

### Initialize Database

```bash
sqlite3 tsm.db < db/migrations/001_init.sql
```

### Check Database Status

```bash
sqlite3 tsm.db "SELECT COUNT(*) as sources FROM sources; 
               SELECT COUNT(*) as articles FROM raw_articles; 
               SELECT COUNT(*) as intels FROM case_intels;"
```

### Backup Database

```bash
sqlite3 tsm.db ".backup tsm_backup.db"
```

## API Endpoints

### Sources

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/sources` | List all sources |
| POST | `/api/sources` | Create new source |
| GET | `/api/sources/{id}` | Get source by ID |

### Intel Records

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/intels` | List intel records (filterable) |
| GET | `/api/intels/{id}` | Get single intel record |

Query parameters for `/api/intels`:
- `status`: Filter by status (new, confirmed, dismissed)
- `risk_level`: Filter by risk level (low, medium, high)
- `region`: Filter by region
- `limit`: Results per page (default 50)
- `offset`: Pagination offset

### Review

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/intels/{id}/review` | Submit review action |

Review payload:
```json
{
  "action": "confirm",  // confirm, dismiss, escalate
  "comment": "Verified as legitimate case"
}
```

### Dashboard

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/summary` | Get dashboard summary |

## Pipeline Flow

```
Source (list URL)
    ↓
Fetch List Page
    ↓
Extract Article Links
    ↓
For each article:
    ├─ Fetch Article Page
    ├─ Parse Content
    ├─ Deduplicate (URL hash + content hash)
    ├─ Classify (is_case_related, case_type)
    ├─ Score Risk
    └─ Persist to DB
        ├─ raw_articles table
        └─ case_intels table (if case-related)
```

## Risk Levels

| Level | Score Range | Description |
|-------|-------------|-------------|
| low | 0-30 | Minor cases, informational |
| medium | 31-60 | Notable cases requiring attention |
| high | 61+ | High-priority cases |

## Case Types

| Type | Keywords |
|------|----------|
| counterfeit | 假冒, 假烟, 伪劣, 仿冒 |
| smuggling | 走私, 跨境, 偷运 |
| unlicensed | 无证经营, 无证销售, 非法经营 |
| tax_evasion | 偷税, 逃税, 漏税 |

## Troubleshooting

### No articles being collected

1. Check source is configured:
   ```bash
   sqlite3 tsm.db "SELECT * FROM sources;"
   ```

2. Check last crawl time:
   ```bash
   sqlite3 tsm.db "SELECT name, last_crawled_at FROM sources;"
   ```

3. Test fetch manually:
   ```python
   from tsm.crawler.fetcher import fetch
   html = fetch("https://your-source-url")
   print(len(html))
   ```

### Duplicate articles appearing

The deduper uses two strategies:
- URL hash: Detects same URL being crawled again
- Content hash: Detects same content at different URLs

If duplicates appear, check:
```bash
sqlite3 tsm.db "SELECT url, url_hash, content_hash FROM raw_articles ORDER BY created_at DESC LIMIT 10;"
```

### Classification not working

1. Verify keywords are present in article content:
   ```bash
   sqlite3 tsm.db "SELECT content_clean FROM raw_articles WHERE id = 1;"
   ```

2. Test classifier manually:
   ```python
   from tsm.intel.classifier import classify_article
   result = classify_article("执法人员查获假烟案件")
   print(result)
   ```

## Monitoring

### Key Metrics

- `sources_crawled`: Number of sources processed
- `articles_found`: Total links discovered
- `articles_added`: New articles persisted
- `duplicates_skipped`: Articles skipped as duplicates
- `intels_created`: New intelligence records

### Health Check

```bash
curl http://localhost:8000/api/dashboard/summary
```

Expected response:
```json
{
  "today_new": 5,
  "high_risk": 2,
  "by_region": []
}
```

## Logs

Pipeline execution logs to stdout. Capture with:

```bash
uvicorn tsm.main:app 2>&1 | tee tsm.log
```

## Security Notes

- Database file `tsm.db` contains crawled content; secure appropriately
- API has no authentication in V0.1; add auth before production
- Only use sources you have permission to crawl