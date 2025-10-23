import requests


def get_repo_tree(owner, repo, path="src-data", branch="main", prefix=None):
    # owner,repo,path,branch = "WCRP-CMIP", "WCRP-universe","src-data","main"

    if prefix is None:
        prefix = repo

    if path[-1] == "/":
        path = path[:-1]
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"
    print(url)

    def tree(url):

        # owner,repo = url.replace('https://github.com/','').split('/',2)[:2]
        # preurl = f"https://{owner}.github.io/{repo}/"

        response = requests.get(url)
        contents = response
        if response.status_code == 200:
            contents = response.json()
        else:
            assert not response.text, response

        owner, repo = url.replace(
            'https://api.github.com/repos/', '').split('/', 2)[:2]
        preurl = f"https://{owner}.github.io/{repo}/"

        for item in contents:
            item['prefix'] = prefix

            if '_links' in item:
                del item['_links']
            item['filename'] = ''+item['name']
            item['name'] = item['name'].split('.json')[0]
            item['path'] = item['path'].replace(path, '')
            item['jsonld'] = f"{preurl}{item['path']}".split('.json')[0]
            if item['type'] == "dir":
                item['children'] = tree(item['url'])

        return contents

    contents = tree(url)

    complete = {
        "name": prefix,
        "path": path,
        "prefix": prefix,
        "html_url": f"https://github.com/{owner}/{repo}/blob/{branch}/{path}",
        "git_url": url,
        "children": contents
    }

    return complete


def display_hierarchy(hierarchy, style="arrow", level=0, prefix="", start_level=0, show=False):
    """
    Display a hierarchy in various styles.

    Args:
        hierarchy (list): Hierarchical data (list of dicts with 'name' and optionally 'children').
        style (str): The style of display. Options are:
            - "tree" (default): Tree-like with branches.
            - "indented": Simple indented list.
            - "bracketed": Square bracket notation.
            - "table": ASCII table style.
            - "numbered": Numbered outline format.
            - "graph": Arrows to show relationships.
            - "bullets": Bullet points for levels.
            - "arrow": Downward-right arrow for nesting.
            - "json": JSON-like structure.
        level (int): Current recursion level for indentation (internal use).
        prefix (str): Prefix used for numbering or custom markers (internal use).
        start_level (int): Base level for indentation.

    Returns:
        str: The formatted hierarchy as a string.
    """
    output = ""

    for i, item in enumerate(hierarchy, 1):
        # Determine prefixes and indentation
        current_prefix = f"{prefix}{i}" if style == "numbered" else ""
        indent = "    " * (level - start_level)
        marker = ""

        if style == "tree":
            marker = f"{'│   ' * (level - start_level)}├── {item['name']}"
        elif style == "indented":
            marker = f"{'  ' * (level - start_level)}- {item['name']}"
        elif style == "bracketed":
            marker = f"{'  ' * (level - start_level)}[{item['name']}]"
        elif style == "table":
            marker = f"{indent}{item['name']}"
        elif style == "numbered":
            marker = f"{current_prefix} {item['name']}"
        elif style == "graph":
            marker = f"{'  ' * (level - start_level)}-> {item['name']}"
        elif style == "bullets":
            marker = f"{'*' * (level - start_level + 1)} {item['name']}"
        elif style == "arrow":
            marker = f"{'    ' * (level - start_level)}↳ {item['name']}"
        elif style == "json":
            marker = f"{indent}{{'name': '{item['name']}'"
            if 'children' in item:
                marker += f", 'children': [\n{display_hierarchy(item['children'], style, level + 1, prefix, start_level)}\n{indent}]"
            marker += f"}}"

        # Append the marker to output
        if style != "json":
            output += f"{marker}\n"
        else:
            output += f"{marker}\n"

        # Handle children recursively
        if 'children' in item and style != "json":
            output += display_hierarchy(item['children'], style,
                                        level + 1, current_prefix + ".", start_level)

    if show:
        #     print(output)
        print(output)
    return output


def showall(contents):
    # Display hierarchy with different styles
    print("Tree Style:\n")
    print(display_hierarchy(contents, style="tree"))

    print("\nArrow Style:\n")
    print(display_hierarchy(contents, style="arrow"))

    print("\nIndented List Style:\n")
    print(display_hierarchy(contents, style="indented"))

    print("\nBracketed Style:\n")
    print(display_hierarchy(contents, style="bracketed"))

    print("\nTable Style:\n")
    print(display_hierarchy(contents, style="table"))

    print("\nNumbered Outline Style:\n")
    print(display_hierarchy(contents, style="numbered"))

    print("\nGraph Style:\n")
    print(display_hierarchy(contents, style="graph"))

    print("\nBullet Point Style:\n")
    print(display_hierarchy(contents, style="bullets"))

    print("\nJSON-Like Style:\n")
    print(display_hierarchy(contents, style="json"))


def filter_nested_dict(data, valid_extensions=[".json"],
                       valid_names=["_context_"]):
    """
    Recursively filters a nested dictionary to include only items whose names 
    have valid extensions or match specific names.

    Args:
        data (list): A list of dictionaries representing the nested structure.
        valid_extensions (list): List of valid file extensions (e.g., ['.json', '.jsonld']).
        valid_names (list): List of specific names to include (e.g., ['_context_']).

    Returns:
        list: Filtered nested dictionary.
    """

    def is_valid(name):
        # Check if the name is valid based on extensions or specific names
        return (
            any(name.endswith(ext) for ext in valid_extensions)
            or name in valid_names
        )

    filtered = []
    for item in data['children']:

        if is_valid(item.get('filename', valid_extensions[0])) or item.get('type') != "file":
            # Keep valid items and filter their children recursively
            if 'children' in item:
                item['children'] = filter_nested_dict(
                    item, valid_extensions, valid_names
                )['children']
            filtered.append(item)

    data['children'] = filtered
    return data
