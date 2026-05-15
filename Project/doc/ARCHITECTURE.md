# System Architecture & Design

## High-Level Architecture Diagram

```mermaid
graph TB
    User["👤 User / API Client"]
    CLI["🖥️ Command-Line Interface"]
    Web["🌐 Web Dashboard<br/>Streamlit"]
    
    User -->|"--url, --active, etc"| CLI
    User -->|"Browser: :8501"| Web
    
    CLI -->|"Execute Scan"| Engine
    Web -->|"Execute Scan"| Engine
    
    Engine["🔍 Vulnerability Scanner Engine<br/>VulnerabilityScanner.scan()"]
    
    Engine -->|"Discover URLs"| Crawler["🕷️ Web Crawler<br/>• URL Discovery<br/>• Form Parsing<br/>• Parameter Extraction"]
    Engine -->|"Manage Sessions"| SessionMgr["🔑 Session Manager<br/>• Authentication<br/>• Cookie Handling<br/>• Token Management"]
    Engine -->|"Rate Limiting"| RateLimiter["⏱️ Rate Limiter<br/>• Async Queue<br/>• 200 req/min<br/>• Backoff Strategy"]
    
    Crawler -->|"URLs & Forms"| Tests["🧪 Vulnerability Tests"]
    SessionMgr -->|"Authenticated Context"| Tests
    
    Tests -->|"Test Payloads"| Injection["💉 Injection Tests<br/>• SQL Injection<br/>• Command Injection<br/>• NoSQL Injection"]
    Tests -->|"Test Payloads"| XSS["<> XSS Tests<br/>• Reflected XSS<br/>• Stored XSS<br/>• DOM XSS"]
    Tests -->|"Test Patterns"| IDOR["🔓 IDOR Tests<br/>• Sequential IDs<br/>• Object References"]
    Tests -->|"Test SSRF Payloads"| SSRF["🔗 SSRF Tests<br/>• AWS Metadata<br/>• GCP Metadata<br/>• Local Files"]
    Tests -->|"Test Redirects"| Redirect["↪️ Redirect Tests<br/>• Open Redirect<br/>• Cross-Domain"]
    Tests -->|"Check Headers"| Headers["📋 Security Headers<br/>• CSP, HSTS<br/>• X-Frame-Options<br/>• X-Content-Type"]
    Tests -->|"SSL Validation"| SSL["🔐 SSL/TLS Tests<br/>• Certificate Expiry<br/>• Weak Ciphers<br/>• Chain Validation"]
    Tests -->|"Info Patterns"| Info["ℹ️ Info Disclosure<br/>• Stack Traces<br/>• API Keys<br/>• Debug Info"]
    Tests -->|"UI Vectors"| Click["☝️ Clickjacking<br/>• Frame-options<br/>• Frameable Pages"]
    
    Injection -->|"Raw Findings"| Analyzer["🔬 Vulnerability Analyzer<br/>VulnerabilityAnalyzer<br/>Static pattern analysis"]
    XSS -->|"Raw Findings"| Analyzer
    IDOR -->|"Raw Findings"| Analyzer
    SSRF -->|"Raw Findings"| Analyzer
    Redirect -->|"Raw Findings"| Analyzer
    Headers -->|"Raw Findings"| Analyzer
    SSL -->|"Raw Findings"| Analyzer
    Info -->|"Raw Findings"| Analyzer
    Click -->|"Raw Findings"| Analyzer
    
    Analyzer -->|"Analyzed Findings"| Processor["📊 Findings Processor<br/>FindingsProcessor"]
    
    Processor -->|"Assign CVSS"| CVSS["📈 CVSS v3.1 Scoring<br/>Base Score Calculation"]
    Processor -->|"Map CWE"| CWE["🏷️ CWE Mapping<br/>Common Weakness Enum"]
    Processor -->|"Map OWASP"| OWASP["🎯 OWASP Top 10<br/>2021 Classification"]
    
    CVSS -->|"Enhanced Findings"| HTML["📄 HTML Report<br/>enhanced_template.py"]
    CWE -->|"Enhanced Findings"| HTML
    OWASP -->|"Enhanced Findings"| HTML
    
    CVSS -->|"Enhanced Findings"| PDF["📕 PDF Report<br/>pdf_generator.py"]
    CWE -->|"Enhanced Findings"| PDF
    OWASP -->|"Enhanced Findings"| PDF
    
    HTML -->|"Report Files"| Output["💾 Output<br/>./reports/<br/>scan_report_*.html"]
    PDF -->|"Report Files"| Output
    
    Output -->|"Display Findings"| Web
    Output -->|"Archive"| User
    
    Crawler -->|"Metrics"| Metrics["📊 Scan Metrics<br/>• URLs scanned<br/>• Requests made<br/>• Forms found<br/>• Parameters tested"]
    
    style Engine fill:#e1f5ff
    style Analyzer fill:#f3e5f5
    style Processor fill:#e8f5e9
    style HTML fill:#fff3e0
    style PDF fill:#fff3e0
    style Output fill:#fce4ec
```

