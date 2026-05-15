# Running the Web Vulnerability Scanner

Complete guide to executing the scanner from basic to advanced configurations.

---

## Table of Contents

1. [Quick Start (30 seconds)](#quick-start-30-seconds)
2. [Basic CLI Usage](#basic-cli-usage)
3. [Web Dashboard](#web-dashboard-streamlit)
4. [Python API (Programmatic)](#python-api-programmatic)
5. [Docker Deployment](#docker-deployment)
6. [Advanced Configuration](#advanced-configuration)
7. [CI/CD Integration](#cicd-integration)
8. [Batch & Automated Scanning](#batch--automated-scanning)
9. [Troubleshooting](#troubleshooting)

---

## Quick Start (30 seconds)

### Prerequisites
```bash
# Install Python 3.10+
python --version  # Should be 3.10 or higher

# Install dependencies
pip install -r requirements.txt
```

### Scan Your First Target
```bash
# Run against a test server
python main.py --url http://localhost:8080 --active

# Or scan a remote target (with authorization!)
python main.py --url https://example.com --timeout 30

# View the report
# Reports are saved to ./reports/scan_report_YYYYMMDD_HHMMSS.html
```

---

## Basic CLI Usage

### 1. **Simplest Scan**

```bash
python main.py --url http://target.com
```

**What happens:**
- Discovers URLs and forms
- Runs passive security checks
- Generates HTML report
- Duration: 1-5 minutes depending on site size

**Output:**
```
Initializing scanner for http://target.com...
Crawling target: 100%|████████| 45/45 URLs
Running vulnerability tests...
Found 12 findings
Report generated: ./reports/scan_report_20260514_143022.html
```

---

### 2. **Active Testing (Payload Injection)**

```bash
python main.py --url http://target.com --active
```

**What happens:**
- Sends test payloads (SQLi, XSS, SSRF, etc.)
- Tests for open redirects, IDOR patterns
- Validates SSL/TLS certificates
- More thorough but slower

**Time:** 2-10 minutes

---

### 3. **With Custom Timeout**

```bash
# Increase timeout for slow servers
python main.py --url http://slow-target.com --timeout 60

# Decrease timeout for quick scanning
python main.py --url http://fast-target.com --timeout 5
```

**Default:** 15 seconds per request

---

### 4. **With Authentication**

```bash
# Scan as authenticated user
python main.py \
  --url http://localhost:8080 \
  --auth-user admin \
  --auth-pass password
```

**What happens:**
- Logs in automatically
- Discovers authenticated endpoints
- Tests authenticated functionality
- Better coverage for logged-in areas

---

### 5. **Both HTML and PDF Reports**

```bash
python main.py \
  --url http://target.com \
  --report-format both
```

**Generates:**
- `scan_report_*.html` (interactive risk matrix, metrics)
- `scan_report_*.pdf` (professional, printable)

---

### 6. **Custom Output Directory**

```bash
python main.py \
  --url http://target.com \
  --output /custom/reports/path
```

**Creates directory if it doesn't exist**

---

### 7. **Verbose Logging**

```bash
python main.py --url http://target.com --verbose
```

**Shows:**
- Every URL discovered
- Each vulnerability test
- Request/response details
- Debugging information

---

### 8. **Adjust Rate Limiting**

```bash
# Slower scanning (respectful, 100 req/min)
python main.py --url http://target.com --rate-limit 100

# Faster scanning (aggressive, 500 req/min)
python main.py --url http://target.com --rate-limit 500
```

**Default:** 200 requests/minute

---

### 9. **Complete Advanced CLI Command**

```bash
python main.py \
  --url https://localhost:8080 \
  --active \
  --timeout 30 \
  --rate-limit 150 \
  --auth-user admin \
  --auth-pass password \
  --report-format both \
  --output ./secure-reports/ \
  --verbose
```

---

## Web Dashboard (Streamlit)

### 1. **Start the Dashboard**

```bash
# In terminal
streamlit run streamlit_app.py

# Opens at http://localhost:8501
```

---

### 2. **Basic Dashboard Scan**

1. Open http://localhost:8501 in browser
2. Enter target URL in input field
3. (Optional) Toggle "Active Testing"
4. Click "Start Scan"
5. Watch real-time progress
6. View findings as they appear
7. Download HTML/PDF reports

---

### 3. **Dashboard with Authentication**

1. Enter target URL
2. Toggle "Authenticated Scanning"
3. Enter username and password
4. Click "Start Scan"
5. Scanner logs in automatically

---

### 4. **Advanced Dashboard Features**

**Real-time Metrics:**
- URLs discovered count
- Requests performed
- Forms found
- Parameters tested
- Success rate percentage

**Interactive Findings:**
- Filter by severity
- Sort by CVSS score
- View detailed remediation
- Copy evidence snippets

**Report Downloads:**
- Download HTML report immediately
- Generate & download PDF
- Both formats simultaneously

---

### 5. **Dashboard with Custom Config**

```bash
# Run on specific port
streamlit run streamlit_app.py --server.port 8888

# Run without browser auto-open
streamlit run streamlit_app.py --logger.level=error

# Run in headless mode (server only, no browser)
streamlit run streamlit_app.py --server.headless true
```

---

### 6. **Multiple Dashboard Sessions**

```bash
# Terminal 1: Dashboard on port 8501
streamlit run streamlit_app.py

# Terminal 2: Second dashboard on port 8502
streamlit run streamlit_app.py --server.port 8502

# Now run two scans in parallel
```

---

## Python API (Programmatic)

### 1. **Basic Async Scan**

```python
import asyncio
from src.web_scanner.scanner.vulnerability_scanner import VulnerabilityScanner

async def simple_scan():
    scanner = VulnerabilityScanner(target_url="http://localhost:8080")
    results = await scanner.scan()
    
    print(f"Found {len(results['findings'])} vulnerabilities")
    for finding in results['findings'][:3]:
        print(f"- {finding['type']} ({finding['severity']})")

asyncio.run(simple_scan())
```

---

### 2. **Scan with Configuration**

```python
import asyncio
from src.web_scanner.scanner.vulnerability_scanner import VulnerabilityScanner

async def configured_scan():
    scanner = VulnerabilityScanner(
        target_url="http://example.com",
        timeout=30,
        rate_limit=150,
        active_testing=True,
        ssl_verify=True
    )
    
    results = await scanner.scan()
    return results

asyncio.run(configured_scan())
```

---

### 3. **With Findings Enhancement**

```python
import asyncio
from src.web_scanner.scanner.vulnerability_scanner import VulnerabilityScanner
from src.web_scanner.reporting.findings_processor import FindingsProcessor

async def enhanced_scan():
    scanner = VulnerabilityScanner("http://localhost:8080")
    results = await scanner.scan()
    
    processor = FindingsProcessor()
    findings = results.get('findings', [])
    
    # Enhance each finding with CVSS, OWASP, CWE
    enhanced_findings = []
    for finding in findings:
        enhanced = processor.enhance_finding(finding)
        enhanced_findings.append(enhanced)
        print(f"{enhanced.type}")
        print(f"  CVSS: {enhanced.cvss_score}")
        print(f"  CWE: {enhanced.cwe_id}")
        print(f"  OWASP: {enhanced.owasp_category}")

asyncio.run(enhanced_scan())
```

---

### 4. **Generate Reports Programmatically**

```python
import asyncio
from src.web_scanner.scanner.vulnerability_scanner import VulnerabilityScanner
from src.web_scanner.reporting.findings_processor import FindingsProcessor
from src.web_scanner.reporting.enhanced_template import generate_enhanced_html_report
from src.web_scanner.reporting.pdf_generator import ReportGenerator

async def scan_and_report():
    # Run scan
    scanner = VulnerabilityScanner("http://localhost:8080")
    results = await scanner.scan()
    
    # Process findings
    processor = FindingsProcessor()
    findings = results['findings']
    enhanced_findings = [processor.enhance_finding(f) for f in findings]
    
    # Calculate risk
    risk_assessment = processor.calculate_risk_score(enhanced_findings)
    executive_summary = processor.generate_executive_summary(enhanced_findings, results['metrics'])
    
    # Generate HTML report
    html_content = generate_enhanced_html_report(
        findings=[f.to_dict() if hasattr(f, 'to_dict') else f for f in enhanced_findings],
        metrics=results['metrics'],
        risk_assessment=risk_assessment,
        executive_summary=executive_summary,
        target_url=results['target']
    )
    
    # Save HTML
    with open('report.html', 'w') as f:
        f.write(html_content)
    
    # Generate PDF
    pdf_generator = ReportGenerator()
    pdf_file = pdf_generator.generate_report(
        findings=[f.to_dict() if hasattr(f, 'to_dict') else f for f in enhanced_findings],
        template_data={
            'target': results['target'],
            'total_findings': len(enhanced_findings),
            'urls_scanned': results['metrics']['unique_urls_discovered']
        }
    )
    
    print(f"Reports generated: report.html and {pdf_file}")

asyncio.run(scan_and_report())
```

---

### 5. **Batch Scanning Multiple Targets**

```python
import asyncio
from src.web_scanner.scanner.vulnerability_scanner import VulnerabilityScanner

async def scan_target(url):
    scanner = VulnerabilityScanner(url, timeout=20)
    results = await scanner.scan()
    return {
        'url': url,
        'findings': len(results['findings']),
        'metrics': results['metrics']
    }

async def batch_scan():
    targets = [
        "http://localhost:8080",
        "http://localhost:3000",
        "https://example.com"
    ]
    
    # Scan all targets concurrently
    results = await asyncio.gather(*[scan_target(url) for url in targets])
    
    for result in results:
        print(f"{result['url']}: {result['findings']} findings")

asyncio.run(batch_scan())
```

---

### 6. **Custom Analysis Pipeline**

```python
import asyncio
from src.web_scanner.scanner.vulnerability_scanner import VulnerabilityScanner
from src.web_scanner.scanner.vulnerability_analyzer import VulnerabilityAnalyzer

async def custom_analysis():
    scanner = VulnerabilityScanner("http://localhost:8080")
    results = await scanner.scan()
    
    # Custom filtering
    critical_findings = [
        f for f in results['findings'] 
        if f['severity'].lower() == 'critical'
    ]
    
    # Custom analysis
    injection_findings = [
        f for f in critical_findings 
        if any(kw in f['type'].lower() for kw in ['injection', 'xss', 'ssrf'])
    ]
    
    print(f"Critical injection findings: {len(injection_findings)}")
    
    # Custom reporting
    for finding in injection_findings:
        print(f"\n⚠️ {finding['type']}")
        print(f"URL: {finding['url']}")
        print(f"Evidence: {finding['evidence'][:100]}...")

asyncio.run(custom_analysis())
```

---

## Docker Deployment

### 1. **Build Docker Image**

```bash
# Create Dockerfile (if not exists)
cat > Dockerfile <<EOF
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app.py"]
EOF

# Build image
docker build -t web-scanner:latest .
```

---

### 2. **Run Scanner in Docker**

```bash
# Run CLI scan
docker run --rm web-scanner:latest \
  python main.py --url http://target.com --active

# Run with output volume
docker run --rm -v $(pwd)/reports:/app/reports web-scanner:latest \
  python main.py --url http://target.com --output /app/reports
```

---

### 3. **Run Dashboard in Docker**

```bash
# Start dashboard container
docker run -p 8501:8501 web-scanner:latest

# Access at http://localhost:8501
```

---

### 4. **Docker Compose Setup**

```yaml
# docker-compose.yml
version: '3.8'

services:
  dvwa:
    image: vulnerables/web-dvwa
    ports:
      - "8080:80"
  
  scanner-dashboard:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./reports:/app/reports
    depends_on:
      - dvwa
    environment:
      - STREAMLIT_SERVER_PORT=8501
  
  scanner-cli:
    build: .
    volumes:
      - ./reports:/app/reports
    depends_on:
      - dvwa
    command: python main.py --url http://dvwa:80 --active --output /app/reports
```

**Run:**
```bash
docker-compose up
# DVWA on http://localhost:8080
# Dashboard on http://localhost:8501
```

---

### 5. **Kubernetes Deployment**

```yaml
# scanner-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-scanner
spec:
  replicas: 1
  selector:
    matchLabels:
      app: web-scanner
  template:
    metadata:
      labels:
        app: web-scanner
    spec:
      containers:
      - name: scanner
        image: web-scanner:latest
        ports:
        - containerPort: 8501
        env:
        - name: STREAMLIT_SERVER_PORT
          value: "8501"
        volumeMounts:
        - name: reports
          mountPath: /app/reports
      volumes:
      - name: reports
        emptyDir: {}
```

**Deploy:**
```bash
kubectl apply -f scanner-deployment.yaml
kubectl port-forward service/web-scanner 8501:8501
```

---

## Advanced Configuration

### 1. **Config File Approach**

```bash
# Create custom config
cat > custom_config.yaml <<EOF
scanner:
  timeout: 30
  rate_limit: 150
  max_retries: 3
  
crawling:
  max_depth: 3
  max_pages: 200
  
testing:
  active_testing: true
  concurrent_requests: 5
  
authentication:
  enabled: true
  follow_login: true
EOF

# Use config
export SCANNER_CONFIG=custom_config.yaml
python main.py --url http://target.com
```

---

### 2. **Environment Variables**

```bash
# Set environment variables
export SCANNER_TIMEOUT=60
export SCANNER_RATE_LIMIT=100
export SCANNER_OUTPUT_DIR=/var/reports
export SCANNER_LOG_LEVEL=DEBUG

# Run - uses env vars
python main.py --url http://target.com
```

---

### 3. **Proxy Support**

```bash
# Via environment
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=https://proxy.company.com:8080
python main.py --url http://target.com

# Or in Python API
scanner = VulnerabilityScanner(
    target_url="http://target.com",
    proxy="http://proxy.company.com:8080"
)
```

---

### 4. **SSL Certificate Customization**

```bash
# Ignore SSL warnings (for testing only!)
python main.py --url https://target.com --ssl-verify false

# Use custom CA certificate
export REQUESTS_CA_BUNDLE=/path/to/ca-bundle.crt
python main.py --url https://target.com
```

---

### 5. **Custom Headers & Cookies**

```python
from src.web_scanner.scanner.vulnerability_scanner import VulnerabilityScanner

async def scan_with_headers():
    scanner = VulnerabilityScanner("http://localhost:8080")
    
    # Add custom headers
    scanner.default_headers = {
        'Authorization': 'Bearer token123',
        'X-Custom-Header': 'value',
        'User-Agent': 'Custom User Agent'
    }
    
    results = await scanner.scan()
    return results

import asyncio
asyncio.run(scan_with_headers())
```

---

## CI/CD Integration

### 1. **GitHub Actions**

```yaml
# .github/workflows/security-scan.yml
name: Security Scan

on: [push, pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    services:
      dvwa:
        image: vulnerables/web-dvwa
        options: >-
          --health-cmd="curl --fail http://localhost || exit 1"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=5
        ports:
          - 8080:80
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: pip install -r requirements.txt
    
    - name: Run security scan
      run: python main.py --url http://localhost:8080 --active --report-format html
    
    - name: Upload reports
      uses: actions/upload-artifact@v3
      with:
        name: security-reports
        path: reports/
```

---

### 2. **GitLab CI**

```yaml
# .gitlab-ci.yml
security-scan:
  image: python:3.10
  services:
    - vulnerables/web-dvwa:latest
  
  before_script:
    - pip install -r requirements.txt
  
  script:
    - python main.py --url http://web-dvwa:80 --active --report-format both
  
  artifacts:
    paths:
      - reports/
    expire_in: 1 week
```

---

### 3. **Jenkins Pipeline**

```groovy
pipeline {
    agent any
    
    stages {
        stage('Setup') {
            steps {
                sh 'python -m pip install -r requirements.txt'
            }
        }
        
        stage('Scan') {
            steps {
                sh 'python main.py --url http://target.com --active --output ./reports'
            }
        }
        
        stage('Archive Reports') {
            steps {
                archiveArtifacts artifacts: 'reports/**', fingerprint: true
            }
        }
    }
    
    post {
        always {
            junit 'reports/*.xml'
            publishHTML([
                reportDir: 'reports',
                reportFiles: '*.html',
                reportName: 'Security Scan'
            ])
        }
    }
}
```

---

## Batch & Automated Scanning

### 1. **Scheduled Scans (Cron)**

```bash
#!/bin/bash
# scan_daily.sh

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_DIR="/var/reports/$TIMESTAMP"

mkdir -p $REPORT_DIR

python main.py \
  --url https://target.com \
  --active \
  --output $REPORT_DIR \
  --report-format both

# Send report via email
mail -s "Daily Security Scan - $TIMESTAMP" security@company.com \
  < $REPORT_DIR/scan_report_*.html
```

**Cron job:**
```bash
# Run daily at 2 AM
0 2 * * * /home/security/scan_daily.sh
```

---

### 2. **Scan Multiple Targets**

```bash
#!/bin/bash
# scan_portfolio.sh

TARGETS=(
    "https://app1.example.com"
    "https://app2.example.com"
    "https://api.example.com"
    "https://admin.example.com"
)

for target in "${TARGETS[@]}"; do
    echo "Scanning $target..."
    python main.py --url "$target" --active --output ./reports
done
```

---

### 3. **Python Batch Script**

```python
# batch_scan.py
import asyncio
import json
from datetime import datetime
from src.web_scanner.scanner.vulnerability_scanner import VulnerabilityScanner
from src.web_scanner.reporting.findings_processor import FindingsProcessor

async def scan_and_report(url):
    """Scan a single URL and return results."""
    try:
        scanner = VulnerabilityScanner(url, timeout=20)
        results = await scanner.scan()
        
        processor = FindingsProcessor()
        findings = results['findings']
        risk = processor.calculate_risk_score([
            processor.enhance_finding(f) for f in findings
        ])
        
        return {
            'url': url,
            'status': 'success',
            'findings': len(findings),
            'risk_level': risk['overall_risk'],
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'url': url,
            'status': 'failed',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

async def batch_scan(targets):
    """Scan multiple targets concurrently."""
    results = await asyncio.gather(*[
        scan_and_report(url) for url in targets
    ])
    
    # Save summary
    with open('batch_scan_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    successful = sum(1 for r in results if r['status'] == 'success')
    print(f"Batch scan complete: {successful}/{len(targets)} successful")
    
    # Print critical findings
    critical = [r for r in results if r.get('risk_level') == 'critical']
    if critical:
        print(f"\n⚠️ CRITICAL RISK FOUND IN:")
        for item in critical:
            print(f"  - {item['url']} ({item['findings']} findings)")

if __name__ == "__main__":
    targets = [
        "https://app1.example.com",
        "https://app2.example.com",
        "https://api.example.com",
    ]
    
    asyncio.run(batch_scan(targets))
```

**Run:**
```bash
python batch_scan.py
cat batch_scan_results.json
```

---

### 4. **Continuous Monitoring**

```python
# monitor.py
import asyncio
import time
from datetime import datetime, timedelta
from src.web_scanner.scanner.vulnerability_scanner import VulnerabilityScanner

async def continuous_monitoring(url, interval_hours=24):
    """Scan target repeatedly at intervals."""
    while True:
        print(f"\n[{datetime.now()}] Starting scan of {url}")
        
        try:
            scanner = VulnerabilityScanner(url)
            results = await scanner.scan()
            
            findings_count = len(results['findings'])
            risk_level = results.get('risk_assessment', {}).get('overall_risk', 'unknown')
            
            print(f"Found {findings_count} vulnerabilities (Risk: {risk_level})")
            
            # Log to file
            with open('monitoring_log.txt', 'a') as f:
                f.write(f"[{datetime.now()}] {url} - {findings_count} findings - {risk_level}\n")
        
        except Exception as e:
            print(f"Scan failed: {e}")
        
        # Wait for next scan
        wait_seconds = interval_hours * 3600
        print(f"Next scan in {interval_hours} hours...")
        await asyncio.sleep(wait_seconds)

if __name__ == "__main__":
    # Monitor target every 24 hours
    asyncio.run(continuous_monitoring("https://target.com", interval_hours=24))
```

---

## Troubleshooting

### Issue: Connection Refused

```bash
# Check if target is running
curl http://target.com

# Try with verbose logging
python main.py --url http://target.com --verbose

# Increase timeout
python main.py --url http://target.com --timeout 60
```

---

### Issue: Slow Scanning

```bash
# Increase rate limit (more aggressive)
python main.py --url http://target.com --rate-limit 500

# Reduce timeout for faster failures
python main.py --url http://target.com --timeout 5
```

---

### Issue: SSL Certificate Errors

```bash
# Skip SSL verification (test only!)
python main.py --url https://target.com --ssl-verify false

# Or use custom CA
export REQUESTS_CA_BUNDLE=/path/to/ca-bundle.crt
python main.py --url https://target.com
```

---

### Issue: Out of Memory

```bash
# Reduce concurrent requests
# Edit config or use Python API with lower concurrency
python main.py --url http://target.com --concurrent 2
```

---

### Issue: No Reports Generated

```bash
# Check if reports directory exists
mkdir -p reports/

# Check file permissions
chmod 755 reports/

# Run with specific output directory
python main.py --url http://target.com --output /tmp/reports
```

---

## Summary Table

| Method | Speed | Control | Best For |
|--------|-------|---------|----------|
| **Basic CLI** | Fast | Limited | Quick scans |
| **Advanced CLI** | Medium | High | One-off scans |
| **Streamlit Dashboard** | Medium | Medium | Interactive use |
| **Python API** | Flexible | Very High | Automation |
| **Docker** | Fast | Medium | Deployment |
| **Batch Scripts** | Slow | High | Multiple targets |
| **CI/CD** | Fast | High | Continuous monitoring |
| **Cron Jobs** | Slow | Medium | Scheduled scanning |

---

## Quick Reference

```bash
# Most common commands
python main.py --url http://target.com                          # Basic scan
python main.py --url http://target.com --active                 # With payloads
python main.py --url http://target.com --active --verbose       # Verbose output
streamlit run streamlit_app.py                                   # Web dashboard
python main.py --url http://target.com --report-format both     # HTML + PDF
python main.py --url http://target.com --auth-user admin --auth-pass pass  # Auth
docker run -p 8501:8501 web-scanner:latest                      # Docker dashboard
```

---

**Choose your preferred method based on your use case!**
