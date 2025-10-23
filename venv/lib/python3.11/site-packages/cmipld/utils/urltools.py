import requests
# import urlparse
from urllib.parse import urlparse, urlunparse
from os.path import relpath


def url_exists(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code == 200
    except requests.ConnectionError:
        return None
    except requests.Timeout:
        return None
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def relative_url(base_url, target_url):
    base_parsed = urlparse(base_url)
    target_parsed = urlparse(target_url)

    if base_parsed.netloc != target_parsed.netloc:
        raise ValueError(
            "URLs have different domains; cannot compute relative path.")

    # Compute relative path
    base_path = base_parsed.path
    target_path = target_parsed.path
    relative_path = relpath(target_path, start=base_path)

    # Reconstruct the relative URL
    return relative_path


# def valid_url(url):
#     parsed_url = urlparse(url)
#     # Check if the URL has a valid scheme (e.g., 'http', 'https') and netloc (domain)
#     return parsed_url.scheme and parsed_url.netloc


def https(url):
    if url.startswith("http://"):
        return url.replace("http://", "https://", 1)
    return url