---

## Component Interaction Flow

### Request Processing Pipeline

```mermaid
sequenceDiagram
    User->>CLI: python main.py --url http://target.com
    CLI->>VulnScanner: VulnerabilityScanner(target_url)
    VulnScanner->>Crawler: Start crawling
    
    Note over Crawler: Discover URLs, forms
    Crawler->>Metrics: Track URLs found
    
    VulnScanner->>Tests: For each URL/param
    
    alt Active Testing
        Tests->>Injection: Test SQL payloads
        Tests->>XSS: Test XSS payloads
        Tests->>SSRF: Test SSRF payloads
    end
    
    Tests->>Analyzer: Analyze responses
    Analyzer->>Analyzer: Pattern matching
    
    Analyzer->>Processor: Raw findings
    Processor->>CVSS: Calculate scores
    Processor->>CWE: Map identifiers
    Processor->>OWASP: Categorize
    
    Processor->>HTMLGen: Generate report
    Processor->>PDFGen: Generate report
    
    HTMLGen->>Reports: scan_report_*.html
    PDFGen->>Reports: scan_report_*.pdf
    
    Reports->>User: Return findings
```

---

## Data Structures

### Finding Object Structure

```mermaid
graph TD
    RawFinding["Raw Finding Dict"]
    RawFinding --> Type["type: str<br/>e.g., 'SQL Injection'"]
    RawFinding --> URL["url: str<br/>Vulnerable endpoint"]
    RawFinding --> Severity["severity: str<br/>critical|high|medium|low|info"]
    RawFinding --> Description["description: str<br/>What was found"]
    RawFinding --> Evidence["evidence: str<br/>Proof of vulnerability"]
    RawFinding --> Remediation["remediation: str<br/>How to fix"]
    RawFinding --> Confidence["confidence_score: float<br/>0.0 - 1.0"]
    RawFinding --> Parameter["affected_parameter: str"]
    RawFinding --> Payload["payload_used: str"]
    
    RawFinding -->|enhance| EnhancedFinding["Enhanced Finding"]
    
    EnhancedFinding --> CVSS["cvss_score: float<br/>3.5 - 9.8"]
    EnhancedFinding --> CWE["cwe_id: str<br/>CWE-89, CWE-79, etc"]
    EnhancedFinding --> OWASP["owasp_category: str<br/>A03:2021"]
    EnhancedFinding --> Hash["finding_hash: str<br/>For deduplication"]
    EnhancedFinding --> Duplicate["is_duplicate: bool<br/>Redundancy flag"]
```

### Scan Results Structure

