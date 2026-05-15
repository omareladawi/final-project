"""Enhanced HTML report template generator with executive summary and metrics."""
from datetime import datetime
from typing import Dict, List, Any, Optional
import json


def generate_enhanced_html_report(
    findings: List[Dict],
    metrics: Dict[str, Any],
    risk_assessment: Dict[str, Any],
    executive_summary: str,
    target_url: str,
    timestamp: Optional[datetime] = None,
) -> str:
    """Generate professional HTML report with all enhancements."""
    
    if timestamp is None:
        timestamp = datetime.now()
    
    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    
    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web Security Assessment Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        :root {{
            --critical: #dc2626;
            --high: #f97316;
            --medium: #eab308;
            --low: #3b82f6;
            --info: #06b6d4;
            --bg: #f9fafb;
            --card-bg: #ffffff;
            --text: #1f2937;
            --border: #e5e7eb;
            --success: #16a34a;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            padding: 2rem;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        /* Report Header */
        .report-header {{
            background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
            color: white;
            padding: 3rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}
        
        .report-header h1 {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }}
        
        .report-meta {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-top: 1.5rem;
            font-size: 0.9rem;
        }}
        
        .meta-item {{
            opacity: 0.9;
        }}
        
        .meta-label {{
            opacity: 0.7;
            display: block;
            margin-bottom: 0.25rem;
        }}
        
        /* Executive Summary */
        .executive-summary {{
            background: var(--card-bg);
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            border-left: 5px solid var(--high);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }}
        
        .executive-summary h2 {{
            font-size: 1.5rem;
            margin-bottom: 1rem;
            color: var(--text);
        }}
        
        .executive-summary p {{
            margin-bottom: 1rem;
            line-height: 1.8;
        }}
        
        /* Risk Dashboard */
        .risk-dashboard {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .risk-card {{
            background: var(--card-bg);
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            border-top: 4px solid var(--border);
        }}
        
        .risk-card.critical {{ border-top-color: var(--critical); }}
        .risk-card.high {{ border-top-color: var(--high); }}
        .risk-card.medium {{ border-top-color: var(--medium); }}
        .risk-card.low {{ border-top-color: var(--low); }}
        
        .risk-number {{
            font-size: 2.5rem;
            font-weight: bold;
            margin: 0.5rem 0;
        }}
        
        .risk-card.critical .risk-number {{ color: var(--critical); }}
        .risk-card.high .risk-number {{ color: var(--high); }}
        .risk-card.medium .risk-number {{ color: var(--medium); }}
        .risk-card.low .risk-number {{ color: var(--low); }}
        
        .risk-label {{
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #6b7280;
        }}
        
        /* Metrics Grid */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
            background: var(--card-bg);
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }}
        
        .metric {{
            padding: 1rem;
            background: var(--bg);
            border-radius: 8px;
            border-left: 4px solid var(--info);
        }}
        
        .metric-value {{
            font-size: 1.75rem;
            font-weight: bold;
            color: var(--info);
        }}
        
        .metric-label {{
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #6b7280;
            margin-top: 0.5rem;
        }}
        
        /* Findings Section */
        .findings-section {{
            margin-bottom: 2rem;
        }}
        
        .findings-section h2 {{
            font-size: 1.75rem;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid var(--border);
        }}
        
        .finding-card {{
            background: var(--card-bg);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border-radius: 12px;
            border-left: 5px solid var(--border);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }}
        
        .finding-card.critical {{ border-left-color: var(--critical); }}
        .finding-card.high {{ border-left-color: var(--high); }}
        .finding-card.medium {{ border-left-color: var(--medium); }}
        .finding-card.low {{ border-left-color: var(--low); }}
        .finding-card.info {{ border-left-color: var(--info); }}
        
        .finding-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 1rem;
            gap: 1rem;
        }}
        
        .finding-title {{
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--text);
        }}
        
        .severity-badge {{
            display: inline-block;
            padding: 0.35rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            white-space: nowrap;
        }}
        
        .severity-badge.critical {{
            background: #fee2e2;
            color: var(--critical);
        }}
        
        .severity-badge.high {{
            background: #fef3c7;
            color: var(--high);
        }}
        
        .severity-badge.medium {{
            background: #fef3c7;
            color: #b45309;
        }}
        
        .severity-badge.low {{
            background: #dbeafe;
            color: var(--low);
        }}
        
        .severity-badge.info {{
            background: #cffafe;
            color: var(--info);
        }}
        
        .finding-details {{
            margin-top: 1rem;
        }}
        
        .finding-detail-row {{
            display: flex;
            margin-bottom: 0.75rem;
            font-size: 0.9rem;
        }}
        
        .detail-label {{
            font-weight: 600;
            min-width: 120px;
            color: #6b7280;
        }}
        
        .detail-value {{
            flex: 1;
            color: var(--text);
            word-break: break-word;
        }}
        
        .evidence-block {{
            background: var(--bg);
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            border-left: 3px solid var(--info);
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 0.85rem;
            overflow-x: auto;
        }}
        
        .remediation-block {{
            background: #f0fdf4;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            border-left: 3px solid var(--success);
        }}
        
        .remediation-block h4 {{
            color: var(--success);
            margin-bottom: 0.5rem;
        }}
        
        .cwe-owasp {{
            font-size: 0.85rem;
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border);
        }}
        
        .cwe-owasp span {{
            display: inline-block;
            background: var(--bg);
            padding: 0.35rem 0.65rem;
            border-radius: 6px;
            margin-right: 0.5rem;
            margin-bottom: 0.5rem;
        }}
        
        /* Risk Matrix */
        .risk-matrix-section {{
            background: var(--card-bg);
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }}
        
        .risk-matrix-section h2 {{
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid var(--border);
        }}
        
        .matrix-container {{
            overflow-x: auto;
            margin: 1rem 0;
        }}
        
        .risk-matrix {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }}
        
        .risk-matrix th, .risk-matrix td {{
            border: 1px solid var(--border);
            padding: 0.75rem;
            text-align: center;
        }}
        
        .risk-matrix th {{
            background: var(--bg);
            font-weight: 600;
            color: var(--text);
        }}
        
        .risk-matrix-cell {{
            min-height: 80px;
            position: relative;
            vertical-align: middle;
        }}
        
        .risk-matrix-cell.risk-green {{
            background: #dcfce7;
        }}
        
        .risk-matrix-cell.risk-yellow {{
            background: #fef3c7;
        }}
        
        .risk-matrix-cell.risk-orange {{
            background: #fed7aa;
        }}
        
        .risk-matrix-cell.risk-red {{
            background: #fecaca;
        }}
        
        .risk-badge {{
            display: inline-block;
            background: white;
            border: 2px solid var(--border);
            border-radius: 50%;
            width: 28px;
            height: 28px;
            line-height: 24px;
            font-weight: bold;
            font-size: 0.8rem;
            color: var(--text);
            cursor: pointer;
            margin: 2px;
        }}
        
        .risk-badge:hover {{
            transform: scale(1.1);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        }}
        
        .matrix-legend {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-top: 1.5rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border);
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}
        
        .legend-color {{
            width: 24px;
            height: 24px;
            border-radius: 4px;
            border: 1px solid var(--border);
        }}
        
        /* Remediation Roadmap */
        .roadmap-tier {{
            margin-bottom: 2rem;
            padding: 1.5rem;
            background: var(--bg);
            border-radius: 12px;
            border-left: 5px solid var(--border);
        }}
        
        .roadmap-tier.immediate {{
            border-left-color: var(--critical);
            background: #fee2e2;
        }}
        
        .roadmap-tier.short-term {{
            border-left-color: var(--high);
            background: #fef3c7;
        }}
        
        .roadmap-tier.long-term {{
            border-left-color: var(--low);
            background: #dbeafe;
        }}
        
        .roadmap-tier h3 {{
            margin-bottom: 1rem;
            color: var(--text);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .roadmap-tier.immediate h3 {{
            color: var(--critical);
        }}
        
        .roadmap-tier.short-term h3 {{
            color: var(--high);
        }}
        
        .roadmap-tier.long-term h3 {{
            color: var(--low);
        }}
        
        .roadmap-list {{
            list-style: none;
        }}
        
        .roadmap-list li {{
            padding: 0.75rem 0;
            padding-left: 1.5rem;
            position: relative;
            border-bottom: 1px solid rgba(0, 0, 0, 0.1);
        }}
        
        .roadmap-list li:last-child {{
            border-bottom: none;
        }}
        
        .roadmap-list li::before {{
            content: "";
            position: absolute;
            left: 0;
            top: 1rem;
            width: 8px;
            height: 8px;
            background: var(--text);
            border-radius: 50%;
        }}
        
        .roadmap-item-title {{
            font-weight: 600;
            color: var(--text);
        }}
        
        .roadmap-item-meta {{
            font-size: 0.85rem;
            color: #6b7280;
            margin-top: 0.25rem;
        }}
        
        /* Footer */
        .report-footer {{
            text-align: center;
            padding: 2rem;
            color: #6b7280;
            font-size: 0.875rem;
            border-top: 1px solid var(--border);
            margin-top: 3rem;
        }}
        
        /* Utility classes */
        .text-muted {{
            color: #6b7280;
        }}
        
        .mt-2 {{ margin-top: 1rem; }}
        .mb-2 {{ margin-bottom: 1rem; }}
        .p-2 {{ padding: 1rem; }}
        
        @media (max-width: 768px) {{
            body {{ padding: 1rem; }}
            .report-header {{ padding: 2rem 1.5rem; }}
            .report-header h1 {{ font-size: 1.75rem; }}
            .finding-header {{ flex-direction: column; }}
            .severity-badge {{ align-self: flex-start; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="report-header">
            <h1>🔒 Web Security Assessment Report</h1>
            <p style="opacity: 0.9; margin-top: 0.5rem;">Professional Security Vulnerability Scan Results</p>
            <div class="report-meta">
                <div class="meta-item">
                    <span class="meta-label">TARGET</span>
                    <strong>{target_url}</strong>
                </div>
                <div class="meta-item">
                    <span class="meta-label">ASSESSMENT DATE</span>
                    <strong>{timestamp_str}</strong>
                </div>
                <div class="meta-item">
                    <span class="meta-label">SCAN DURATION</span>
                    <strong>{metrics.get('scan_duration_seconds', 0):.1f} seconds</strong>
                </div>
                <div class="meta-item">
                    <span class="meta-label">TOTAL FINDINGS</span>
                    <strong>{len(findings)} issue(s)</strong>
                </div>
            </div>
        </div>
        
        <!-- Executive Summary -->
        <div class="executive-summary">
            <h2>📋 Executive Summary</h2>
            <div style="white-space: pre-wrap; font-family: 'Segoe UI', sans-serif; line-height: 1.8;">
{executive_summary}
            </div>
        </div>
        
        <!-- Risk Dashboard -->
        <div style="margin-bottom: 2rem;">
            <h2 style="font-size: 1.5rem; margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 2px solid var(--border);">
                📊 Risk Assessment Dashboard
            </h2>
            <div class="risk-dashboard">
                <div class="risk-card critical">
                    <div class="risk-label">Critical</div>
                    <div class="risk-number">{risk_assessment.get('critical_findings', 0)}</div>
                    <div class="risk-label">Findings</div>
                </div>
                <div class="risk-card high">
                    <div class="risk-label">High</div>
                    <div class="risk-number">{risk_assessment.get('high_findings', 0)}</div>
                    <div class="risk-label">Findings</div>
                </div>
                <div class="risk-card medium">
                    <div class="risk-label">Medium</div>
                    <div class="risk-number">{risk_assessment.get('medium_findings', 0)}</div>
                    <div class="risk-label">Findings</div>
                </div>
                <div class="risk-card low">
                    <div class="risk-label">Low</div>
                    <div class="risk-number">{risk_assessment.get('low_findings', 0)}</div>
                    <div class="risk-label">Findings</div>
                </div>
                <div class="risk-card" style="border-top-color: var(--success); background: #f0fdf4;">
                    <div class="risk-label" style="color: var(--success);">Overall Risk</div>
                    <div style="font-size: 2.5rem; font-weight: bold; color: var(--success); margin: 0.5rem 0;">
                        {risk_assessment.get('overall_risk', 'Unknown')}
                    </div>
                    <div class="risk-label">Risk Level</div>
                </div>
            </div>
        </div>
        
        <!-- Scan Metrics -->
        <div class="metrics-grid">
            <div class="metric">
                <div class="metric-value">{metrics.get('unique_urls_discovered', 0)}</div>
                <div class="metric-label">URLs Discovered</div>
            </div>
            <div class="metric">
                <div class="metric-value">{metrics.get('total_requests', 0)}</div>
                <div class="metric-label">Requests Performed</div>
            </div>
            <div class="metric">
                <div class="metric-value">{metrics.get('forms_discovered', 0)}</div>
                <div class="metric-label">Forms Discovered</div>
            </div>
            <div class="metric">
                <div class="metric-value">{metrics.get('parameters_tested_total', 0)}</div>
                <div class="metric-label">Parameters Tested</div>
            </div>
            <div class="metric">
                <div class="metric-value">{metrics.get('authenticated_pages_visited', 0)}</div>
                <div class="metric-label">Authenticated Pages</div>
            </div>
            <div class="metric">
                <div class="metric-value">{metrics.get('success_rate_percent', 0):.1f}%</div>
                <div class="metric-label">Success Rate</div>
            </div>
        </div>
        
        <!-- Risk Matrix -->
        <div class="risk-matrix-section">
            <h2>⚠️ Risk Matrix (Likelihood × Impact)</h2>
            {_generate_risk_matrix_html(findings)}
        </div>
        
        <!-- Remediation Roadmap -->
        <div class="risk-matrix-section">
            <h2>🛠️ Remediation Roadmap</h2>
            {_generate_remediation_roadmap_html(findings)}
        </div>
        
        <!-- Detailed Findings -->
        <div class="findings-section">
            <h2>🔍 Detailed Findings</h2>
            
            {_generate_findings_html(findings)}
        </div>
        
        <!-- Footer -->
        <div class="report-footer">
            <p>This security assessment report was generated by Web Application Security Scanner</p>
            <p style="margin-top: 1rem; opacity: 0.7;">
                For questions or concerns regarding this assessment, please contact your security administrator.
            </p>
        </div>
    </div>
</body>
</html>
"""
    return html


def _generate_risk_matrix_html(findings: List[Dict]) -> str:
    """Generate a 5x5 risk matrix showing likelihood vs impact."""
    
    # Define axes
    likelihood_levels = ["Very Low", "Low", "Medium", "High", "Very High"]
    impact_levels = ["Negligible", "Minor", "Moderate", "Major", "Critical"]
    
    # Map severity to impact (0-4)
    severity_to_impact = {
        "info": 0,
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4,
    }
    
    # Map confidence_score to likelihood (0-4)
    def score_to_likelihood(score):
        # Convert string scores to numeric values
        if isinstance(score, str):
            score_map = {'high': 0.9, 'medium': 0.6, 'low': 0.3}
            score = score_map.get(score.lower(), 0.5)
        
        # Ensure score is numeric
        try:
            score = float(score) if score is not None else 0.5
        except (ValueError, TypeError):
            score = 0.5
        
        if score < 0.2:
            return 0
        elif score < 0.4:
            return 1
        elif score < 0.6:
            return 2
        elif score < 0.8:
            return 3
        else:
            return 4
    
    # Risk color mapping: risk_score = likelihood + impact
    def get_risk_color(risk_score):
        if risk_score <= 4:
            return "risk-green"
        elif risk_score <= 9:
            return "risk-yellow"
        elif risk_score <= 14:
            return "risk-orange"
        else:
            return "risk-red"
    
    # Initialize 5x5 matrix with empty lists
    matrix = [[[] for _ in range(5)] for _ in range(5)]
    
    # Plot findings on matrix
    for idx, finding in enumerate(findings):
        severity = finding.get('severity', 'info').lower()
        confidence = finding.get('confidence_score', 0.5)
        
        impact = severity_to_impact.get(severity, 0)
        likelihood = score_to_likelihood(confidence)
        
        matrix[likelihood][impact].append({
            'type': finding.get('type', 'Unknown'),
            'severity': severity,
            'index': idx + 1
        })
    
    # Generate HTML
    html = '<div class="matrix-container"><table class="risk-matrix"><tr><th>Likelihood ↓ / Impact →</th>'
    
    # Header row (impact levels)
    for impact_label in impact_levels:
        html += f'<th>{impact_label}</th>'
    html += '</tr>'
    
    # Data rows
    for likelihood_idx, likelihood_label in enumerate(likelihood_levels):
        html += f'<tr><th>{likelihood_label}</th>'
        
        for impact_idx in range(5):
            risk_score = likelihood_idx + impact_idx
            cell_class = get_risk_color(risk_score)
            findings_in_cell = matrix[likelihood_idx][impact_idx]
            
            html += f'<td class="risk-matrix-cell {cell_class}">'
            
            # Add finding badges
            for finding_info in findings_in_cell:
                html += f'<span class="risk-badge" title="{finding_info["type"]} ({finding_info["severity"].upper()})">{finding_info["index"]}</span>'
            
            html += '</td>'
        
        html += '</tr>'
    
    html += '</table></div>'
    
    # Add legend
    html += '''<div class="matrix-legend">
        <div class="legend-item">
            <div class="legend-color" style="background: #dcfce7;"></div>
            <span><strong>Low Risk</strong> (score ≤ 4)</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #fef3c7;"></div>
            <span><strong>Medium Risk</strong> (score 5–9)</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #fed7aa;"></div>
            <span><strong>High Risk</strong> (score 10–14)</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #fecaca;"></div>
            <span><strong>Critical Risk</strong> (score 15–25)</span>
        </div>
    </div>'''
    
    # Add explanation
    html += f'''<p style="margin-top: 1.5rem; font-size: 0.9rem; color: #6b7280; padding: 1rem; background: var(--bg); border-radius: 8px; border-left: 3px solid var(--info);">
        <strong>Note:</strong> Each numbered badge represents a finding plotted on the risk matrix.
        The position indicates the finding's likelihood (vertical) and impact (horizontal).
        Total of {len(findings)} finding(s) plotted. Click on any badge to view details in the findings section below.
    </p>'''
    
    return html


def _generate_remediation_roadmap_html(findings: List[Dict]) -> str:
    """Generate a prioritized remediation roadmap grouped by timeframe."""
    
    # Categorize findings by severity
    immediate = []  # Critical/High - 24-48 hours
    short_term = []  # Medium - 30 days
    long_term = []  # Low/Info - next cycle
    
    for finding in findings:
        severity = finding.get('severity', 'info').lower()
        cvss_score = finding.get('cvss_score', 0.0)
        
        # Ensure cvss_score is a float
        try:
            cvss_score = float(cvss_score) if cvss_score is not None else 0.0
        except (ValueError, TypeError):
            cvss_score = 0.0
        
        if severity in ['critical', 'high']:
            immediate.append((finding, cvss_score))
        elif severity == 'medium':
            short_term.append((finding, cvss_score))
        else:
            long_term.append((finding, cvss_score))
    
    # Sort by CVSS score (descending)
    immediate.sort(key=lambda x: x[1], reverse=True)
    short_term.sort(key=lambda x: x[1], reverse=True)
    long_term.sort(key=lambda x: x[1], reverse=True)
    
    html = ''
    
    # Immediate tier
    if immediate:
        html += '''
        <div class="roadmap-tier immediate">
            <h3>🚨 Immediate Priority (24–48 Hours)</h3>
            <p style="color: #dc2626; font-weight: 500; margin-bottom: 1rem;">
                Critical and high-severity findings that require immediate remediation.
            </p>
            <ol class="roadmap-list" style="list-style: decimal; padding-left: 1.5rem;">
        '''
        
        for idx, (finding, cvss_score) in enumerate(immediate, 1):
            finding_type = finding.get('type', 'Unknown')
            severity = finding.get('severity', 'Unknown').upper()
            url = finding.get('url', 'N/A')
            html += f'''
                <li style="padding-left: 0; border-bottom: 1px solid rgba(0, 0, 0, 0.1);">
                    <div class="roadmap-item-title">{idx}. {finding_type} ({severity})</div>
                    <div class="roadmap-item-meta">CVSS Score: {cvss_score:.1f} | URL: {url}</div>
                </li>
            '''
        
        html += '</ol></div>'
    
    # Short-term tier
    if short_term:
        html += '''
        <div class="roadmap-tier short-term">
            <h3>⚠️ Short-Term Priority (30 Days)</h3>
            <p style="color: #f97316; font-weight: 500; margin-bottom: 1rem;">
                Medium-severity findings that should be resolved within the current development cycle.
            </p>
            <ol class="roadmap-list" style="list-style: decimal; padding-left: 1.5rem;">
        '''
        
        for idx, (finding, cvss_score) in enumerate(short_term, 1):
            finding_type = finding.get('type', 'Unknown')
            severity = finding.get('severity', 'Unknown').upper()
            url = finding.get('url', 'N/A')
            html += f'''
                <li style="padding-left: 0; border-bottom: 1px solid rgba(0, 0, 0, 0.1);">
                    <div class="roadmap-item-title">{idx}. {finding_type} ({severity})</div>
                    <div class="roadmap-item-meta">CVSS Score: {cvss_score:.1f} | URL: {url}</div>
                </li>
            '''
        
        html += '</ol></div>'
    
    # Long-term tier
    if long_term:
        html += '''
        <div class="roadmap-tier long-term">
            <h3>📋 Long-Term Priority (Next Cycle)</h3>
            <p style="color: #3b82f6; font-weight: 500; margin-bottom: 1rem;">
                Low and informational findings to be addressed in future assessments or hardening cycles.
            </p>
            <ol class="roadmap-list" style="list-style: decimal; padding-left: 1.5rem;">
        '''
        
        for idx, (finding, cvss_score) in enumerate(long_term, 1):
            finding_type = finding.get('type', 'Unknown')
            severity = finding.get('severity', 'Unknown').upper()
            url = finding.get('url', 'N/A')
            html += f'''
                <li style="padding-left: 0; border-bottom: 1px solid rgba(0, 0, 0, 0.1);">
                    <div class="roadmap-item-title">{idx}. {finding_type} ({severity})</div>
                    <div class="roadmap-item-meta">CVSS Score: {cvss_score:.1f} | URL: {url}</div>
                </li>
            '''
        
        html += '</ol></div>'
    
    if not immediate and not short_term and not long_term:
        html += '''
        <div style="text-align: center; padding: 2rem; background: var(--bg); border-radius: 8px; color: var(--success);">
            <p>✓ No remediation items needed. Target passed all security assessments.</p>
        </div>
        '''
    
    return html


def _generate_findings_html(findings: List[Dict]) -> str:
    """Generate HTML for individual findings."""
    if not findings:
        return """
            <div style="text-align: center; padding: 2rem; background: #f0fdf4; border-radius: 12px; color: var(--success);">
                <h3>✓ No Security Issues Found</h3>
                <p>The target passed all security assessments.</p>
            </div>
        """
    
    html = ""
    for finding in findings:
        severity = finding.get('severity', 'info').lower()
        cwe_id = finding.get('cwe_id')
        owasp_cat = finding.get('owasp_category')
        
        html += f"""
        <div class="finding-card {severity}">
            <div class="finding-header">
                <div class="finding-title">{finding.get('type', 'Unknown Finding')}</div>
                <span class="severity-badge {severity}">{severity}</span>
            </div>
            
            <div class="finding-details">
                <div class="finding-detail-row">
                    <span class="detail-label">URL:</span>
                    <span class="detail-value">{finding.get('url', 'N/A')}</span>
                </div>
                <div class="finding-detail-row">
                    <span class="detail-label">Description:</span>
                </div>
                <p style="margin-left: 120px; margin-bottom: 1rem; color: var(--text);">
                    {finding.get('description', 'N/A')}
                </p>
        """
        
        if finding.get('affected_parameter'):
            html += f"""
                <div class="finding-detail-row">
                    <span class="detail-label">Parameter:</span>
                    <span class="detail-value">{finding.get('affected_parameter')}</span>
                </div>
            """
        
        if finding.get('evidence'):
            html += f"""
                <div class="evidence-block">
                    <strong>Evidence:</strong><br>
                    {finding.get('evidence')}
                </div>
            """
        
        if finding.get('remediation'):
            html += f"""
                <div class="remediation-block">
                    <h4>💡 Remediation</h4>
                    <div style="white-space: pre-wrap; font-family: sans-serif; font-size: 0.9rem;">
                        {finding.get('remediation')}
                    </div>
                </div>
            """
        
        if cwe_id or owasp_cat:
            html += '<div class="cwe-owasp">'
            if cwe_id:
                html += f'<span><strong>CWE:</strong> {cwe_id}</span>'
            if owasp_cat:
                html += f'<span><strong>OWASP:</strong> {owasp_cat}</span>'
            html += '</div>'
        
        html += """
            </div>
        </div>
        """
    
    return html
