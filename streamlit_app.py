#!/usr/bin/env python3
"""
Professional Web Vulnerability Scanner - Streamlit Web Interface
Provides a user-friendly dashboard for security assessments
"""

import streamlit as st
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import sys
import traceback

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.web_scanner.scanner.vulnerability_scanner import VulnerabilityScanner as Scanner
from src.web_scanner.types import ScannerConfig
from src.web_scanner.core.metrics import ScanMetrics
from src.web_scanner.reporting.findings_processor import FindingsProcessor
from src.web_scanner.reporting.enhanced_template import generate_enhanced_html_report

# Configure page
st.set_page_config(
    page_title="Web Security Scanner",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
    .critical {
        color: #dc2626;
        font-weight: bold;
    }
    .high {
        color: #f97316;
        font-weight: bold;
    }
    .medium {
        color: #eab308;
        font-weight: bold;
    }
    .low {
        color: #3b82f6;
        font-weight: bold;
    }
    .success-box {
        background-color: #d1fae5;
        border-left: 4px solid #10b981;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #fee2e2;
        border-left: 4px solid #ef4444;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'scan_results' not in st.session_state:
        st.session_state.scan_results = None
    if 'scanning' not in st.session_state:
        st.session_state.scanning = False
    if 'scan_error' not in st.session_state:
        st.session_state.scan_error = None
    if 'scan_start_time' not in st.session_state:
        st.session_state.scan_start_time = None


@st.cache_resource
def get_logger():
    """Get or create logger."""
    logger = logging.getLogger("web_scanner")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def normalize_url(url: str) -> str:
    """Ensure URL has a scheme."""
    if not url.startswith(("http://", "https://")):
        return f"https://{url}"
    return url


def convert_confidence_score(confidence: Any) -> float:
    """Convert confidence score from various formats to float (0-1)."""
    if isinstance(confidence, float):
        return confidence
    elif isinstance(confidence, int):
        return float(confidence) / 100 if confidence > 1 else float(confidence)
    elif isinstance(confidence, str):
        # Map string values to floats - match scanner output
        confidence_map = {
            "high": 1.0,
            "medium": 0.65,
            "low": 0.35,
            "info": 0.15,
        }
        return confidence_map.get(confidence.lower(), 0.5)
    else:
        return 0.5  # default


def run_scan(config: ScannerConfig) -> Optional[Dict[str, Any]]:
    """Run the vulnerability scan synchronously."""
    try:
        scanner = Scanner(config)
        try:
            results = asyncio.run(scanner.scan())
        except RuntimeError as exc:
            # Streamlit may already have an event loop running
            if "event loop is running" in str(exc).lower():
                import nest_asyncio
                nest_asyncio.apply()
                loop = asyncio.get_event_loop()
                results = loop.run_until_complete(scanner.scan())
            else:
                raise
        return results
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        st.session_state.scan_error = error_msg
        st.error(f"Scan Error: {error_msg}")
        return None


def display_metrics_dashboard(results: Dict[str, Any]):
    """Display metrics dashboard with statistics."""
    st.subheader("📊 Scan Metrics")
    
    if 'metrics' in results:
        metrics_data = results['metrics']
        
        # Key metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Scan Duration",
                value=f"{metrics_data.get('scan_duration_seconds', 0):.2f}s"
            )
        
        with col2:
            success_rate = metrics_data.get('success_rate_percent', 0)
            st.metric(
                label="Success Rate",
                value=f"{success_rate:.1f}%"
            )
        
        with col3:
            urls = metrics_data.get('unique_urls_discovered', 0)
            st.metric(
                label="URLs Discovered",
                value=urls
            )
        
        with col4:
            total_findings = metrics_data.get('total_findings', 0)
            st.metric(
                label="Findings",
                value=total_findings
            )
        
        # Detailed metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Request Statistics**")
            request_data = {
                'Total Requests': metrics_data.get('total_requests', 0),
                'Successful': metrics_data.get('successful_requests', 0),
                'Failed': metrics_data.get('failed_requests', 0),
            }
            for key, value in request_data.items():
                st.text(f"• {key}: {value}")
        
        with col2:
            st.markdown("**Coverage Analysis**")
            coverage_data = {
                'Forms Discovered': metrics_data.get('forms_discovered', 0),
                'Parameters Tested': metrics_data.get('parameters_tested_total', 0),
                'Unique Parameters': metrics_data.get('unique_parameters_tested', 0),
                'Coverage Rate': f"{metrics_data.get('coverage_percent', 0):.1f}%",
            }
            for key, value in coverage_data.items():
                st.text(f"• {key}: {value}")


def display_findings_dashboard(results: Dict[str, Any]):
    """Display findings with risk visualization."""
    st.subheader("🎯 Findings Summary")
    
    findings = results.get('findings', [])
    metrics_data = results.get('metrics', {})
    
    if not findings:
        st.info("✓ No vulnerabilities found during this scan")
        return
    
    # Severity distribution
    col1, col2 = st.columns([2, 1])
    
    with col1:
        severity_counts = metrics_data.get('findings_by_severity', {})
        
        if severity_counts:
            # Create bar chart
            severities = []
            counts = []
            colors_map = {
                'critical': '#dc2626',
                'high': '#f97316',
                'medium': '#eab308',
                'low': '#3b82f6',
                'info': '#06b6d4'
            }
            
            for severity in ['critical', 'high', 'medium', 'low', 'info']:
                if severity in severity_counts:
                    count = severity_counts[severity]
                    if count > 0:
                        severities.append(severity.capitalize())
                        counts.append(count)
            
            if severities:
                fig = px.bar(
                    x=severities,
                    y=counts,
                    labels={'x': 'Severity', 'y': 'Count'},
                    color=severities,
                    color_discrete_map={s: colors_map.get(s.lower(), '#667eea') for s in severities}
                )
                fig.update_layout(showlegend=False, height=300)
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**Severity Breakdown**")
        severity_counts = metrics_data.get('findings_by_severity', {})
        for severity in ['critical', 'high', 'medium', 'low', 'info']:
            count = severity_counts.get(severity, 0)
            if count > 0:
                st.markdown(f"<span class='{severity}'>{severity.upper()}: {count}</span>", unsafe_allow_html=True)
    
    # Findings by type
    st.markdown("---")
    st.markdown("**Findings by Type**")
    
    type_counts = metrics_data.get('findings_by_type', {})
    if type_counts:
        fig = px.pie(
            values=list(type_counts.values()),
            names=list(type_counts.keys()),
            hole=0.3
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)


def display_detailed_findings(results: Dict[str, Any]):
    """Display detailed findings list."""
    st.subheader("📋 Detailed Findings")
    
    findings = results.get('findings', [])
    
    if not findings:
        st.info("No detailed findings available")
        return
    
    # Sort findings by severity
    severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
    sorted_findings = sorted(
        findings,
        key=lambda x: severity_order.get(x.get('severity', 'info'), 5)
    )
    
    for i, finding in enumerate(sorted_findings, 1):
        severity = finding.get('severity', 'info').upper()
        severity_class = finding.get('severity', 'info').lower()
        
        with st.expander(f"**{i}. {finding.get('type', 'Unknown')}** - {severity}"):
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                st.markdown(f"**Severity:** <span class='{severity_class}'>{severity}</span>", unsafe_allow_html=True)
                st.markdown(f"**URL:** `{finding.get('url', 'N/A')}`")
            
            with col2:
                if finding.get('affected_parameter'):
                    st.markdown(f"**Parameter:** `{finding['affected_parameter']}`")
                if finding.get('cwe_id'):
                    st.markdown(f"**CWE:** {finding['cwe_id']}")
            
            with col3:
                if finding.get('confidence_score'):
                    confidence = convert_confidence_score(finding['confidence_score'])
                    st.markdown(f"**Confidence:** {confidence:.0%}")
                if finding.get('owasp_category'):
                    st.markdown(f"**OWASP:** {finding['owasp_category']}")
            
            st.markdown("---")
            st.markdown("**Description:**")
            st.write(finding.get('description', 'N/A'))
            
            if finding.get('evidence'):
                st.markdown("**Evidence:**")
                st.code(finding.get('evidence', ''), language='html')
            
            if finding.get('remediation'):
                st.markdown("**Remediation:**")
                st.write(finding.get('remediation', 'N/A'))


def display_risk_assessment(results: Dict[str, Any]):
    """Display risk assessment and executive summary."""
    st.subheader(" Risk Assessment")
    
    metrics_data = results.get('metrics', {})
    findings = results.get('findings', [])
    
    # Calculate risk score
    processor = FindingsProcessor()
    try:
        enhanced_findings = [processor.enhance_finding(f) for f in findings]
        risk_assessment = processor.calculate_risk_score(enhanced_findings)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            risk_level = risk_assessment.get('overall_risk', 'Unknown')
            risk_colors = {
                'Minimal': '#10b981',
                'Low': '#3b82f6',
                'Medium': '#eab308',
                'High': '#f97316',
                'Critical': '#dc2626'
            }
            color = risk_colors.get(risk_level, '#667eea')
            st.markdown(f"<h2 style='color: {color};'>Risk Level</h2>", unsafe_allow_html=True)
            st.markdown(f"<h1 style='color: {color}; text-align: center;'>{risk_level}</h1>", unsafe_allow_html=True)
        
        with col2:
            risk_score = float(risk_assessment.get('risk_score', 0))
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=risk_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Risk Score"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 20], 'color': "#10b981"},
                        {'range': [20, 40], 'color': "#3b82f6"},
                        {'range': [40, 60], 'color': "#eab308"},
                        {'range': [60, 80], 'color': "#f97316"},
                        {'range': [80, 100], 'color': "#dc2626"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': risk_score
                    }
                }
            ))
            fig.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            st.markdown("**Exploitable Issues**")
            st.metric("Critical/High Severity", risk_assessment.get('exploitable_findings', 0))
            
            st.markdown("**Finding Counts**")
            st.text(f"Critical: {risk_assessment.get('critical_findings', 0)}")
            st.text(f"High: {risk_assessment.get('high_findings', 0)}")
            st.text(f"Medium: {risk_assessment.get('medium_findings', 0)}")
        
        # Executive Summary
        st.markdown("---")
        summary = processor.generate_executive_summary(enhanced_findings, metrics_data)
        st.markdown(summary)
        
    except Exception as e:
        st.error(f"Error calculating risk assessment: {str(e)}")


