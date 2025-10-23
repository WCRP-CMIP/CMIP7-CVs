"""
JSON-LD SSL debugging and fixing utilities for CMIP-LD
"""

import requests
import json
from urllib.parse import urlparse
import ssl
import urllib3
from typing import Dict, Any, Optional

# Disable SSL warnings for local development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class JsonLdSSLFixer:
    """
    Utility class to handle JSON-LD context loading with SSL issues
    """
    
    def __init__(self, server_url: str):
        self.server_url = server_url.rstrip('/')
        self.parsed_server = urlparse(self.server_url)
        self.is_https = self.parsed_server.scheme == 'https'
        
        # Create a session configured for local development
        self.session = requests.Session()
        self.session.verify = False  # Disable SSL verification
        
        # Configure adapters for both HTTP and HTTPS
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def test_context_url(self, context_path: str) -> Dict[str, Any]:
        """
        Test accessing a JSON-LD context URL and provide diagnostic information
        """
        results = {
            'context_path': context_path,
            'attempts': [],
            'success': False,
            'final_url': None,
            'content': None,
            'recommendations': []
        }
        
        # Try different URL combinations
        urls_to_try = [
            f"{self.server_url}{context_path}",
            f"{self.server_url}/{context_path.lstrip('/')}",
        ]
        
        # If running HTTPS, also try HTTP
        if self.is_https:
            http_server = self.server_url.replace('https://', 'http://')
            urls_to_try.extend([
                f"{http_server}{context_path}",
                f"{http_server}/{context_path.lstrip('/')}"
            ])
        # If running HTTP, also try HTTPS  
        else:
            https_server = self.server_url.replace('http://', 'https://')
            urls_to_try.extend([
                f"{https_server}{context_path}",
                f"{https_server}/{context_path.lstrip('/')}"
            ])
        
        for url in urls_to_try:
            attempt = self._try_url(url)
            results['attempts'].append(attempt)
            
            if attempt['success']:
                results['success'] = True
                results['final_url'] = url
                results['content'] = attempt['content']
                break
        
        # Generate recommendations
        results['recommendations'] = self._generate_recommendations(results)
        
        return results
    
    def _try_url(self, url: str) -> Dict[str, Any]:
        """
        Try to access a single URL and return detailed results
        """
        attempt = {
            'url': url,
            'success': False,
            'status_code': None,
            'error': None,
            'content': None,
            'headers': {},
            'is_json': False
        }
        
        try:
            response = self.session.get(url, timeout=10)
            attempt['status_code'] = response.status_code
            attempt['headers'] = dict(response.headers)
            
            if response.status_code == 200:
                attempt['content'] = response.text
                attempt['success'] = True
                
                # Check if it's valid JSON
                try:
                    json.loads(response.text)
                    attempt['is_json'] = True
                except json.JSONDecodeError:
                    attempt['is_json'] = False
            
        except requests.exceptions.SSLError as e:
            attempt['error'] = f"SSL Error: {str(e)}"
        except requests.exceptions.ConnectionError as e:
            attempt['error'] = f"Connection Error: {str(e)}"
        except requests.exceptions.Timeout as e:
            attempt['error'] = f"Timeout: {str(e)}"
        except Exception as e:
            attempt['error'] = f"Unknown Error: {str(e)}"
        
        return attempt
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> list:
        """
        Generate recommendations based on test results
        """
        recommendations = []
        
        if not results['success']:
            # No successful attempts
            ssl_errors = [a for a in results['attempts'] if 'SSL Error' in str(a.get('error', ''))]
            connection_errors = [a for a in results['attempts'] if 'Connection Error' in str(a.get('error', ''))]
            
            if ssl_errors:
                recommendations.append(
                    "SSL Certificate issues detected. Try running server with --no-ssl flag for HTTP-only mode."
                )
                recommendations.append(
                    "For production, ensure SSL certificates are properly configured."
                )
            
            if connection_errors:
                recommendations.append(
                    "Connection refused - check if server is running and accessible."
                )
                recommendations.append(
                    "Verify the server URL and port are correct."
                )
            
            recommendations.append(
                "Try testing individual URLs manually with curl or wget."
            )
        
        else:
            # Successful attempt
            if not results['content']:
                recommendations.append("URL accessible but returned empty content.")
            elif results['attempts'][0]['is_json']:
                recommendations.append("✓ JSON-LD context loaded successfully!")
            else:
                recommendations.append("Content loaded but may not be valid JSON - check format.")
        
        return recommendations
    
    def fix_json_ld_processor_ssl(self):
        """
        Apply monkey patches to help JSON-LD processors work with local SSL
        """
        # Patch requests globally for JSON-LD libraries
        original_get = requests.get
        
        def patched_get(url, **kwargs):
            # For localhost URLs, disable SSL verification
            parsed = urlparse(url)
            if parsed.hostname in ['localhost', '127.0.0.1']:
                kwargs.setdefault('verify', False)
                
                # Try the original URL first
                try:
                    return original_get(url, **kwargs)
                except (requests.exceptions.SSLError, requests.exceptions.ConnectionError):
                    # Try switching protocols for localhost
                    if url.startswith('https://'):
                        alt_url = url.replace('https://', 'http://')
                        print(f"SSL failed, trying HTTP: {alt_url}")
                        return original_get(alt_url, **kwargs)
                    elif url.startswith('http://'):
                        alt_url = url.replace('http://', 'https://')
                        print(f"HTTP failed, trying HTTPS: {alt_url}")
                        kwargs.setdefault('verify', False)
                        return original_get(alt_url, **kwargs)
            
            return original_get(url, **kwargs)
        
        # Apply the patch
        requests.get = patched_get
        
        print("Applied JSON-LD SSL compatibility patches")
        return original_get
    
    def restore_requests(self, original_get):
        """
        Restore original requests.get function
        """
        requests.get = original_get
        print("Restored original requests behavior")


