# from .utils import DotAccessibleDict
import re
import json
import os

# Load prefix mappings from JSON file
def _load_prefix_mappings():
    """Load prefix mappings from JSON file"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, 'prefix_mappings.json')
    
    with open(json_path, 'r') as f:
        return json.load(f)

# Load the prefix data
_prefix_data = _load_prefix_mappings()

# Generate mappings from prefix data
def _generate_mapping(url_template):
    """Generate mapping dictionary using a URL template"""
    mapping = {}
    for prefix, data in _prefix_data.items():
        owner = data['owner']
        repo = data['repo']
        mapping[prefix] = url_template.format(owner=owner, repo=repo)
    return mapping

# Registered locations (GitHub Pages URLs)
mapping = _generate_mapping('https://{owner}.github.io/{repo}/')

# Direct mappings (GitHub repository URLs)
direct = _generate_mapping('https://github.com/{owner}/{repo}/')

# IO mappings (GitHub raw content URLs)
io = _generate_mapping('https://raw.githubusercontent.com/{owner}/{repo}/main/')

# sort all mappings
mapping = dict(sorted(mapping.items(), key=lambda item: len(item[0])))
direct = dict(sorted(direct.items(), key=lambda item: len(item[0])))
io = dict(sorted(io.items(), key=lambda item: len(item[0])))
# # a dot accessible dict of the mapping
# latest = DotAccessibleDict(dict([i, j + 'graph'] for i, j in mapping.items()))


reverse_mapping = {v: k for k, v in mapping.items()}

reverse_direct = {v: k for k, v in direct.items()}

reverse_io = {v: k for k, v in io.items()}


def fetch_all(subset=None):
    from pyld import jsonld
    from tqdm import tqdm

    if subset:
        subset = {k: mapping[k] for k in subset}
    else:
        subset = latest

    expanded = []

    for url in tqdm(subset.values()):
        try:
            expanded.extend(jsonld.expand(url+'graph.jsonld'))
        except Exception as e:
            print('error expanding', url, e)

    return expanded


# regex matching if these exist
matches = re.compile(f"({'|'.join([i+':' for i in mapping.keys()])})")


def resolve_url(url):
    if url.startswith('http') and url.count(':') > 2:
        return mapping.get(url, url)
    else:
        return url


def resolve_direct_url(url):
    """Resolve URL using direct mappings"""
    if url.startswith('http') and url.count(':') > 2:
        return direct.get(url, url)
    else:
        return url


def resolve_io_url(url):
    """Resolve URL using io mappings"""
    if url.startswith('http') and url.count(':') > 2:
        return io.get(url, url)
    else:
        return url


def compact_url(url):
    if url.startswith('http') and url.count(':') > 2:
        for k, v in mapping.items():
            if url.startswith(v):
                return url.replace(v, k+':')
        return url
    else:
        return url


def compact_direct_url(url):
    """Compact URL using direct mappings"""
    if url.startswith('http') and url.count(':') > 2:
        for k, v in direct.items():
            if url.startswith(v):
                return url.replace(v, k+':')
        return url
    else:
        return url


def compact_io_url(url):
    """Compact URL using io mappings"""
    if url.startswith('http') and url.count(':') > 2:
        for k, v in io.items():
            if url.startswith(v):
                return url.replace(v, k+':')
        return url
    else:
        return url


def prefix_url(url):
    url = url.replace('http:','https:')
    if url.startswith('http') :
        for k, v in mapping.items():
            if url.startswith(v):
                return url.replace(v, k+':')
        return url
    else:
        return url


def prefix_direct_url(url):
    """Prefix URL using direct mappings"""
    url = url.replace('http:', 'https:')
    if url.startswith('http'):
        for k, v in direct.items():
            if url.startswith(v):
                return url.replace(v, k+':')
        return url
    else:
        return url


def prefix_io_url(url):
    """Prefix URL using io mappings"""
    url = url.replace('http:', 'https:')
    if url.startswith('http'):
        for k, v in io.items():
            if url.startswith(v):
                return url.replace(v, k+':')
        return url
    else:
        return url
    
    
def resolve_prefix(query, mapping_type='default'):
    """
    Resolve prefix in query string using specified mapping type
    
    Args:
        query: The query string to resolve
        mapping_type: Type of mapping to use ('default', 'direct', 'io')
    """
    # Select the appropriate mapping
    if mapping_type == 'direct':
        current_mapping = direct
    elif mapping_type == 'io':
        current_mapping = io
    else:
        current_mapping = mapping
    
    if isinstance(query, str) and not query.startswith('http'):
        m = matches.search(query+':')
        if m:
            match = m.group()
            if len(match)-1 == len(query):
                if mapping_type == 'io':
                    query = f"{current_mapping[match]}graph.jsonld"
                else:
                    query = f"{current_mapping[match]}graph.jsonld"
            else:
                query = query.replace(match, current_mapping[match[:-1]])
            print('Substituting prefix:')
            print(match, query)
    return query


# Helper functions for easy access to different mapping types
def get_github_pages_url(prefix):
    """Get GitHub Pages URL for prefix"""
    return mapping.get(prefix)


def get_github_repo_url(prefix):
    """Get GitHub repository URL for prefix"""
    return direct.get(prefix)


def get_github_raw_url(prefix):
    """Get GitHub raw content URL for prefix"""
    return io.get(prefix)


def get_repo_info(prefix):
    """Get repository owner and name for prefix"""
    return _prefix_data.get(prefix, {})
