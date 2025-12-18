"""
HTTP client for Zillow scraping using curl_cffi
Bypasses anti-bot detection by impersonating real browsers
"""

from curl_cffi import requests
from typing import Optional
import random


class HTTPClient:
    """
    Simple HTTP client using curl_cffi for anti-bot bypass

    Uses curl_cffi's browser impersonation to bypass Zillow's anti-bot protection.
    Much faster and lighter than Playwright - no browser needed!

    Anti-detection features:
    - User agent rotation (Chrome, Firefox, Safari, Edge)
    - Referrer header simulation (navigation patterns)
    - Session/cookie persistence
    - Accept-Language rotation
    - Random browser versions
    """

    # User agents pool - rotate between different browsers and OS
    # NOTE: Includes both desktop AND mobile user agents for better anti-detection
    # Mobile user agents help bypass IP restrictions (some IPs blocked for desktop but not mobile)
    USER_AGENTS = [
        # ===== MOBILE USER AGENTS (iOS Safari) =====
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        # ===== MOBILE USER AGENTS (Android Chrome) =====
        "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.39 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.58 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.70 Mobile Safari/537.36",
        # ===== DESKTOP USER AGENTS =====
        # Chrome on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        # Chrome on Mac
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        # Firefox on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
        # Firefox on Mac
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:132.0) Gecko/20100101 Firefox/132.0",
        # Safari on Mac
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15",
        # Edge on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    ]

    # Accept-Language pool - simulate users from different regions
    ACCEPT_LANGUAGES = [
        "en-US,en;q=0.9",
        "en-US,en;q=0.9,es;q=0.8",
        "en-GB,en;q=0.9",
        "en-US,en;q=0.8",
        "en-CA,en;q=0.9",
    ]

    # Mobile user agents only (for restricted IPs)
    MOBILE_USER_AGENTS = [
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.39 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.58 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.70 Mobile Safari/537.36",
    ]

    def __init__(
        self,
        timeout: int = 30,
        proxy: Optional[str] = None,
        mobile_only: bool = True  # Default to mobile-only for better bypass
    ):
        """
        Initialize HTTP client

        Args:
            timeout: Request timeout in seconds (default: 30)
            proxy: Proxy URL in format 'http://user:pass@host:port'
            mobile_only: Use mobile user agents only (better for restricted IPs)
        """
        self.timeout = timeout
        self.proxy = proxy
        self.mobile_only = mobile_only

        # Setup proxies dict if provided
        self.proxies = None
        if proxy:
            self.proxies = {
                "http": proxy,
                "https": proxy
            }

        # Session for cookie persistence (like a real browser)
        self.session = requests.Session()

        # Pick random user agent and language for this session (stays consistent)
        # Use mobile-only UAs by default for better IP restriction bypass
        if mobile_only:
            self.user_agent = random.choice(self.MOBILE_USER_AGENTS)
        else:
            self.user_agent = random.choice(self.USER_AGENTS)

        self.accept_language = random.choice(self.ACCEPT_LANGUAGES)

        # Determine if mobile user agent (for curl_cffi impersonate parameter)
        self.is_mobile = "Mobile" in self.user_agent or "iPhone" in self.user_agent or "Android" in self.user_agent

        # Track last visited URL for referrer headers
        self.last_url = None

        # Warm-up flag
        self._warmed_up = False

    def warmup(self):
        """
        Warm-up the session by visiting Zillow homepage first
        Simulates real user navigation pattern
        """
        if self._warmed_up:
            return

        try:
            print("🔥 Warming up session (visiting Zillow homepage)...")
            homepage_url = "https://www.zillow.com"

            # Build headers for homepage visit
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": self.accept_language,
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",  # Direct navigation (typed URL or bookmark)
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": self.user_agent,
            }

            # Use appropriate impersonate: safari_ios for mobile, chrome124 for desktop
            # For mobile, skip impersonate to avoid fingerprint mismatch
            if self.is_mobile:
                response = self.session.get(
                    homepage_url,
                    timeout=self.timeout,
                    proxies=self.proxies,
                    headers=headers
                )
            else:
                response = self.session.get(
                    homepage_url,
                    timeout=self.timeout,
                    proxies=self.proxies,
                    impersonate="chrome124",
                    headers=headers
                )

            response.raise_for_status()
            self.last_url = homepage_url
            self._warmed_up = True
            print("   ✅ Session warmed up")

        except Exception as e:
            print(f"   ⚠️  Warmup failed (continuing anyway): {e}")

    def get_page_html(self, url: str, is_profile: bool = False) -> str:
        """
        Fetch page HTML using curl_cffi with browser impersonation

        Args:
            url: URL to fetch
            is_profile: Whether this is a profile page (for referrer simulation)

        Returns:
            Page HTML content

        Raises:
            Exception: If request fails
        """
        try:
            # Warm up session on first request
            if not self._warmed_up:
                self.warmup()

            print(f"🌐 Fetching: {url}")

            # Determine Sec-Fetch-Site based on navigation pattern
            if self.last_url:
                # Coming from another page on Zillow
                sec_fetch_site = "same-origin"
            else:
                # Direct navigation (first request or after warmup)
                sec_fetch_site = "none"

            # Build headers with referrer if we have a last URL
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": self.accept_language,
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": sec_fetch_site,
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": self.user_agent,
            }

            # Add referrer header if we have previous URL (critical for looking human!)
            if self.last_url:
                headers["Referer"] = self.last_url

            # Use session for cookie persistence
            # Use appropriate impersonate: skip for mobile, chrome124 for desktop
            if self.is_mobile:
                response = self.session.get(
                    url,
                    timeout=self.timeout,
                    proxies=self.proxies,
                    headers=headers
                )
            else:
                response = self.session.get(
                    url,
                    timeout=self.timeout,
                    proxies=self.proxies,
                    impersonate="chrome124",
                    headers=headers
                )

            response.raise_for_status()

            html = response.text
            print(f"✅ Page loaded successfully ({len(html):,} bytes)")

            # Update last URL for next request's referrer
            self.last_url = url

            return html

        except Exception as e:
            # Check if it's an HTTP error by looking at the response
            if hasattr(e, 'response') and hasattr(e.response, 'status_code'):
                if e.response.status_code == 403:
                    raise Exception(
                        f"❌ 403 Forbidden. Zillow blocked the request.\n"
                        f"This shouldn't happen with anti-detection features enabled.\n"
                        f"Try using a proxy or wait before retrying."
                    )
                else:
                    raise Exception(f"❌ HTTP Error {e.response.status_code}: {e}")
            else:
                raise Exception(f"❌ Failed to fetch page: {e}")

    def close(self):
        """
        Close client (placeholder for consistency with Playwright version)

        curl_cffi doesn't need cleanup like Playwright did
        """
        pass

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

    def __del__(self):
        """Cleanup on object destruction"""
        self.close()
