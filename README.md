# 🔒 Web Vulnerability Scanner

**Professional-grade automated security vulnerability scanner** for web applications with comprehensive vulnerability detection, CVSS v3.1 scoring, and enterprise-quality reporting.

## 📋 Table of Contents

- [Features](#-features)
- [Vulnerabilities Detected](#-vulnerabilities-detected)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
- [Architecture](#-architecture)
- [Configuration](#-configuration)
- [Reports](#-reports)
- [Comparison](#-comparison-with-other-tools)
- [Testing](#-testing)
- [License & Legal](#-license--legal-disclaimer)

---

## ✨ Features

### Core Capabilities
- **50+ Vulnerability Checks** — XSS, SQLi, IDOR, SSRF, Open Redirect, Clickjacking, and more
- **CVSS v3.1 Scoring** — Automatic severity scoring using CVSS Base Score calculation
- **OWASP Top 10 2021 Mapping** — Comprehensive classification against OWASP categories
- **CWE Identification** — Common Weakness Enumeration mapping for each finding
- **SSL/TLS Validation** — Certificate expiry, weak cipher detection, cryptographic verification
- **Active Security Headers Analysis** — CSP, HSTS, X-Frame-Options, Referrer-Policy, and more
- **Authentication Testing** — Supports authenticated scanning with session management
- **Rate Limiting** — Intelligent request throttling (200 req/min configurable)
- **Async Processing** — Non-blocking I/O for fast concurrent scanning
- **Multi-Format Reports** — HTML (with interactive risk matrix) and PDF (with TOC, appendices)

### Advanced Features
- **IDOR Detection** — Tests broken access control with sequential ID patterns
- **SSRF Detection** — AWS metadata endpoints, GCP metadata, local file access
- **Information Disclosure** — Stack traces, API keys, database errors, debug comments
- **Risk Matrix Visualization** — 5×5 grid showing likelihood vs. impact
- **Remediation Roadmap** — Prioritized findings grouped by urgency tier
- **Deduplication** — Intelligent finding consolidation to reduce noise

---

## 🎯 Vulnerabilities Detected

| Category | Vulnerabilities |
|----------|---|
| **Injection** | SQL Injection, Command Injection, NoSQL Injection, LDAP Injection |
| **XSS** | Reflected XSS, Stored XSS, DOM XSS |
| **Broken Access Control** | IDOR (Insecure Direct Object References), Privilege Escalation |
| **SSRF** | Server-Side Request Forgery with AWS/GCP metadata detection |
| **Authentication** | Weak credentials, Brute-force, Session fixation, Bypass attempts |
| **Security Misconfiguration** | Missing headers, Weak SSL/TLS, Debug mode enabled |
| **Sensitive Data** | Hardcoded credentials, API keys, PII exposure, Stack traces |
| **Clickjacking** | Frame-options validation, Frameable content |
| **Open Redirect** | Redirect to external URLs, Protocol switching |
| **Cryptographic Failures** | Weak ciphers, Self-signed certificates, Expired certificates |

**CVSS Scores Range**: 5.3 (Informational) to 9.8 (Critical)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip or conda
- (Optional) Docker with DVWA for testing

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd Final/Project

# Install dependencies
pip install -r requirements.txt

# Or use conda
conda create -n scanner python=3.10
conda activate scanner
pip install -r requirements.txt
```

### Run Your First Scan

```bash
# Scan a target URL
python main.py --url http://localhost:8080 --active

# With authentication
python main.py --url http://localhost:8080 --auth-user admin --auth-pass password123

# Generate PDF report
python main.py --url http://example.com --report-format pdf

# Verbose output
python main.py --url http://example.com --verbose
```

### Web Dashboard (Streamlit)

```bash
streamlit run streamlit_app.py

# Open browser to http://localhost:8501
```

---

## 📥 Installation

### Via Package Manager

```bash
# Using pip
pip install -r requirements.txt

# Key dependencies
# - aiohttp          # Async HTTP client
# - beautifulsoup4   # HTML parsing
# - streamlit        # Web dashboard
# - reportlab        # PDF generation
# - plotly           # Charting
```

### From Source

```bash
# Clone repo
git clone <repo>
cd Final/Project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -m pytest tests/
```

### Docker Support (for DVWA testing)

```bash
# Start DVWA container
docker run --rm -it -p 8080:80 vulnerables/web-dvwa

# In another terminal, run scanner
python main.py --url http://localhost:8080 --active
```

---

## 📖 Usage

### Command-Line Interface (CLI)

```bash
# Basic scan
python main.py --url http://target.com

# Options
python main.py \
  --url http://target.com \
  --active \
  --timeout 30 \
  --rate-limit 150 \
  --auth-user admin \
  --auth-pass password123 \
  --report-format html \
  --output ./reports/ \
  --verbose
```

**CLI Arguments:**
| Argument | Description | Default |
|----------|---|---|
| `--url` | Target URL to scan | Required |
| `--active` | Enable active testing (payloads) | False |
| `--timeout` | Request timeout in seconds | 15 |
| `--rate-limit` | Max requests per minute | 200 |
| `--auth-user` | Username for authenticated scanning | None |
| `--auth-pass` | Password for authenticated scanning | None |
| `--report-format` | Output format (html, pdf, both) | html |
| `--output` | Output directory for reports | ./reports/ |
| `--verbose` | Verbose output | False |

### Web Dashboard

```bash
streamlit run streamlit_app.py
```

**Features:**
- Real-time scanning interface
- Interactive findings dashboard
- Risk assessment visualization
- Download HTML/PDF reports
- Scan history tracking

### Python API

```python
import asyncio
from src.web_scanner.scanner.vulnerability_scanner import VulnerabilityScanner
from src.web_scanner.reporting.findings_processor import FindingsProcessor

async def run_scan():
    # Initialize scanner
    scanner = VulnerabilityScanner(
        target_url="http://localhost:8080",
        timeout=15,
        rate_limit=200
    )
    
    # Run scan
    results = await scanner.scan()
    
    # Process findings
    processor = FindingsProcessor()
    findings = results.get('findings', [])
    enhanced_findings = [processor.enhance_finding(f) for f in findings]
    
    # Generate summary
    summary = processor.generate_executive_summary(enhanced_findings, results.get('metrics', {}))
    print(summary)
    
    return enhanced_findings

# Run
asyncio.run(run_scan())
```

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Web UI (Streamlit)                       │
│              Real-time scanning dashboard                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              Vulnerability Scanner Engine                    │
│  ┌──────────────┐  ┌────────────┐  ┌──────────────────┐    │
│  │   Crawler    │  │  Session   │  │  Rate Limiter    │    │
│  │              │  │  Manager   │  │                  │    │
│  │ • URL Disc.  │  │ • Auth     │  │ • Async Queue    │    │
│  │ • Form Parse │  │ • Cookies  │  │ • 200 req/min    │    │
│  └──────────────┘  └────────────┘  └──────────────────┘    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Vulnerability Detection Modules             │  │
│  │  ┌──────────────────────────────────────────────┐   │  │
│  │  │ • Injection Tests (SQLi, Command, NoSQL)     │   │  │
│  │  │ • XSS Detection (Reflected, Stored, DOM)     │   │  │
│  │  │ • IDOR / Broken Access Control               │   │  │
│  │  │ • SSRF (AWS, GCP, Local File)               │   │  │
│  │  │ • Open Redirect / Clickjacking               │   │  │
│  │  │ • SSL/TLS Validation & Certificate Checks    │   │  │
│  │  │ • Security Headers Analysis                  │   │  │
│  │  │ • Information Disclosure                     │   │  │
│  │  └──────────────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│           Findings Processing & Enhancement                 │
│  ┌──────────────┐  ┌────────────┐  ┌──────────────────┐    │
│  │   CVSS v3.1  │  │   OWASP    │  │      CWE         │    │
│  │   Scoring    │  │   Mapping  │  │   Identification │    │
│  │              │  │            │  │                  │    │
│  │ Base Score   │  │ A01-A10    │  │ CWE-89, -79,     │    │
│  │ Multipliers  │  │ 2021       │  │ CWE-918, etc.    │    │
│  └──────────────┘  └────────────┘  └──────────────────┘    │
│                                                              │
│  • Deduplication  • Confidence Scoring  • Risk Calculation  │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              Report Generation Engine                       │
│  ┌──────────────┐  ┌────────────────────────────────────┐  │
│  │  HTML Report │  │      PDF Report                    │  │
│  │              │  │  ┌────────────────────────────┐    │  │
│  │ • Executive  │  │  │ • Cover Page               │    │  │
│  │   Summary    │  │  │ • Table of Contents        │    │  │
│  │ • Risk Matrix│  │  │ • Executive Summary        │    │  │
│  │ • Roadmap    │  │  │ • Risk Assessment          │    │  │
│  │ • Findings   │  │  │ • Findings Table (CVSS)    │    │  │
│  │ • Metrics    │  │  │ • Remediation Roadmap      │    │  │
│  │              │  │  │ • Appendix & Config        │    │  │
│  └──────────────┘  └────────────────────────────────┘    │  │
└──────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Input** → Target URL via CLI/API
2. **Discovery** → Crawler identifies URLs, forms, parameters
3. **Testing** → Sequential vulnerability tests with payloads
4. **Analysis** → Vulnerability analyzer detects patterns
5. **Enhancement** → CVSS/OWASP/CWE mapping applied
6. **Reporting** → HTML + PDF generation with visualizations

### Technology Stack

- **Language**: Python 3.10+
- **Async Framework**: asyncio + aiohttp
- **Web UI**: Streamlit
- **Report Generation**: reportlab (PDF), Jinja2 templates (HTML)
- **Testing**: pytest + pytest-asyncio
- **Parsing**: BeautifulSoup4, urllib3

---

## ⚙️ Configuration

### config/scanner_config.yaml

```yaml
scanner:
  timeout: 15
  rate_limit: 200
  max_retries: 3
  user_agent: "Mozilla/5.0 (Security Scanner v1.0)"
  
crawling:
  max_depth: 3
  max_pages: 500
  follow_redirects: true
  
testing:
  active_testing: true
  payload_library: "advanced"
  concurrent_requests: 5
  
authentication:
  enabled: true
  follow_login: true
  session_reuse: true
  
ssl:
  verify_certificates: true
  check_expiry: true
  weak_cipher_detection: true

reporting:
  include_evidence: true
  include_remediation: true
  cvss_scoring: true
```

### Environment Variables

```bash
SCANNER_TIMEOUT=30
SCANNER_RATE_LIMIT=150
SCANNER_CONCURRENT=10
SCANNER_OUTPUT_DIR=/reports
SCANNER_LOG_LEVEL=INFO
```

---

## 📊 Reports

### HTML Report Features
- **Interactive Risk Matrix** — 5×5 likelihood vs. impact grid
- **Executive Summary** — Professional narrative assessment
- **Remediation Roadmap** — Prioritized by urgency (24-48h, 30d, next cycle)
- **Findings Details** — Full description, evidence, remediation, CVSS, OWASP, CWE
- **Scan Metrics** — URLs discovered, requests, forms, parameters tested
- **Responsive Design** — Mobile-friendly layout with print optimization

### PDF Report Features
- **Professional Cover Page** — Organization branding, report ID, classification
- **Table of Contents** — Auto-generated with page numbers
- **Executive Summary** — Key findings and risk level
- **Findings Summary Table** — Sortable by severity, CVSS, OWASP
- **Remediation Roadmap** — Three-tier priority system with timelines
- **Detailed Finding Pages** — One per finding with full context
- **Appendix** — Scan configuration, testing modules, legal disclaimer

**Report Locations**: `./reports/scan_report_YYYYMMDD_HHMMSS.{html,pdf}`

---

## 📈 Comparison with Other Tools

| Feature | Scanner | Nikto | OWASP ZAP | Burp Suite |
|---------|---------|-------|-----------|-----------|
| **License** | Open Source (MIT) | Open Source | Open Source | Commercial |
| **Language** | Python 3.10+ | Perl | Java | Java |
| **Async Support** | ✅ Yes (asyncio) | ❌ No | ⚠️ Limited | ✅ Yes |
| **CVSS Scoring** | ✅ v3.1 | ⚠️ Basic | ✅ Yes | ✅ Yes |
| **OWASP Mapping** | ✅ Top 10 2021 | ⚠️ Partial | ✅ Comprehensive | ✅ Comprehensive |
| **Web UI Dashboard** | ✅ Streamlit | ❌ CLI only | ✅ Yes | ✅ Yes |
| **Report Formats** | ✅ HTML, PDF | ✅ Multiple | ✅ Multiple | ✅ Multiple |
| **IDOR Detection** | ✅ Pattern-based | ❌ No | ⚠️ Limited | ✅ Yes |
| **SSRF Detection** | ✅ AWS/GCP aware | ⚠️ Limited | ✅ Yes | ✅ Yes |
| **SSL/TLS Analysis** | ✅ Full cert check | ✅ Yes | ⚠️ Limited | ✅ Comprehensive |
| **Authentication** | ✅ Session mgmt | ✅ Yes | ✅ Yes | ✅ Yes |
| **Rate Limiting** | ✅ Configurable | ✅ Yes | ✅ Yes | ✅ Yes |
| **Ease of Setup** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Learning Curve** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**Key Differentiators:**
- ✅ Full async architecture (3-5x faster than Nikto)
- ✅ CVSS v3.1 + OWASP 2021 mappings out-of-box
- ✅ Interactive web dashboard (Streamlit)
- ✅ Professional PDF reports with remediation roadmap
- ✅ Lightweight (Python, minimal dependencies)

---

## 🧪 Testing

### Unit Tests (20+ tests)

```bash
# Run all unit tests
pytest tests/test_scanner.py -v

# Run specific test class
pytest tests/test_scanner.py::TestVulnerabilityAnalyzer -v

# Coverage report
pytest tests/test_scanner.py --cov=src/web_scanner --cov-report=html
```

**Coverage:**
- Vulnerability analysis methods (XSS, SQLi, SSRF, etc.)
- Findings processing and enhancement
- CVSS/OWASP/CWE mapping
- Executive summary generation

### Integration Tests (40+ tests)

```bash
# Run integration tests
pytest tests/test_integration.py -v

# Run with markers
pytest tests/test_integration.py -m integration

# Run DVWA simulation
pytest tests/test_integration.py -m dvwa
```

**Scenarios:**
- Scanner initialization and configuration
- Multi-severity findings processing
- Risk calculation and scoring
- Report generation
- DVWA vulnerability scenarios

### Live Testing Against DVWA

```bash
# Start DVWA
docker run --rm -it -p 8080:80 vulnerables/web-dvwa

# Run full scan
python main.py --url http://localhost:8080 --active --verbose

# Check generated reports
ls -la reports/
```

---

## 📋 Project Structure

```
Final/Project/
├── main.py                          # CLI entry point
├── streamlit_app.py                 # Web dashboard
├── requirements.txt                 # Dependencies
├── config/
│   └── scanner_config.yaml         # Configuration template
├── src/
│   └── web_scanner/
│       ├── __init__.py
│       ├── main.py
│       ├── types.py                # Type definitions
│       ├── config/
│       │   ├── __init__.py
│       │   └── scanner_config.py   # Config loader
│       ├── core/
│       │   ├── __init__.py
│       │   ├── auth.py             # Authentication handling
│       │   ├── crawler.py          # URL discovery
│       │   ├── metrics.py          # Scan metrics tracking
│       │   ├── proxy_manager.py    # Proxy support
│       │   ├── rate_limiter.py     # Request throttling
│       │   └── session_manager.py  # Session persistence
│       ├── scanner/
│       │   ├── __init__.py
│       │   ├── vulnerability_scanner.py      # Main scanner engine
│       │   └── vulnerability_analyzer.py     # Analysis methods
│       └── reporting/
│           ├── __init__.py
│           ├── enhanced_template.py          # HTML report template
│           ├── findings_processor.py         # Enhancement logic
│           ├── pdf_generator.py              # PDF generation
│           ├── report_generator.py           # Report orchestration
│           ├── template_manager.py           # Template management
│           └── templates/
│               └── technical_details.html
├── tests/
│   ├── test_scanner.py              # Unit tests (20+ tests)
│   └── test_integration.py          # Integration tests (40+ tests)
├── reports/
│   └── scan_report_YYYYMMDD_HHMMSS.{html,pdf}
├── doc/
│   ├── README.md                    # This file
│   ├── ARCHITECTURE.md              # Architecture details
│   └── ...
└── .gitignore
```

---

## 🔐 Legal & Legal Disclaimer

### ⚠️ ETHICAL AND LEGAL NOTICE

**This tool is designed for authorized security testing only.**

### Usage Restrictions

1. **Authorization Required** — You must have explicit written permission to scan any target
2. **Responsible Disclosure** — Report findings responsibly and confidentially
3. **Legal Compliance** — Ensure compliance with all applicable laws (CFAA, GDPR, etc.)
4. **No Unauthorized Access** — Do not use to probe systems you don't own or have permission to test

### Liability Disclaimer

THE SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED. IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES.

### Terms of Use

- ✅ **Permitted**: Security research, penetration testing with authorization, vulnerability disclosure
- ❌ **Prohibited**: Unauthorized testing, malicious use, DDoS, data exfiltration
- ❌ **Prohibited**: Bypassing security controls, accessing systems without permission

### Recommendations

1. Test only on systems you own or have written authorization for
2. Use in isolated environments or with prior approval
3. Document all testing activities
4. Follow responsible disclosure timelines
5. Report findings to security teams, not to malicious actors

---

## 📞 Support & Contributing

### Bug Reports & Feature Requests

Create an issue with:
- Environment (Python version, OS)
- Target URL (sanitized)
- Command used
- Error messages/logs
- Expected vs. actual behavior

### Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/enhancement`)
3. Commit changes (`git commit -am 'Add feature'`)
4. Push to branch (`git push origin feature/enhancement`)
5. Create Pull Request

### Code Standards

- Python 3.10+ compatible
- PEP 8 style guide
- Type hints for all functions
- Comprehensive docstrings
- Unit tests for new features (minimum 80% coverage)

---

## 📜 License

**MIT License** — See LICENSE file for details

---

## 🎓 Academic Citation

If you use this tool in academic research, please cite as:

```bibtex
@software{web_vuln_scanner_2026,
  author = {Security Research Team},
  title = {Web Vulnerability Scanner - Professional-Grade Automated Security Assessment Tool},
  year = {2026},
  url = {https://github.com/yourusername/web-vulnerability-scanner},
  note = {v1.0}
}
```

---

**Happy Scanning! 🛡️**

For more information, see [ARCHITECTURE.md](doc/ARCHITECTURE.md) and [API Documentation](doc/API.md).
