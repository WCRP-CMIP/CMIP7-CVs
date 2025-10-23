#!/usr/bin/env python3
"""
Test script for the CMIP-LD SSL patches

This script demonstrates how to:
1. Start a local server with SSL auto-detection
2. Test JSON-LD context loading with SSL fixes
3. Handle HTTP/HTTPS protocol switching
"""

import sys
import os
import time
import requests

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from offline_patched import LD_server
from jsonld_ssl_debug import diagnose_jsonld_ssl_issue


def test_ssl_scenarios():
    """Test different SSL scenarios"""
    
    print("🧪 Testing CMIP-LD SSL Scenarios")
    print("=" * 50)
    
    # Test 1: Auto-detect SSL (default behavior)
    print("\n1️⃣  Testing SSL Auto-Detection")
    print("-" * 30)
    
    try:
        server = LD_server(use_ssl=None)  # Auto-detect
        url = server.start_server()
        print(f"✓ Server started: {url}")
        
        # Test a simple request
        try:
            response = requests.get(f"{url}/", verify=False, timeout=5)
            print(f"✓ Server responding: {response.status_code}")
        except Exception as e:
            print(f"⚠ Server request failed: {e}")
        
        server.stop_server()
        print("✓ Server stopped")
        
    except Exception as e:
        print(f"✗ Auto-detect test failed: {e}")
    
    time.sleep(1)
    
    # Test 2: Force HTTP (no SSL)
    print("\n2️⃣  Testing Force HTTP Mode")
    print("-" * 30)
    
    try:
        server = LD_server(use_ssl=False)  # Force HTTP
        url = server.start_server()
        print(f"✓ HTTP Server started: {url}")
        
        if url.startswith('http://'):
            print("✓ Correctly using HTTP protocol")
        else:
            print("⚠ Expected HTTP but got: " + url.split('://')[0])
        
        server.stop_server()
        print("✓ HTTP Server stopped")
        
    except Exception as e:
        print(f"✗ Force HTTP test failed: {e}")
    
    time.sleep(1)
    
    # Test 3: Force SSL (if possible)
    print("\n3️⃣  Testing Force SSL Mode")
    print("-" * 30)
    
    try:
        server = LD_server(use_ssl=True)  # Force SSL
        url = server.start_server()
        print(f"✓ SSL Server started: {url}")
        
        if url.startswith('https://'):
            print("✓ Correctly using HTTPS protocol")
        else:
            print(f"⚠ Expected HTTPS but got: {url.split('://')[0]} (SSL may not be available)")
        
        server.stop_server()
        print("✓ SSL Server stopped")
        
    except Exception as e:
        print(f"✗ Force SSL test failed: {e}")


def test_jsonld_context():
    """Test JSON-LD context loading"""
    
    print("\n🔗 Testing JSON-LD Context Loading")
    print("=" * 50)
    
    # Start a server for testing
    server = LD_server(use_ssl=None)  # Auto-detect
    url = server.start_server()
    
    try:
        # Test common context paths
        test_contexts = [
            "/cmip7/experiment/_context_",
            "/_context_",
            "/test/_context_"
        ]
        
        for context_path in test_contexts:
            print(f"\n🔍 Testing context: {context_path}")
            print("-" * 40)
            
            results = diagnose_jsonld_ssl_issue(url, context_path)
            
            if results['success']:
                print(f"✅ Context loading successful!")
                print(f"   Working URL: {results['final_url']}")
            else:
                print(f"❌ Context loading failed")
                print("📋 Recommendations:")
                for rec in results['recommendations']:
                    print(f"   • {rec}")
            
    finally:
        server.stop_server()
        print("\n✓ Test server stopped")


def demo_usage():
    """Demonstrate basic usage patterns"""
    
    print("\n📖 Usage Examples")
    print("=" * 50)
    
    print("""
Basic Usage:

1. Auto-detect SSL (recommended):
   server = LD_server()
   url = server.start_server()

2. Force HTTP only (no SSL issues):
   server = LD_server(use_ssl=False)
   url = server.start_server()

3. Force HTTPS (requires SSL setup):
   server = LD_server(use_ssl=True)
   url = server.start_server()

Command Line Usage:

1. Auto-detect SSL:
   python -m cmipld.utils.server_tools.offline_patched

2. Force HTTP:
   python -m cmipld.utils.server_tools.offline_patched --no-ssl

3. Force HTTPS:
   python -m cmipld.utils.server_tools.offline_patched --ssl

4. With repositories:
   python -m cmipld.utils.server_tools.offline_patched --repos repo1,repo2

5. Debug mode:
   python -m cmipld.utils.server_tools.offline_patched --debug --no-ssl
    """)


def main():
    """Main test function"""
    
    print("🚀 CMIP-LD SSL Patch Test Suite")
    print("================================")
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--test-ssl':
            test_ssl_scenarios()
        elif sys.argv[1] == '--test-jsonld':
            test_jsonld_context()
        elif sys.argv[1] == '--demo':
            demo_usage()
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Available options: --test-ssl, --test-jsonld, --demo")
    else:
        print("Available test options:")
        print("  --test-ssl     Test SSL scenarios")
        print("  --test-jsonld  Test JSON-LD context loading")
        print("  --demo         Show usage examples")
        print("\nExample: python test_ssl_patches.py --test-ssl")


if __name__ == "__main__":
    main()
