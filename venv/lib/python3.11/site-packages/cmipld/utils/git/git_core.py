import os
import subprocess
import sys
import re
from .git_repo_metadata import extract_repo_info

def toplevel():
    """Get the top-level directory of the git repository"""
    return os.popen('git rev-parse --show-toplevel').read().strip()

def url():
    """Get the repository's remote URL"""
    return subprocess.getoutput('git remote get-url origin').replace('.git', '').strip()


def url2io(github_repo_url, branch='main', path_base=''):
    print('make test for url2io')

    if '/tree/' in github_repo_url:
        # Regex to extract username, repo name, and path from GitHub repo URL
        pattern = rf"https://github\.com/(?P<username>[^/]+)/(?P<repo_name>[^/]+)/tree/{branch}/{path_base}(?P<path>.*)"

    else:
        pattern = rf"https://github\.com/(?P<username>[^/]+)/(?P<repo_name>[^/]+)"

    match = re.match(pattern, github_repo_url)

    if not match:
        raise ValueError("Invalid GitHub repository URL format.")

    username = match.group("username")
    repo_name = match.group("repo_name")
    path = match.groupdict().get("path", "").strip('/')

    github_pages_url = f"https://{username.lower()}.github.io/{repo_name}/{path}/"
    if github_pages_url[-2:] == '//':
        github_pages_url = github_pages_url[:-1]
    elif github_pages_url[-1] != '/':
        github_pages_url += '/'

    return github_pages_url


def io2repo(github_pages_url):

    username, repo_name, path = extract_repo_info(github_pages_url)
    base_url = f'https://github.com/{username}/{repo_name}.git'

    return base_url


def url2io(github_repo_url, branch='main', path_base=''):
    print('make test for url2io')

    if '/tree/' in github_repo_url:
        # Regex to extract username, repo name, and path from GitHub repo URL
        pattern = rf"https://github\.com/(?P<username>[^/]+)/(?P<repo_name>[^/]+)/tree/{branch}/{path_base}(?P<path>.*)"

    else:
        pattern = rf"https://github\.com/(?P<username>[^/]+)/(?P<repo_name>[^/]+)"

    match = re.match(pattern, github_repo_url)

    if not match:
        raise ValueError("Invalid GitHub repository URL format.")

    username = match.group("username")
    repo_name = match.group("repo_name")
    path = match.groupdict().get("path", "").strip('/')

    github_pages_url = f"https://{username.lower()}.github.io/{repo_name}/{path}/"
    if github_pages_url[-2:] == '//':
        github_pages_url = github_pages_url[:-1]
    elif github_pages_url[-1] != '/':
        github_pages_url += '/'

    return github_pages_url