```
ScanResults {
    "target": "http://example.com",
    "metrics": {
        "scan_duration_seconds": 45.2,
        "total_requests": 312,
        "successful_requests": 298,
        "failed_requests": 14,
        "unique_urls_discovered": 58,
        "forms_discovered": 12,
        "parameters_tested_total": 245,
        "unique_parameters_tested": 89,
        "total_findings": 14,
        "findings_by_severity": {
            "critical": 2,
            "high": 4,
            "medium": 6,
            "low": 2,
            "info": 0
        },
        "findings_by_type": {
            "SQL Injection": 2,
            "XSS": 4,
            "Missing Header": 6,
            "IDOR": 1,
            "SSRF": 1
        },
        "success_rate_percent": 95.5,
        "coverage_percent": 87.3,
        "authenticated_pages_visited": 3,
        "urls_scanned_count": 58
    },
    "findings": [
        { ... finding objects ... }
    ],
    "risk_assessment": {
        "overall_risk": "high",
        "risk_score": 78,
        "critical_findings": 2,
        "high_findings": 4,
        "exploitable_findings": 6
    }
}
```

---

## Scanning Workflow

### Phase 1: Reconnaissance

```mermaid
graph LR
    Start["🔴 Start"]
    Start --> Fetch["Fetch target URL"]
    Fetch --> Parse["Parse HTML/JS"]
    Parse --> Extract["Extract URLs<br/>Forms<br/>Parameters"]
    Extract --> Crawl["Follow links<br/>up to max depth"]
    Crawl --> Metrics["Update Metrics<br/>URLs discovered<br/>Forms found"]
    Metrics --> End["✅ Phase 1 Complete"]
    
    style Start fill:#ffcdd2
    style End fill:#c8e6c9
```

### Phase 2: Vulnerability Testing

```mermaid
graph LR
    Start["🔴 Recon Complete"]
    Start --> Queue["Queue all tests"]
    Queue --> Injection["Injection Tests<br/>SQLi, Command, etc"]
    Queue --> XSS["XSS Tests<br/>Reflected, Stored"]
    Queue --> Logic["Logic Tests<br/>IDOR, Authz"]
    Queue --> Config["Config Tests<br/>Headers, SSL"]
    Queue --> Info["Info Tests<br/>Disclosure patterns"]
    
    Injection --> Analysis["Analysis phase"]
    XSS --> Analysis
    Logic --> Analysis
    Config --> Analysis
    Info --> Analysis
    
    analysis --> Results["Raw results<br/>200+ data points"]
    Results --> End["✅ Phase 2 Complete"]
    
    style Start fill:#ffcdd2
    style End fill:#c8e6c9
```

### Phase 3: Analysis & Enhancement

```mermaid
graph LR
    RawFindings["Raw Findings<br/>Detection results"]
    RawFindings --> Dedup["Deduplication<br/>Remove duplicates"]
    Dedup --> CVSS["CVSS Scoring<br/>v3.1 Base Score"]
    CVSS --> CWE["CWE Mapping<br/>Weakness enum"]
    CWE --> OWASP["OWASP Mapping<br/>Top 10 2021"]
    OWASP --> Enhanced["Enhanced Findings<br/>Rich metadata"]
    Enhanced --> Risk["Risk Calculation<br/>Overall score"]
    Risk --> Summary["Executive Summary<br/>Narrative"]
    Summary --> Report["📄 Ready for Report"]
    
    style RawFindings fill:#ffcdd2
    style Report fill:#c8e6c9
```

### Phase 4: Report Generation

