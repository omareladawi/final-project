"""Enhanced session management with authentication state validation."""
import aiohttp
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import http.cookies
from bs4 import BeautifulSoup


class SessionManager:
    """Manage authenticated sessions with state validation."""
    
    logger = logging.getLogger(__name__)
    
    def __init__(self, verify_ssl: bool = False, timeout: int = 10):
        """Initialize session manager."""
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
        self.auth_state = {
            "authenticated": False,
            "username": None,
            "timestamp": None,
            "cookies": {},
            "auth_headers": {},
            "validation_count": 0,
            "failed_validations": 0,
        }
        self.session_created_at = None
    
    async def create_session(self) -> aiohttp.ClientSession:
        """Create and return an aiohttp session."""
        if self.session and not self.session.closed:
            return self.session
        
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        connector = aiohttp.TCPConnector(ssl=self.verify_ssl)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=self._get_default_headers(),
        )
        self.session_created_at = datetime.now()
        
        self.logger.debug(
            f"Session created with {self.timeout}s timeout, "
            f"SSL verification: {self.verify_ssl}"
        )
        return self.session
    
    async def close_session(self) -> None:
        """Close the current session."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.logger.debug("Session closed")
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default HTTP headers."""
        return {
            "User-Agent": "Mozilla/5.0 (Security Scanner/1.0)",
            "Accept": "text/html,application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
        }
    
    async def authenticate(
        self, 
        login_url: str,
        username: str,
        password: str,
        username_field: str = "username",
        password_field: str = "password",
    ) -> bool:
        """Attempt to authenticate with credentials."""
        try:
            session = await self.create_session()
            # Only reject local file paths, not valid host-relative login paths
            parsed_login_url = urlparse(login_url)
            if parsed_login_url.scheme and parsed_login_url.scheme not in {"http", "https"}:
                self.logger.warning(
                    f"Unsupported login URL scheme detected: {login_url}."
                )
                return False
            if not parsed_login_url.scheme and login_url.startswith(("C:\\", "c:\\")):
                self.logger.warning(
                    f"Invalid login URL detected: {login_url}. This looks like a local file path."
                )
                return False
            self.logger.debug(f"Attempting authentication to {login_url}")

            async with session.get(
                login_url,
                timeout=self.timeout,
                ssl=self.verify_ssl,
                allow_redirects=True,
                headers=self._get_default_headers(),
            ) as initial_response:
                login_page = await initial_response.text()
                login_action = login_url
                form = BeautifulSoup(login_page, "html.parser").find("form")
                payload = {}

                if form is not None:
                    action_attr = form.get("action")
                    method_attr = (form.get("method") or "post").lower()
                    if action_attr:
                        login_action = urljoin(login_url, action_attr)

                    for input_field in form.find_all("input"):
                        input_name = input_field.get("name")
                        if not input_name:
                            continue
                        input_type = (input_field.get("type") or "text").lower()
                        input_value = input_field.get("value") or ""
                        payload[input_name] = input_value

                        if input_type in {"text", "email"} and username_field == "username":
                            username_field = input_name
                        if input_type == "password" and password_field == "password":
                            password_field = input_name

                payload[username_field] = username
                payload[password_field] = password

            self.logger.debug(f"Submitting authentication payload to {login_action}")
            async with session.post(
                login_action,
                data=payload,
                allow_redirects=True,
                ssl=self.verify_ssl,
                headers=self._get_default_headers(),
            ) as response:
                for cookie in session.cookie_jar:
                    self.auth_state["cookies"][cookie.key] = cookie.value

                content = await response.text()
                if response.status in {200, 302, 303, 307} and self._check_auth_success(content):
                    self.auth_state["authenticated"] = True
                    self.auth_state["username"] = username
                    self.auth_state["timestamp"] = datetime.now()
                    self.logger.info(f"Authentication successful for user: {username}")
                    return True

                self.logger.warning(f"Authentication failed for user: {username}")
                return False
        except Exception as exc:
            self.logger.error(f"Authentication error: {str(exc)}")
            return False
    
    def _check_auth_success(self, content: str) -> bool:
        """Check if authentication was successful based on response content."""
        # Simple heuristics
        failure_indicators = [
            "invalid",
            "unauthorized",
            "forbidden",
            "login failed",
            "incorrect",
            "denied",
        ]
        
        success_indicators = [
            "dashboard",
            "welcome",
            "profile",
            "account",
            "logged in",
            "authenticated",
        ]
        
        content_lower = content.lower()
        
        # Check for failure indicators
        for indicator in failure_indicators:
            if indicator in content_lower:
                return False
        
        # Check for success indicators
        for indicator in success_indicators:
            if indicator in content_lower:
                return True
        
        # If no clear indicators, assume success (allow user to verify)
        return True
    
    async def validate_session(self, validation_url: str) -> bool:
        """Validate that authentication is still active."""
        try:
            session = await self.create_session()
            
            self.auth_state["validation_count"] += 1
            
            async with session.get(
                validation_url,
                allow_redirects=True,
                ssl=self.verify_ssl,
            ) as response:
                if response.status == 401 or response.status == 403:
                    self.logger.warning("Session validation failed - authentication expired")
                    self.auth_state["authenticated"] = False
                    self.auth_state["failed_validations"] += 1
                    return False
                
                self.logger.debug("Session validation successful")
                return True
        
        except Exception as exc:
            self.logger.error(f"Session validation error: {str(exc)}")
            self.auth_state["failed_validations"] += 1
            return False
    
    async def detect_session_expiration(self, test_url: str) -> bool:
        """Detect if session has expired by testing a protected endpoint."""
        try:
            session = await self.create_session()
            
            async with session.get(test_url, allow_redirects=False) as response:
                # Check for redirect to login
                if response.status in [301, 302, 303, 307, 308]:
                    location = response.headers.get('Location', '').lower()
                    if 'login' in location or 'auth' in location:
                        self.logger.warning("Session appears to have expired (redirect to login)")
                        self.auth_state["authenticated"] = False
                        return True
                
                # Check for 401/403
                if response.status in [401, 403]:
                    self.logger.warning("Session appears to have expired (403/401 response)")
                    self.auth_state["authenticated"] = False
                    return True
            
            return False
        
        except Exception as exc:
            self.logger.error(f"Expiration detection error: {str(exc)}")
            return False
    
    def get_session_cookies(self) -> Dict[str, str]:
        """Get current session cookies."""
        if not self.session:
            return {}
        
        cookies = {}
        for cookie in self.session.cookie_jar:
            cookies[cookie.key] = cookie.value
        
        return cookies
    
    def get_auth_state(self) -> Dict[str, Any]:
        """Get current authentication state."""
        return {
            "authenticated": self.auth_state["authenticated"],
            "username": self.auth_state["username"],
            "authenticated_since": (
                self.auth_state["timestamp"].isoformat()
                if self.auth_state["timestamp"] else None
            ),
            "session_age_seconds": (
                (datetime.now() - self.session_created_at).total_seconds()
                if self.session_created_at else None
            ),
            "validation_attempts": self.auth_state["validation_count"],
            "failed_validations": self.auth_state["failed_validations"],
            "cookie_count": len(self.get_session_cookies()),
        }
    
    def is_authenticated(self) -> bool:
        """Check if currently authenticated."""
        if not self.auth_state["authenticated"]:
            return False
        
        # Check if session is too old (24 hours)
        if self.auth_state["timestamp"]:
            age = datetime.now() - self.auth_state["timestamp"]
            if age > timedelta(hours=24):
                self.logger.warning("Session too old, marking as expired")
                self.auth_state["authenticated"] = False
                return False
        
        return True
    
    async def cleanup(self) -> None:
        """Clean up session resources."""
        await self.close_session()
        self.logger.debug("Session manager cleaned up")
