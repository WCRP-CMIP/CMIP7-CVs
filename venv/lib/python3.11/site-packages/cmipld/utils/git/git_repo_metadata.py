import subprocess, os, re
import requests
from ..io import shell

from .gh_utils import GitHubUtils,json

def list_repo_files(owner, repo, branch='main', path=''):
    
    utils = GitHubUtils()
    returncode, result, stderr = utils.run_gh_cmd_safe(['api', f'/repos/{owner}/{repo}/contents/{path}?ref={branch}'])
    
    if returncode != 0:
        raise Exception(f"Failed to list files in repository {owner}/{repo} on branch {branch}: {stderr}")
    
    # result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    items = json.loads(result)

    return [{'name': i['name'], 'type': i['type'], 'path': i['path']} for i in (items if isinstance(items, list) else [items])]


def getreponame():
    """Get the repository name"""
    return subprocess.getoutput('git remote get-url origin').split('/')[-1].replace('.git', '').strip()

def getrepoowner():
    """Get the repository owner"""
    return subprocess.getoutput('git remote get-url origin').split('/')[-2].strip()

def getlastcommit():
    """Get the last commit hash"""
    return subprocess.getoutput('git rev-parse HEAD').strip()

def getlasttag():
    """Get the most recent tag"""
    return subprocess.getoutput('git describe --tags --abbrev=0').strip()

def getfilenames(branch='main'):
    """Get file names in the repository"""
    return shell(f'git ls-tree -r {branch} --name-only ').split()

def get_cmip_repo_info():
    """Retrieve repository information and tags"""
    repo = subprocess.getoutput(
        'git remote get-url origin').replace('.git', '/blob/main/JSONLD').strip()
    cv_tag = subprocess.getoutput(
        "curl -s https://api.github.com/repos/WCRP-CMIP/CMIP6Plus_CVs/tags | jq -r '.[0].name'").strip()
    mip_tag = subprocess.getoutput(
        "curl -s https://api.github.com/repos/PCMDI/mip-cmor-tables/tags | jq -r '.[0].name'").strip()
    return repo, cv_tag, mip_tag


def extract_repo_info(github_pages_url):
    """Extract username and repository name from GitHub Pages URL."""
    pattern = r'https{0,1}://([a-zA-Z0-9-_]+)\.github\.io/([a-zA-Z0-9-_]+)/(.*)?'
    match = re.match(pattern, github_pages_url)

    if match:
        username = match.group(1)
        repo_name = match.group(2)
        path = match.group(3)
        return username, repo_name, path
    else:
        raise ValueError("Invalid GitHub Pages URL")

# ... (rest of the URL conversion functions remain the same)



import os
import subprocess

def get_repo_url():
    # Get the GitHub repository URL using `git config`
    repo_url = subprocess.check_output(
        ['git', 'config', '--get', 'remote.origin.url'], 
        universal_newlines=True
    ).strip()
    
    # If the URL is in SSH format (git@github.com:...), convert it to HTTPS
    if repo_url.startswith("git@github.com:"):
        repo_url = "https://github.com/" + repo_url.replace("git@github.com:", "").replace(".git", "")
    elif repo_url.endswith(".git"):
        # If it's already HTTPS, just remove the .git
        repo_url = repo_url.replace(".git", "")
    
    if not repo_url.endswith('/'):
        repo_url = repo_url + '/'
        
    parts = repo_url.split('/')

    # GitHub org is the 4th part (index 3)
    parts[3] = parts[3].lower()

    repo_url = '/'.join(parts)
    return repo_url

def get_relative_path(cwd = None):
    # Get the current working directory
    if cwd == None:
        cwd = os.getcwd()
    
    # Get the root of the git repository using `git rev-parse --show-toplevel`
    repo_root = subprocess.check_output(
        ['git', 'rev-parse', '--show-toplevel'], 
        universal_newlines=True
    ).strip()
    
    # Get the relative path from the repo root to the current directory
    relative_path = os.path.relpath(cwd, repo_root)
    
    return relative_path