```mermaid
graph TD
    Enhanced["Enhanced Findings<br/>+ Metrics<br/>+ Risk Assessment"]
    
    Enhanced --> HTML["🌐 HTML Report<br/>enhanced_template.py"]
    Enhanced --> PDF["📕 PDF Report<br/>pdf_generator.py"]
    
    HTML --> HTMLContent["✅ HTML Output<br/>• Executive Summary<br/>• Risk Matrix<br/>• Finding Details<br/>• Remediation Roadmap<br/>• Metrics Dashboard"]
    
    PDF --> PDFContent["✅ PDF Output<br/>• Cover Page<br/>• Table of Contents<br/>• Executive Summary<br/>• Risk Assessment<br/>• Findings Table<br/>• Remediation Roadmap<br/>• Detailed Findings<br/>• Appendix"]
    
    HTMLContent --> Reports["💾 ./reports/<br/>scan_report_*.html"]
    PDFContent --> Reports
    
    Reports --> Display["Display to User<br/>Web dashboard<br/>Email<br/>Archive"]
```

---

## Async Architecture

### Concurrent Request Handling

```mermaid
graph TB
    Queue["Request Queue<br/>100+ pending requests"]
    
    Queue --> Limiter["Rate Limiter<br/>200 req/min"]
    
    Limiter --> Worker1["🔄 Worker 1"]
    Limiter --> Worker2["🔄 Worker 2"]
    Limiter --> Worker3["🔄 Worker 3"]
    Limiter --> WorkerN["🔄 Worker N"]
    
    Worker1 --> HTTP["HTTP Request<br/>Async aiohttp"]
    Worker2 --> HTTP
    Worker3 --> HTTP
    WorkerN --> HTTP
    
    HTTP --> Parse["Parse Response<br/>BeautifulSoup4"]
    Parse --> Analyze["Quick Analysis<br/>Pattern match"]
    Analyze --> Queue2["Add to Result Queue"]
    
    Queue2 --> Collector["Result Collector<br/>Merge findings"]
    Collector --> Processor["Send to Processor"]
    
    style Queue fill:#bbdefb
    style Worker1 fill:#c5e1a5
    style Worker2 fill:#c5e1a5
    style Worker3 fill:#c5e1a5
    style WorkerN fill:#c5e1a5
```

---

## Security & Configuration

### Configuration Hierarchy

```
Environment Variables (highest priority)
    ↓
Command-line Arguments
    ↓
config/scanner_config.yaml
    ↓
Hardcoded Defaults (lowest priority)
```

### Authentication Flow

```mermaid
sequenceDiagram
    Scanner->>Target: Initial request
    Target-->>Scanner: Login page
    Scanner->>LoginForm: Extract form fields
    Scanner->>Target: POST credentials
    Target-->>Scanner: Session cookie
    Scanner->>SessionMgr: Store cookie
    
    loop Authenticated Scanning
        Scanner->>SessionMgr: Get cookie
        SessionMgr-->>Scanner: Valid cookie
        Scanner->>Target: Request with cookie
        Target-->>Scanner: Authenticated response
    end
```

---

## Performance Characteristics

### Scanning Speed Optimization

| Component | Optimization | Result |
|-----------|---|---|
| HTTP Requests | Async concurrency (5 workers) | 3-5x faster than sequential |
| Parsing | BeautifulSoup4 with lxml backend | Fast HTML parsing |
| Analysis | Static pattern matching (re module) | Near-instant detection |
| Rate Limiting | Async queue + exponential backoff | No request overflow |

### Memory Usage Profile

- **Small site** (10-50 URLs): ~50 MB
- **Medium site** (50-200 URLs): ~150 MB
- **Large site** (200+ URLs): ~300-500 MB

### Typical Scan Durations

| Target Size | URLs | Estimated Time |
|---|---|---|
| Small | 5-10 | 30-60 seconds |
| Medium | 50-100 | 2-5 minutes |
| Large | 200-500 | 10-30 minutes |

*(Times vary based on response times and complexity)*

---

## Deployment Architecture

### Local Development

```
Developer Machine
├── Python 3.10 environment
├── scanner code (src/)
├── tests/ (pytest)
├── streamlit_app.py (web dashboard)
└── main.py (CLI)
```

### CI/CD Pipeline (Recommended)

