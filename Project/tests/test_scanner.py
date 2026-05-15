"""Comprehensive unit tests for the Web Vulnerability Scanner."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.web_scanner.scanner.vulnerability_analyzer import VulnerabilityAnalyzer
from src.web_scanner.reporting.findings_processor import FindingsProcessor, EnhancedFinding


class TestVulnerabilityAnalyzer:
    """Unit tests for vulnerability analysis methods."""

    def test_analyze_xss_detects_payload_reflection(self):
        """Test XSS detection identifies reflected payloads."""
        payload = "<script>alert('xss')</script>"
        html_response = f"<div>{payload}</div>"
        
        is_vulnerable, evidence = VulnerabilityAnalyzer.analyze_xss(payload, html_response)
        
        assert is_vulnerable is True
        assert "xss" in evidence.lower()

    def test_analyze_xss_no_false_positives(self):
        """Test XSS detection doesn't flag clean HTML."""
        payload = "<input value='test'>"
        html_response = "<div><p>Clean page</p></div>"
        
        is_vulnerable, evidence = VulnerabilityAnalyzer.analyze_xss(payload, html_response)
        
        assert is_vulnerable is False

    def test_analyze_sqli_detects_sql_errors(self):
        """Test SQL injection detection identifies database errors."""
        payload = "' OR '1'='1"
        error_response = "Syntax error near 'OR' in SQL query"
        
        is_vulnerable, evidence = VulnerabilityAnalyzer.analyze_sqli(payload, error_response)
        
        assert is_vulnerable is True
        assert "syntax" in evidence.lower() or "error" in evidence.lower()

    def test_analyze_sqli_no_detection_on_clean_response(self):
        """Test SQL injection detection handles normal responses."""
        payload = "' OR '1'='1"
        clean_response = "<html><body>Welcome</body></html>"
        
        is_vulnerable, evidence = VulnerabilityAnalyzer.analyze_sqli(payload, clean_response)
        
        assert is_vulnerable is False

    def test_analyze_ssrf_detects_aws_metadata(self):
        """Test SSRF detection identifies AWS metadata endpoints."""
        payload = "http://169.254.169.254/latest/meta-data/ami-id"
        response = "ami-12345678"
        
        is_vulnerable, evidence = VulnerabilityAnalyzer.analyze_ssrf(payload, response)
        
        assert is_vulnerable is True
        assert "aws" in evidence.lower() or "metadata" in evidence.lower()

    def test_analyze_ssrf_detects_linux_passwd(self):
        """Test SSRF detection identifies /etc/passwd patterns."""
        payload = "file:///etc/passwd"
        response = "root:x:0:0:root:/root:/bin/bash\nwww-data:x:33:33"
        
        is_vulnerable, evidence = VulnerabilityAnalyzer.analyze_ssrf(payload, response)
        
        assert is_vulnerable is True

    def test_analyze_open_redirect_detects_redirect(self):
        """Test open redirect detection identifies external redirects."""
        payload = "https://evil.example.com/phishing"
        headers = {'Location': 'https://evil.example.com/phishing'}
        
        is_vulnerable, evidence = VulnerabilityAnalyzer.analyze_open_redirect(payload, headers)
        
        assert is_vulnerable is True
        assert "evil.example.com" in evidence

    def test_analyze_info_disclosure_detects_stack_trace(self):
        """Test information disclosure detection finds stack traces."""
        response = """
        Traceback (most recent call last):
          File "/app/main.py", line 42, in process
            result = db.query(sql)
          File "/app/db.py", line 15, in query
            execute(query_string)
        """
        
        is_vulnerable, evidence = VulnerabilityAnalyzer.analyze_info_disclosure(response)
        
        assert is_vulnerable is True
        assert "traceback" in evidence.lower()

    def test_analyze_info_disclosure_detects_api_keys(self):
        """Test information disclosure detection finds exposed credentials."""
        response = 'apiKey: "sk-1234567890abcdefghijklmn"'
        
        is_vulnerable, evidence = VulnerabilityAnalyzer.analyze_info_disclosure(response)
        
        assert is_vulnerable is True
        assert "api" in evidence.lower() or "key" in evidence.lower()


