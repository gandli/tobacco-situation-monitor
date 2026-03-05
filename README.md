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
- **Real-time Alerting**: Instant notifications via web dashboard, mobile app, and messaging platforms

### Law Enforcement Support
- **Dark Theme Dashboard**: Professional interface inspired by security monitoring systems like Iran Immersive Translate
- **Geospatial Visualization**: Interactive heatmaps showing violation hotspots and transportation routes
- **Evidence Preservation**: Automated screenshot capture, timestamping, and digital evidence management
- **Mobile Field Operations**: On-site verification tools for执法人员 with offline capabilities

## 🛠️ Technical Architecture

### Frontend
- **Framework**: Vue 3 + TypeScript
- **UI Library**: Tailwind CSS + DaisyUI (Dark Theme)
- **Charts**: ECharts for data visualization
- **Maps**: Leaflet for geospatial analysis

### Backend  
- **API Layer**: Cloudflare Workers (Serverless)
- **Database**: Cloudflare D1 (SQLite)
- **Storage**: Cloudflare R2 (Evidence files)
- **Real-time**: WebSocket/SSE for live updates

### Data Sources
- **E-commerce Platforms**: Taobao, JD, Pinduoduo, Xianyu
- **Social Media**: Weibo, Douyin, Xiaohongshu, QQ Groups
- **Logistics APIs**: Major courier companies (with partnerships)
- **Public Records**: Business registration, maritime AIS data
- **Crowdsourced Intelligence**: Anonymous tip submissions

## 📚 Documentation

- **[Operations Runbook](docs/runbook-v01.md)** - Operational procedures for V0.1 pipeline

## 📈 OSINT Effect Dashboard (V0.1)

The KPI Dashboard provides real-time effectiveness metrics for monitoring OSINT pipeline performance.

### KPI Definitions

| KPI | Chinese | Description | Formula |
|-----|---------|-------------|---------|
| **Coverage Rate** | 覆盖率 | % of configured sources successfully crawled | `crawled_sources / total_sources × 100` |
| **Timeliness Score** | 时效性 | Average hours from article publication to collection | `AVG(fetched_at - published_at)` in hours |
| **Accuracy Rate** | 识别准确率 | % of confirmed cases among reviewed intels | `confirmed / (confirmed + dismissed) × 100` |
| **Noise Rate** | 噪音率 | % of false positives among reviewed intels | `dismissed / (confirmed + dismissed) × 100` |
| **Reviewable Rate** | 可复核率 | % of intels with review logs | `reviewed_intels / total_intels × 100` |

## 📊 Analytics & Reporting (V0.2)

The Analytics module provides comprehensive data analysis and report generation capabilities.

### Analytics Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/analytics/trend` | Time series trend of intel collection |
| `GET /api/analytics/risk-distribution` | Distribution by risk level (high/medium/low) |
| `GET /api/analytics/regional` | Geographic distribution of cases |
| `GET /api/analytics/case-types` | Breakdown by case type |
| `GET /api/analytics/sources` | Data source effectiveness metrics |
| `GET /api/analytics/hourly-pattern` | Intel creation pattern by hour |
| `GET /api/analytics/weekly-pattern` | Intel creation pattern by day of week |

### Report Generation

| Endpoint | Description |
|----------|-------------|
| `GET /api/reports/summary` | Executive summary in Chinese |
| `GET /api/reports/weekly` | Weekly comprehensive report (Markdown/JSON) |
| `GET /api/reports/monthly` | Monthly comprehensive report (Markdown/JSON) |
| `GET /api/reports/custom` | Custom date range report |
| `GET /api/reports/export` | Export report section as CSV |

### Sample Analytics Response

```json
{
  "period": {"start": "2026-02-01", "end": "2026-03-05"},
  "total_regions": 15,
  "data": [
    {
      "region": "上海",
      "count": 42,
      "percentage": 21.0,
      "case_types": {"counterfeit": 20, "smuggling": 15, "unlicensed": 7}
    }
  ]
}
```

### API Endpoint

```bash
GET /api/dashboard/kpi
```

### Sample Response

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

## 🧪 Testing

Run all tests:
```bash
pytest -v
```

Run specific test categories:
```bash
# Unit tests
pytest tests/test_classifier.py tests/test_scoring.py tests/test_deduper.py -v

# API tests
pytest tests/test_sources_api.py tests/test_dashboard_api.py tests/test_review_api.py -v

# End-to-end pipeline test
pytest tests/test_e2e_pipeline.py -v
```

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- SQLite3

### Installation

#### Python Backend
```bash
# Clone the repository
git clone https://github.com/gandli/tobacco-situation-monitor.git
cd tobacco-situation-monitor

# Create virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# Run tests
pytest -v
```

#### Frontend (coming soon)
```bash
# Install dependencies
npm install

# Configure environment variables
cp .env.example .env
# Edit .env with your Cloudflare credentials

# Deploy to Cloudflare
npm run deploy
```

### Local Development
```bash
# Start frontend development server
npm run dev:frontend

# Start backend development server  
npm run dev:backend

# Run end-to-end tests
npm test
```

## 📊 Use Cases

### Tobacco Monopoly Bureau
- **Proactive Enforcement**: Shift from reactive to proactive law enforcement
- **Resource Optimization**: Focus limited resources on high-threat areas
- **Intelligence-Driven Operations**: Make data-driven decisions for raids and investigations
- **Compliance Monitoring**: Ensure legal tobacco market integrity

### Multi-agency Collaboration
- **Customs Integration**: Share maritime smuggling intelligence with customs authorities
- **Transportation Department**: Coordinate vehicle inspection checkpoints
- **Public Security**: Joint operations for counterfeit production site raids
- **Market Supervision**: Verify business licenses and retail permits

## ⚖️ Compliance & Ethics

### Data Privacy
- **Public Data Only**: Collects only publicly available information
- **Anonymized Processing**: Personal data is anonymized and aggregated
- **Local Processing**: Sensitive data processed locally, not transmitted externally
- **Audit Logging**: Complete audit trail of all system operations

### Legal Compliance
- **Authorized Use**: Designed for authorized law enforcement personnel only
- **Evidence Standards**: Digital evidence meets legal admissibility requirements
- **Procedural Safeguards**: Built-in compliance checks for proper procedures
- **Regular Audits**: System undergoes regular security and compliance audits

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork** the repository
2. Create a **feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add some amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. Open a **Pull Request**

Please ensure your code follows our coding standards and includes appropriate tests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ for tobacco law enforcement professionals worldwide.**

*Note: This tool is designed for legitimate law enforcement purposes only. Unauthorized use is prohibited.*