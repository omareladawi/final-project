"""Comprehensive metrics collection for vulnerability scanning."""
from dataclasses import dataclass, field
from typing import Dict, List, Set
from datetime import datetime
import logging


@dataclass
class ScanMetrics:
    """Tracks scanning operation metrics for reporting."""
    
    # Timing metrics
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime = None
    
    # URL discovery metrics
    unique_urls_discovered: Set[str] = field(default_factory=set)
    duplicate_urls_removed: int = 0
    static_assets_skipped: int = 0
    
    # Scanning activity metrics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    
    # Page analysis metrics
    authenticated_pages_visited: int = 0
    unauthenticated_pages_visited: int = 0
    
    # Form and parameter discovery
    forms_discovered: int = 0
    parameters_tested: int = 0
    unique_parameters: Set[str] = field(default_factory=set)
    
    # Payload metrics
    injection_payloads_sent: int = 0
    active_tests_performed: int = 0
    
    # Finding metrics
    findings_total: int = 0
    findings_by_severity: Dict[str, int] = field(
        default_factory=lambda: {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0,
        }
    )
    findings_by_type: Dict[str, int] = field(default_factory=dict)
    
    # Deduplication metrics
    findings_deduplicated: int = 0
    false_positives_filtered: int = 0
    
    # Session metrics
    session_creation_attempts: int = 0
    session_validation_passed: int = 0
    session_validation_failed: int = 0
    
    logger = logging.getLogger(__name__)
    
    @property
    def duration_seconds(self) -> float:
        """Calculate total scan duration."""
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()
    
    @property
    def average_response_time(self) -> float:
        """Calculate average response time per request."""
        if self.total_requests == 0:
            return 0
        return self.duration_seconds / self.total_requests
    
    @property
    def success_rate(self) -> float:
        """Calculate request success rate."""
        if self.total_requests == 0:
            return 0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def coverage_rate(self) -> float:
        """Calculate coverage of authenticated content."""
        total = self.authenticated_pages_visited + self.unauthenticated_pages_visited
        if total == 0:
            return 0
        return (self.authenticated_pages_visited / total) * 100
    
    def mark_url_discovered(self, url: str) -> bool:
        """Register a discovered URL, return True if new."""
        if url in self.unique_urls_discovered:
            self.duplicate_urls_removed += 1
            return False
        self.unique_urls_discovered.add(url)
        return True
    
    def record_request(self, success: bool = True) -> None:
        """Record a request attempt."""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
    
    def record_finding(self, severity: str, finding_type: str) -> None:
        """Record a vulnerability finding."""
        self.findings_total += 1
        severity_key = severity.lower()
        if severity_key in self.findings_by_severity:
            self.findings_by_severity[severity_key] += 1
        self.findings_by_type[finding_type] = self.findings_by_type.get(finding_type, 0) + 1
    
    def record_parameter(self, param_name: str) -> None:
        """Record a tested parameter."""
        self.parameters_tested += 1
        self.unique_parameters.add(param_name)
    
    def get_summary(self) -> Dict:
        """Generate a summary of all metrics."""
        return {
            "scan_duration_seconds": round(self.duration_seconds, 2),
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate_percent": round(self.success_rate, 1),
            "unique_urls_discovered": len(self.unique_urls_discovered),
            "duplicate_urls_removed": self.duplicate_urls_removed,
            "authenticated_pages_visited": self.authenticated_pages_visited,
            "unauthenticated_pages_visited": self.unauthenticated_pages_visited,
            "coverage_percent": round(self.coverage_rate, 1),
            "forms_discovered": self.forms_discovered,
            "unique_parameters_tested": len(self.unique_parameters),
            "parameters_tested_total": self.parameters_tested,
            "injection_payloads_sent": self.injection_payloads_sent,
            "active_tests_performed": self.active_tests_performed,
            "findings_total": self.findings_total,
            "findings_by_severity": dict(self.findings_by_severity),
            "findings_by_type": dict(self.findings_by_type),
            "findings_deduplicated": self.findings_deduplicated,
            "false_positives_filtered": self.false_positives_filtered,
            "session_attempts": self.session_creation_attempts,
            "session_validation_success_rate": (
                round((self.session_validation_passed / self.session_creation_attempts * 100), 1)
                if self.session_creation_attempts > 0 else 0
            ),
        }
