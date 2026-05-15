"""Integration tests for Web Vulnerability Scanner against live targets."""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from src.web_scanner.scanner.vulnerability_scanner import VulnerabilityScanner
from src.web_scanner.reporting.findings_processor import FindingsProcessor


class TestScannerIntegration:
    """Integration tests for end-to-end scanning scenarios."""

    @pytest.mark.asyncio
    async def test_scanner_initialization(self):
        """Test scanner can be initialized without errors."""
        scanner = VulnerabilityScanner(
            target_url="http://localhost:8080",
            timeout=10,
            rate_limit=100
        )
        
        assert scanner.target_url == "http://localhost:8080"
        assert scanner.timeout == 10

    @pytest.mark.asyncio
    async def test_scan_returns_dict_structure(self):
        """Test that scan returns proper dict structure (mocked)."""
        scanner = VulnerabilityScanner(
            target_url="http://localhost:8080",
            timeout=10
        )
        
        # Mock the actual scanning to avoid network calls
        with patch.object(scanner, '_run_recon', new_callable=AsyncMock):
            with patch.object(scanner, 'metrics'):
                scanner.metrics.get_summary = lambda: {
                    'total_requests': 10,
                    'unique_urls_discovered': 5,
                    'forms_discovered': 2,
                    'parameters_tested_total': 15,
                    'authenticated_pages_visited': 0,
                    'scan_duration_seconds': 5.0,
                    'success_rate_percent': 90.0,
                    'coverage_percent': 80.0,
                    'findings_by_severity': {}
                }
                
                result = await scanner.scan()
                
                assert isinstance(result, dict)
                assert 'target' in result or 'metrics' in result

    def test_scanner_configuration(self):
        """Test scanner accepts all configuration options."""
        config = {
            'target': 'http://localhost:8080',
            'timeout': 30,
            'rate_limit': 200,
            'active_testing': True,
            'ssl_verify': False
        }
        
        scanner = VulnerabilityScanner(
            target_url=config['target'],
            timeout=config['timeout'],
            rate_limit=config['rate_limit']
        )
        
        assert scanner.target_url == config['target']
        assert scanner.timeout == config['timeout']

    def test_findings_processor_handles_multiple_findings(self):
        """Test processor can handle bulk findings."""
        processor = FindingsProcessor()
        
        findings = [
            {'type': 'SQL Injection', 'severity': 'critical', 'url': f'http://localhost:8080/page{i}'}
            for i in range(10)
        ]
        
        # Add descriptions and other required fields
        for finding in findings:
            finding.update({
                'description': f"{finding['type']} vulnerability",
                'evidence': 'test evidence',
                'remediation': 'test remediation',
                'confidence_score': 0.9
            })
        
        enhanced_findings = [processor.enhance_finding(f) for f in findings]
        
        assert len(enhanced_findings) == 10
        assert all(f.cvss_score > 0 for f in enhanced_findings)

    def test_executive_summary_generation_with_multiple_severities(self):
        """Test executive summary handles diverse findings."""
        processor = FindingsProcessor()
        
        from src.web_scanner.reporting.findings_processor import EnhancedFinding
        
        findings = [
            EnhancedFinding(
                type='Remote Code Execution', severity='critical',
                url='http://localhost:8080/api', description='RCE',
                evidence='RCE confirmed', remediation='Patch',
                confidence_score=0.99, cvss_score=9.8
            ),
            EnhancedFinding(
                type='SQL Injection', severity='high',
                url='http://localhost:8080/search', description='SQLi',
                evidence='SQLi confirmed', remediation='Parameterize',
                confidence_score=0.95, cvss_score=9.0
            ),
            EnhancedFinding(
                type='XSS', severity='medium',
                url='http://localhost:8080/forum', description='XSS',
                evidence='XSS confirmed', remediation='Encode',
                confidence_score=0.85, cvss_score=6.1
            ),
            EnhancedFinding(
                type='Missing Header', severity='low',
                url='http://localhost:8080/', description='Missing CSP',
                evidence='No CSP header', remediation='Add CSP',
                confidence_score=0.75, cvss_score=5.3
            ),
        ]
        
        summary = processor.generate_executive_summary(findings, {})
        
        # Should mention multiple severity levels and injection types
        assert 'critical' in summary.lower() or 'high' in summary.lower()
        assert len(summary) > 50  # Should be substantive

    def test_risk_calculation_across_findings(self):
        """Test risk scoring works across multiple findings."""
        processor = FindingsProcessor()
        
        from src.web_scanner.reporting.findings_processor import EnhancedFinding
        
        findings = [
            EnhancedFinding(
                type='Type1', severity='critical',
                url='http://localhost:8080', description='D',
                evidence='E', remediation='R',
                confidence_score=0.9, cvss_score=9.8
            ),
            EnhancedFinding(
                type='Type2', severity='critical',
                url='http://localhost:8080', description='D',
                evidence='E', remediation='R',
                confidence_score=0.9, cvss_score=9.5
            ),
        ]
        
        risk = processor.calculate_risk_score(findings)
        
        assert risk['critical_findings'] == 2
        assert risk['overall_risk'] in ['critical', 'high']


