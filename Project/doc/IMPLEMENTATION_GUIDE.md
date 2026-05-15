# Implementation Guide - Using Professional Features

## Quick Start

### 1. Basic Scan (Reconnaissance)

```bash
python -m src.web_scanner.main --url https://example.com
```

Output: `reports/scan_report_<timestamp>.html`

---

### 2. Comprehensive Scan with Active Tests

```bash
python -m src.web_scanner.main \
  --url https://example.com \
  --active-tests \
  --crawl-depth 3 \
  --format html \
  --verbose
```

**What happens:**
- Discovers URLs up to 3 levels deep
- Tests for injection vulnerabilities (XSS, SQLi, Command Injection)
- Generates detailed HTML report with metrics
- Logs all operations in DEBUG mode

---

### 3. Authenticated Scanning

```bash
python -m src.web_scanner.main \
  --url https://internal-app.local \
  --auth-url https://internal-app.local/login \
  --auth-user admin \
  --auth-pass SuperSecret123 \
  --active-tests \
  --format html
```

**What happens:**
- Creates authenticated session
- Validates session before scanning
- Scans both authenticated and unauthenticated pages
- Reports coverage metrics
- Includes authentication status in report

---

### 4. JSON Output for Integration

```bash
python -m src.web_scanner.main \
  --url https://example.com \
  --format json \
  --output results.json
```

**JSON includes:**
- All findings with CWE/OWASP mappings
- Comprehensive metrics
- Risk assessment
- Executive summary

---

### 5. Debugging Session/Auth Issues

```bash
python -m src.web_scanner.main \
  --url https://app.local \
  --auth-url /login \
  --auth-user testuser \
  --auth-pass password123 \
  --debug-auth \
  --verbose
```

**Output:**
- Detailed auth attempt logs
- Session validation results
- Cookie information
- Response analysis

---

## Integration Examples

### 1. Python Integration

```python
from src.web_scanner.main import run_scanner
from src.web_scanner.types import ScannerConfig
import asyncio

# Create configuration
config = ScannerConfig(
    target_url="https://example.com",
    active_tests=True,
    timeout=15,
)

# Run scan
async def scan():
    from src.web_scanner.scanner.vulnerability_scanner import VulnerabilityScanner
    scanner = VulnerabilityScanner(config)
    results = await scanner.scan()
    return results

# Generate metrics
from src.web_scanner.core.metrics import ScanMetrics
from src.web_scanner.reporting.findings_processor import FindingsProcessor

metrics = ScanMetrics()
processor = FindingsProcessor()

# Process findings
for finding_data in results.get('findings', []):
    enhanced = processor.enhance_finding(finding_data)
    metrics.record_finding(enhanced.severity, enhanced.type)

print(metrics.get_summary())
```

---

### 2. Metrics Analysis

```python
from src.web_scanner.core.metrics import ScanMetrics
from datetime import datetime

metrics = ScanMetrics()

# Simulate scanning activity
metrics.record_request(success=True)
metrics.record_request(success=True)
metrics.record_request(success=False)
metrics.mark_url_discovered("http://app.local/page1")
metrics.mark_url_discovered("http://app.local/page2")
metrics.record_finding("critical", "SQL Injection")
metrics.forms_discovered = 5
metrics.parameters_tested = 20

# Get summary
summary = metrics.get_summary()

print(f"URLs Discovered: {summary['unique_urls_discovered']}")
print(f"Success Rate: {summary['success_rate_percent']}%")
print(f"Critical Findings: {summary['findings_by_severity']['critical']}")
```

---

### 3. Risk Assessment