```
GitHub/GitLab
    ↓
[Lint: pylint, black]
    ↓
[Unit Tests: pytest (20+ tests)]
    ↓
[Integration Tests: pytest-asyncio]
    ↓
[Coverage Report: 80%+ required]
    ↓
[Build Artifact]
    ↓
[Deploy to container registry]
```

### Docker Deployment

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app.py"]
```

---

## Class Hierarchy

```mermaid
classDiagram
    class VulnerabilityScanner {
        target_url: str
        timeout: int
        rate_limit: int
        +scan() -> dict
        -_run_recon()
        -_run_active_injection_tests()
        -run_ssl_tls_checks()
        -run_config_tests()
        -run_idor_tests()
        -run_info_disclosure_tests()
    }
    
    class VulnerabilityAnalyzer {
        +analyze_xss(payload, response) -> tuple
        +analyze_sqli(payload, response) -> tuple
        +analyze_ssrf(payload, response) -> tuple
        +analyze_open_redirect(payload, headers) -> tuple
        +analyze_info_disclosure(response) -> tuple
    }
    
    class FindingsProcessor {
        CVSS_SCORES: dict
        CWE_MAPPING: dict
        OWASP_MAPPING: dict
        +enhance_finding(finding) -> EnhancedFinding
        +generate_executive_summary(findings, metrics) -> str
        +calculate_risk_score(findings) -> dict
        +deduplicate_findings(findings) -> list
        +group_findings_by_severity(findings) -> dict
    }
    
    class EnhancedFinding {
        type: str
        severity: str
        url: str
        description: str
        evidence: str
        remediation: str
        confidence_score: float
        cvss_score: float
        cwe_id: str
        owasp_category: str
        +to_dict() -> dict
    }
    
    class WebCrawler {
        target_url: str
        max_depth: int
        +crawl() -> list[str]
        +extract_urls()
        +extract_forms()
        +extract_parameters()
    }
    
    class SessionManager {
        cookies: dict
        +login(username, password) -> bool
        +maintain_session()
        +get_authenticated_headers() -> dict
    }
    
    class RateLimiter {
        max_requests_per_minute: int
        +wait_if_needed()
        +get_next_slot() -> float
    }
    
    class ScanMetrics {
        total_requests: int
        successful_requests: int
        urls_discovered: int
        +get_summary() -> dict
        +increment_requests()
    }
    
    VulnerabilityScanner --> WebCrawler
    VulnerabilityScanner --> VulnerabilityAnalyzer
    VulnerabilityScanner --> FindingsProcessor
    VulnerabilityScanner --> SessionManager
    VulnerabilityScanner --> RateLimiter
    VulnerabilityScanner --> ScanMetrics
    
    FindingsProcessor --> EnhancedFinding
    
    style VulnerabilityScanner fill:#bbdefb
    style VulnerabilityAnalyzer fill:#c8e6c9
    style FindingsProcessor fill:#fff9c4
    style EnhancedFinding fill:#f0f4c3
```

---

## Integration Points

### External Services (Optional)

```mermaid
graph TB
    Scanner["Web Vulnerability<br/>Scanner"]
    
    Scanner -->|"(Optional)"| Slack["Slack Webhook<br/>Send notifications"]
    Scanner -->|"(Optional)"| Email["SMTP Server<br/>Email reports"]
    Scanner -->|"(Optional)"| S3["AWS S3<br/>Archive reports"]
    Scanner -->|"(Optional)"| GitHub["GitHub Issues<br/>File bugs"]
    
    style Scanner fill:#bbdefb
```

---

## Summary

This architecture provides:

✅ **Modularity** — Each component has single responsibility  
✅ **Scalability** — Async design handles 100+ concurrent requests  
✅ **Maintainability** — Clear data flow and class hierarchy  
✅ **Testability** — Unit and integration test coverage  
✅ **Extensibility** — Easy to add new vulnerability tests or report formats  

Total codebase: **~2,500 lines** across 12 core modules
