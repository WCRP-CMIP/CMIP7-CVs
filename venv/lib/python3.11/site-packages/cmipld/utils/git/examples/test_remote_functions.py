#!/usr/bin/env python3
"""
Test script to verify remote repository functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from cmipld.utils.git.git_repo_metadata import (
    get_files_changed_from_repo_shorthand,
    get_files_changed_from_github_url,
    _parse_repo_url
)

def test_remote_functions():
    """Test remote repository functions"""
    
    print("🧪 Testing Remote Repository Functions\n")
    
    # Test 1: URL parsing
    print("1. Testing URL parsing...")
    owner, repo = _parse_repo_url('https://github.com/WCRP-CMIP/CMIP6Plus_CVs')
    print(f"   Parsed: owner='{owner}', repo='{repo}'")
    assert owner == 'WCRP-CMIP', f"Expected 'WCRP-CMIP', got '{owner}'"
    assert repo == 'CMIP6Plus_CVs', f"Expected 'CMIP6Plus_CVs', got '{repo}'"
    print("   ✅ URL parsing works correctly")
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Shorthand function
    print("2. Testing shorthand function...")
    try:
        files = get_files_changed_from_repo_shorthand(
            'WCRP-CMIP/CMIP6Plus_CVs',
            '2024-01-01'
        )
        print(f"   Found {len(files)} files changed since 2024-01-01")
        if files:
            print(f"   Sample files: {files[:3]}")
        print("   ✅ Shorthand function works")
    except Exception as e:
        print(f"   ❌ Shorthand function failed: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 3: GitHub URL function
    print("3. Testing GitHub URL function...")
    try:
        files = get_files_changed_from_github_url(
            'https://github.com/WCRP-CMIP/CMIP6Plus_CVs',
            '2024-01-01'
        )
        print(f"   Found {len(files)} files changed since 2024-01-01")
        if files:
            print(f"   Sample files: {files[:3]}")
        print("   ✅ GitHub URL function works")
    except Exception as e:
        print(f"   ❌ GitHub URL function failed: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 4: Filtered results
    print("4. Testing with filtering...")
    try:
        files = get_files_changed_from_repo_shorthand(
            'WCRP-CMIP/CMIP6Plus_CVs',
            '2024-01-01',
            base_path_filter='src-data'
        )
        print(f"   Found {len(files)} files in src-data/ since 2024-01-01")
        if files:
            print(f"   Sample files: {files[:3]}")
        print("   ✅ Filtering works")
    except Exception as e:
        print(f"   ❌ Filtering failed: {e}")
    
    print("\n🎉 Remote repository tests completed!")

if __name__ == "__main__":
    test_remote_functions()
