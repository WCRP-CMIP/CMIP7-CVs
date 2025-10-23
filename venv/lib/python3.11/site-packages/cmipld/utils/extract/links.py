from pyld import jsonld
from urllib.parse import urljoin
from typing import Any, Dict, List, Union, Set
from ...locations import mapping



def depends(url: str, prefix: bool = False, relative: bool = False, graph=False) -> Set[str]:
        """
        Extract all dependencies (@id references) from a JSON-LD document.

        Args:
            url: URL of the JSON-LD document
            relative: If True, returns relative URLs, if False returns absolute URLs
            graph: Returns the location of the graph object - incompatible with relative

        Returns:
            Set of dependency URLs found in the document
        """
        try:
            # Frame the document to extract all @id references
            # query = self.replace_prefix(url)
            
            # "@context":url
            frm = {'@explicit': True}
            
            if prefix: # use the context to apply prefixes to the dependancies. 
                frm['@context'] = mapping
                # {'wcrpo':'https://wcrp-cmip.github.io/'}
            
            framed = jsonld.frame(url, frm)
            
            ids = framed.get('@graph', [])

            # Process URLs based on relative flag
            if relative:
                return {item['@id'] for item in ids if '@id' in item}

            elif graph:
                return list(set({urljoin(url, self.graphify(item['@id'])) for item in ids if '@id' in item}))

            else:
                return {urljoin(url, item['@id']) for item in ids if '@id' in item}

        except Exception as e:
            print(f"Error extracting dependencies: {str(e)}")
            return set()

def display_depends(url: str, prefix: bool = True, relative: bool = False) -> None:
    """
    Display dependencies of a JSON-LD document in a formatted panel.

    Args:
        url: URL of the JSON-LD document
        prefix: If True, uses prefixes for formatting
        relative: If True, displays relative URLs
    """

    from rich.console import Console, Group
    from rich.panel import Panel
    from rich.text import Text
    import re
    # Define colors for styled output
    colours = {
        "PacificCyan": "#26A3C1",
        "SteelPink": "#B74EB6",
        "Aero": "#28B7D8",
        "Aureolin": "#E5E413",
        "Imperial red": "#F04D4C",
        "Jade": "#0DA66B",
        "Azul": "#2372C7"
    }

    # Import dependencies (assumes extract.depends is defined elsewhere)
    dep = list(depends(url, relative=relative, prefix=prefix))
    dep.sort()

    # Define regex based on format type (prefix vs full URL)
    if prefix:
        # Match: prefix:folder/filename(.jsonld)?
        pattern = re.compile(r'(\w+:)([\w\-/]+\/)([\w\-/]+)(\.jsonld)?')
    else:
        # Match: full URL with domain, folder/, and filename(.jsonld)?
        pattern = re.compile(r'https?://([\w\-.]+/[\w\-/]+/)([\w\-/]+/)([\w\-/]+)(\.jsonld)?')

    # Set fixed widths for aligned display
    widths = [42, 4, 50]

    # Format each match into aligned colored segments using Rich markup
    def replace(m: re.Match) -> str:
        part1 = (m.group(1)[:-1] + '[/]' + m.group(1)[-1])  # Close style before last char (e.g., colon)
        return (
            f"  [bold {colours['Aureolin']}]{part1.rjust(widths[0])}"
            f"[{colours['Aero']}]{m.group(2).rjust(widths[1])}[/]"
            f"[{colours['Imperial red']}]{(m.group(3) or '').ljust(widths[2])}[/]"
            
        )

    # Apply regex substitution and wrap each in a Rich Text object
    text_sections: List[Text] = [Text.from_markup(pattern.sub(replace, d)) for d in dep]

    # Build panel with grouped lines
    panel = Panel(
        Group(*text_sections),
        title=f"Dependencies for {url}",
        # title_style=f"bold {colours['Jade']}",
        border_style=colours['Azul'],
        padding=(1, 2)
    )

    # Display in console
    console = Console()
    console.print(panel)