def main():
    """Main Streamlit application."""
    initialize_session_state()
    
    # Header
    st.markdown("""
        <div class="main-header">
            <h1> Web Security Scanner</h1>
            <p>Professional vulnerability assessment and security analysis tool</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.markdown("##  Scan Configuration")
        
        # Target URL
        target_url = st.text_input(
            label="Target URL",
            value="https://example.com",
            placeholder="https://example.com",
            help="The URL to scan for vulnerabilities (e.g., http://localhost:3000)"
        )
        
        # Scan options
        st.markdown("### Scanning Options")
        active_tests = st.checkbox(
            label="Enable Active Tests",
            value=False,
            help="Perform injection tests (XSS, SQLi, etc.) - requires authorization"
        )
        
        crawl_depth = st.slider(
            label="Crawl Depth",
            min_value=1,
            max_value=5,
            value=2,
            help="Maximum depth for link discovery"
        )
        
        timeout = st.number_input(
            label="Request Timeout (seconds)",
            min_value=5,
            max_value=60,
            value=10,
            help="Timeout for individual requests"
        )
        
        # Authentication
        st.markdown("### Authentication (Optional)")
        use_auth = st.checkbox(
            label="Enable Authenticated Scanning",
            value=False,
            help="Perform scan with user credentials"
        )
        
        auth_url = None
        auth_user = None
        auth_pass = None
        
        if use_auth:
            auth_url = st.text_input(
                label="Login URL",
                placeholder="/login",
                help="Authentication endpoint"
            )
            auth_user = st.text_input(
                label="Username",
                placeholder="admin",
                help="Authentication username"
            )
            auth_pass = st.text_input(
                label="Password",
                type="password",
                placeholder="password",
                help="Authentication password"
            )
        
        # Scan button
        st.markdown("---")
        if st.button(" Start Scan", use_container_width=True):
            if not target_url:
                st.error("Please enter a target URL")
            else:
                st.session_state.scanning = True
                st.session_state.scan_error = None
                st.session_state.scan_start_time = datetime.now()

                # Create scan configuration
                config = ScannerConfig(
                    target_url=normalize_url(target_url),
                    active_tests=active_tests,
                    crawl_depth=crawl_depth,
                    timeout=timeout,
                    verify_ssl=False,
                )

                # Add authentication if provided
                if use_auth and auth_url and auth_user and auth_pass:
                    config.auth_enabled = True
                    config.auth_url = auth_url
                    config.auth_user = auth_user
                    config.auth_pass = auth_pass

                with st.spinner(" Running scan, this may take a few moments..."):
                    try:
                        results = run_scan(config)
                        if results:
                            st.session_state.scan_results = results
                            st.success(" Scan complete. Results are ready.")
                        else:
                            st.error(f" Scan failed: {st.session_state.scan_error or 'Unknown error'}")
                    except Exception as e:
                        st.error(f" Error: {str(e)}")
                        st.error(traceback.format_exc())
                    finally:
                        st.session_state.scanning = False
    
    # Main content area
    if st.session_state.scan_results:
        results = st.session_state.scan_results
        
        # Create tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            " Metrics",
            " Risk Assessment",
            " Findings",
            " Details",
            " Full Report"
        ])
        
        with tab1:
            display_metrics_dashboard(results)
        
        with tab2:
            display_risk_assessment(results)
        
        with tab3:
            display_findings_dashboard(results)
        
        with tab4:
            display_detailed_findings(results)
        
        with tab5:
            st.markdown("### 📄 HTML Report")
            
            # Generate professional HTML report
            try:
                findings = results.get('findings', [])
                metrics_data = results.get('metrics', {})
                
                processor = FindingsProcessor()
                enhanced_findings = [processor.enhance_finding(f) for f in findings]
                risk_assessment = processor.calculate_risk_score(enhanced_findings)
                summary = processor.generate_executive_summary(enhanced_findings, metrics_data)
                
                html_report = generate_enhanced_html_report(
                    findings=findings,
                    metrics=metrics_data,
                    risk_assessment=risk_assessment,
                    executive_summary=summary,
                    target_url=results.get('target', 'Unknown'),
                    timestamp=datetime.now()
                )
                
                # Display HTML in iframe
                st.components.v1.html(html_report, height=1000, scrolling=True)
                
                # Download button
                st.download_button(
                    label=" Download Report (HTML)",
                    data=html_report,
                    file_name=f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html"
                )
                
                # JSON export
                json_data = json.dumps(results, indent=2, default=str)
                st.download_button(
                    label=" Download Report (JSON)",
                    data=json_data,
                    file_name=f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
                
            except Exception as e:
                st.error(f"Error generating report: {str(e)}")
    
    else:
        # Welcome message
        st.markdown("""
            ### Welcome to Web Security Scanner
            
            This professional vulnerability assessment tool helps you identify security issues in web applications.
            
            **Features:**
            -  Comprehensive reconnaissance scanning
            -  Active vulnerability testing (SQLi, XSS, etc.)
            -  Support for authenticated scanning
            -  Detailed metrics and analytics
            -  Risk assessment and scoring
            -  Professional HTML and JSON reports
            -  Intelligent URL and form discovery
            
            **Getting Started:**
            1. Enter your target URL in the sidebar
            2. Configure scan options (optional)
            3. Click "Start Scan" to begin
            4. View results in the tabs above
            
            **Important:** Always ensure you have authorization before scanning any system.
        """)
        
        # Example queries
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
                **Example Targets:**
                - OWASP Juice Shop: http://localhost:3000
                - DVWA: http://localhost:8080
                - Your own app: https://your-domain.com
            """)
        
        with col2:
            st.markdown("""
                **Security Notes:**
                - Use only on authorized systems
                - Active tests may cause temporary impact
                - Results show detected issues only
                - Consider false positives
            """)


if __name__ == "__main__":
    main()
