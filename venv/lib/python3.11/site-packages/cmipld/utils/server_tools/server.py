import http.server
import socketserver
import ssl
import threading
# import tempfile
import os,re
import subprocess
import shutil
from ..io import shell
from rich import print
from rich.console import Console
from rich.text import Text
from ...locations import mapping
from .monkeypatch_requests_patched import RequestRedirector
console = Console()

from ..logging.unique import UniqueLogger
log = UniqueLogger()

def check_openssl_available():
    """Check if OpenSSL is available in the system PATH."""
    return shutil.which('openssl') is not None

def create_self_signed_cert_python(certfile, keyfile):
    """
    Create a self-signed certificate using Python's cryptography library
    as a fallback when OpenSSL is not available.
    """
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        import datetime
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Create certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(u"localhost"),
                x509.IPAddress(u"127.0.0.1"),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        
        # Write certificate file
        with open(certfile, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        # Write private key file
        with open(keyfile, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        return True
        
    except ImportError:
        log.warn("cryptography library not available for SSL certificate generation")
        return False
    except Exception as e:
        log.warn(f"Failed to create SSL certificate with Python: {e}")
        return False

# class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
#     def end_headers(self):
#         self.send_header('Access-Control-Allow-Origin', '*')
#         self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
#         self.send_header('Access-Control-Allow-Headers', '*')
#         super().end_headers()

#     def do_OPTIONS(self):
#         self.send_response(200, "ok")
#         self.end_headers()

class LocalServer:
    def __init__(self, base_path, port=None, debug=False, use_ssl=None):
        self.base_path = base_path
        self.port = port
        self.debug = debug
        self.server = None
        self.thread = None
        self.requests = None
        self.prefix_map = None
        self.redirect_rules = None
        
        # SSL configuration
        self.use_ssl = use_ssl
        self.certfile = None
        self.keyfile = None
        self.ssl_available = False
        
        # Auto-detect SSL availability if not explicitly set
        if self.use_ssl is None:
            self.use_ssl = self._auto_detect_ssl()
        
        # Create SSL certificates if SSL is enabled
        if self.use_ssl:
            self.ssl_available = self._setup_ssl_certificates()
            if not self.ssl_available:
                log.warn("SSL setup failed, falling back to HTTP")
                self.use_ssl = False
        
        if not port:
            with socketserver.TCPServer(("", 0), http.server.SimpleHTTPRequestHandler) as temp_server:
                self.port = temp_server.server_address[1]
                log.debug(f"Using port: {self.port}")

    def _auto_detect_ssl(self):
        """Auto-detect if SSL should be used based on available tools."""
        openssl_available = check_openssl_available()
        
        if openssl_available:
            log.debug("OpenSSL detected - SSL will be enabled")
            return True
        
        # Check if cryptography library is available
        try:
            import cryptography
            log.debug("OpenSSL not found, but cryptography library available - SSL will be enabled with fallback")
            return True
        except ImportError:
            log.warn("Neither OpenSSL nor cryptography library available - SSL will be disabled")
            return False

    def _setup_ssl_certificates(self):
        """Set up SSL certificates using available methods."""
        self.certfile = os.path.join(self.base_path, 'temp_cert.pem')
        self.keyfile = os.path.join(self.base_path, 'temp_key.pem')
        
        # Try OpenSSL first
        if check_openssl_available():
            try:
                return self._create_ssl_certificates_openssl()
            except Exception as e:
                log.warn(f"OpenSSL certificate creation failed: {e}")
        
        # Fallback to Python cryptography library
        log.debug("Attempting SSL certificate creation with Python cryptography library")
        return create_self_signed_cert_python(self.certfile, self.keyfile)

    def _create_ssl_certificates_openssl(self):
        """Create self-signed SSL certificates using OpenSSL and return success status."""
        try:
            # Use OpenSSL to generate a self-signed certificate
            subprocess.run([
                'openssl', 'req', '-x509', '-newkey', 'rsa:4096', '-keyout', self.keyfile,
                '-out', self.certfile, '-days', '365', '-nodes', '-subj', '/CN=localhost', '-quiet'
            ], check=True)
            
            log.debug(f"Created SSL certificates with OpenSSL in: [bold #FF7900]{self.base_path}[/bold #FF7900]")
            return True
            
        except subprocess.CalledProcessError as e:
            log.warn(f"OpenSSL certificate creation failed: {e}")
            return False
        except FileNotFoundError:
            log.warn("OpenSSL not found in PATH")
            return False

    def create_ssl_certificates(self):
        """Legacy method for backward compatibility."""
        if self._setup_ssl_certificates():
            return self.certfile, self.keyfile
        else:
            raise RuntimeError("Failed to create SSL certificates")

    def start_server(self):
        """Start the HTTP/HTTPS server without changing the working directory."""
        self.stop_server()  # Ensure any existing server is stopped

        if not self.debug:
            http.server.SimpleHTTPRequestHandler.log_message = lambda *args: None
        else:
            http.server.SimpleHTTPRequestHandler.log_message = lambda *args: log.debug(
                f"[bold #FF7900] {str(args)} [/bold #FF7900] "
            )

        # Call the request redirector to handle the requests
        if not self.prefix_map:
            self.prefix_map = mapping  # from cmipld.mapping

        ssl_config = {
            'disable_ssl_verify': True,  # Always disable for local development
            'auto_protocol_fix': True    # Enable protocol switching
        }
        
        self.requests = RequestRedirector(
            prefix_map=self.prefix_map,
            redirect_rules=self.redirect_rules or {},
            ssl_config=ssl_config
        )

        # # Test redirect with the appropriate protocol
        # test_protocol = "https" if self.use_ssl else "http"
        # test_url = f'{test_protocol}://wcrp-cmip.github.io/WCRP-universe/bob'
        # print(f"Testing redirect with: {test_url}")
        # try:
        #     self.requests.test_redirect(test_url)
        # except Exception as e:
        #     log.warn(f"Redirect test failed (this is usually ok): {e}")

        # Define a custom handler that serves files from the specified base_path
        handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(
            *args, directory=self.base_path, **kwargs
        )

        socketserver.TCPServer.allow_reuse_address = True
        self.server = socketserver.TCPServer(("", self.port), handler)

        # Wrap the server with SSL if enabled
        if self.use_ssl and self.ssl_available:
            try:
                # Create an SSL context
                context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                context.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)

                # Wrap the server socket with SSL
                self.server.socket = context.wrap_socket(
                    self.server.socket, server_side=True)
                
                protocol = "https"
                log.debug(f"[bold orange]Serving[/bold orange] [italic #FF7900]{self.base_path}[/italic #FF7900] at [bold magenta]https://localhost:{self.port}[/bold magenta]")
                
            except Exception as e:
                log.warn(f"SSL setup failed at runtime: {e}, falling back to HTTP")
                self.use_ssl = False
                protocol = "http"
                log.debug(f"[bold orange]Serving[/bold orange] [italic #FF7900]{self.base_path}[/italic #FF7900] at [bold cyan]http://localhost:{self.port}[/bold cyan]")
        else:
            protocol = "http"
            log.debug(f"[bold orange]Serving[/bold orange] [italic #FF7900]{self.base_path}[/italic #FF7900] at [bold cyan]http://localhost:{self.port}[/bold cyan]")

        def run_server():
            self.server.serve_forever()

        # Start the server in a separate thread
        self.thread = threading.Thread(target=run_server, daemon=True)
        self.thread.start()
        return f"{protocol}://localhost:{self.port}"

    def stop_server(self):
        """Stop the HTTP/HTTPS server if it's running."""
        if self.server:
            print("Shutting down the server...")
            self.server.shutdown()
            self.thread.join()
            self.server = None
            self.thread = None
            self.requests.restore_defaults()
            log.info("[bold yellow]Server stopped.[/bold yellow]")
            

    def test(self, **args):
        return self.requests.test_redirect(**args)
    