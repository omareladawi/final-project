"""Improved web crawler for comprehensive URL and form discovery."""
from typing import Set, Dict, List, Tuple, Optional
from urllib.parse import urljoin, urlparse
import re
import logging


class WebCrawler:
    """Extract URLs and forms from HTML with deduplication and filtering."""
    
    # Static asset patterns to skip
    STATIC_ASSET_PATTERNS = [
        r'\.(jpg|jpeg|png|gif|svg|ico|webp|bmp|tiff)$',  # Images
        r'\.(css|less|scss)$',  # Stylesheets
        r'\.(js|ts)$',  # Scripts
        r'\.(woff|woff2|ttf|eot|otf)$',  # Fonts
        r'\.(mp4|webm|mp3|wav|ogg|m4a)$',  # Media
        r'\.(zip|tar|gz|rar|7z|exe|dmg|pkg)$',  # Archives
        r'\.(pdf|doc|docx|xls|xlsx|ppt|pptx)$',  # Documents
    ]
    
    # Query parameter patterns that indicate non-crawlable content
    SKIP_PARAM_PATTERNS = [
        r'.*logout.*',
        r'.*delete.*',
        r'.*remove.*',
        r'.*unsubscribe.*',
    ]
    
    logger = logging.getLogger(__name__)
    
    def __init__(self, base_url: str, max_crawl_depth: int = 2):
        """Initialize the crawler."""
        self.base_url = base_url
        self.base_domain = urlparse(base_url).netloc
        self.max_crawl_depth = max_crawl_depth
        self.discovered_urls: Set[str] = set()
        self.discovered_forms: List[Dict] = []
    
    def is_internal_url(self, url: str) -> bool:
        """Check if URL belongs to target domain."""
        try:
            parsed = urlparse(url)
            # Allow relative URLs and same-domain URLs
            if not parsed.netloc:
                return True
            return parsed.netloc == self.base_domain
        except Exception:
            return False
    
    def is_static_asset(self, url: str) -> bool:
        """Check if URL points to static asset to skip."""
        url_lower = url.lower()
        for pattern in self.STATIC_ASSET_PATTERNS:
            if re.search(pattern, url_lower):
                return True
        return False
    
    def should_skip_url(self, url: str) -> bool:
        """Check if URL should be skipped."""
        url_lower = url.lower()
        
        # Skip fragments
        if url.startswith('#'):
            return True
        
        # Skip javascript
        if url.startswith('javascript:'):
            return True
        
        # Skip mailto
        if url.startswith('mailto:'):
            return True
        
        # Skip static assets
        if self.is_static_asset(url):
            return True
        
        # Skip suspicious parameters
        for pattern in self.SKIP_PARAM_PATTERNS:
            if re.search(pattern, url_lower):
                return True
        
        return False
    
    def normalize_url(self, url: str, relative_to: Optional[str] = None) -> Optional[str]:
        """Normalize and validate a URL."""
        if not url or self.should_skip_url(url):
            return None
        
        # Resolve relative URLs
        base = relative_to or self.base_url
        try:
            absolute_url = urljoin(base, url)
        except Exception:
            return None
        
        # Check if internal
        if not self.is_internal_url(absolute_url):
            return None
        
        # Remove fragments
        parsed = urlparse(absolute_url)
        clean_url = parsed._replace(fragment='').geturl()
        
        return clean_url
    
    def extract_urls_from_html(
        self, html: str, page_url: str
    ) -> Tuple[Set[str], int]:
        """Extract all URLs from HTML content."""
        discovered_new = 0
        
        # Extract from <a> tags
        a_href_pattern = r'href=["\']([^"\']+)["\']'
        for match in re.finditer(a_href_pattern, html, re.IGNORECASE):
            url = match.group(1)
            normalized = self.normalize_url(url, page_url)
            if normalized and normalized not in self.discovered_urls:
                self.discovered_urls.add(normalized)
                discovered_new += 1
        
        # Extract from <form> action
        form_action_pattern = r'<form[^>]*action=["\']([^"\']+)["\']'
        for match in re.finditer(form_action_pattern, html, re.IGNORECASE):
            url = match.group(1)
            normalized = self.normalize_url(url, page_url)
            if normalized and normalized not in self.discovered_urls:
                self.discovered_urls.add(normalized)
                discovered_new += 1
        
        # Extract from redirect/meta tags
        meta_redirect_pattern = r'<meta\s+http-equiv=["\']?refresh["\']?[^>]*content=["\']([^"\']+)["\']'
        for match in re.finditer(meta_redirect_pattern, html, re.IGNORECASE):
            content = match.group(1)
            # Extract URL from "5;url=..."
            url_match = re.search(r'url=([^\s;]+)', content, re.IGNORECASE)
            if url_match:
                url = url_match.group(1).strip('\'"')
                normalized = self.normalize_url(url, page_url)
                if normalized and normalized not in self.discovered_urls:
                    self.discovered_urls.add(normalized)
                    discovered_new += 1
        
        # Extract from onclick handlers (basic)
        onclick_pattern = r'onclick=["\']([^"\']*)(location|href|window\.open)\(["\']?([^"\']+)["\']?'
        for match in re.finditer(onclick_pattern, html, re.IGNORECASE):
            url = match.group(3)
            normalized = self.normalize_url(url, page_url)
            if normalized and normalized not in self.discovered_urls:
                self.discovered_urls.add(normalized)
                discovered_new += 1
        
        # Extract from URL parameters
        param_pattern = r'(https?://[^\s"\'<>]+)'
        for match in re.finditer(param_pattern, html):
            url = match.group(1)
            normalized = self.normalize_url(url, page_url)
            if normalized and normalized not in self.discovered_urls:
                self.discovered_urls.add(normalized)
                discovered_new += 1
        
        return self.discovered_urls, discovered_new
    
    def extract_forms_from_html(self, html: str, page_url: str) -> List[Dict]:
        """Extract form information from HTML."""
        forms = []
        
        # Simple form extraction
        form_pattern = r'<form[^>]*>(.*?)</form>'
        for form_match in re.finditer(form_pattern, html, re.IGNORECASE | re.DOTALL):
            form_html = form_match.group(0)
            
            # Extract form attributes
            action_match = re.search(r'action=["\']([^"\']+)["\']', form_html, re.IGNORECASE)
            method_match = re.search(r'method=["\']([^"\']+)["\']', form_html, re.IGNORECASE)
            
            action = action_match.group(1) if action_match else ""
            method = method_match.group(1).upper() if method_match else "GET"
            
            # Normalize form action
            normalized_action = self.normalize_url(action, page_url) if action else page_url
            if not normalized_action:
                continue
            
            # Extract input fields
            fields = []
            input_pattern = r'<input[^>]*>'
            for input_match in re.finditer(input_pattern, form_html, re.IGNORECASE):
                input_html = input_match.group(0)
                
                name_match = re.search(r'name=["\']?([^\s"\']+)["\']?', input_html, re.IGNORECASE)
                type_match = re.search(r'type=["\']?([^\s"\']+)["\']?', input_html, re.IGNORECASE)
                
                if name_match:
                    field_name = name_match.group(1)
                    field_type = type_match.group(1).lower() if type_match else "text"
                    fields.append({
                        "name": field_name,
                        "type": field_type,
                    })
            
            # Extract textarea fields
            textarea_pattern = r'<textarea[^>]*name=["\']?([^\s"\']+)["\']?[^>]*>'
            for textarea_match in re.finditer(textarea_pattern, form_html, re.IGNORECASE):
                field_name = textarea_match.group(1)
                fields.append({
                    "name": field_name,
                    "type": "textarea",
                })
            
            if fields or not action:  # Include form even with no fields if has action
                form_info = {
                    "action": normalized_action,
                    "method": method,
                    "fields": fields,
                    "found_on_page": page_url,
                }
                forms.append(form_info)
                self.discovered_forms.append(form_info)
        
        return forms
    
    def extract_parameters_from_html(self, html: str) -> Set[str]:
        """Extract all input parameter names from HTML."""
        parameters = set()
        
        # From input fields
        input_pattern = r'<input[^>]*name=["\']?([^\s"\']+)["\']?'
        for match in re.finditer(input_pattern, html, re.IGNORECASE):
            parameters.add(match.group(1))
        
        # From textarea
        textarea_pattern = r'<textarea[^>]*name=["\']?([^\s"\']+)["\']?'
        for match in re.finditer(textarea_pattern, html, re.IGNORECASE):
            parameters.add(match.group(1))
        
        # From select
        select_pattern = r'<select[^>]*name=["\']?([^\s"\']+)["\']?'
        for match in re.finditer(select_pattern, html, re.IGNORECASE):
            parameters.add(match.group(1))
        
        # From URL query string patterns
        query_pattern = r'[\?&]([a-zA-Z_][a-zA-Z0-9_]*)\s*='
        for match in re.finditer(query_pattern, html):
            parameters.add(match.group(1))
        
        return parameters
    
    def get_crawl_statistics(self) -> Dict:
        """Get crawling statistics."""
        return {
            "total_urls_discovered": len(self.discovered_urls),
            "forms_discovered": len(self.discovered_forms),
            "urls": sorted(list(self.discovered_urls)),
            "forms": self.discovered_forms,
        }
