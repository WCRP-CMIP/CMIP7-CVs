import requests
from requests.adapters import HTTPAdapter
from urllib.parse import urlparse
import re
import ssl
import urllib3

from rich.console import Console, Group
from rich.table import Table
from rich.panel import Panel

# Disable SSL warnings for local development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class PrefixResolvingSession(requests.Session):
    def __init__(self, prefix_map, ssl_config=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix_map = prefix_map
        self.ssl_config = ssl_config or {}
        
        # Configure SSL settings for self-signed certificates
        if self.ssl_config.get('disable_ssl_verify', False):
            self.verify = False
        
    def request(self, method, url, *args, **kwargs):
        if ":" in url and not url.startswith(("http://", "https://")):
            prefix, path = url.split(":", 1)
            base = self.prefix_map.get(prefix)
            if base:
                url = base + path
            else:
                raise ValueError(f"Unknown prefix: {prefix}")
        
        # Handle SSL verification for local servers
        if 'verify' not in kwargs and self.ssl_config.get('disable_ssl_verify', False):
            kwargs['verify'] = False
            
        return super().request(method, url, *args, **kwargs)


class URLRewritingAdapter(HTTPAdapter):
    def __init__(self, redirect_rules, ssl_config=None, **kwargs):
        self.redirect_rules = redirect_rules
        self.ssl_config = ssl_config or {}
        super().__init__(**kwargs)

    def send(self, request, **kwargs):
        parsed = urlparse(request.url)
        host = parsed.hostname
        original_url = request.url

        # Apply redirect rules
        rules = self.redirect_rules.get(host, [])
        for rule in rules:
            new_url = rule['regex_in'].sub(rule['regex_out'], request.url)
            if new_url != request.url:
                request.url = new_url
                # Update host header if URL changed
                new_parsed = urlparse(request.url)
                request.headers['Host'] = new_parsed.hostname
                break

        # Handle protocol mismatch (HTTP -> HTTPS or HTTPS -> HTTP)
        if self.ssl_config.get('auto_protocol_fix', False):
            request.url = self._fix_protocol_mismatch(request.url, original_url)

        # Disable SSL verification for localhost/local servers
        if 'verify' not in kwargs:
            parsed_final = urlparse(request.url)
            if (parsed_final.hostname in ['localhost', '127.0.0.1'] and 
                parsed_final.scheme == 'https'):
                kwargs['verify'] = False

        return super().send(request, **kwargs)
    
    def _fix_protocol_mismatch(self, url, original_url):
        """
        Try to fix common protocol mismatches between HTTP and HTTPS
        """
        parsed = urlparse(url)
        
        # If this is a localhost URL, try both HTTP and HTTPS
        if parsed.hostname in ['localhost', '127.0.0.1']:
            # First try the URL as-is, but if it fails we'll let the retry logic handle it
            pass
            
        return url


class RequestRedirector:
    def __init__(self, redirect_rules=None, prefix_map=None, ssl_config=None):
        self.redirect_rules = { 
            host: [
                {
                    **rule,
                    "regex_in": re.compile(rule["regex_in"]) if isinstance(rule["regex_in"], str) else rule["regex_in"]
                }
                for rule in rules
            ]
            for host, rules in (redirect_rules or {}).items()
        }
        
        self.default_rules = self.redirect_rules.copy()
        self.prefix_map = prefix_map or {}
        self.default_prefix_map = self.prefix_map.copy()
        
        # SSL configuration for handling self-signed certificates
        self.ssl_config = ssl_config or {
            'disable_ssl_verify': True,  # Disable SSL verification for local development
            'auto_protocol_fix': True    # Try to fix HTTP/HTTPS mismatches
        }

        self.default_session = requests.Session
        self._patch_requests()

    def _patch_requests(self):
        session = PrefixResolvingSession(self.prefix_map, self.ssl_config)
        adapter = URLRewritingAdapter(self.redirect_rules, self.ssl_config)
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Configure session defaults for local development
        session.verify = False  # Disable SSL verification by default
        
        requests.sessions.Session = lambda: session

    def restore_defaults(self):
        self.redirect_rules = self.default_rules.copy()
        self.prefix_map = self.default_prefix_map.copy()
        requests.sessions.Session = self.default_session
        print("Restored default session and redirect rules.")

    def add_redirect(self, host, regex_in, regex_out):
        # Handle both string patterns and compiled regexes
        if isinstance(regex_in, str):
            regex_in = re.compile(regex_in)
            
        self.redirect_rules.setdefault(host, []).append({
            "regex_in": regex_in,
            "regex_out": regex_out
        })
        self._patch_requests()
        print(f"Added redirect: {host} | {regex_in.pattern} -> {regex_out}")

    def add_prefix(self, prefix, base_url):
        self.prefix_map[prefix] = base_url
        self._patch_requests()
        print(f"Added prefix: {prefix}: → {base_url}")

    def list_redirects(self):
        console = Console()
        table = Table(title="Regex-Based URL Redirects (by Host)", expand=True)

        table.add_column("Host", justify="center", style="cyan", no_wrap=True)
        table.add_column("Rules", justify="left", style="magenta")

        for host, rules in self.redirect_rules.items():
            host_panel = Panel(host, expand=True, width=30)
            rule_panels = [
                Panel(f"[bold]Match:[/bold] {rule['regex_in'].pattern}\n[bold]Replace:[/bold] {rule['regex_out']}", expand=True)
                for rule in rules
            ]
            rules_group = Group(*rule_panels)
            table.add_row(host_panel, rules_group)

        if self.prefix_map:
            prefix_panel = Panel(
                "\n".join(f"[cyan]{k}[/cyan]: {v}" for k, v in self.prefix_map.items()),
                title="Prefix Resolvers",
                border_style="green"
            )
            console.print(prefix_panel)

        console.print(table)

    @staticmethod
    def test_redirect(url, result=True):
        """Test URL redirection with proper SSL handling"""
        try:
            response = requests.get(url, verify=False, timeout=10)
            print(f"✓ Original URL: {url}")
            print(f"✓ Final URL: {response.url}")
            if result:
                print(f"✓ Status Code: {response.status_code}")
                if response.status_code == 200:
                    print(f"✓ Content preview: {response.text[:300]}...")
                else:
                    print(f"⚠ Response: {response.text[:200]}...")
        except requests.exceptions.SSLError as e:
            print(f"✗ SSL Error for {url}: {e}")
            # Try with HTTP instead of HTTPS
            if url.startswith('https://'):
                http_url = url.replace('https://', 'http://')
                print(f"  Retrying with HTTP: {http_url}")
                try:
                    response = requests.get(http_url, timeout=10)
                    print(f"✓ HTTP fallback successful: {response.status_code}")
                except Exception as e2:
                    print(f"✗ HTTP fallback also failed: {e2}")
        except requests.exceptions.ConnectionError as e:
            print(f"✗ Connection Error for {url}: {e}")
            # Try switching protocols
            if url.startswith('http://'):
                https_url = url.replace('http://', 'https://')
                print(f"  Retrying with HTTPS: {https_url}")
                try:
                    response = requests.get(https_url, verify=False, timeout=10)
                    print(f"✓ HTTPS fallback successful: {response.status_code}")
                except Exception as e2:
                    print(f"✗ HTTPS fallback also failed: {e2}")
        except Exception as e:
            print(f"✗ Error testing {url}: {e}")


class ProtocolAwareSession(requests.Session):
    """
    A requests session that can handle HTTP/HTTPS protocol switching
    for local development servers
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.verify = False  # Disable SSL verification for local dev
        
    def request(self, method, url, **kwargs):
        # Disable SSL verification for localhost
        parsed = urlparse(url)
        if parsed.hostname in ['localhost', '127.0.0.1']:
            kwargs.setdefault('verify', False)
            
        try:
            return super().request(method, url, **kwargs)
        except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as e:
            # Try switching protocols for localhost
            if parsed.hostname in ['localhost', '127.0.0.1']:
                if url.startswith('https://'):
                    alt_url = url.replace('https://', 'http://')
                elif url.startswith('http://'):
                    alt_url = url.replace('http://', 'https://')
                else:
                    raise e
                    
                print(f"Protocol switch attempt: {url} -> {alt_url}")
                kwargs.setdefault('verify', False)
                return super().request(method, alt_url, **kwargs)
            else:
                raise e


def patch_requests_for_local_ssl():
    """
    Monkey patch requests to handle local SSL certificates better
    """
    original_session = requests.Session
    
    def patched_session():
        session = ProtocolAwareSession()
        return session
    
    requests.Session = patched_session
    # Also patch the default session
    requests.sessions.Session = patched_session
    
    return original_session


def restore_requests(original_session=None):
    """
    Restore original requests behavior
    """
    if original_session:
        requests.Session = original_session
        requests.sessions.Session = original_session
