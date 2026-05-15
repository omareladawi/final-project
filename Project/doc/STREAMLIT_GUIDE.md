# 🌐 Web UI - Streamlit Dashboard Guide

## Quick Start

### Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

### Run the Web Interface

```bash
# From the project directory
streamlit run streamlit_app.py

# Or with custom port
streamlit run streamlit_app.py --server.port 8501
```

The app will open in your browser at: **http://localhost:8501**

---

## Features Overview

### 🎯 User-Friendly Dashboard

1. **Sidebar Configuration Panel**
   - Enter target URL
   - Configure scan options (active tests, crawl depth)
   - Set request timeout
   - Optional: Add authentication credentials

2. **Tabbed Results Interface**
   - **📊 Metrics Tab**: Scan statistics and coverage analysis
   - **⚠️ Risk Assessment**: Risk dashboard with gauge and recommendations
   - **🎯 Findings Summary**: Visual charts of vulnerabilities
   - **📋 Details Tab**: Expandable detailed findings with CWE/OWASP info
   - **📄 Full Report**: Professional HTML report with export options

3. **Real-Time Scan Progress**
   - Progress indicator during scan
   - Status updates
   - Error handling with user-friendly messages

---

## Workflow

### Step 1: Configure Target
```
1. Open the web interface
2. Enter target URL (e.g., https://example.com)
3. Adjust scan options as needed
```

### Step 2: Start Scan
```
1. Click "🚀 Start Scan" button
2. Monitor progress indicator
3. Wait for completion
```

### Step 3: View Results
```
1. View metrics and coverage in Metrics tab
2. Check risk assessment in Risk tab
3. Review findings in Findings/Details tabs
4. Download reports in Full Report tab
```

### Step 4: Export Results
```
1. Download HTML report for sharing
2. Download JSON for integration
3. Share reports with stakeholders
```

---

## Example Usage Scenarios

### Scenario 1: Quick Security Check
```
Target: https://my-app.local
Active Tests: Disabled (reconnaissance only)
Crawl Depth: 2
Timeout: 10s
→ Fast baseline security assessment
```

### Scenario 2: Comprehensive Assessment
```
Target: https://staging.company.com
Active Tests: Enabled
Crawl Depth: 3
Timeout: 15s
→ Detailed vulnerability testing
```

### Scenario 3: Authenticated Scanning
```
Target: https://internal.app
Enable Authenticated Scanning: Yes
Login URL: /login.php
Username: testuser
Password: ****
Active Tests: Enabled
→ Protected area assessment
```

---

## Dashboard Components

### 📊 Metrics Dashboard
Displays:
- Scan duration
- Request success rate
- URLs discovered
- Total findings count
- Request statistics (total, successful, failed)
- Coverage analysis (forms, parameters)

**Visualization:**
- Key metrics in large format
- Summary tables for detailed stats
- Color-coded severity distribution

### ⚠️ Risk Assessment
Shows:
- **Risk Level**: Minimal → Low → Medium → High → Critical
- **Risk Score**: 0-100 gauge visualization
- **Exploitable Issues**: Count of critical/high severity findings
- **Executive Summary**: AI-style analysis with recommendations

**Includes:**
- Severity breakdown
- Recommended actions
- Key findings highlights

### 🎯 Findings Summary
Visualizations:
- Bar chart: Findings by severity
- Pie chart: Findings by type
- Color-coded severity indicators

### 📋 Detailed Findings
For each finding shows:
- Type and severity
- Affected URL and parameter
- CWE ID and OWASP category
- Confidence score
- Description and evidence
- Remediation guidance

### 📄 Full Report
Includes:
- Professional HTML rendering
- Embedded styling
- All metrics and findings
- Executive summary
- Remediation recommendations
- Download options

---

## Advanced Features

### Real-Time Metrics Collection
- Tracks every request
- Accumulates findings
- Calculates coverage percentage
- Monitors success rates

### Intelligent Risk Assessment
- **Risk Score Algorithm**:
  ```
  Risk = (Critical × 40) + (High × 20) + (Medium × 10) + (Low × 2)
  Normalized to 0-100 scale
  ```
- Risk level classification
- Exploitable finding identification