def get_path_url(path = None):
    # Get the base GitHub URL
    repo_url = get_repo_url()
    
    # Get the relative path from the repo root
    relative_path = get_relative_path(path)
    
    # Construct the URL for the folder
    github_url = f"{repo_url}/tree/main/{relative_path}"
    
    return github_url


def get_files_changed_since_date(since_date, branch='main', base_path_filter=None, exclude_paths=None, repo_url=None, owner=None, repo=None):
    """
    Get all files changed since a specific date from all commits
    
    Args:
        since_date (str): Date in format 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'
        branch (str): Branch to check (default: 'main')
        base_path_filter (str): Optional base path to filter files (e.g., 'src-data/' to only include files in src-data directory)
        exclude_paths (list): Optional list of paths to exclude (e.g., ['.git/', '__pycache__/'])
        repo_url (str): Optional remote repository URL (e.g., 'https://github.com/user/repo')
        owner (str): Optional repository owner (alternative to repo_url)
        repo (str): Optional repository name (alternative to repo_url)
    
    Returns:
        list: List of unique file paths that were changed since the date
    """
    import subprocess
    from datetime import datetime
    
    try:
        # If remote repository is specified, use GitHub API
        if repo_url or (owner and repo):
            return _get_remote_files_changed_since_date(since_date, branch, base_path_filter, exclude_paths, repo_url, owner, repo)
        
        # Local repository operation
        # Get all commits since the date with file names
        cmd = f'git log --since="{since_date}" --name-only --pretty=format: {branch}'
        result = subprocess.getoutput(cmd)
        
        # Filter out empty lines and get unique files
        files = [f.strip() for f in result.split('\\n') if f.strip()]
        unique_files = list(set(files))
        
        # Apply base path filter if provided
        if base_path_filter:
            # Normalize the base path (ensure it ends with / if it's a directory)
            if base_path_filter and not base_path_filter.endswith('/'):
                base_path_filter += '/'
            
            unique_files = [f for f in unique_files if f.startswith(base_path_filter)]
        
        # Apply exclusion filters if provided
        if exclude_paths:
            for exclude_path in exclude_paths:
                unique_files = [f for f in unique_files if not f.startswith(exclude_path)]
        
        return sorted(unique_files)
        
    except Exception as e:
        print(f"Error getting files changed since {since_date}: {e}")
        return []


def get_files_changed_between_dates(start_date, end_date, branch='main', base_path_filter=None, exclude_paths=None, repo_url=None, owner=None, repo=None):
    """
    Get all files changed between two specific dates
    
    Args:
        start_date (str): Start date in format 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'
        end_date (str): End date in format 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'
        branch (str): Branch to check (default: 'main')
        base_path_filter (str): Optional base path to filter files
        exclude_paths (list): Optional list of paths to exclude
        repo_url (str): Optional remote repository URL (e.g., 'https://github.com/user/repo')
        owner (str): Optional repository owner (alternative to repo_url)
        repo (str): Optional repository name (alternative to repo_url)
    
    Returns:
        list: List of unique file paths that were changed between the dates
    """
    import subprocess
    
    try:
        # If remote repository is specified, use GitHub API
        if repo_url or (owner and repo):
            return _get_remote_files_changed_between_dates(start_date, end_date, branch, base_path_filter, exclude_paths, repo_url, owner, repo)
        
        # Local repository operation
        # Get all commits between the dates with file names
        cmd = f'git log --since="{start_date}" --until="{end_date}" --name-only --pretty=format: {branch}'
        result = subprocess.getoutput(cmd)
        
        # Filter out empty lines and get unique files
        files = [f.strip() for f in result.split('\\n') if f.strip()]
        unique_files = list(set(files))
        
        # Apply base path filter if provided
        if base_path_filter:
            # Normalize the base path (ensure it ends with / if it's a directory)
            if base_path_filter and not base_path_filter.endswith('/'):
                base_path_filter += '/'
            
            unique_files = [f for f in unique_files if f.startswith(base_path_filter)]
        
        # Apply exclusion filters if provided
        if exclude_paths:
            for exclude_path in exclude_paths:
                unique_files = [f for f in unique_files if not f.startswith(exclude_path)]
        
        return sorted(unique_files)
        
    except Exception as e:
        print(f"Error getting files changed between {start_date} and {end_date}: {e}")
        return []


