"""
A JSON-LD loader with caching and retries built on a patched version of pyld's Requests-based loader.

Source of the base loader logic: 
https://github.com/digitalbazaar/pyld/blob/master/lib/pyld/documentloader/requests.py
"""

import string
import urllib3
import urllib.parse as urllib_parse
import re
from typing import Any, Dict

# Suppress only the specific InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


import requests
from pyld import jsonld
from pyld.jsonld import JsonLdError, parse_link_header, LINK_HEADER_REL

from ..logging.unique import UniqueLogger
from ..urltools import https  # assumes custom https normalizer

log = UniqueLogger()
# Global cache
custom_cache: Dict[str, Dict] = {}


def requests_document_loader(prefix, **kwargs):
    """
    Create a Requests document loader with proper error handling.

    :param kwargs: passed directly to `requests.get`.
    :return: a function that loads and returns a JSON-LD RemoteDocument.
    """
    
    scheme_allowed = ['http', 'https',*prefix]

    def loader(url: str, options: Dict = {}) -> Dict:
        pieces = urllib_parse.urlparse(url)
        # not all([pieces.scheme, pieces.netloc]) or
        if pieces.scheme not in scheme_allowed:
            raise JsonLdError(
                'URL could not be dereferenced; only "http" and "https" or valid prefixes are supported.',
                'jsonld.InvalidUrl', {'url': url},
                code='loading document failed')

        headers = options.get('headers') or {
            'Accept': 'application/ld+json, application/json'
        }

        response = requests.get(url, headers=headers, **kwargs)
        
        content_type = response.headers.get('content-type') or 'application/octet-stream'
        
        try:
            data = response.json()

            
        except Exception as e:
            log.warn(f'Error parsing JSON from {url}: {e}')
            data = {"@id": url, "@context":"","error": str(e)}
        
        doc = {
            'contentType': content_type,
            'contextUrl': None,
            'documentUrl': response.url,
            
            'document': data
        }


        link_header = response.headers.get('link')
        
        # print('-----------------------')
        # print('link header', link_header)
        # print('content type', content_type)
        # print('document url', response.url)
        # print('document', doc)
        # print('-----------------------')
        
        
        if link_header:
            linked_context = parse_link_header(link_header).get(LINK_HEADER_REL)
            if linked_context and content_type != 'application/ld+json':
                if isinstance(linked_context, list):
                    raise JsonLdError(
                        'Multiple context link headers found.',
                        'jsonld.LoadDocumentError', {'url': url},
                        code='multiple context link headers')
                doc['contextUrl'] = linked_context['target']

            linked_alternate = parse_link_header(link_header).get('alternate')
            if (linked_alternate and
                linked_alternate.get('type') == 'application/ld+json' and
                not re.match(r'^application\/(\w*\+)?json$', content_type)):
                doc['contentType'] = 'application/ld+json'
                doc['documentUrl'] = jsonld.prepend_base(url, linked_alternate['target'])


        return doc

    return loader