"""
Git co-author utilities for CMIP-LD

Simple functions for retrieving and managing co-authors from git history.
"""

import subprocess
from pathlib import Path
from typing import List, Set, Union


def get_file_authors(file_path: Union[str, Path]) -> List[str]:
    """
    Get all unique authors of a file from git history.
    
    Args:
        file_path: Path to the file
        
    Returns:
        List of unique author strings in "Name <email>" format
    """
    file_path = Path(file_path)
    
    try:
        # Get all unique authors for this file
        cmd = ['git', 'log', '--format=%an <%ae>', '--', str(file_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return []
        
        # Split by newlines and remove empty strings
        authors = [a.strip() for a in result.stdout.strip().split('\n') if a.strip()]
        
        # Remove duplicates by email while preserving order
        # Also filter out None authors
        seen_emails = set()
        unique_authors = []
        
        for author in authors:
            # Skip if author contains 'None'
            if 'None' in author or '<>' in author:
                continue
                
            # Extract email from "Name <email>" format
            if '<' in author and '>' in author:
                email_start = author.find('<')
                email_end = author.find('>')
                email = author[email_start+1:email_end].strip()
                
                # Skip if email is empty, already seen, or invalid (no @ symbol)
                if not email or email in seen_emails or '@' not in email:
                    continue
                    
                seen_emails.add(email)
                unique_authors.append(author)
            else:
                # Skip malformed entries
                continue
        
        return unique_authors
        
    except Exception:
        return []


def get_coauthor_lines(file_paths: Union[Union[str, Path], List[Union[str, Path]]]) -> List[str]:
    """
    Get formatted co-author lines for one or more files.
    
    Args:
        file_paths: Single file path or list of file paths
        
    Returns:
        List of unique formatted co-author lines ready for commit messages
    """
    if isinstance(file_paths, (str, Path)):
        file_paths = [file_paths]
    
    # Use email as key to prevent duplicates with different names
    authors_by_email = {}
    
    for file_path in file_paths:
        authors = get_file_authors(file_path)
        for author in authors:
            # Extract email
            if '<' in author and '>' in author:
                email_start = author.find('<')
                email_end = author.find('>')
                email = author[email_start+1:email_end].strip()
                
                # Store author, keeping the first occurrence of each email
                # Only if email is valid (contains @)
                if email and '@' in email and email not in authors_by_email:
                    authors_by_email[email] = author
    
    # Format as co-author lines and sort by name
    coauthor_lines = [f"Co-authored-by: {author}" for author in sorted(authors_by_email.values())]
    return coauthor_lines


def commit_with_coauthors(file_paths: List[Union[str, Path]], message: str) -> bool:
    """
    Create a commit with co-authors from the given files.
    
    Args:
        file_paths: List of file paths that were modified
        message: Commit message
        
    Returns:
        True if commit was created successfully
    """
    if not file_paths:
        return False
    
    # Get co-author lines
    coauthor_lines = get_coauthor_lines(file_paths)
    
    # Build full message
    if coauthor_lines:
        full_message = message + "\n\n" + "\n".join(coauthor_lines)
    else:
        full_message = message
    
    try:
        # Stage files
        for file_path in file_paths:
            subprocess.run(['git', 'add', str(file_path)], check=True)
        
        # Create commit
        result = subprocess.run(['git', 'commit', '-m', full_message], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"\n✅ Commit created with {len(coauthor_lines)} co-authors")
            return True
        else:
            print(f"\n❌ Failed to create commit: {result.stderr}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error creating commit: {e}")
        return False


def is_git_repo(path: Union[str, Path] = '.') -> bool:
    """Check if the path is inside a git repository."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            capture_output=True,
            cwd=str(path)
        )
        return result.returncode == 0
    except:
        return False