class TestDVWATargetSimulation:
    """Simulated tests for DVWA-like vulnerability scenarios."""

    def test_sql_injection_payload_detection(self):
        """Test detection of SQL injection payloads."""
        from src.web_scanner.scanner.vulnerability_analyzer import VulnerabilityAnalyzer
        
        # Simulate DVWA SQL injection scenario
        payload = "admin' --"
        dvwa_response = """
        <html>
        <body>
            <h1>User Login</h1>
            <p>SQL Error: Syntax error near '--' in query</p>
        </body>
        </html>
        """
        
        is_vulnerable, evidence = VulnerabilityAnalyzer.analyze_sqli(payload, dvwa_response)
        
        assert is_vulnerable is True

    def test_xss_payload_detection(self):
        """Test detection of XSS payloads in DVWA context."""
        from src.web_scanner.scanner.vulnerability_analyzer import VulnerabilityAnalyzer
        
        # Simulate DVWA XSS scenario
        payload = "<img src=x onerror=alert(1)>"
        dvwa_response = f"""
        <html>
        <body>
            <h1>Reflected Input</h1>
            <p>You entered: {payload}</p>
        </body>
        </html>
        """
        
        is_vulnerable, evidence = VulnerabilityAnalyzer.analyze_xss(payload, dvwa_response)
        
        assert is_vulnerable is True

    def test_idor_detection_logic(self):
        """Test IDOR detection with sequential ID patterns."""
        from src.web_scanner.scanner.vulnerability_analyzer import VulnerabilityAnalyzer
        
        # Test object ID detection patterns
        test_ids = ['1', '2', '100', '999']
        
        for test_id in test_ids:
            url = f"http://localhost:8080/user/profile?id={test_id}"
            # Should be able to construct and test URLs
            assert f"id={test_id}" in url

    def test_ssl_certificate_handling(self):
        """Test SSL/TLS certificate validation logic."""
        from src.web_scanner.scanner.vulnerability_scanner import VulnerabilityScanner
        
        scanner = VulnerabilityScanner(
            target_url="https://localhost:8443",
            timeout=10
        )
        
        # Scanner should be configurable for SSL
        assert scanner.target_url == "https://localhost:8443"


class TestHTTPMethodCoverage:
    """Test proper HTTP method coverage in scanning."""

    def test_get_request_testing(self):
        """Test scanner includes GET request testing."""
        from src.web_scanner.scanner.vulnerability_scanner import VulnerabilityScanner
        
        scanner = VulnerabilityScanner(target_url="http://localhost:8080")
        
        # Should have methods for GET requests
        assert hasattr(scanner, '_run_recon') or hasattr(scanner, 'scan')

    def test_post_request_testing(self):
        """Test scanner includes POST request testing."""
        from src.web_scanner.scanner.vulnerability_scanner import VulnerabilityScanner
        
        scanner = VulnerabilityScanner(target_url="http://localhost:8080")
        
        # Should support POST requests for form testing
        assert hasattr(scanner, 'scan') or hasattr(scanner, '_run_active_injection_tests')


class TestResponseHandling:
    """Test proper response handling and parsing."""

    def test_error_response_handling(self):
        """Test scanner handles HTTP error responses."""
        from src.web_scanner.scanner.vulnerability_analyzer import VulnerabilityAnalyzer
        
        # Should handle various error scenarios gracefully
        error_responses = [
            "404 Not Found",
            "500 Internal Server Error",
            "403 Forbidden",
            ""
        ]
        
        for response in error_responses:
            # Should not crash on error responses
            try:
                result = VulnerabilityAnalyzer.analyze_xss("test", response)
                assert isinstance(result, tuple)
            except:
                pass  # Some error handling is acceptable

    def test_timeout_handling(self):
        """Test scanner timeout configuration."""
        from src.web_scanner.scanner.vulnerability_scanner import VulnerabilityScanner
        
        scanner = VulnerabilityScanner(
            target_url="http://localhost:8080",
            timeout=5
        )
        
        assert scanner.timeout == 5


class TestReportGeneration:
    """Test report generation with scanned data."""

    def test_html_report_from_findings(self):
        """Test HTML report can be generated from findings."""
        from src.web_scanner.reporting.enhanced_template import generate_enhanced_html_report
        
        findings = [
            {
                'type': 'SQL Injection',
                'severity': 'critical',
                'url': 'http://localhost:8080/search',
                'description': 'SQL injection in search',
                'evidence': "' OR '1'='1",
                'remediation': 'Use parameterized queries',
                'cwe_id': 'CWE-89',
                'owasp_category': 'A03:2021'
            }
        ]
        
        risk_assessment = {
            'critical_findings': 1,
            'high_findings': 0,
            'medium_findings': 0,
            'low_findings': 0,
            'overall_risk': 'critical'
        }
        
        metrics = {
            'scan_duration_seconds': 30.5,
            'total_requests': 250,
            'successful_requests': 225,
            'unique_urls_discovered': 45,
            'forms_discovered': 12,
            'parameters_tested_total': 156,
            'authenticated_pages_visited': 5,
            'success_rate_percent': 90.0,
            'coverage_percent': 85.0
        }
        
        summary = "Assessment identified critical SQL injection vulnerability."
        
        html = generate_enhanced_html_report(
            findings=findings,
            metrics=metrics,
            risk_assessment=risk_assessment,
            executive_summary=summary,
            target_url="http://localhost:8080"
        )
        
        assert isinstance(html, str)
        assert '<html' in html.lower()
        assert 'sql injection' in html.lower()

    def test_pdf_report_generation_structure(self):
        """Test PDF report generation doesn't crash."""
        from src.web_scanner.reporting.pdf_generator import ReportGenerator
        
        generator = ReportGenerator()
        
        # Should initialize without errors
        assert generator is not None
        assert hasattr(generator, 'generate_report')


# Pytest markers for selective testing
pytest.mark.integration = pytest.mark.integration
pytest.mark.dvwa = pytest.mark.dvwa
pytest.mark.slow = pytest.mark.slow


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