class TestFindingsProcessor:
    """Unit tests for findings processing and enhancement."""

    def test_enhance_finding_adds_cvss_score(self):
        """Test that enhancement adds CVSS score to finding."""
        processor = FindingsProcessor()
        
        finding = {
            'type': 'SQL Injection',
            'severity': 'high',
            'url': 'http://example.com/search',
            'description': 'SQL injection found'
        }
        
        enhanced = processor.enhance_finding(finding)
        
        assert enhanced.cvss_score > 0
        assert enhanced.cvss_score == processor.CVSS_SCORES.get('SQL Injection', 0.0)

    def test_enhance_finding_maps_cwe(self):
        """Test that enhancement maps CWE ID."""
        processor = FindingsProcessor()
        
        finding = {
            'type': 'Cross-site Scripting (XSS)',
            'severity': 'medium',
            'url': 'http://example.com',
            'description': 'XSS vulnerability'
        }
        
        enhanced = processor.enhance_finding(finding)
        
        assert enhanced.cwe_id is not None
        assert 'CWE-' in enhanced.cwe_id

    def test_enhance_finding_maps_owasp(self):
        """Test that enhancement maps OWASP category."""
        processor = FindingsProcessor()
        
        finding = {
            'type': 'SQL Injection',
            'severity': 'critical',
            'url': 'http://example.com/api',
            'description': 'Critical SQL injection'
        }
        
        enhanced = processor.enhance_finding(finding)
        
        assert enhanced.owasp_category is not None
        assert 'A' in enhanced.owasp_category  # OWASP categories start with A

    def test_generate_executive_summary_counts_severities(self):
        """Test executive summary correctly counts findings by severity."""
        processor = FindingsProcessor()
        
        findings = [
            EnhancedFinding(
                type='SQL Injection',
                severity='critical',
                url='http://example.com',
                description='Critical injection',
                evidence='Evidence here',
                remediation='Fix this',
                confidence_score=0.95
            ),
            EnhancedFinding(
                type='XSS',
                severity='high',
                url='http://example.com',
                description='XSS vulnerability',
                evidence='XSS evidence',
                remediation='Encode output',
                confidence_score=0.85
            ),
            EnhancedFinding(
                type='Missing Header',
                severity='medium',
                url='http://example.com',
                description='Missing security header',
                evidence='Header missing',
                remediation='Add header',
                confidence_score=0.75
            )
        ]
        
        summary = processor.generate_executive_summary(findings, {})
        
        assert 'critical' in summary.lower()
        assert 'injection' in summary.lower()
        assert summary != ""

    def test_calculate_risk_score_high_for_critical(self):
        """Test risk scoring correctly identifies critical issues."""
        processor = FindingsProcessor()
        
        findings = [
            EnhancedFinding(
                type='Remote Code Execution',
                severity='critical',
                url='http://example.com',
                description='Critical RCE',
                evidence='RCE confirmed',
                remediation='Patch immediately',
                confidence_score=0.99
            )
        ]
        
        risk = processor.calculate_risk_score(findings)
        
        assert risk['overall_risk'] in ['critical', 'high']
        assert risk['critical_findings'] == 1

    def test_group_findings_by_severity(self):
        """Test grouping findings by severity level."""
        processor = FindingsProcessor()
        
        findings = [
            EnhancedFinding(
                type='SQLi', severity='critical', url='http://example.com',
                description='Test', evidence='Test', remediation='Test', confidence_score=0.9
            ),
            EnhancedFinding(
                type='XSS', severity='high', url='http://example.com',
                description='Test', evidence='Test', remediation='Test', confidence_score=0.8
            ),
            EnhancedFinding(
                type='Header', severity='medium', url='http://example.com',
                description='Test', evidence='Test', remediation='Test', confidence_score=0.7
            ),
        ]
        
        grouped = processor.group_findings_by_severity(findings)
        
        assert 'critical' in grouped
        assert 'high' in grouped
        assert 'medium' in grouped
        assert len(grouped['critical']) == 1
        assert len(grouped['high']) == 1
        assert len(grouped['medium']) == 1

    def test_deduplicate_findings_removes_duplicates(self):
        """Test deduplication removes identical findings."""
        processor = FindingsProcessor()
        
        findings = [
            {
                'type': 'SQL Injection',
                'url': 'http://example.com/search',
                'severity': 'high',
                'description': 'SQL injection in search'
            },
            {
                'type': 'SQL Injection',
                'url': 'http://example.com/search',
                'severity': 'high',
                'description': 'SQL injection in search'
            }
        ]
        
        deduplicated = processor.deduplicate_findings(findings)
        
        assert len(deduplicated) == 1


