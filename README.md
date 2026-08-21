# Tobacco Situation Monitor 🚬

**Real-time OSINT-powered surveillance system for tobacco law enforcement**

Tobacco Situation Monitor (TSM) is an open-source intelligence (OSINT) platform designed specifically for tobacco monopoly law enforcement agencies. It provides real-time monitoring, threat detection, and situational awareness for five major tobacco violation patterns: **door-to-door sales**, **dedicated vehicle transport**, **logistics delivery**, **maritime smuggling**, and **counterfeit production sites**.

## 🎯 Key Features

### Real-time Violation Monitoring
- **Door-to-Door Sales Detection**: Monitor social media, local forums, and community groups for suspicious tobacco sales activities
- **Vehicle Transport Tracking**: Analyze GPS trajectories and vehicle movement patterns for illegal tobacco transportation
- **Logistics Surveillance**: Track package shipments and detect suspicious tobacco-related deliveries
- **Maritime Smuggling Alerts**: Monitor AIS vessel data and port activities for potential smuggling operations
- **Counterfeit Site Identification**: Detect fake production facilities through business registration anomalies and utility consumption patterns

### Intelligent Threat Assessment
- **Multi-dimensional Scoring**: AI-powered threat scoring based on violation patterns, geographic location, and historical data
- **Behavioral Pattern Recognition**: Identify abnormal trading behaviors and distribution networks
- **Cross-platform Correlation**: Correlate data from e-commerce, social media, logistics, and public records

## 🛠️ Technical Architecture (V0.1)

| Component | Stack |
|-----------|-------|
| Crawler | Python + httpx + BeautifulSoup4 |
| Intel pipeline | Rule-based classifier, scoring, dedup |
| API / Dashboard | FastAPI ([`src/tsm/api/`](src/tsm/api/)) |
| Scheduler | APScheduler ([`src/tsm/jobs/`](src/tsm/jobs/)) |
| Database | SQLite ([`db/migrations/001_init.sql`](db/migrations/001_init.sql)) |

> Frontend (Vue 3 + Cloudflare Workers) is planned; the current implementation is the Python V0.1 pipeline.

## 🚀 Quick Start

### Prerequisites

- Python 3.10+

### Installation

```bash
# Clone the repository
git clone https://github.com/gandli/tobacco-situation-monitor.git
cd tobacco-situation-monitor

# Create virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### Run Tests

```bash
# All tests
pytest -v

# Unit tests only
pytest tests/test_classifier.py tests/test_scoring.py tests/test_deduper.py -v

# API tests
pytest tests/test_sources_api.py tests/test_dashboard_api.py tests/test_review_api.py -v

# End-to-end pipeline test
pytest tests/test_e2e_pipeline.py -v
```

## 📚 Documentation

- [Operations Runbook](docs/runbook-v01.md) — Operational procedures for the V0.1 pipeline
- [OSINT Design](docs/plans/2026-03-05-osint-design.md)
- [PRD](docs/PRD.md)

## ⚖️ Compliance & Ethics

- **Public Data Only**: Collects only publicly available information
- **Anonymized Processing**: Personal data is anonymized and aggregated
- **Authorized Use**: Designed for authorized law enforcement personnel only — unauthorized use is prohibited

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License