```python
from src.web_scanner.reporting.findings_processor import FindingsProcessor

processor = FindingsProcessor()

findings = [
    {
        "type": "SQL Injection",
        "severity": "critical",
        "url": "http://app.local/search",
        "description": "SQL injection in search parameter",
        "evidence": "Error message indicates query manipulation",
        "remediation": "Use parameterized queries"
    },
    {
        "type": "XSS",
        "severity": "high",
        "url": "http://app.local/comment",
        "description": "Reflected XSS in comment",
        "evidence": "Payload reflected in response",
        "remediation": "Implement output encoding"
    }
]

# Enhance findings
enhanced = [processor.enhance_finding(f) for f in findings]

# Calculate risk
risk = processor.calculate_risk_score(enhanced)

print(f"Risk Level: {risk['overall_risk']}")
print(f"Risk Score: {risk['risk_score']}/100")
print(f"Exploitable Issues: {risk['exploitable_findings']}")

# Generate summary
summary = processor.generate_executive_summary(enhanced, {})
print(summary)
```

---

### 4. Web Crawling

```python
from src.web_scanner.core.crawler import WebCrawler

# Initialize crawler
crawler = WebCrawler(
    base_url="https://example.com",
    max_crawl_depth=2
)

# Extract URLs
html_content = """
<html>
    <a href="/page1">Page 1</a>
    <a href="/page2">Page 2</a>
    <form action="/search">
        <input name="q" type="text">
    </form>
</html>
"""

urls, new_count = crawler.extract_urls_from_html(html_content, "https://example.com")
print(f"Discovered {new_count} new URLs")

forms = crawler.extract_forms_from_html(html_content, "https://example.com")
print(f"Found {len(forms)} forms")

params = crawler.extract_parameters_from_html(html_content)
print(f"Found parameters: {params}")

stats = crawler.get_crawl_statistics()
print(f"Total URLs: {stats['total_urls_discovered']}")
```

---

### 5. Session Management

```python
import asyncio
from src.web_scanner.core.session_manager import SessionManager

async def auth_example():
    # Create session manager
    mgr = SessionManager(verify_ssl=False, timeout=10)
    
    # Create session
    session = await mgr.create_session()
    
    # Authenticate
    success = await mgr.authenticate(
        login_url="https://app.local/login",
        username="admin",
        password="secret123",
        username_field="username",
        password_field="password"
    )
    
    if success:
        # Validate session
        is_valid = await mgr.validate_session("https://app.local/dashboard")
        
        # Get auth state
        state = mgr.get_auth_state()
        print(f"Authenticated: {state['authenticated']}")
        print(f"Username: {state['username']}")
        print(f"Session age: {state['session_age_seconds']} seconds")
    
    # Cleanup
    await mgr.cleanup()

# Run
asyncio.run(auth_example())
```

---

### 6. Generating Professional Reports

```python
from src.web_scanner.reporting.enhanced_template import generate_enhanced_html_report
from src.web_scanner.reporting.findings_processor import FindingsProcessor
from src.web_scanner.core.metrics import ScanMetrics
from datetime import datetime

# Prepare data
metrics = ScanMetrics()
processor = FindingsProcessor()

findings = [
    {
        "type": "SQL Injection",
        "severity": "critical",
        "url": "http://app.local/search?q=test",
        "description": "SQL injection vulnerability detected",
        "evidence": "Error message indicates query manipulation",
        "remediation": "Use parameterized queries",
        "affected_parameter": "q"
    }
]

# Enhance findings
enhanced_findings = [processor.enhance_finding(f) for f in findings]

# Calculate risk
risk = processor.calculate_risk_score(enhanced_findings)

# Generate summary
summary = processor.generate_executive_summary(
    enhanced_findings,
    metrics.get_summary()
)

# Generate HTML
html_report = generate_enhanced_html_report(
    findings=findings,
    metrics=metrics.get_summary(),
    risk_assessment=risk,
    executive_summary=summary,
    target_url="http://app.local",
    timestamp=datetime.now()
)

# Save report
with open("report.html", "w") as f:
    f.write(html_report)

print("Report generated: report.html")
```

---

## Configuration Examples

### config/scanner_config.yaml