def get_files_changed_with_details(since_date, branch='main', base_path_filter=None, exclude_paths=None, repo_url=None, owner=None, repo=None):
    """
    Get detailed information about files changed since a specific date
    
    Args:
        since_date (str): Date in format 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'
        branch (str): Branch to check (default: 'main')
        base_path_filter (str): Optional base path to filter files
        exclude_paths (list): Optional list of paths to exclude
        repo_url (str): Optional remote repository URL (e.g., 'https://github.com/user/repo')
        owner (str): Optional repository owner (alternative to repo_url)
        repo (str): Optional repository name (alternative to repo_url)
    
    Returns:
        list: List of dictionaries with file details (path, commit_hash, author, date, message)
    """
    import subprocess
    
    try:
        # If remote repository is specified, use GitHub API
        if repo_url or (owner and repo):
            return _get_remote_files_changed_with_details(since_date, branch, base_path_filter, exclude_paths, repo_url, owner, repo)
        
        # Local repository operation
        # Get commits with file details since the date
        cmd = f'git log --since="{since_date}" --name-only --pretty=format:"%H|%an|%ae|%ad|%s" --date=iso {branch}'
        result = subprocess.getoutput(cmd)
        
        files_with_details = []
        current_commit = None
        
        for line in result.split('\\n'):
            line = line.strip()
            if not line:
                continue
                
            # Check if this is a commit info line (contains |)
            if '|' in line:
                parts = line.split('|')
                if len(parts) >= 5:
                    current_commit = {
                        'hash': parts[0],
                        'author': parts[1],
                        'email': parts[2],
                        'date': parts[3],
                        'message': '|'.join(parts[4:])  # Join back in case message contains |
                    }
            else:
                # This is a file path
                if current_commit:
                    # Apply base path filter if provided
                    if base_path_filter:
                        if not base_path_filter.endswith('/'):
                            base_path_filter += '/'
                        if not line.startswith(base_path_filter):
                            continue
                    
                    # Apply exclusion filters if provided
                    if exclude_paths:
                        skip = False
                        for exclude_path in exclude_paths:
                            if line.startswith(exclude_path):
                                skip = True
                                break
                        if skip:
                            continue
                    
                    files_with_details.append({
                        'path': line,
                        'commit_hash': current_commit['hash'],
                        'author': current_commit['author'],
                        'email': current_commit['email'],
                        'date': current_commit['date'],
                        'message': current_commit['message']
                    })
        
        return files_with_details
        
    except Exception as e:
        print(f"Error getting detailed file changes since {since_date}: {e}")
        return []


def get_files_changed_from_github_url(github_url, since_date, branch='main', base_path_filter=None, exclude_paths=None):
    """
    Convenience function to get files changed from a GitHub URL
    
    Args:
        github_url (str): GitHub repository URL (e.g., 'https://github.com/user/repo')
        since_date (str): Date in format 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'
        branch (str): Branch to check (default: 'main')
        base_path_filter (str): Optional base path to filter files
        exclude_paths (list): Optional list of paths to exclude
    
    Returns:
        list: List of unique file paths that were changed since the date
    """
    return get_files_changed_since_date(
        since_date=since_date,
        branch=branch,
        base_path_filter=base_path_filter,
        exclude_paths=exclude_paths,
        repo_url=github_url
    )