def depends_keys(url: str, prefix: bool = False, external_only: bool = True) -> Set[str]:
    """
    Extract property keys that reference external dependencies using RDF triples.
    
    This approach analyzes the actual RDF graph structure to find which properties
    (predicates) point to external resources.

    Args:
        url: URL of the JSON-LD document
        prefix: If True, returns prefixed property names where possible
        external_only: If True, only returns keys that reference external URIs

    Returns:
        Set of property keys (predicates) that reference external dependencies
    """
    try:
        from urllib.parse import urlparse
        
        # Convert JSON-LD to RDF triples
        rdf_dataset = jsonld.to_rdf(url)
        
        external_properties = set()
        base_domain = urlparse(url).netloc if external_only else None
        
        # Analyze each triple in the RDF dataset
        for graph_name, triples in rdf_dataset.items():
            for triple in triples:
                predicate_uri = triple['predicate']['value'] 
                object_val = triple['object']['value']
                object_type = triple['object']['type']
                
                # Only analyze triples where the object is an IRI (not a literal)
                if object_type == 'IRI':
                    object_domain = urlparse(object_val).netloc
                    
                    # Filter for external references if requested
                    if external_only:
                        if base_domain and object_domain and object_domain != base_domain:
                            prop_key = _uri_to_key(predicate_uri, prefix)
                            external_properties.add(prop_key)
                    else:
                        # Include all IRI references
                        prop_key = _uri_to_key(predicate_uri, prefix)
                        external_properties.add(prop_key)
        
        return external_properties
        
    except Exception as e:
        print(f"Error extracting dependency keys via RDF: {str(e)}")
        return set()


def depends_keys_detailed(url: str, prefix: bool = False) -> dict:
    """
    Extract property keys and their external values using RDF triples.
    
    Returns detailed mapping of which properties reference which external URIs.

    Args:
        url: URL of the JSON-LD document
        prefix: If True, uses prefixes for both keys and values

    Returns:
        Dict mapping property keys to sets of external URIs they reference
    """
    try:
        from urllib.parse import urlparse
        from collections import defaultdict
        
        rdf_dataset = jsonld.to_rdf(url)
        
        external_refs = defaultdict(set)
        base_domain = urlparse(url).netloc
        
        for graph_name, triples in rdf_dataset.items():
            for triple in triples:
                predicate_uri = triple['predicate']['value']
                object_val = triple['object']['value']
                object_type = triple['object']['type']
                
                # Only analyze IRI objects
                if object_type == 'IRI':
                    object_domain = urlparse(object_val).netloc
                    
                    # Check if this is an external reference
                    if object_domain and object_domain != base_domain:
                        prop_key = _uri_to_key(predicate_uri, prefix)
                        object_key = _uri_to_key(object_val, prefix) if prefix else object_val
                        
                        external_refs[prop_key].add(object_key)
        
        return dict(external_refs)
        
    except Exception as e:
        print(f"Error extracting detailed dependency mapping via RDF: {str(e)}")
        return {}


def _uri_to_key(uri: str, use_prefix: bool = False) -> str:
    """
    Convert a full URI to a readable key name using existing prefix mappings.
    
    Args:
        uri: Full URI of the property
        use_prefix: Whether to use prefix notation
        
    Returns:
        Human-readable key name
    """
    if use_prefix and mapping:
        # Try to find a matching prefix from your existing mappings
        for prefix_key, base_uri in mapping.items():
            if uri.startswith(base_uri):
                remainder = uri[len(base_uri):].lstrip('/')
                return f"{prefix_key}:{remainder}" if remainder else prefix_key
    
    # Fallback: extract the local name from the URI
    if '#' in uri:
        return uri.split('#')[-1]
    elif '/' in uri:
        return uri.split('/')[-1]
    else:
        return uri


def display_depends_keys(url: str, prefix: bool = True) -> None:
    """
    Display external dependency keys in a formatted panel.

    Args:
        url: URL of the JSON-LD document
        prefix: If True, uses prefixes for formatting
    """
    from rich.console import Console, Group
    from rich.panel import Panel
    from rich.text import Text
    
    # Define colors (reusing your existing color scheme)
    colours = {
        "PacificCyan": "#26A3C1", 
        "SteelPink": "#B74EB6",
        "Aero": "#28B7D8",
        "Aureolin": "#E5E413",
        "Imperial red": "#F04D4C",
        "Jade": "#0DA66B",
        "Azul": "#2372C7"
    }

    # Get the keys and detailed mapping
    external_keys = depends_keys(url, prefix=prefix, external_only=True)
    key_details = depends_keys_detailed(url, prefix=prefix)
    
    console = Console()
    
    if not external_keys:
        console.print(f"[bold yellow]No external dependency keys found for {url}[/bold yellow]")
        return
    
    # Create formatted output
    text_sections = []
    
    for key in sorted(external_keys):
        # Show the key
        key_text = f"[bold {colours['Aureolin']}]{key}[/]"
        
        # Show what it references
        if key in key_details and key_details[key]:
            references = ", ".join(sorted(key_details[key]))
            key_text += f" → [{colours['Imperial red']}]{references}[/]"
        
        text_sections.append(Text.from_markup(key_text))
    
    # Build panel
    panel = Panel(
        Group(*text_sections),
        title=f"External Dependency Keys for {url}",
        border_style=colours['Azul'],
        padding=(1, 2)
    )
    
    console.print(panel)