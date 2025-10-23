from pyld import jsonld
from ..logging.unique import UniqueLogger
log = UniqueLogger()

def get(link, compact=True, depth=2):
    """
    Retrieves and processes a JSON-LD document from the given link.

    Parameters:
        link (str): URL to the JSON-LD document.
        compact (bool): Whether to compact the final output using the original context.
        depth (int): How many levels deep to follow and resolve @id references.

    Returns:
        dict or list: The resolved and optionally compacted JSON-LD document.
    """
    body = jsonld.expand(link, options={'extractAllScripts': True})

    
    resolved = _resolve_ids(body, compact=compact, depth=depth)

    if compact:
        return jsonld.compact(resolved, link)

    return resolved


def frame(link, frame_obj, compact=True, depth=2):
    """
    Retrieves and frames a JSON-LD document from the given link using a frame object.

    Parameters:
        link (str): URL to the JSON-LD document.
        frame_obj (dict): The JSON-LD frame to apply to the document.
        compact (bool): Whether to compact the final output using the original context.
        depth (int): How many levels deep to follow and resolve @id references.

    Returns:
        dict or list: The framed and optionally compacted JSON-LD document.
    """
    
    if '@context' not in frame_obj:
        frame_obj['@context'] = link  # Use the link as context if not provided
        
        
    # First get the resolved document
    resolved = get(link, compact=False, depth=depth)
    
    try:
        # Apply the frame to the resolved document
        framed = jsonld.frame(resolved, frame_obj)
        
        if compact:
            # Compact using the original document's context
            return jsonld.compact(framed, link)
        
        return framed
        
    except jsonld.JsonLdError as e:
        log.warn(f'WARNING: Framing failed for {link}: {e}')
        # Fallback to original resolved document
        return resolved if not compact else jsonld.compact(resolved, link)


def _resolve_ids(data, compact=True, depth=2):
    """
    Recursively resolves @id references in a JSON-LD structure.

    Parameters:
        data (dict or list): The expanded JSON-LD structure to resolve.
        compact (bool): Whether to compact merged results when combining data.
        depth (int): How many levels deep to resolve @id references.

    Returns:
        dict or list: The structure with @id references resolved.
    """
    if not depth:
        return data

    if isinstance(data, dict):
        if '@id' in data and not '@type' in data and data['@id'].startswith('http'):
            try:
                # Recursively fetch and resolve the linked JSON-LD document
                expanded = get(data['@id'], compact=compact, depth=depth - 1)
                
                if isinstance(expanded, list):
                    expanded = expanded[0] if len(expanded) == 1 else expanded
                
            except jsonld.JsonLdError:
                log.warn('\n WARNING missing id: '+data['@id'])
                expanded = None

            if expanded:
                if len(data.keys()) - 1:
                    # Merge original data into the expanded structure (excluding @id)
                    del data['@id']
                    if compact:
                        # Compact the merged data using the original context
                        data = jsonld.compact({**expanded, **data}, expanded)
                    else:
                        # Just merge without compacting
                        data = jsonld.expand({**expanded, **data}, expanded)
                    # data = jsonld.compact({**expanded, **data}, expanded)
                else:
                    data = expanded
                    
        if isinstance(data, list):
            data = data[0] if len(data) == 1 else data
            
        return {
            key: _resolve_ids(value, compact, depth)
            for key, value in data.items()
        }

    elif isinstance(data, list):
        if len(data) > 3 and depth < 2:
            # (Placeholder for parallel map)
            return list(map(lambda item: _resolve_ids(item, compact, depth), data))
        else:
            return [_resolve_ids(item, compact, depth) for item in data]

    # Base case for primitives (e.g., strings, numbers)
    return data


def view(link, compact=True, depth=1):
    from rich.console import Console
    from rich.syntax import Syntax
    import json

    # Example JSON data
    json_data = get(link, compact=compact, depth=depth)


    # Convert parsed JSON data back to a formatted string for pretty display
    json_pretty = json.dumps(json_data, indent=4)

    # Create a Syntax object to apply rich formatting
    syntax = Syntax(json_pretty, "json", theme="monokai", line_numbers=True)

    # Display the formatted JSON
    console = Console()
    console.print(syntax)


def view_frame(link, frame_obj, compact=True, depth=1):
    """
    Retrieves, frames, and displays a JSON-LD document with rich formatting.

    Parameters:
        link (str): URL to the JSON-LD document.
        frame_obj (dict): The JSON-LD frame to apply to the document.
        compact (bool): Whether to compact the final output using the original context.
        depth (int): How many levels deep to follow and resolve @id references.
    """
    from rich.console import Console
    from rich.syntax import Syntax
    import json

    # Get framed JSON data
    json_data = frame(link, frame_obj, compact=compact, depth=depth)

    # Convert parsed JSON data back to a formatted string for pretty display
    json_pretty = json.dumps(json_data, indent=4)

    # Create a Syntax object to apply rich formatting
    syntax = Syntax(json_pretty, "json", theme="monokai", line_numbers=True)

    # Display the formatted JSON
    console = Console()
    console.print("[bold green]Framed JSON-LD Document:[/bold green]")
    console.print(syntax)