def get_files_changed_from_repo_shorthand(repo_shorthand, since_date, branch='main', base_path_filter=None, exclude_paths=None):
    """
    Convenience function to get files changed using 'owner/repo' shorthand notation
    
    Args:
        repo_shorthand (str): Repository in 'owner/repo' format (e.g., 'WCRP-CMIP/CMIP6Plus_CVs')
        since_date (str): Date in format 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'
        branch (str): Branch to check (default: 'main')
        base_path_filter (str): Optional base path to filter files
        exclude_paths (list): Optional list of paths to exclude
    
    Returns:
        list: List of unique file paths that were changed since the date
    """
    if '/' not in repo_shorthand:
        raise ValueError("repo_shorthand must be in 'owner/repo' format")
    
    owner, repo = repo_shorthand.split('/', 1)
    return get_files_changed_since_date(
        since_date=since_date,
        branch=branch,
        base_path_filter=base_path_filter,
        exclude_paths=exclude_paths,
        owner=owner,
        repo=repo
    )


# Helper functions for remote repository operations

def _parse_repo_url(repo_url):
    """
    Parse GitHub repository URL to extract owner and repo name
    
    Args:
        repo_url (str): GitHub repository URL
    
    Returns:
        tuple: (owner, repo) or (None, None) if invalid
    """
    import re
    
    if not repo_url:
        return None, None
    
    # Handle various GitHub URL formats
    patterns = [
        r'https://github\\.com/([^/]+)/([^/]+?)(?:\\.git)?/?$',
        r'git@github\\.com:([^/]+)/([^/]+?)(?:\\.git)?$',
        r'github\\.com/([^/]+)/([^/]+?)(?:\\.git)?/?$'
    ]
    
    for pattern in patterns:
        match = re.match(pattern, repo_url)
        if match:
            return match.group(1), match.group(2)
    
    return None, None


def _get_remote_commits(owner, repo, branch='main', since_date=None, until_date=None):
    """
    Get commits from a remote repository using GitHub API
    
    Args:
        owner (str): Repository owner
        repo (str): Repository name
        branch (str): Branch name
        since_date (str): Optional since date
        until_date (str): Optional until date
    
    Returns:
        list: List of commit objects
    """
    import requests
    from datetime import datetime
    
    try:
        # Convert date strings to ISO format for GitHub API
        params = {'sha': branch, 'per_page': 100}
        
        if since_date:
            # Convert to ISO format if needed
            try:
                if len(since_date) == 10:  # YYYY-MM-DD format
                    since_date += 'T00:00:00Z'
                elif 'T' not in since_date and 'Z' not in since_date:
                    since_date += 'T00:00:00Z'
                params['since'] = since_date
            except:
                pass
        
        if until_date:
            try:
                if len(until_date) == 10:  # YYYY-MM-DD format
                    until_date += 'T23:59:59Z'
                elif 'T' not in until_date and 'Z' not in until_date:
                    until_date += 'T23:59:59Z'
                params['until'] = until_date
            except:
                pass
        
        url = f'https://api.github.com/repos/{owner}/{repo}/commits'
        
        all_commits = []
        page = 1
        
        while True:
            params['page'] = page
            response = requests.get(url, params=params)
            
            if response.status_code != 200:
                print(f"Error fetching commits: {response.status_code} - {response.text}")
                break
            
            commits = response.json()
            if not commits:
                break
            
            all_commits.extend(commits)
            
            # GitHub API returns 100 items per page by default
            if len(commits) < 100:
                break
            
            page += 1
            
            # Limit to reasonable number of requests
            if page > 10:  # Max 1000 commits
                break
        
        return all_commits
        
    except Exception as e:
        print(f"Error fetching remote commits: {e}")
        return []


def _get_commit_files(owner, repo, commit_sha):
    """
    Get files changed in a specific commit
    
    Args:
        owner (str): Repository owner
        repo (str): Repository name
        commit_sha (str): Commit SHA
    
    Returns:
        list: List of file paths changed in the commit
    """
    import requests
    
    try:
        url = f'https://api.github.com/repos/{owner}/{repo}/commits/{commit_sha}'
        response = requests.get(url)
        
        if response.status_code != 200:
            return []
        
        commit_data = response.json()
        files = commit_data.get('files', [])
        
        return [f['filename'] for f in files]
        
    except Exception as e:
        print(f"Error fetching commit files for {commit_sha}: {e}")
        return []


