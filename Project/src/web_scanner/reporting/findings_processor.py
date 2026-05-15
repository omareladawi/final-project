"""Finding processor for improved vulnerability structuring and confidence scoring."""
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
import hashlib
import logging


@dataclass
class EnhancedFinding:
    """Improved finding structure with additional context."""
    
    # Core vulnerability info
    type: str
    severity: str
    url: str
    description: str
    evidence: str
    remediation: str
    
    # Enhanced metadata
    confidence_score: float = 0.8  # 0.0-1.0
    cvss_score: float = 0.0  # 0.0-10.0
    cwe_id: Optional[str] = None  # e.g., "CWE-79" for XSS
    owasp_category: Optional[str] = None  # e.g., "A03:2021 – Injection"
    
    # Contextual information
    affected_parameter: Optional[str] = None
    request_method: str = "GET"
    response_status: int = 200
    payload_used: Optional[str] = None
    
    # Request/Response snippets
    request_snippet: Optional[str] = None
    response_snippet: Optional[str] = None
    
    # Deduplication
    finding_hash: Optional[str] = None
    is_duplicate: bool = False
    duplicate_of: Optional[str] = None
    
    # Additional metadata
    tags: List[str] = None
    verified: bool = False
    
    logger = logging.getLogger(__name__)
    
    def __post_init__(self):
        """Initialize tags if None."""
        if self.tags is None:
            self.tags = []
        # Calculate hash for deduplication
        if not self.finding_hash:
            self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Generate a hash for finding deduplication."""
        content = f"{self.type}|{self.url}|{self.affected_parameter}|{self.description}"
        self.finding_hash = hashlib.md5(content.encode()).hexdigest()
        return self.finding_hash
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "type": self.type,
            "severity": self.severity,
            "url": self.url,
            "description": self.description,
            "evidence": self.evidence,
            "remediation": self.remediation,
            "confidence_score": self.confidence_score,
            "cvss_score": self.cvss_score,
            "cwe_id": self.cwe_id,
            "owasp_category": self.owasp_category,
            "affected_parameter": self.affected_parameter,
            "request_method": self.request_method,
            "response_status": self.response_status,
            "payload_used": self.payload_used,
            "request_snippet": self.request_snippet,
            "response_snippet": self.response_snippet,
            "tags": self.tags,
            "verified": self.verified,
        }


class FindingsProcessor:
    """Process and enhance vulnerability findings."""
    
    # CVSS v3.1 Scores
    CVSS_SCORES = {
        "SQL Injection": 9.8,
        "Login Form SQL Injection": 9.0,
        "Command Injection": 9.8,
        "Reflected XSS": 6.1,
        "Login Form XSS": 6.1,
        "Stored XSS": 8.8,
        "Server-Side Request Forgery (SSRF)": 8.6,
        "Open Redirect": 6.1,
        "Path Traversal": 7.5,
        "Potential IDOR": 7.5,
        "Expired SSL Certificate": 7.5,
        "Weak SSL Cipher": 7.5,
        "SSL Certificate Verification Failed": 7.4,
        "Insecure Protocol": 7.4,
        "Clickjacking Vulnerability": 6.5,
        "CSRF Protection": 6.5,
        "Missing Security Headers": 5.3,
        "Missing Security Header": 5.3,
        "Misconfigured Security Header": 4.3,
        "Weak Security Header": 4.3,
        "Information Disclosure": 5.3,
        "Version Disclosure": 4.0,
        "Directory Listing": 5.3,
        "Debug Code in Production": 3.1,
        "Hardcoded Credentials": 7.5,
        "Insecure Session Cookie": 6.5,
        "Database Error Exposure": 5.3,
        "Stack Trace Exposure": 5.3,
        "Weak HSTS Configuration": 4.3,
        "Weak Authentication": 6.5,
    }
    
    # CWE Mapping - expanded to cover all finding types
    CWE_MAPPING = {
        "SQL Injection": "CWE-89",
        "Login Form SQL Injection": "CWE-89",
        "Command Injection": "CWE-78",
        "Reflected XSS": "CWE-79",
        "Login Form XSS": "CWE-79",
        "Stored XSS": "CWE-79",
        "Path Traversal": "CWE-22",
        "Open Redirect": "CWE-601",
        "Potential IDOR": "CWE-639",
        "CSRF Protection": "CWE-352",
        "Server-Side Request Forgery (SSRF)": "CWE-918",
        "Insecure Protocol": "CWE-319",
        "Expired SSL Certificate": "CWE-298",
        "Weak SSL Cipher": "CWE-326",
        "SSL Certificate Verification Failed": "CWE-295",
        "Clickjacking Vulnerability": "CWE-1021",
        "Missing Security Headers": "CWE-693",
        "Missing Security Header": "CWE-693",
        "Misconfigured Security Header": "CWE-693",
        "Weak Security Header": "CWE-693",
        "Information Disclosure": "CWE-200",
        "Version Disclosure": "CWE-200",
        "Directory Listing": "CWE-548",
        "Debug Code in Production": "CWE-489",
        "Hardcoded Credentials": "CWE-798",
        "Insecure Session Cookie": "CWE-614",
        "Database Error Exposure": "CWE-209",
        "Stack Trace Exposure": "CWE-209",
        "Weak HSTS Configuration": "CWE-693",
        "Weak Authentication": "CWE-287",
    }
    
    # OWASP Top 10 2021 Mapping
    OWASP_MAPPING = {
        "SQL Injection": "A03:2021 – Injection",
        "Login Form SQL Injection": "A03:2021 – Injection",
        "Command Injection": "A03:2021 – Injection",
        "Reflected XSS": "A03:2021 – Injection",
        "Login Form XSS": "A03:2021 – Injection",
        "Stored XSS": "A03:2021 – Injection",
        "Path Traversal": "A03:2021 – Injection",
        "Server-Side Request Forgery (SSRF)": "A10:2021 – SSRF",
        "Open Redirect": "A01:2021 – Broken Access Control",
        "Potential IDOR": "A01:2021 – Broken Access Control",
        "CSRF Protection": "A01:2021 – Broken Access Control",
        "Insecure Protocol": "A02:2021 – Cryptographic Failures",
        "Expired SSL Certificate": "A02:2021 – Cryptographic Failures",
        "Weak SSL Cipher": "A02:2021 – Cryptographic Failures",
        "SSL Certificate Verification Failed": "A02:2021 – Cryptographic Failures",
        "Missing Security Headers": "A05:2021 – Security Misconfiguration",
        "Missing Security Header": "A05:2021 – Security Misconfiguration",
        "Misconfigured Security Header": "A05:2021 – Security Misconfiguration",
        "Weak Security Header": "A05:2021 – Security Misconfiguration",
        "Clickjacking Vulnerability": "A05:2021 – Security Misconfiguration",
        "Information Disclosure": "A05:2021 – Security Misconfiguration",
        "Version Disclosure": "A05:2021 – Security Misconfiguration",
        "Directory Listing": "A05:2021 – Security Misconfiguration",
        "Debug Code in Production": "A05:2021 – Security Misconfiguration",
        "Hardcoded Credentials": "A07:2021 – Authentication Failures",
        "Insecure Session Cookie": "A07:2021 – Authentication Failures",
        "Database Error Exposure": "A09:2021 – Security Logging and Monitoring Failures",
        "Stack Trace Exposure": "A09:2021 – Security Logging and Monitoring Failures",
        "Weak HSTS Configuration": "A05:2021 – Security Misconfiguration",
        "Weak Authentication": "A07:2021 – Authentication Failures",
    }
    
    REMEDIATION_TEMPLATES = {
        "Cross-site Scripting (XSS)": [
            "Implement context-aware output encoding for all user-controlled data",
            "Use Content Security Policy (CSP) headers to prevent inline script execution",
            "Validate and sanitize all user input on both client and server sides",
            "Use secure templating engines that auto-escape output by default",
        ],
        "SQL Injection": [
            "Use parameterized queries or prepared statements for all database access",
            "Implement input validation with strict type checking",
            "Apply the principle of least privilege to database accounts",
            "Use ORM frameworks that automatically escape user input",
        ],
        "Command Injection": [
            "Avoid executing shell commands with user-controlled input",
            "Use APIs that directly call functions instead of shell commands",
            "Implement strict input validation and whitelisting",
            "Run application with minimal required system privileges",
        ],
    }
    
    logger = logging.getLogger(__name__)
    
    def __init__(self):
        """Initialize the findings processor."""
        self.seen_hashes: Dict[str, str] = {}  # hash -> finding_type
        self.deduplication_count = 0
    
    def enhance_finding(self, finding: Dict[str, Any]) -> EnhancedFinding:
        """Enhance a basic finding with additional context."""
        finding_type = finding.get("type", "Unknown")
        
        enhanced = EnhancedFinding(
            type=finding_type,
            severity=finding.get("severity", "medium"),
            url=finding.get("url", ""),
            description=finding.get("description", ""),
            evidence=finding.get("evidence", ""),
            remediation=finding.get("remediation", ""),
            confidence_score=self._calculate_confidence(finding),
            cvss_score=self.CVSS_SCORES.get(finding_type, 0.0),
            affected_parameter=finding.get("affected_parameter"),
            request_method=finding.get("request_method", "GET"),
            response_status=finding.get("response_status", 200),
            payload_used=finding.get("payload_used"),
        )
        
        # Add CWE and OWASP mappings
        enhanced.cwe_id = self.CWE_MAPPING.get(finding_type)
        enhanced.owasp_category = self.OWASP_MAPPING.get(finding_type)
        
        # Enhance remediation with template
        if finding_type in self.REMEDIATION_TEMPLATES:
            enhanced.remediation = "\n• ".join(
                [enhanced.remediation] + self.REMEDIATION_TEMPLATES[finding_type]
            )
        
        return enhanced
    
    def _calculate_confidence(self, finding: Dict[str, Any]) -> float:
        """Calculate confidence score based on finding characteristics."""
        confidence = 0.5  # base
        
        # Severity-based adjustment
        severity = finding.get("severity", "").lower()
        severity_boost = {
            "critical": 0.4,
            "high": 0.3,
            "medium": 0.2,
            "low": 0.1,
            "info": 0.0,
        }
        confidence += severity_boost.get(severity, 0.1)
        
        # Evidence type adjustment
        evidence = finding.get("evidence", "").lower()
        if "confirmed" in evidence or "verified" in evidence:
            confidence += 0.1
        elif "detected" in evidence or "found" in evidence:
            confidence += 0.05
        
        # Type-based adjustments
        finding_type = finding.get("type", "").lower()
        if "injection" in finding_type:
            confidence = min(confidence + 0.05, 1.0)
        elif "security header" in finding_type:
            confidence = min(confidence + 0.1, 1.0)
        
        return min(confidence, 1.0)
    
    def deduplicate_findings(self, findings: List[EnhancedFinding]) -> List[EnhancedFinding]:
        """Remove duplicate findings while tracking deduplication."""
        unique_findings = []
        
        for finding in findings:
            if finding.finding_hash in self.seen_hashes:
                finding.is_duplicate = True
                finding.duplicate_of = self.seen_hashes[finding.finding_hash]
                self.deduplication_count += 1
                self.logger.debug(
                    f"Deduplicated finding: {finding.type} at {finding.url}"
                )
            else:
                self.seen_hashes[finding.finding_hash] = finding.type
                unique_findings.append(finding)
        
        return unique_findings
    
    def group_findings_by_type(self, findings: List[EnhancedFinding]) -> Dict[str, List[EnhancedFinding]]:
        """Group findings by vulnerability type."""
        grouped = {}
        for finding in findings:
            if finding.type not in grouped:
                grouped[finding.type] = []
            grouped[finding.type].append(finding)
        return grouped
    
    def group_findings_by_severity(self, findings: List[EnhancedFinding]) -> Dict[str, List[EnhancedFinding]]:
        """Group findings by severity level."""
        severity_order = ["critical", "high", "medium", "low", "info"]
        grouped = {severity: [] for severity in severity_order}
        
        for finding in findings:
            severity = finding.severity.lower()
            if severity in grouped:
                grouped[severity].append(finding)
        
        # Remove empty groups
        return {k: v for k, v in grouped.items() if v}
    
    def calculate_risk_score(self, findings: List[EnhancedFinding]) -> Dict[str, Any]:
        """Calculate overall risk metrics from findings."""
        if not findings:
            return {
                "overall_risk": "Minimal",
                "risk_score": 0,
                "critical_findings": 0,
                "exploitable_findings": 0,
            }
        
        critical_count = sum(1 for f in findings if f.severity.lower() == "critical")
        high_count = sum(1 for f in findings if f.severity.lower() == "high")
        medium_count = sum(1 for f in findings if f.severity.lower() == "medium")
        low_count = sum(1 for f in findings if f.severity.lower() == "low")
        
        # Simple risk scoring: 0-100
        risk_score = (
            (critical_count * 40) +
            (high_count * 20) +
            (medium_count * 10) +
            (low_count * 2)
        )
        risk_score = min(risk_score, 100)
        
        # Determine risk level
        if risk_score >= 80:
            risk_level = "Critical"
        elif risk_score >= 60:
            risk_level = "High"
        elif risk_score >= 40:
            risk_level = "Medium"
        elif risk_score >= 20:
            risk_level = "Low"
        else:
            risk_level = "Minimal"
        
        # Count exploitable findings (injection, authentication, etc.)
        exploitable_types = {
            "SQL Injection", "Command Injection", "Cross-site Scripting (XSS)",
            "Broken Authentication", "Server-Side Request Forgery (SSRF)"
        }
        exploitable_count = sum(
            1 for f in findings if f.type in exploitable_types
        )
        
        return {
            "overall_risk": risk_level,
            "risk_score": risk_score,
            "critical_findings": critical_count,
            "high_findings": high_count,
            "medium_findings": medium_count,
            "low_findings": low_count,
            "exploitable_findings": exploitable_count,
        }
    
    def generate_executive_summary(self, findings: List[EnhancedFinding], metrics: Dict) -> str:
        """Generate a professional executive summary narrative."""
        if not findings:
            return (
                "The security assessment completed without detecting any vulnerabilities. "
                "It is recommended to enable active testing mode and ensure the target application "
                "is fully accessible for a comprehensive evaluation."
            )

        critical = sum(1 for f in findings if f.severity.lower() == "critical")
        high = sum(1 for f in findings if f.severity.lower() == "high")
        medium = sum(1 for f in findings if f.severity.lower() == "medium")
        low = sum(1 for f in findings if f.severity.lower() == "low")
        total = len(findings)

        injection_types = [f for f in findings if any(
            kw in f.type.lower() for kw in ["injection", "xss", "traversal", "ssrf"]
        )]
        config_types = [f for f in findings if any(
            kw in f.type.lower() for kw in ["header", "ssl", "protocol", "cookie", "certificate"]
        )]

        risk_level = "critical" if critical > 0 else "high" if high > 0 else "medium" if medium > 0 else "low"

        summary = (
            f"The automated security assessment identified {total} security issue(s) across the target application, "
            f"representing an overall {risk_level} risk profile. "
        )

        if critical + high > 0:
            summary += (
                f"Of immediate concern are {critical + high} critical/high severity finding(s) "
                f"that require prompt remediation. "
            )

        if injection_types:
            unique_types = set(f.type for f in injection_types[:2])
            summary += (
                f"The assessment detected {len(injection_types)} injection-class vulnerability/vulnerabilities "
                f"(including {', '.join(unique_types)}), "
                f"which represent the most significant risk to the application. "
            )

        if config_types:
            summary += (
                f"Additionally, {len(config_types)} security misconfiguration(s) were identified "
                f"related to HTTP security headers and transport layer security. "
            )

        if medium + low > 0:
            summary += f"A further {medium + low} medium/low severity issue(s) were noted for future remediation. "

        summary += (
            "Immediate action is recommended for all critical and high severity findings. "
            "A follow-up assessment should be conducted after remediation to verify the issues have been resolved."
        )
        return summary