def diagnose_jsonld_ssl_issue(server_url: str, context_path: str):
    """
    Comprehensive diagnosis of JSON-LD SSL issues
    """
    print(f"🔍 Diagnosing JSON-LD SSL issue...")
    print(f"   Server: {server_url}")
    print(f"   Context: {context_path}")
    print()
    
    fixer = JsonLdSSLFixer(server_url)
    results = fixer.test_context_url(context_path)
    
    print("📊 Test Results:")
    print(f"   Success: {'✓' if results['success'] else '✗'}")
    
    if results['success']:
        print(f"   Working URL: {results['final_url']}")
        print(f"   Content Length: {len(results['content']) if results['content'] else 0} characters")
    
    print("\n🔍 Detailed Attempts:")
    for i, attempt in enumerate(results['attempts'], 1):
        status = "✓" if attempt['success'] else "✗"
        print(f"   {i}. {status} {attempt['url']}")
        if attempt['error']:
            print(f"      Error: {attempt['error']}")
        elif attempt['success']:
            print(f"      Status: {attempt['status_code']}")
            print(f"      JSON Valid: {'Yes' if attempt['is_json'] else 'No'}")
    
    print("\n💡 Recommendations:")
    for rec in results['recommendations']:
        print(f"   • {rec}")
    
    return results


def apply_global_jsonld_ssl_fix():
    """
    Apply global patches to make JSON-LD work with local SSL servers
    """
    import requests
    import urllib3
    
    # Disable SSL warnings
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Store original functions
    original_get = requests.get
    original_session = requests.Session
    
    def patched_get(url, **kwargs):
        parsed = urlparse(url)
        if parsed.hostname in ['localhost', '127.0.0.1']:
            kwargs.setdefault('verify', False)
            
            try:
                return original_get(url, **kwargs)
            except requests.exceptions.SSLError:
                if url.startswith('https://'):
                    alt_url = url.replace('https://', 'http://')
                    print(f"🔄 SSL issue, trying HTTP: {alt_url}")
                    return original_get(alt_url, **kwargs)
                raise
            except requests.exceptions.ConnectionError:
                if url.startswith('http://'):
                    alt_url = url.replace('http://', 'https://')
                    print(f"🔄 Connection issue, trying HTTPS: {alt_url}")
                    kwargs.setdefault('verify', False)
                    return original_get(alt_url, **kwargs)
                raise
        
        return original_get(url, **kwargs)
    
    class PatchedSession(requests.Session):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.verify = False
        
        def get(self, url, **kwargs):
            return patched_get(url, **kwargs)
    
    # Apply patches
    requests.get = patched_get
    requests.Session = PatchedSession
    
    print("🔧 Applied global JSON-LD SSL compatibility patches")
    
    return {'original_get': original_get, 'original_session': original_session}


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python jsonld_ssl_debug.py <server_url> <context_path>")
        print("Example: python jsonld_ssl_debug.py https://localhost:8081 /cmip7/experiment/_context_")
        sys.exit(1)
    
    server_url = sys.argv[1]
    context_path = sys.argv[2]
    
    diagnose_jsonld_ssl_issue(server_url, context_path)
