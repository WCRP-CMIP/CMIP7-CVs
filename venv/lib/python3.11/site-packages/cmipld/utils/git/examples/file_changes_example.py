#!/usr/bin/env python3
"""
Example script demonstrating the new file change tracking functions
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from cmipld.utils.git.git_repo_metadata import (
    get_files_changed_since_date,
    get_files_changed_between_dates,
    get_files_changed_with_details,
    get_files_changed_from_github_url,
    get_files_changed_from_repo_shorthand
)

def example_usage():
    """
    Example usage of the new file change tracking functions
    """
    
    print("=== File Change Tracking Examples ===\n")
    
    # Example 1: Get all files changed since a specific date
    print("1. Files changed since 2024-01-01:")
    try:
        files_since = get_files_changed_since_date('2024-01-01')
        print(f"   Found {len(files_since)} files changed since 2024-01-01")
        for file in files_since[:5]:  # Show first 5 files
            print(f"   - {file}")
        if len(files_since) > 5:
            print(f"   ... and {len(files_since) - 5} more")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 2: Get files changed in a specific directory
    print("2. Files changed in 'src-data/' directory since 2024-01-01:")
    try:
        files_in_src = get_files_changed_since_date(
            '2024-01-01', 
            base_path_filter='src-data'
        )
        print(f"   Found {len(files_in_src)} files in src-data/ changed since 2024-01-01")
        for file in files_in_src[:5]:
            print(f"   - {file}")
        if len(files_in_src) > 5:
            print(f"   ... and {len(files_in_src) - 5} more")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 3: Get files changed between two dates
    print("3. Files changed between 2024-01-01 and 2024-06-01:")
    try:
        files_between = get_files_changed_between_dates(
            '2024-01-01', 
            '2024-06-01'
        )
        print(f"   Found {len(files_between)} files changed between dates")
        for file in files_between[:5]:
            print(f"   - {file}")
        if len(files_between) > 5:
            print(f"   ... and {len(files_between) - 5} more")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 4: Get detailed file information
    print("4. Detailed information for files changed since 2024-01-01 (excluding build files):")
    try:
        files_detailed = get_files_changed_with_details(
            '2024-01-01',
            exclude_paths=['build/', '__pycache__/', '.git/']
        )
        print(f"   Found {len(files_detailed)} file changes with details")
        for detail in files_detailed[:3]:  # Show first 3 detailed entries
            print(f"   - {detail['path']}")
            print(f"     Author: {detail['author']}")
            print(f"     Date: {detail['date']}")
            print(f"     Message: {detail['message'][:50]}...")
            print(f"     Commit: {detail['commit_hash'][:8]}")
            print()
        if len(files_detailed) > 3:
            print(f"   ... and {len(files_detailed) - 3} more detailed entries")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 5: Filter by multiple exclusions
    print("5. Files changed since 2024-01-01 (excluding build, cache, and git files):")
    try:
        files_filtered = get_files_changed_since_date(
            '2024-01-01',
            exclude_paths=['build/', '__pycache__/', '.git/', 'node_modules/', '.DS_Store']
        )
        print(f"   Found {len(files_filtered)} files (after filtering)")
        for file in files_filtered[:5]:
            print(f"   - {file}")
        if len(files_filtered) > 5:
            print(f"   ... and {len(files_filtered) - 5} more")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 6: Remote repository using GitHub URL
    print("6. Files changed in remote repository (WCRP-CMIP/CMIP6Plus_CVs) since 2024-01-01:")
    try:
        remote_files = get_files_changed_from_github_url(
            'https://github.com/WCRP-CMIP/CMIP6Plus_CVs',
            '2024-01-01'
        )
        print(f"   Found {len(remote_files)} files in remote repository")
        for file in remote_files[:5]:
            print(f"   - {file}")
        if len(remote_files) > 5:
            print(f"   ... and {len(remote_files) - 5} more")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 7: Remote repository using shorthand notation
    print("7. Files changed in 'WCRP-CMIP/CMIP6Plus_CVs' src-data directory since 2024-01-01:")
    try:
        remote_src_files = get_files_changed_from_repo_shorthand(
            'WCRP-CMIP/CMIP6Plus_CVs',
            '2024-01-01',
            base_path_filter='src-data'
        )
        print(f"   Found {len(remote_src_files)} files in src-data directory")
        for file in remote_src_files[:5]:
            print(f"   - {file}")
        if len(remote_src_files) > 5:
            print(f"   ... and {len(remote_src_files) - 5} more")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 8: Remote repository with detailed information
    print("8. Detailed changes from remote repository since 2024-01-01:")
    try:
        remote_details = get_files_changed_with_details(
            '2024-01-01',
            owner='WCRP-CMIP',
            repo='CMIP6Plus_CVs',
            exclude_paths=['.git/', '__pycache__/']
        )
        print(f"   Found {len(remote_details)} detailed file changes")
        for detail in remote_details[:2]:  # Show first 2 detailed entries
            print(f"   - {detail['path']}")
            print(f"     Author: {detail['author']}")
            print(f"     Date: {detail['date']}")
            print(f"     Message: {detail['message'][:50]}...")
            print(f"     Commit: {detail['commit_hash'][:8]}")
            print()
        if len(remote_details) > 2:
            print(f"   ... and {len(remote_details) - 2} more detailed entries")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    print("\n🚀 Starting File Change Tracking Examples...\n")
    example_usage()
    print("\n✅ Examples completed!\n")
    print("💡 Pro tip: You can now use these functions with both local and remote repositories!")
    print("   - For local repos: Just use the basic functions")
    print("   - For remote repos: Add owner/repo or repo_url parameters")
    print("   - Use convenience functions for easier remote access")
