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