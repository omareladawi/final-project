# 🚀 Web UI Setup & Deployment Guide

## Quick Start (3 Steps)

### 1. Install Dependencies
```bash
cd D:\Final\Project
pip install -r requirements.txt
```

### 2. Run the Web Interface
```bash
streamlit run streamlit_app.py
```

### 3. Open in Browser
```
http://localhost:8501
```

---

## Installation Methods

### Method 1: Direct Installation (Recommended for Windows)

**Prerequisites:** Python 3.8+ installed

```bash
# Navigate to project directory
cd D:\Final\Project

# Install all dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py
```

**That's it!** The app will open in your default browser.

---

### Method 2: Virtual Environment (Best Practice)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py
```

---

### Method 3: Docker (For Production)

**Prerequisites:** Docker and Docker Compose installed

```bash
# Build and run with Docker Compose
docker-compose up --build

# The app will be available at:
# http://localhost:8501
```

**Includes:**
- Web scanner on port 8501
- OWASP Juice Shop on port 3000 (for testing)

---

## Accessing the Application

### Local Access
- **URL**: http://localhost:8501
- **Default Port**: 8501
- **Address**: 127.0.0.1

### Custom Port
```bash
# Run on different port
streamlit run streamlit_app.py --server.port 8502
```

### Network Access
```bash
# Run on all interfaces (for network access)
streamlit run streamlit_app.py --server.address 0.0.0.0
```

---

## System Requirements

### Minimum
- Python 3.8+
- 2GB RAM
- 500MB disk space
- Internet connection (for first scan)

### Recommended
- Python 3.10+
- 4GB+ RAM
- 1GB disk space
- Stable internet connection

### Supported OS
- ✅ Windows 10/11
- ✅ macOS (Intel/Apple Silicon)
- ✅ Linux (Ubuntu, Debian, CentOS)

---

## Configuration

### Environment Variables
```bash
# Set Streamlit config
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_SERVER_PORT=8501

# Or on Windows:
set STREAMLIT_SERVER_HEADLESS=true
set STREAMLIT_SERVER_PORT=8501
```

### Custom Config File
Create `~/.streamlit/config.toml`:
```toml
[server]
port = 8501
headless = true
enableCORS = false

[client]
showErrorDetails = true

[logger]
level = "info"
```

---

## Features Checklist

After launching, you should see:

✅ **Sidebar Controls**
- Target URL input
- Active tests toggle
- Crawl depth slider
- Timeout setting
- Authentication options
- Start Scan button

✅ **Welcome Screen**
- Feature overview
- Example targets
- Security notes
- Getting started guide

✅ **After Scan**
- 📊 Metrics Tab with statistics
- ⚠️ Risk Assessment with score
- 🎯 Findings Summary with charts
- 📋 Detailed Findings with CWE/OWASP
- 📄 Full Report with exports

✅ **Export Options**
- HTML report download
- JSON data export
- Professional formatting

---

## Testing the Installation

### Test 1: Verify Python
```bash
python --version
# Should show Python 3.8+
```

### Test 2: Verify Dependencies
```bash
python -c "import streamlit; print('Streamlit OK')"
python -c "import plotly; print('Plotly OK')"
python -c "import pandas; print('Pandas OK')"
```

### Test 3: Run Scanner
```bash
# Test with OWASP Juice Shop (if running on localhost:3000)
python -m src.web_scanner.main --url http://localhost:3000 --format html
# Check: reports/ directory should have a new report
```

### Test 4: Run Streamlit App
```bash
streamlit run streamlit_app.py

# The browser should open to http://localhost:8501
# You should see the welcome screen
```

---

## Troubleshooting

### Issue: `streamlit: command not found`
**Solution:**
```bash
# Install Streamlit
pip install streamlit

# Or install all requirements
pip install -r requirements.txt
```

### Issue: `ModuleNotFoundError: No module named 'streamlit'`
**Solution:**
```bash
# Verify Streamlit is installed
pip list | grep streamlit

# If not, install it
pip install streamlit

# Try running again
streamlit run streamlit_app.py
```

### Issue: Port 8501 already in use
**Solution:**
```bash
# Use different port
streamlit run streamlit_app.py --server.port 8502

# Or kill the process using the port
# Windows:
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# macOS/Linux:
lsof -i :8501
kill -9 <PID>
```

### Issue: Scanner timeout
**Solution:**
- Increase timeout in sidebar (set to 20-30 seconds)
- Check internet connection
- Verify target is accessible
- Check firewall rules

### Issue: Report not displaying
**Solution:**
- Try a different URL
- Clear browser cache (Ctrl+Shift+Del)
- Check browser console for errors (F12)
- Try different format (JSON instead of HTML)

### Issue: Scan keeps failing
**Solution:**
```bash
# Run with verbose logging
streamlit run streamlit_app.py --logger.level=debug

