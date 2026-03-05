# TSM V0.1 Operations Runbook

## Overview

This runbook covers operational procedures for the Tobacco Situation Monitor V0.1 OSINT pipeline.

## Version History

| Version | Date | Changes |
|---------|------|---------|
| V0.2 | 2026-03-05 | Added analytics and reporting module |
| V0.1 | Initial | Core OSINT pipeline |

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
| GET | `/api/dashboard/kpi` | Get OSINT effectiveness KPIs |

### Analytics (V0.2)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/trend` | Time series trend analysis |
| GET | `/api/analytics/risk-distribution` | Risk level distribution |
| GET | `/api/analytics/regional` | Geographic distribution |
| GET | `/api/analytics/case-types` | Case type breakdown |
| GET | `/api/analytics/sources` | Data source effectiveness |
| GET | `/api/analytics/hourly-pattern` | Hourly activity pattern |
| GET | `/api/analytics/weekly-pattern` | Weekly activity pattern |

Query parameters for analytics:
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)
- `period`: Trend period (daily, weekly, monthly)
- `limit`: Results limit (default 20)

### Reports (V0.2)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/reports/summary` | Executive summary (中文) |
| GET | `/api/reports/weekly` | Weekly report |
| GET | `/api/reports/monthly` | Monthly report |
| GET | `/api/reports/custom` | Custom date range report |
| GET | `/api/reports/export` | CSV export |

Report parameters:
- `format`: Output format (markdown, json)
- `section`: Export section (summary, regional, case_types, sources)

#### Sample Analytics Request

```bash
# Get trend for last 30 days
curl "http://localhost:8000/api/analytics/trend?period=daily"

# Get regional distribution
curl "http://localhost:8000/api/analytics/regional?limit=10"

# Generate weekly report
curl "http://localhost:8000/api/reports/weekly?format=markdown"
```

#### KPI Dashboard (V0.1)

The `/api/dashboard/kpi` endpoint returns 5 key performance indicators for monitoring OSINT pipeline effectiveness:

| KPI | Chinese | Description | Formula |
|-----|---------|-------------|---------|
| `coverage_rate` | 覆盖率 | % of sources successfully crawled | `crawled_sources / total_sources × 100` |
| `timeliness_score` | 时效性 | Avg hours from publish to collection | `AVG(fetched_at - published_at)` |
| `accuracy_rate` | 识别准确率 | % of confirmed intels | `confirmed / (confirmed + dismissed) × 100` |
| `noise_rate` | 噪音率 | % of false positives | `dismissed / (confirmed + dismissed) × 100` |
| `reviewable_rate` | 可复核率 | % of intels with reviews | `reviewed_intels / total_intels × 100` |

**Sample KPI Response:**
```json
{
  "coverage_rate": {
    "value": 8,
    "total": 10,
    "percentage": 80.0,
    "description": "8/10 sources successfully crawled"
  },
  "timeliness_score": {
    "value": 4.5,
    "avg_hours": 4.5,
    "description": "Average 4.5 hours from publish to collection"
  },
  "accuracy_rate": {
    "value": 45,
    "total": 60,
    "percentage": 75.0,
    "description": "45/60 reviewed intels confirmed as valid cases"
  },
  "noise_rate": {
    "value": 15,
    "total": 60,
    "percentage": 25.0,
    "description": "15/60 reviewed intels dismissed as noise"
  },
  "reviewable_rate": {
    "value": 80,
    "total": 100,
    "percentage": 80.0,
    "description": "80/100 intels have review logs"
  }
}
```

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

### KPI Health Check

```bash
curl http://localhost:8000/api/dashboard/kpi
```

Expected response includes all 5 KPIs with percentages and descriptions.

## Logs

Pipeline execution logs to stdout. Capture with:

```bash
uvicorn tsm.main:app 2>&1 | tee tsm.log
```

## Security Notes

- Database file `tsm.db` contains crawled content; secure appropriately
- API has no authentication in V0.1; add auth before production
- Only use sources you have permission to crawl