### Findings Processing
- **CWE Mapping**: Automatic Common Weakness Enumeration classification
- **OWASP Mapping**: OWASP Top 10 categorization
- **Confidence Scoring**: 0.0-1.0 confidence per finding
- **Deduplication**: Removes duplicate findings
- **Enrichment**: Adds context and remediation

### Professional Reporting
- **HTML Export**: Styled, responsive reports
- **JSON Export**: Structured data for integration
- **Summary Generation**: Executive-friendly overview

---

## Tips & Best Practices

### ✅ Do's
- ✓ Always scan authorized targets
- ✓ Start with reconnaissance (active tests disabled)
- ✓ Use appropriate timeout values
- ✓ Export reports for documentation
- ✓ Review findings carefully
- ✓ Use authentication for protected areas

### ❌ Don'ts
- ✗ Don't scan without authorization
- ✗ Don't use excessive timeout values on production
- ✗ Don't rely on single scan results
- ✗ Don't ignore low-severity findings
- ✗ Don't assume false positives without verification

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+L` | Clear sidebar |
| `Ctrl+R` | Rerun app |
| `Ctrl+C` | Stop scan (terminal) |
| Tab Key | Navigate between fields |

---

## Troubleshooting

### Issue: Streamlit not found
```bash
# Solution: Install Streamlit
pip install streamlit
```

### Issue: Port already in use
```bash
# Solution: Use different port
streamlit run streamlit_app.py --server.port 8502
```

### Issue: Scan timeout
```bash
# Solution: Increase timeout in sidebar or check network
# Timeout value: Request timeout in seconds (increase for slow networks)
```

### Issue: Connection refused
```bash
# Solution: Verify target is running and accessible
curl -I https://target.com
```

### Issue: Authentication fails
```bash
# Ensure credentials are correct
# Check login URL format
# Try without authentication first
```

---

## Configuration Options

### Sidebar Settings

**Target URL**
- Required field
- Format: `https://example.com` or `http://localhost:3000`
- Auto-adds https:// if scheme missing

**Active Tests**
- Enable/disable injection testing
- Default: Disabled (reconnaissance only)
- Impact: Higher risk but more thorough

**Crawl Depth**
- Range: 1-5
- Default: 2
- Higher = more URLs but slower scan

**Request Timeout**
- Range: 5-60 seconds
- Default: 10 seconds
- Increase for slow networks

**Authentication**
- Optional credentials
- Login URL: Path or full URL
- Username/Password: Credentials for login form

---

## Performance Tuning

### For Fast Scans
```
Crawl Depth: 1-2
Active Tests: Disabled
Timeout: 5-10 seconds
```

### For Thorough Scans
```
Crawl Depth: 3-4
Active Tests: Enabled
Timeout: 15-20 seconds
```

### For Production Systems
```
Crawl Depth: 1
Active Tests: Disabled
Timeout: 10 seconds
```

---

## Data Privacy

The Streamlit app:
- ✓ Runs locally on your machine
- ✓ Doesn't send data to external servers
- ✓ Processes all data in-memory
- ✓ Stores reports in local `/reports` directory
- ✓ Doesn't require authentication to app

**Note**: Ensure you have authorization before scanning any target.

---

## Integration with CI/CD

You can also run the CLI scanner from the app or integrate with pipelines:

```bash
# CLI mode (non-interactive)
python -m src.web_scanner.main \
  --url https://example.com \
  --active-tests \
  --format json \
  --output results.json
```

---

## Support & Documentation

- **Project Index**: `PROJECT_INDEX.md`
- **Implementation Guide**: `IMPLEMENTATION_GUIDE.md`
- **Professional Features**: `PROFESSIONAL_ENHANCEMENTS.md`
- **Presentation Guide**: `PRESENTATION_ROADMAP.md`

---

## Next Steps

1. **Customize Dashboard**
   - Modify colors and styling in CSS section
   - Add additional metrics
   - Create custom visualizations

2. **Extend Functionality**
   - Add scheduled scanning
   - Implement result history
   - Create scanning templates
   - Add multi-target support

3. **Production Deployment**
   - Deploy with Docker
   - Add authentication to Streamlit
   - Configure logging
   - Set up monitoring

---

*Streamlit Web Interface - Version 1.0*  
*Professional Security Assessment Tool*  
*Built with ❤️ for security professionals*