```yaml
target_url: https://example.com
timeout: 15
verify_ssl: false

modules:
  recon:
    enabled: true

active_tests: true

authentication:
  enabled: true
  login_url: /login
  username_field: email
  password_field: password

crawling:
  max_depth: 2
  follow_external_links: false
  skip_static_assets: true
```

### Usage

```bash
python -m src.web_scanner.main \
  --url https://example.com \
  --config config/scanner_config.yaml
```

---

## Command-Line Reference

### Basic Options

| Option | Description | Example |
|--------|-------------|---------|
| `--url` | Target URL (required) | `--url https://example.com` |
| `--format` | Report format (html/json/pdf) | `--format json` |
| `--output` | Custom output path | `--output report.html` |

### Scanning Options

| Option | Description | Example |
|--------|-------------|---------|
| `--active-tests` | Enable injection testing | `--active-tests` |
| `--crawl-depth` | Maximum crawl depth | `--crawl-depth 3` |
| `--timeout` | Request timeout seconds | `--timeout 20` |

### Authentication

| Option | Description | Example |
|--------|-------------|---------|
| `--auth-url` | Login URL | `--auth-url /login` |
| `--auth-user` | Username | `--auth-user admin` |
| `--auth-pass` | Password | `--auth-pass secret123` |
| `--debug-auth` | Debug auth attempts | `--debug-auth` |

### Logging

| Option | Description | Example |
|--------|-------------|---------|
| `--verbose` | Enable DEBUG logging | `--verbose` |
| `--quiet` | Only show errors | `--quiet` |

---

## Real-World Examples

### Example 1: Security Assessment

```bash
# Comprehensive assessment with reporting
python -m src.web_scanner.main \
  --url https://vulnerable-app.local \
  --active-tests \
  --crawl-depth 2 \
  --format html \
  --output assessment_report.html \
  --verbose
```

### Example 2: CI/CD Integration

```bash
# Quick scan, exit with error if critical issues found
python -m src.web_scanner.main \
  --url https://staging.company.com \
  --active-tests \
  --format json \
  --output scan_results.json \
  --quiet

# Parse JSON and check for critical findings
python -c "
import json
with open('scan_results.json') as f:
    data = json.load(f)
    critical = [f for f in data['findings'] if f['severity'] == 'critical']
    exit(1 if critical else 0)
"
```

### Example 3: Penetration Testing

```bash
# Full authenticated scan with all tests
python -m src.web_scanner.main \
  --url https://internal.company.net \
  --auth-url https://internal.company.net/login \
  --auth-user pentester \
  --auth-pass temporary_pwd \
  --active-tests \
  --crawl-depth 3 \
  --timeout 20 \
  --format html \
  --output pentest_report_$(date +%Y%m%d_%H%M%S).html \
  --debug-auth \
  --verbose
```

---

## Troubleshooting

### Issue: "Connection refused"

```bash
# Solution: Verify target is running and accessible
curl -I https://example.com
python -m src.web_scanner.main --url https://example.com --timeout 30
```

### Issue: "Authentication failed"

```bash
# Solution: Debug with --debug-auth flag
python -m src.web_scanner.main \
  --url https://app.local \
  --auth-url /login \
  --auth-user admin \
  --auth-pass password123 \
  --debug-auth \
  --verbose
```

### Issue: "No findings detected"

```bash
# Solution: Enable active tests and increase crawl depth
python -m src.web_scanner.main \
  --url https://example.com \
  --active-tests \
  --crawl-depth 3 \
  --verbose
```

---

## Next Steps

1. **Customize** vulnerability patterns in `vulnerability_analyzer.py`
2. **Extend** findings processor with additional CWE mappings
3. **Integrate** with CI/CD pipelines
4. **Deploy** as microservice with FastAPI wrapper
5. **Monitor** scan metrics over time

---

*For more details, see PROFESSIONAL_ENHANCEMENTS.md*