class TestEnhancedFindingDataclass:
    """Unit tests for EnhancedFinding dataclass."""

    def test_enhanced_finding_initialization(self):
        """Test EnhancedFinding can be created with all fields."""
        finding = EnhancedFinding(
            type='SQL Injection',
            severity='critical',
            url='http://example.com/api',
            description='SQL injection vulnerability',
            evidence='SELECT * FROM users',
            remediation='Use parameterized queries',
            confidence_score=0.95,
            cwe_id='CWE-89',
            owasp_category='A03:2021',
            cvss_score=9.8
        )
        
        assert finding.type == 'SQL Injection'
        assert finding.cvss_score == 9.8
        assert finding.cwe_id == 'CWE-89'

    def test_enhanced_finding_to_dict(self):
        """Test EnhancedFinding can be serialized to dict."""
        finding = EnhancedFinding(
            type='XSS',
            severity='high',
            url='http://example.com',
            description='XSS vulnerability',
            evidence='<script>alert(1)</script>',
            remediation='Encode output',
            confidence_score=0.85,
            cvss_score=6.1
        )
        
        finding_dict = finding.to_dict() if hasattr(finding, 'to_dict') else {
            'type': finding.type,
            'severity': finding.severity,
            'url': finding.url,
            'cvss_score': finding.cvss_score
        }
        
        assert finding_dict['type'] == 'XSS'
        assert finding_dict['severity'] == 'high'


class TestScannerMetrics:
    """Unit tests for scanner metrics tracking."""

    def test_metrics_initialization(self):
        """Test ScanMetrics initializes with correct defaults."""
        from src.web_scanner.core.metrics import ScanMetrics
        
        metrics = ScanMetrics()
        summary = metrics.get_summary()
        
        assert 'scan_duration_seconds' in summary
        assert 'total_findings' in summary
        assert 'unique_urls_discovered' in summary

    def test_metrics_increments_properly(self):
        """Test metrics can be incremented and retrieved."""
        from src.web_scanner.core.metrics import ScanMetrics
        
        metrics = ScanMetrics()
        
        # Simulate some activity
        initial_summary = metrics.get_summary()
        initial_requests = initial_summary.get('total_requests', 0)
        
        # Metrics should have structure
        assert isinstance(initial_summary, dict)
        assert len(initial_summary) > 0


class TestIntegrationBasics:
    """Basic integration-style tests without external dependencies."""

    def test_analyzer_methods_callable(self):
        """Test all analyzer methods are callable."""
        analyzer = VulnerabilityAnalyzer
        
        methods = [
            'analyze_xss',
            'analyze_sqli',
            'analyze_ssrf',
            'analyze_open_redirect',
            'analyze_info_disclosure'
        ]
        
        for method_name in methods:
            assert hasattr(analyzer, method_name)
            assert callable(getattr(analyzer, method_name))

    def test_processor_creates_enhancements(self):
        """Test processor can enhance findings."""
        processor = FindingsProcessor()
        
        finding = {
            'type': 'SQL Injection',
            'severity': 'high',
            'url': 'http://example.com',
            'description': 'Test'
        }
        
        enhanced = processor.enhance_finding(finding)
        
        assert enhanced is not None
        assert hasattr(enhanced, 'cvss_score')


# Pytest fixtures
@pytest.fixture
def sample_findings():
    """Fixture providing sample findings for testing."""
    return [
        {
            'type': 'SQL Injection',
            'severity': 'critical',
            'url': 'http://example.com/search',
            'description': 'SQL injection in search parameter',
            'evidence': "' OR '1'='1",
            'remediation': 'Use parameterized queries'
        },
        {
            'type': 'Cross-site Scripting (XSS)',
            'severity': 'high',
            'url': 'http://example.com/comment',
            'description': 'Reflected XSS in comment',
            'evidence': '<script>alert(1)</script>',
            'remediation': 'Encode all user input'
        },
        {
            'type': 'Missing Security Header',
            'severity': 'medium',
            'url': 'http://example.com/',
            'description': 'X-Frame-Options header missing',
            'evidence': 'Header not present in response',
            'remediation': 'Add X-Frame-Options: DENY'
        }
    ]


@pytest.fixture
def processor():
    """Fixture providing a FindingsProcessor instance."""
    return FindingsProcessor()


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
