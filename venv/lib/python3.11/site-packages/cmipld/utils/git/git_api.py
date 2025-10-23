import requests

def get_tags(owner, repo):
    """Get the tags from a repository"""
    return requests.get(f'https://api.github.com/repos/{owner}/{repo}/tags').json()

def get_contents(owner, repo, path):
    """Get the contents from a repository"""
    return requests.get(f'https://api.github.com/repos/{owner}/{repo}/contents/{path}').json()
