from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, KeepTogether
from reportlab.platypus.flowables import HRFlowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
from typing import Dict, List
from pathlib import Path
import os

class ReportGenerator:
    def __init__(self):
        # Ensure we're in the project root directory
        self.project_root = Path(__file__).parent.parent.parent.parent
        os.chdir(str(self.project_root))
        
        # Initialize colors first
        self.primary_color = colors.HexColor('#0047AB')  # Enterprise blue
        self.secondary_color = colors.HexColor('#2F4F4F')
        self.accent_color = colors.HexColor('#16A34A')  # Success green
        
        # Set logo path relative to project root
        self.company_logo = self.project_root / "assets" / "logo.png"
        
        # Use system fonts by default
        self.base_font = 'Helvetica'
        self.bold_font = 'Helvetica-Bold'
        
        # Try to register custom fonts, but don't fail if unavailable
        self._register_fonts()
        
        # Initialize styles with simplified attributes
        self.styles = self._create_styles()
        
        # Update existing Heading4 style instead of adding new one
        self.styles['Heading4'].fontName = self.bold_font
        self.styles['Heading4'].fontSize = 12
        self.styles['Heading4'].textColor = self.primary_color
        self.styles['Heading4'].spaceBefore = 12
        self.styles['Heading4'].spaceAfter = 6
        
        # Add simplified custom styles
        self.styles.add(ParagraphStyle(
            'Evidence',
            parent=self.styles['Normal'],
            fontName='Courier',
            fontSize=9,
            textColor=colors.HexColor('#334155'),
            backColor=colors.HexColor('#f8fafc'),
            spaceBefore=6,
            spaceAfter=6,
            leftIndent=12,
            rightIndent=12,
            leading=14
        ))
        
        self.styles.add(ParagraphStyle(
            'Remediation',
            parent=self.styles['Normal'],
            fontName=self.base_font,
            fontSize=10,
            textColor=self.accent_color,
            backColor=colors.HexColor('#f0fdf4'),
            spaceBefore=6,
            spaceAfter=6,
            leftIndent=12,
            rightIndent=12,
            leading=14
        ))

        # Add HTML-matching colors
        self.colors = {
            'primary': colors.HexColor('#2563eb'),
            'danger': colors.HexColor('#dc2626'),
            'warning': colors.HexColor('#f59e0b'),
            'info': colors.HexColor('#3b82f6'),
            'success': colors.HexColor('#16a34a'),
            'text': colors.HexColor('#1f2937'),
            'bg': colors.HexColor('#f9fafb'),
            'card_bg': colors.white,
            'border': colors.HexColor('#e5e7eb')
        }

    def _register_fonts(self):
        """Register fonts with fallbacks to system fonts"""
        try:
            font_dir = Path(__file__).parent / 'fonts'
            if font_dir.exists():
                for font_file in ['Roboto-Regular.ttf', 'Roboto-Bold.ttf']:
                    font_path = font_dir / font_file
                    if font_path.exists():
                        font_name = font_file.split('.')[0].replace('-Regular', '')
                        try:
                            pdfmetrics.registerFont(TTFont(font_name, str(font_path)))
                            if 'Bold' in font_file:
                                self.bold_font = font_name
                            else:
                                self.base_font = font_name
                        except:
                            continue
        except Exception as e:
            print(f"Font registration failed, using system fonts: {e}")

    def _create_styles(self):
        """Create enterprise-grade styles with system fonts"""
        styles = getSampleStyleSheet()
        
        # Add SectionTitle style first as it's a base style for others
        styles.add(ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading1'],
            fontName=self.bold_font,
            fontSize=16,
            textColor=self.primary_color,
            spaceAfter=16,
            keepWithNext=True,
            leading=20
        ))
        
        # Update existing styles to match HTML template
        styles.add(ParagraphStyle(
            'CoverTitle',
            parent=styles['SectionTitle'],  # Now uses SectionTitle as parent
            fontSize=24,
            spaceAfter=30,
            alignment=1
        ))
        
        styles.add(ParagraphStyle(
            'ModuleTitle',
            parent=styles['Heading2'],
            fontName=self.bold_font,
            fontSize=14,
            textColor=self.primary_color,
            spaceAfter=12
        ))

        styles.add(ParagraphStyle(
            'CategoryTitle',
            parent=styles['Heading3'],
            fontName=self.bold_font,
            fontSize=12,
            textColor=self.secondary_color,
            spaceAfter=8
        ))

        # Add new styles for assessment framework
        styles.add(ParagraphStyle(
            'PhaseTitle',
            parent=styles['Heading4'],
            fontName=self.bold_font,
            fontSize=11,
            textColor=self.primary_color,
            spaceAfter=6
        ))

        return styles

    def _create_cover_page(self, template_data):
        """Generate an attractive cover page"""
        elements = []
        
        # Add logo
        if os.path.exists(self.company_logo):
            elements.append(Image(self.company_logo, width=2*inch, height=1*inch))
        
        elements.append(Spacer(1, 60))
        elements.append(Paragraph("Security Assessment Report", self.styles['CoverTitle']))
        
        # Add cover info table with modern styling
        cover_info = [
            ['Target Organization:', template_data.get('target', 'Unknown')],
            ['Report Generated:', datetime.now().strftime('%B %d, %Y')],
            ['Classification:', 'CONFIDENTIAL'],
            ['Report ID:', f"SEC-{datetime.now():%Y%m%d-%H%M}"]
        ]
        
        cover_table = Table(cover_info, colWidths=[150, 300])
        cover_table.setStyle(self._get_cover_table_style())
        elements.append(cover_table)
        
        elements.append(PageBreak())
        return elements

    def _get_cover_table_style(self):
        """Create style for cover page table"""
        return TableStyle([
            ('TEXTCOLOR', (0, 0), (0, -1), self.secondary_color),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
            ('FONTNAME', (0, 0), (0, -1), self.bold_font),
            ('FONTNAME', (1, 0), (1, -1), self.base_font),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ])

    def _create_executive_summary(self, template_data: Dict) -> List:
        """Create an executive summary section with compact spacing"""
        elements = []
        elements.append(Paragraph("Executive Summary", self.styles['SectionTitle']))
        
        # Reduce spacing after title
        elements.append(Spacer(1, 6))  # Reduced from 12
        
        summary_text = f"""This security assessment was conducted on {template_data.get('target', 'the target system')} on {datetime.now().strftime('%B %d, %Y')}. The assessment identified {template_data.get('total_findings', 0)} security findings across {template_data.get('urls_scanned', 1)} URLs."""
        elements.append(Paragraph(summary_text, self.styles['Normal']))
        elements.append(Spacer(1, 8))  # Reduced from 12
        
        # Add summary statistics with compact styling
        stats = [
            ['Total Tests', 'Tests Run', 'Issues Found', 'URLs Scanned'],
            [
                str(template_data.get('total_tests', 0)),
                str(template_data.get('tests_completed', 0)),
                str(template_data.get('total_findings', 0)),
                str(template_data.get('urls_scanned', 1))
            ]
        ]
        
        summary_table = Table(stats, colWidths=[120, 120, 120, 120])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), self.bold_font),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),  # Reduced padding
            ('TOPPADDING', (0, 0), (-1, -1), 8),     # Reduced padding
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 12))  # Reduced from 20
        
        return elements

    def _create_risk_matrix(self, findings: List[Dict]) -> List:
        """Create a risk matrix visualization"""
        elements = []
        
        # Count findings by severity
        severity_counts = {
            'high': 0,
            'medium': 0,
            'low': 0,
            'info': 0
        }
        
        for finding in findings:
            severity = finding.get('severity', '').lower()
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        # Create risk summary table
        risk_data = [
            ['Risk Level', 'Count', 'Percentage'],
            ['High', str(severity_counts['high']), f"{(severity_counts['high']/len(findings))*100:.1f}%"],
            ['Medium', str(severity_counts['medium']), f"{(severity_counts['medium']/len(findings))*100:.1f}%"],
            ['Low', str(severity_counts['low']), f"{(severity_counts['low']/len(findings))*100:.1f}%"],
            ['Info', str(severity_counts['info']), f"{(severity_counts['info']/len(findings))*100:.1f}%"]
        ]
        
        risk_table = Table(risk_data, colWidths=[150, 100, 100])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), self.bold_font),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(risk_table)
        elements.append(Spacer(1, 20))
        
        return elements

    def _create_module_results(self, template_data: Dict) -> List:
        """Create module results with compact spacing"""
        elements = []
        elements.append(Paragraph("Module Results", self.styles['SectionTitle']))
        elements.append(Spacer(1, 8))  # Reduced spacing
        
        try:
            for module in template_data.get('modules', []):
                # Safely get numeric values
                tests_run = str(module.get('tests_run', 0))
                tests_available = str(module.get('tests_available', 0))
                duration = str(module.get('duration', 0))
                issues_found = str(module.get('issues_found', 0))
                
                # Create module card with stats
                stats_data = [
                    [Paragraph(str(module.get('name', 'Unknown')), self.styles['ModuleTitle'])],
                    [Table([
                        ['Tests Run', 'Duration', 'Issues Found'],
                        [
                            f"{tests_run}/{tests_available}",
                            f"{duration}s",
                            issues_found
                        ]
                    ],
                    colWidths=[120, 120, 120],
                    style=self._get_module_table_style())]
                ]
                
                module_card = Table(stats_data, colWidths=[400])
                module_card.setStyle(self._create_card_style())
                elements.append(module_card)
                elements.append(Spacer(1, 10))  # Reduced from 16
                
        except Exception as e:
            print(f"Error in module results: {str(e)}")
            # Add fallback simple table
            elements.append(self._create_simple_module_table(template_data))
            
        return elements

    def _get_module_table_style(self):
        """Get consistent table style for module stats"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), self.bold_font),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['border']),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8)
        ])

    def _create_simple_module_table(self, template_data: Dict) -> Table:
        """Create a simple fallback table for module results"""
        data = [['Module', 'Tests', 'Issues']]
        try:
            for module in template_data.get('modules', []):
                data.append([
                    str(module.get('name', 'Unknown')),
                    f"{module.get('tests_run', 0)}/{module.get('tests_available', 0)}",
                    str(module.get('issues_found', 0))
                ])
        except Exception:
            data.append(['Error loading module data', '', ''])
            
        table = Table(data, colWidths=[200, 100, 100])
        table.setStyle(self._get_module_table_style())
        return table

    def _create_assessment_framework(self) -> List:
        """Enhanced security assessment framework section with visual cards"""
        elements = []
        elements.append(Paragraph("Security Assessment Framework", self.styles['SectionTitle']))
        
        try:
            # Define categories and tests as static data
            categories = [
                ('Authentication & Session', [
                    'CSRF Protection',
                    'Session Management',
                    'Password Policy',
                    'Authentication Bypass',
                    'Token Security'
                ]),
                ('Injection & Code Execution', [
                    'SQL Injection',
                    'Cross-site Scripting (XSS)',
                    'Command Injection',
                    'XML External Entity (XXE)',
                    'Remote Code Execution'
                ]),
                ('Configuration & Headers', [
                    'Security Headers Analysis',
                    'SSL/TLS Configuration',
                    'Server Information',
                    'Error Handling',
                    'Cookie Security'
                ]),
                ('Information Disclosure', [
                    'Sensitive Data Exposure',
                    'Directory Traversal',
                    'File Inclusion',
                    'Version Information'
                ])
            ]

            # Create category cards
            for category_name, tests in categories:
                card_content = [[
                    Paragraph(category_name, self.styles['CategoryTitle'])
                ]]
                
                for test in tests:
                    card_content.append([
                        Paragraph(f"• {test}", 
                                ParagraphStyle(
                                    'TestItem',
                                    parent=self.styles['Normal'],
                                    leftIndent=20,
                                    spaceBefore=6,
                                    spaceAfter=6,
                                    textColor=self.colors['text']
                                ))
                    ])
                
                card = Table(card_content, colWidths=[400])
                card.setStyle(self._create_card_style())
                elements.append(card)
                elements.append(Spacer(1, 20))

            # Add methodology section
            elements.append(Paragraph("Testing Methodology", self.styles['SectionTitle']))
            elements.append(Spacer(1, 12))

            # Define phases
            phases = [
                ('Phase 1: Reconnaissance', [
                    'Domain Information Gathering',
                    'Service Enumeration',
                    'Technology Stack Detection'
                ]),
                ('Phase 2: Vulnerability Assessment', [
                    'Automated Security Testing',
                    'Configuration Analysis',
                    'Security Header Validation'
                ]),
                ('Phase 3: Exploit Testing', [
                    'Authentication Testing',
                    'Injection Testing',
                    'Security Control Bypass'
                ]),
                ('Phase 4: Compliance', [
                    'OWASP Top 10',
                    'Security Best Practices',
                    'Industry Standards'
                ])
            ]

            for phase_name, steps in phases:
                phase_content = [[
                    Paragraph(phase_name, self.styles['PhaseTitle'])
                ]]
                
                for step in steps:
                    phase_content.append([
                        Paragraph(f"→ {step}", self.styles['Normal'])
                    ])
                
                phase_card = Table(phase_content, colWidths=[350])
                phase_card.setStyle(self._create_card_style(has_shadow=True))
                elements.append(phase_card)
                elements.append(Spacer(1, 16))

        except Exception as e:
            print(f"Error in assessment framework: {str(e)}")
            # Add simplified framework section
            elements.append(Paragraph("Security Assessment Categories", self.styles['Normal']))
            elements.append(Spacer(1, 12))

        return elements

    def _create_card_style(self, has_shadow=True):
        """Create a card-like container style matching HTML"""
        style_commands = [
            ('BACKGROUND', (0, 0), (-1, -1), self.colors['card_bg']),
            ('TOPPADDING', (0, 0), (-1, -1), 16),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 16),
            ('LEFTPADDING', (0, 0), (-1, -1), 16),
            ('RIGHTPADDING', (0, 0), (-1, -1), 16),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['border']),
        ]
        
        # Add shadow if requested
        if has_shadow:
            style_commands.append(('LINEBELOW', (0, -1), (-1, -1), 1, self.colors['text'].clone(alpha=0.2)))
            style_commands.append(('LINEAFTER', (-1, 0), (-1, -1), 1, self.colors['text'].clone(alpha=0.2)))
        
        return TableStyle(style_commands)

    def generate_report(self, findings: List[Dict], template_data: Dict) -> str:
        """Generate an enterprise-grade PDF security report"""
        try:
            # Ensure we're in project root
            os.chdir(str(self.project_root))
            
            # Create reports directory in project root
            reports_dir = self.project_root / 'reports'
            reports_dir.mkdir(exist_ok=True)
            
            # Change the filename format to match expected format
            report_file = reports_dir / f"scan_report_{datetime.now():%Y%m%d_%H%M%S}.pdf"
            
            # Create PDF document with custom settings
            doc = SimpleDocTemplate(
                str(report_file),
                pagesize=A4,
                rightMargin=25*mm,
                leftMargin=25*mm,
                topMargin=20*mm,
                bottomMargin=20*mm
            )

            story = []
            
            # Add cover page
            story.extend(self._create_cover_page(template_data))
            
            # Add table of contents
            story.extend(self._create_table_of_contents())
            story.append(PageBreak())
            
            # Create first page content - keep these sections together
            first_page_content = []
            
            # Add executive summary with error handling
            try:
                first_page_content.extend(self._create_executive_summary(template_data))
            except Exception as e:
                print(f"Warning: Error creating executive summary: {e}")
                first_page_content.append(Paragraph("Executive Summary", self.styles['SectionTitle']))
            
            # Add findings summary with error handling
            try:
                first_page_content.append(Paragraph("Key Findings Overview", self.styles['SectionTitle']))
                if findings:
                    first_page_content.extend(self._create_risk_matrix(findings))
            except Exception as e:
                print(f"Warning: Error creating risk matrix: {e}")
            
            # Add module results with error handling
            try:
                if template_data.get('modules'):
                    first_page_content.extend(self._create_module_results(template_data))
            except Exception as e:
                print(f"Warning: Error creating module results: {e}")
            
            # Keep all first page content together
            story.append(KeepTogether(first_page_content))
            
            # Force page break before assessment framework
            story.append(PageBreak())
            
            # Add assessment framework with error handling
            try:
                story.extend(self._create_assessment_framework())
            except Exception as e:
                print(f"Warning: Error creating assessment framework: {e}")
            
            # Force page break before findings summary table
            story.append(PageBreak())
            
            # Add findings summary table with CVSS/OWASP/CWE
            try:
                story.extend(self._create_findings_summary_table(findings))
            except Exception as e:
                print(f"Warning: Error creating findings summary table: {e}")
            
            # Add remediation roadmap
            try:
                story.extend(self._create_remediation_roadmap(findings))
            except Exception as e:
                print(f"Warning: Error creating remediation roadmap: {e}")
            
            # Force page break before detailed findings
            story.append(PageBreak())
            
            # Add findings with error handling
            try:
                for finding in findings:
                    story.extend(self._create_finding_page(finding))
            except Exception as e:
                print(f"Warning: Error creating findings pages: {e}")
            
            # Add scan configuration appendix
            try:
                story.append(PageBreak())
                story.extend(self._create_scan_configuration(template_data))
            except Exception as e:
                print(f"Warning: Error creating scan configuration: {e}")
            
            # Build the PDF
            doc.build(
                story,
                onFirstPage=self._header_footer,
                onLaterPages=self._header_footer
            )
            
            return str(report_file)
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate PDF report: {str(e)}") from e

    def _header_footer(self, canvas, doc):
        """Add professional header and footer to each page with fallback fonts"""
        width, height = A4
        
        canvas.saveState()
        canvas.setFont(self.bold_font, 8)
        canvas.drawString(25*mm, height - 15*mm, "Security Assessment Report")
        canvas.drawRightString(width - 25*mm, height - 15*mm, f"Page {doc.page}")
        
        canvas.setFont(self.base_font, 8)
        canvas.drawString(25*mm, 15*mm, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        canvas.drawRightString(width - 25*mm, 15*mm, "CONFIDENTIAL")
        canvas.restoreState()

    def _create_table_of_contents(self) -> List:
        """Create a table of contents page"""
        elements = []
        elements.append(Paragraph("Table of Contents", self.styles['SectionTitle']))
        elements.append(Spacer(1, 12))
        
        toc_items = [
            "1. Executive Summary",
            "2. Key Findings Overview",
            "3. Security Assessment Framework",
            "4. Findings Summary (with CVSS & OWASP mappings)",
            "5. Remediation Roadmap",
            "6. Detailed Findings",
            "7. Scan Configuration & Appendices"
        ]
        
        for item in toc_items:
            elements.append(Paragraph(item, self.styles['Normal']))
            elements.append(Spacer(1, 8))
        
        return elements

    def _create_findings_summary_table(self, findings: List[Dict]) -> List:
        """Create a comprehensive findings summary table with CVSS/OWASP/CWE columns"""
        elements = []
        elements.append(Paragraph("Findings Summary", self.styles['SectionTitle']))
        elements.append(Spacer(1, 12))
        
        if not findings:
            elements.append(Paragraph("No findings to report.", self.styles['Normal']))
            return elements
        
        # Create findings table with extended columns
        table_data = [['#', 'Type', 'Severity', 'CVSS', 'OWASP', 'CWE', 'URL']]
        
        for idx, finding in enumerate(findings[:50], 1):  # Limit to 50 for PDF readability
            finding_type = finding.get('type', 'Unknown')[:30]
            severity = finding.get('severity', 'Unknown')
            cvss = f"{finding.get('cvss_score', 0.0):.1f}"
            owasp = finding.get('owasp_category', 'N/A')[:15]
            cwe = finding.get('cwe_id', 'N/A')[:10]
            url = finding.get('url', 'N/A')[:40]
            
            table_data.append([str(idx), finding_type, severity, cvss, owasp, cwe, url])
        
        findings_table = Table(table_data, colWidths=[30, 80, 60, 45, 60, 50, 70])
        findings_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), self.bold_font),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f8f8')]),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(findings_table)
        elements.append(Spacer(1, 12))
        
        if len(findings) > 50:
            elements.append(Paragraph(f"Note: Showing first 50 of {len(findings)} findings. See detailed findings section for complete list.", 
                                     self.styles['Normal']))
        
        elements.append(Spacer(1, 12))
        return elements

    def _create_remediation_roadmap(self, findings: List[Dict]) -> List:
        """Create a remediation roadmap grouped by priority"""
        elements = []
        elements.append(Paragraph("Remediation Roadmap", self.styles['SectionTitle']))
        elements.append(Spacer(1, 12))
        
        # Categorize findings
        immediate = [f for f in findings if f.get('severity', '').lower() in ['critical', 'high']]
        short_term = [f for f in findings if f.get('severity', '').lower() == 'medium']
        long_term = [f for f in findings if f.get('severity', '').lower() in ['low', 'info']]
        
        # Sort by CVSS score - ensure it's a float
        def get_cvss_score(item):
            score = item.get('cvss_score', 0.0)
            try:
                return float(score) if score is not None else 0.0
            except (ValueError, TypeError):
                return 0.0
        
        immediate.sort(key=get_cvss_score, reverse=True)
        short_term.sort(key=get_cvss_score, reverse=True)
        long_term.sort(key=get_cvss_score, reverse=True)
        
        # Immediate tier
        if immediate:
            elements.append(Paragraph("Immediate Priority (24–48 Hours)", self.styles['Heading4']))
            immediate_data = [['#', 'Finding', 'CVSS', 'Action Required']]
            for idx, finding in enumerate(immediate[:10], 1):
                immediate_data.append([
                    str(idx),
                    finding.get('type', 'Unknown')[:40],
                    f"{finding.get('cvss_score', 0.0):.1f}",
                    "Apply security patch"
                ])
            
            immed_table = Table(immediate_data, colWidths=[25, 250, 50, 140])
            immed_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), self.bold_font),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fee2e2')]),
                ('PADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(immed_table)
            elements.append(Spacer(1, 12))
        
        # Short-term tier
        if short_term:
            elements.append(Paragraph("Short-Term Priority (30 Days)", self.styles['Heading4']))
            short_data = [['#', 'Finding', 'CVSS', 'Action Required']]
            for idx, finding in enumerate(short_term[:10], 1):
                short_data.append([
                    str(idx),
                    finding.get('type', 'Unknown')[:40],
                    f"{finding.get('cvss_score', 0.0):.1f}",
                    "Schedule remediation"
                ])
            
            short_table = Table(short_data, colWidths=[25, 250, 50, 140])
            short_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f59e0b')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), self.bold_font),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fef3c7')]),
                ('PADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(short_table)
            elements.append(Spacer(1, 12))
        
        # Long-term tier
        if long_term:
            elements.append(Paragraph("Long-Term Priority (Next Cycle)", self.styles['Heading4']))
            long_data = [['#', 'Finding', 'CVSS', 'Action Required']]
            for idx, finding in enumerate(long_term[:10], 1):
                long_data.append([
                    str(idx),
                    finding.get('type', 'Unknown')[:40],
                    f"{finding.get('cvss_score', 0.0):.1f}",
                    "Monitor and track"
                ])
            
            long_table = Table(long_data, colWidths=[25, 250, 50, 140])
            long_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), self.bold_font),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#dbeafe')]),
                ('PADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(long_table)
            elements.append(Spacer(1, 12))
        
        return elements

    def _create_scan_configuration(self, template_data: Dict) -> List:
        """Create scan configuration and appendices section"""
        elements = []
        elements.append(Paragraph("Appendix: Scan Configuration", self.styles['SectionTitle']))
        elements.append(Spacer(1, 12))
        
        config_data = [
            ['Setting', 'Value'],
            ['Target URL', template_data.get('target', 'N/A')],
            ['Scan Start Time', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Scan Type', 'Automated Security Assessment'],
            ['Testing Scope', 'Full Application Scan'],
            ['Authentication', 'Enabled' if template_data.get('authenticated') else 'Disabled'],
            ['Active Testing', 'Enabled' if template_data.get('active_testing') else 'Disabled'],
            ['SSL/TLS Checks', 'Enabled'],
            ['Crawl Depth', str(template_data.get('crawl_depth', 'Unlimited'))],
            ['Rate Limit', '200 req/min'],
        ]
        
        config_table = Table(config_data, colWidths=[200, 350])
        config_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), self.bold_font),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f8f8')]),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(config_table)
        elements.append(Spacer(1, 20))
        
        # Add testing modules
        elements.append(Paragraph("Testing Modules Executed", self.styles['Heading4']))
        elements.append(Spacer(1, 8))
        
        modules_text = """
        • Authentication & Session Management
        • Injection Vulnerabilities (SQL, NoSQL, Command)
        • Cross-Site Scripting (XSS) Detection
        • Security Misconfiguration Analysis
        • Sensitive Information Disclosure
        • Broken Access Control (IDOR/BAC)
        • Server-Side Request Forgery (SSRF)
        • SSL/TLS Certificate Validation
        • HTTP Security Headers Analysis
        • Clickjacking Detection
        """
        
        elements.append(Paragraph(modules_text, self.styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Add disclaimer
        elements.append(Paragraph("Disclaimer", self.styles['Heading4']))
        elements.append(Spacer(1, 8))
        
        disclaimer_text = """
        This security assessment report and all findings are provided for authorized security testing purposes only.
        The scanner was executed with explicit permission and in accordance with applicable laws and regulations.
        All information contained within this report is confidential and intended solely for the organization's security team.
        Unauthorized access, disclosure, or misuse of this report is prohibited.
        """
        
        elements.append(Paragraph(disclaimer_text, self.styles['Normal']))
        
        return elements

    def _create_finding_page(self, finding: Dict) -> List:
        """Enhanced finding details with modern card design"""
        elements = []
        
        # Create finding card with enhanced styling
        severity = finding.get('severity', 'Unknown').lower()
        severity_colors = {
            'high': self.colors['danger'],
            'medium': self.colors['warning'],
            'low': self.colors['info'],
            'info': self.colors['success']
        }
        
        # Create badge-style severity indicator with fixed styling
        severity_badge = Table([[
            Paragraph(finding.get('severity', 'Unknown').upper(),
                     ParagraphStyle('SeverityBadge',
                                  parent=self.styles['Normal'],
                                  textColor=severity_colors.get(severity, colors.black),
                                  fontSize=9,
                                  alignment=1))
        ]], colWidths=[80])
        severity_badge.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), severity_colors.get(severity, colors.black).clone(alpha=0.1)),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
        ]))

        # Create elements for this finding
        title = Paragraph(finding.get('type', 'Unknown Issue'), self.styles['SectionTitle'])
        spacer = Spacer(1, 12)
        
        # Create details table
        severity = finding.get('severity', 'Unknown').lower()
        severity_colors = {
            'high': colors.HexColor('#dc2626'),
            'medium': colors.HexColor('#f59e0b'),
            'low': colors.HexColor('#3b82f6'),
            'info': colors.HexColor('#16a34a')
        }
        
        details = [
            ['Severity:', finding.get('severity', 'Unknown')],
            ['URL:', finding.get('url', 'Unknown')],
            ['Description:', finding.get('description', 'No description provided')]
        ]
        
        details_table = Table(details, colWidths=[100, 400])
        details_table.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (0, -1), self.secondary_color),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
            ('TEXTCOLOR', (1, 0), (1, 0), severity_colors.get(severity, colors.black)),
            ('FONTNAME', (0, 0), (0, -1), self.bold_font),
            ('FONTNAME', (1, 0), (1, -1), self.base_font),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))

        # Create list of elements for this finding
        elements = [title, spacer, details_table, Spacer(1, 12)]
        
        # Add evidence section if present
        if finding.get('evidence'):
            evidence_elements = [
                Paragraph("Evidence:", self.styles['Heading4']),
                Spacer(1, 6),
                Paragraph(str(finding['evidence']).replace('\n', '<br/>').strip(), self.styles['Evidence']),
                Spacer(1, 12)
            ]
            elements.extend(evidence_elements)
        
        # Add remediation section if present
        if finding.get('remediation'):
            remediation_elements = [
                Paragraph("Remediation:", self.styles['Heading4']),
                Spacer(1, 6),
                Paragraph(str(finding['remediation']).replace('\n', '<br/>').strip(), self.styles['Remediation']),
                Spacer(1, 12)
            ]
            elements.extend(remediation_elements)
        
        # Add final spacing and page break
        elements.append(Spacer(1, 20))
        elements.append(PageBreak())
        
        # Return all elements wrapped in KeepTogether
        return [KeepTogether(elements[:-1]), elements[-1]]  # Keep everything except PageBreak together

    def _create_compliance_section(self, compliance_data: Dict) -> List:
        """Create a compliance requirements section"""
        elements = []
        # Compliance section implementation
        # ...existing code...
        return elements

    def _create_appendices(self, template_data: Dict) -> List:
        """Create appendices with supporting information"""
        elements = []
        # Appendices implementation
        # ...existing code...
        return elements
