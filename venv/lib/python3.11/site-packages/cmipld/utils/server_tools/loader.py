
from typing import Any, Dict, List, Union, Set
from ..urltools import https
from pyld import jsonld
from ...locations import mapping
from .pyld_requests import requests_document_loader


from ..logging.unique import UniqueLogger

log = UniqueLogger()
custom_cache = {}


class Loader:

    def __init__(self, tries=3):
        """Initialize the processor with a cached document loader."""
        self.loader = None
        self.set_cache_loader(tries)
        assert self.loader == jsonld.get_document_loader()

    # @lru_cache(maxsize=100)

    def _load_document(self, url: str) -> Dict:
        """
        Load and cache a JSON-LD document from a URL.

        Args:
            url: The URL to fetch the document from

        Returns:
            The loaded document
        """
        return self.loader(url)['document']

    @staticmethod
    def clear_cache():
        global custom_cache
        custom_cache = {}

    def set_cache_loader(self, tries=3):

        default_loader = requests_document_loader(prefix=list(mapping.keys()) , verify=False)
        
        log.debug(f"default_loader: {default_loader}")

        def cached_loader(url, kwargs={}):
            global custom_cache
            url = https(url)
            
            # log.debug(f'Loading {url} with {self.loader}')
            
            # cache hit
            if url in custom_cache:
                # log.debug(f'Cache hit for {url}')
                
                return custom_cache[url]

            # cache miss
            for _ in range(tries):
                try:
                    custom_cache[url] = default_loader(url)
                    return custom_cache[url]
                except:
                    log.warn(f'Error loading {url}, retrying...')
                    pass

            # last time to throw the error
            
            custom_cache[url] = default_loader(url)
            
            # if '@context' in custom_cache[url]['document']:
            # # fetched_contexts[url] = doc['document']
            #     print('context', custom_cache[url]['document']['@context'])
            
            return custom_cache[url]

        # update jsonld loader
        jsonld.set_document_loader(cached_loader)

        self.loader = jsonld.get_document_loader()