def _get_remote_files_changed_since_date(since_date, branch='main', base_path_filter=None, exclude_paths=None, repo_url=None, owner=None, repo=None):
    """
    Get files changed since a date from a remote repository
    """
    # Parse repository info
    if repo_url:
        owner, repo = _parse_repo_url(repo_url)
    
    if not owner or not repo:
        print("Error: Could not parse repository information")
        return []
    
    # Get commits since the date
    commits = _get_remote_commits(owner, repo, branch, since_date)
    
    # Get all files changed in these commits
    all_files = set()
    
    for commit in commits:
        files = _get_commit_files(owner, repo, commit['sha'])
        all_files.update(files)
    
    # Apply filters
    filtered_files = list(all_files)
    
    # Apply base path filter if provided
    if base_path_filter:
        if not base_path_filter.endswith('/'):
            base_path_filter += '/'
        filtered_files = [f for f in filtered_files if f.startswith(base_path_filter)]
    
    # Apply exclusion filters if provided
    if exclude_paths:
        for exclude_path in exclude_paths:
            filtered_files = [f for f in filtered_files if not f.startswith(exclude_path)]
    
    return sorted(filtered_files)


def _get_remote_files_changed_between_dates(start_date, end_date, branch='main', base_path_filter=None, exclude_paths=None, repo_url=None, owner=None, repo=None):
    """
    Get files changed between two dates from a remote repository
    """
    # Parse repository info
    if repo_url:
        owner, repo = _parse_repo_url(repo_url)
    
    if not owner or not repo:
        print("Error: Could not parse repository information")
        return []
    
    # Get commits between the dates
    commits = _get_remote_commits(owner, repo, branch, start_date, end_date)
    
    # Get all files changed in these commits
    all_files = set()
    
    for commit in commits:
        files = _get_commit_files(owner, repo, commit['sha'])
        all_files.update(files)
    
    # Apply filters
    filtered_files = list(all_files)
    
    # Apply base path filter if provided
    if base_path_filter:
        if not base_path_filter.endswith('/'):
            base_path_filter += '/'
        filtered_files = [f for f in filtered_files if f.startswith(base_path_filter)]
    
    # Apply exclusion filters if provided
    if exclude_paths:
        for exclude_path in exclude_paths:
            filtered_files = [f for f in filtered_files if not f.startswith(exclude_path)]
    
    return sorted(filtered_files)


def _get_remote_files_changed_with_details(since_date, branch='main', base_path_filter=None, exclude_paths=None, repo_url=None, owner=None, repo=None):
    """
    Get detailed file change information from a remote repository
    """
    # Parse repository info
    if repo_url:
        owner, repo = _parse_repo_url(repo_url)
    
    if not owner or not repo:
        print("Error: Could not parse repository information")
        return []
    
    # Get commits since the date
    commits = _get_remote_commits(owner, repo, branch, since_date)
    
    # Get detailed file information
    files_with_details = []
    
    for commit in commits:
        files = _get_commit_files(owner, repo, commit['sha'])
        
        for file_path in files:
            # Apply base path filter if provided
            if base_path_filter:
                if not base_path_filter.endswith('/'):
                    base_path_filter += '/'
                if not file_path.startswith(base_path_filter):
                    continue
            
            # Apply exclusion filters if provided
            if exclude_paths:
                skip = False
                for exclude_path in exclude_paths:
                    if file_path.startswith(exclude_path):
                        skip = True
                        break
                if skip:
                    continue
            
            files_with_details.append({
                'path': file_path,
                'commit_hash': commit['sha'],
                'author': commit['commit']['author']['name'],
                'email': commit['commit']['author']['email'],
                'date': commit['commit']['author']['date'],
                'message': commit['commit']['message']
            })
    
    return files_with_details