# Or use CLI scanner directly
python -m src.web_scanner.main --url http://localhost:3000 --verbose
```

---

## Performance Optimization

### For Faster Loading
```bash
# Clear Streamlit cache
streamlit cache clear

# Run with reduced logging
streamlit run streamlit_app.py --logger.level=warning
```

### For Better Performance
```bash
# Disable auto-rerun
streamlit run streamlit_app.py --client.toolbarMode=minimal

# Run with specific Python version
python3.11 -m streamlit run streamlit_app.py
```

---

## Production Deployment

### Deployment Steps

1. **Choose Platform**
   - Streamlit Cloud (free, limited)
   - Heroku (paid)
   - Docker on cloud (AWS, GCP, Azure)
   - Self-hosted server

2. **Prepare Repository**
   ```bash
   # Ensure .gitignore excludes sensitive files
   git add .
   git commit -m "Ready for deployment"
   ```

3. **Deploy to Streamlit Cloud**
   - Push to GitHub
   - Visit https://share.streamlit.io
   - Connect repository
   - Select branch and script
   - Deploy

4. **Deploy with Docker**
   ```bash
   # Build image
   docker build -t web-scanner:latest .
   
   # Run container
   docker run -p 8501:8501 web-scanner:latest
   ```

### Security Checklist for Production
- [ ] Add authentication to Streamlit app
- [ ] Use HTTPS (reverse proxy with nginx/Apache)
- [ ] Restrict IP access
- [ ] Enable firewall
- [ ] Use environment variables for secrets
- [ ] Enable logging and monitoring
- [ ] Set resource limits
- [ ] Regular backups of reports
- [ ] Keep dependencies updated

---

## Monitoring & Logging

### View Logs
```bash
# On Windows:
# Logs appear in terminal window running streamlit

# For persistent logging:
streamlit run streamlit_app.py > app.log 2>&1
```

### Monitor Performance
```bash
# Check resource usage
# Windows Task Manager (Ctrl+Shift+Esc)
# macOS Activity Monitor
# Linux: top or htop
```

---

## Common Workflows

### Workflow 1: Quick Reconnaissance
1. Enter URL
2. Disable Active Tests
3. Set Crawl Depth to 1-2
4. Click Start Scan
5. View Metrics tab
6. Download HTML report

### Workflow 2: Full Assessment
1. Enter URL
2. Enable Active Tests
3. Set Crawl Depth to 3-4
4. Click Start Scan
5. Review all tabs
6. Export both HTML and JSON

### Workflow 3: Authenticated Scan
1. Enter URL
2. Enable "Authenticated Scanning"
3. Enter login URL (e.g., /login.php)
4. Enter credentials
5. Enable Active Tests (optional)
6. Click Start Scan
7. View detailed findings

---

## Integration with Other Tools

### Export to JIRA
```bash
# Download JSON report
# Parse JSON and create JIRA issues
python scripts/export_to_jira.py scan_report.json
```

### Import to Security Dashboard
```bash
# Use JSON export
curl -X POST http://security-dashboard/api/reports \
  -H "Content-Type: application/json" \
  -d @scan_report.json
```

### CI/CD Integration
```yaml
# GitHub Actions example
- name: Run Security Scan
  run: |
    python -m src.web_scanner.main \
      --url ${{ secrets.TARGET_URL }} \
      --format json \
      --output report.json
```

---

## Uninstallation

### Remove Everything
```bash
# Deactivate virtual environment
deactivate

# Remove venv folder
rmdir /s venv

# Or reinstall
pip uninstall streamlit plotly pandas pillow -y
pip install --upgrade pip
```

---

## Support & Help

### Troubleshooting Resources
- Streamlit Docs: https://docs.streamlit.io
- Project Documentation: See `PROJECT_INDEX.md`
- Implementation Guide: See `IMPLEMENTATION_GUIDE.md`
- CLI Scanner: `python -m src.web_scanner.main --help`

### Getting Help
1. Check `STREAMLIT_GUIDE.md` for feature documentation
2. Review troubleshooting section above
3. Check project GitHub issues
4. Review logs for error messages

---

## Next Steps After Installation

1. **Customize the Interface**
   - Edit colors in CSS section of `streamlit_app.py`
   - Add custom metrics
   - Modify report templates

2. **Test with Sample Targets**
   - OWASP Juice Shop: http://localhost:3000
   - DVWA: http://localhost:8080
   - Your own applications

3. **Configure Advanced Features**
   - Add authentication to Streamlit
   - Setup result history
   - Create scanning profiles
   - Configure integrations

4. **Production Ready**
   - Review security checklist
   - Setup monitoring
   - Configure backups
   - Document procedures

---

*Streamlit Web UI - Setup & Deployment Guide v1.0*  
*Professional Web Vulnerability Scanner*
