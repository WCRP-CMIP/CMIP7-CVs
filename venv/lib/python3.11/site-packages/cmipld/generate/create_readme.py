#!/usr/bin/env python3
"""
Create README files for WCRP universe data directories.
"""

import os
import re
import json
import glob
import sys
import argparse
import numpy as np
import urllib.parse
from collections import defaultdict
import cmipld
from cmipld.utils.server_tools.offline_patched import LD_server
from cmipld.utils.git import get_path_url, get_repo_url, get_relative_path, url2io
from cmipld import prefix_url
from cmipld.utils.extract.links import depends_keys, depends_keys_detailed

parser = argparse.ArgumentParser(description='Create README files for WCRP universe data directories')
parser.add_argument('directory', help='Directory path to process')

try:
    import esgvoc
    from esgvoc.api.data_descriptors import DATA_DESCRIPTOR_CLASS_MAPPING
except ImportError:
    print("Warning: esgvoc not available. Pydantic models will not be used.")
    DATA_DESCRIPTOR_CLASS_MAPPING = {}


def sort_keys_like_json(keys):
    """Sort keys in the same order as JSON files."""
    priority_keys = ['id', 'validation-key', 'ui-label', 'description']
    end_keys = ['@context', 'type']
    
    sorted_keys = []
    
    for key in priority_keys:
        if key in keys:
            sorted_keys.append(key)
    
    remaining_keys = [k for k in keys if k not in priority_keys and k not in end_keys]
    sorted_keys.extend(sorted(remaining_keys))
    
    for key in end_keys:
        if key in keys:
            sorted_keys.append(key)
    
    return sorted_keys


def bullet_pydantic(pm):
    """Generate bullet points from Pydantic model."""
    if not pm:
        return ""
    
    field_names = list(pm.__pydantic_fields__.keys())
    sorted_fields = sort_keys_like_json(field_names)
    
    keys = ""
    for key in sorted_fields:
        if key in pm.__pydantic_fields__:
            value = pm.__pydantic_fields__[key]
            typename = getattr(value.annotation, '__name__', str(value.annotation))
            description = value.description or '_No description in pydantic model (see esgvoc)_'
            keys += f"- **`{key}`** (**{typename}**) \n  {description.rstrip()}\n"
    
    return keys


def bullet_names(keynames):
    """Generate bullet points from key names."""
    sorted_keynames = sort_keys_like_json(keynames)
    
    keys = ""
    for key in sorted_keynames:
        keys += f"- **`{key}`**  \n   [**unknown**]\n  No Pydantic model found.\n"
    
    return keys


def extract_description(readme_content):
    """Extract description from README file content."""
    pattern = r'<section id="description">(.*?)</section>'
    match = re.search(pattern, readme_content, re.DOTALL)
    
    if not match:
        return None
    
    section_content = match.group(1).strip()
    desc_pattern = r'## Description\s*(.*?)(?=\n\n|\Z)'
    desc_match = re.search(desc_pattern, section_content, re.DOTALL)
    
    return desc_match.group(1).strip() if desc_match else None


def extract_external_contexts(context):
    """Extract external contexts from JSON-LD context."""
    mappings = []
    repos = defaultdict(set)

    inner_context = context["@context"][1] if isinstance(context["@context"], list) else context["@context"]

    for key, value in inner_context.items():
        if key.startswith("@"):
            continue

        ext_context = value.get("@context") if isinstance(value, dict) else None
        key_type = value.get("@type") if isinstance(value, dict) else None

        if ext_context:
            parsed = urllib.parse.urlparse(ext_context)
            path_parts = parsed.path.strip("/").split("/")
            org = path_parts[0] if len(path_parts) > 1 else "unknown"
            repo = path_parts[1] if len(path_parts) > 2 else "unknown"
            path = "/" + "/".join(path_parts[2:]) if len(path_parts) > 2 else parsed.path

            mappings.append({
                "key": key,
                "type": key_type,
                "context_url": ext_context,
                "organization": org,
                "repository": repo,
                "path": path
            })

            repos[(org, repo)].add(path)

    return mappings, repos


def create_breadcrumb_dependencies(all_deps, self_prefix, current_name):
    """Create breadcrumb-style dependency navigation with key → prefix:location [link] format."""
    last = re.compile(r'/[^/]+$')
    external_deps = set([last.sub('', x) for x in all_deps if not x.startswith(self_prefix)])
    
    if not external_deps:
        return "", ""
    
    # Create breadcrumb summary
    dep_count = len(external_deps)
    # if dep_count <= 3:
    #     breadcrumb = " → ".join(sorted(external_deps))
    # else:
    #     top_3 = sorted(external_deps)[:3]
    #     breadcrumb = " → ".join(top_3) + f" → (+{dep_count-3} more)"
    
    breadcrumb_summary = f"""**{current_name}** depends on **{dep_count} external vocabularies**  

The following external vocabularies are required to fully describe the data:"""
    
    # Create combined key → prefix:location [link] format
    detailed_links = []
    for x in sorted(external_deps):
        sprefix, spath = x.split(':', 1)
        base_link = cmipld.mapping.get(sprefix, 'prefix_not_in_cmipld')
        
        # For each path component, create the key → prefix:loc [link] format
        path_components = [comp for comp in spath.split('/') if comp]
        
        temp_link = base_link
        for i, component in enumerate(path_components):
            temp_link += f'{component}/'
            # Create the format: key → prefix:component [link]
            key_display = component
            prefix_loc = f"{sprefix}:{'/'.join(path_components[:i+1])}"
            detailed_links.append(f"- `{key_display} → {prefix_loc}` [link]({temp_link})")
    
    return breadcrumb_summary, "\n".join(detailed_links)


def links(ctxloc, graph_url=None, prefix_name=None, all_deps=None, self_prefix=None):
    """Generate combined links and dependencies section."""
    # Context-based analysis
    try:
        jsonld_context = json.load(open(ctxloc, 'r', encoding='utf-8'))
    except FileNotFoundError:
        return "<section id='links'>\n\n## 🔗 Links and Dependencies\n\nNo context file found!!!</section> \n\n"
    
    mappings, repo_breakdown = extract_external_contexts(jsonld_context)

    # RDF-based analysis
    external_keys = set()
    key_details = {}
    rdf_summary = ""
    
    if graph_url:
        try:
            external_keys = depends_keys(graph_url, prefix=True, external_only=True)
            key_details = depends_keys_detailed(graph_url, prefix=True)
            
            if external_keys:
                key_count = len(external_keys)
                total_refs = sum(len(refs) for refs in key_details.values())
                
                breadcrumb_keys = " → ".join(sorted(list(external_keys)[:5]))
                if len(external_keys) > 5:
                    breadcrumb_keys += f" → (+{len(external_keys)-5} more)"
                    
                rdf_summary = f"""
### 🔍 RDF Analysis Summary
**{key_count} properties** reference **{total_refs} external resources**  
**Property path:** `{breadcrumb_keys}`
"""
        except Exception as e:
            print(f"Error in RDF analysis: {e}")
            rdf_summary = "\n### 🔍 RDF Analysis\n*Error analyzing RDF dependencies*\n"

    # Dependencies analysis
    dep_summary = ""
    dep_details = ""
    if all_deps and self_prefix and prefix_name:
        breadcrumb_summary, detailed_deps = create_breadcrumb_dependencies(all_deps, self_prefix, prefix_name)
        if detailed_deps:
            dep_summary = f"\n### External Dependencies\n{breadcrumb_summary}\n"
            dep_details = f"\n{detailed_deps}\n"

    # Build markdown output
    markdown_output = ['<section id="links">\n']
    markdown_output.append("## 🔗 Links and Dependencies\n")
    
    # Add dependencies first if they exist
    if dep_summary:
        markdown_output.append(dep_summary)
        markdown_output.append(dep_details)
    
    if rdf_summary:
        markdown_output.append(rdf_summary)
    
    # RDF-based External Property Analysis
    if external_keys:
        markdown_output.append("\n### Properties with External References\n")
        markdown_output.append("*Based on RDF triple analysis*\n")
        
        for key in sorted(external_keys):
            if key in key_details and key_details[key]:
                refs = ", ".join([f"`{ref}`" for ref in sorted(key_details[key])])
                markdown_output.append(f"- **`{key}`** → {refs}")
            else:
                markdown_output.append(f"- **`{key}`**")
        markdown_output.append("")

    # Context-based External Mappings  
    if mappings:
        markdown_output.append("\n### Contexts of External Mappings\n")
        ctxrp = r'\_context\_'
        for m in mappings:
            markdown_output.append(f"- **`{m['key']}`** → `@type: {m['type']}`")
            markdown_output.append(f"  - Context: [{m['context_url'].replace('_context_', ctxrp)}]({m['context_url']})")
            markdown_output.append(f"  - Source: `{m['organization']}/{m['repository']}{m['path']}`\n")

    if len(markdown_output) < 4:
        return '\n<section id="links">\n\n## 🔗 Links and Dependencies\n\nNo external links or dependencies found.\n\n</section>\n\n'

    markdown_output.append("\n</section>\n")
    return "\n".join(markdown_output)


def main():
    """Main function to process directory and create README files."""
    args = parser.parse_args()
    
    if not os.path.exists(args.directory):
        print(f"Error: Directory {args.directory} does not exist")
        sys.exit(1)
    
    directory_path = args.directory
    
    # Set up local server
    repo_url = cmipld.utils.git.get_repo_url()
    prefix = cmipld.reverse_direct[repo_url]
    
    location = directory_path.split('src-data')[0] + 'src-data'
    local = [(location, cmipld.mapping[prefix], prefix)]
    server = LD_server(copy=local, use_ssl=False)
    base_url = server.start_server(port=8081)
    
    # Change to the specified directory
    os.chdir(directory_path)
    
    # Get all subdirectories
    folders = glob.glob('*/')
    print(folders)
    missing_pydantic = []
    
    for dir_path in folders:
        print(f"Processing {dir_path}")
        name = dir_path.strip('/')
        
        if name == 'project':
            print("Skipping 'project' directory.")
            continue
        
        # Skip if no JSON files
        json_files = [f for f in os.listdir(dir_path) if f.endswith('.json')]
        if not json_files:
            print(f"Skipping {dir_path} as it does not contain any JSON files.")
            continue
        
        # Get the first JSON file alphabetically
        select = sorted(json_files, key=lambda x: x.lower())[0].strip('.json')
        
        # Analyze JSON keys
        try:
            keys_output = os.popen(f"jq -r 'recurse(.[]? // empty) | objects | keys_unsorted[]' {dir_path}*.json | sort | uniq -c | sort -nr").read()
            keynames = [i.split(' ')[-1] for i in keys_output.split('\n') if i.strip()]
            
            if keynames:
                keynumbers = [int(i.split(' ')[-2]) for i in keys_output.split('\n') if i.strip()]
                avg = int(np.median(keynumbers))
                different = [keynames[i] for i, x in enumerate(keynumbers) if x != avg]
                
                if different:
                    print('The following keys are not present in all files:', different)
                    print('<<add these to an issue>>')
            
        except (ValueError, IndexError) as e:
            print(f"Error processing {dir_path}: {e}")
            continue
        
        # Check for Pydantic model
        dname = dir_path.strip('/').replace('-', '_')
        pydantic = False
        
        if dname in DATA_DESCRIPTOR_CLASS_MAPPING:
            pydantic = dname
        elif dname + '_new' in DATA_DESCRIPTOR_CLASS_MAPPING:
            pydantic = dname + '_new'
        elif dir_path.strip('/') in DATA_DESCRIPTOR_CLASS_MAPPING:
            pydantic = dir_path.strip('/')
        else:
            missing_pydantic.append(dname)
            print(f"Adding {dname} to DATA_DESCRIPTOR_CLASS_MAPPING")
        
        # Generate bullet points
        if pydantic and DATA_DESCRIPTOR_CLASS_MAPPING:
            bullets = bullet_pydantic(DATA_DESCRIPTOR_CLASS_MAPPING[pydantic])
        else:
            bullets = bullet_names(keynames)
        
        # Generate URLs
        content = get_path_url(dir_path).replace('wolfiex', 'wcrp-cmip')
        repo = get_repo_url().replace('wolfiex', 'wcrp-cmip')
        relpath = get_relative_path(dir_path)
        
        io = relpath.replace('src-data/', url2io(repo, 'main', relpath))
        short = prefix_url(io)
        
        # Generate content sections
        self = f'{prefix}:{name}'
        graph_url = f'{self}/graph.jsonld'
        
        # Dependencies analysis
        all = cmipld.depends(graph_url, prefix=True)
        
        # Combined links and dependencies section
        link_content = links(f"{dir_path}/_context_", graph_url, name, all, self)
        
        # Description section
        existing_description = ""
        readme_path = f"{dir_path}README.md"
        if os.path.exists(readme_path):
            with open(readme_path, 'r') as f:
                existing_content = f.read()
            existing_description = extract_description(existing_content)
        
        description = f'''
<section id="description">

# {name.title().replace('-', ' ').replace(':', ' : ')}  ({prefix})

## Description
{existing_description or ""}

</section>
'''
        
        # Info section
        info = f'''
<section id="info">

| Item | Reference |
| --- | --- |
| Type | `{prefix}:{name}` |
| Pydantic class | [`{pydantic}`](https://github.com/ESGF/esgf-vocab/blob/main/src/esgvoc/api/data_descriptors/{pydantic}.py): {DATA_DESCRIPTOR_CLASS_MAPPING[pydantic].__name__ if pydantic and DATA_DESCRIPTOR_CLASS_MAPPING else ' Not yet implemented'} |
| | |
| JSON-LD | `{short}` |
| Expanded reference link | [{io}]({io}) |
| Developer Repo | [![Open in GitHub](https://img.shields.io/badge/Open-GitHub-blue?logo=github&style=flat-square)]({content}) |

</section>
'''
        
        # Schema section
        schema = f'''
<section id="schema">

## Content Schema

{bullets}

</section>   
'''
        
        # Usage section
        usage = f'''
<section id="usage">

## Usage

### Online Viewer 
#### Direct
To view a file in a browser use the content link with `.json` appended.

For example: `{content}/{select}.json`

#### Use cmipld.js [in development]
[View self resolving files here](https://wcrp-cmip.github.io/CMIPLD/viewer/index.html?uri={short.replace(':','%253A').replace('/', '%252F')}/{select})

### Getting a File

A short example of how to integrate the computed ld file into your code. 

```python
import cmipld
cmipld.get("{short}/{select}")
```

### Framing
Framing is a way we can filter the downloaded data to match what we want. 
```python
frame = {{
    "@context": "{io}/_context_",
    "@type": "{prefix}:{name}",
    "keys we want": "",
    "@explicit": True
}}
        
import cmipld
cmipld.frame("{short}/{select}", frame)
```
</section>
'''
        
        htmllink = f"[View in HTML]({io}/{relpath.replace('src-data/', '')})\n" 
        
        # Combine all sections
        readme = f'''{htmllink}{description}{info}{link_content}{schema}{usage}'''
        
        # Write README file
        with open(f'{dir_path}README.md', 'w') as f:
            f.write(readme)
        
        print(f"Created README for {dir_path}")
    
    print(f"\nProcessing complete. Missing pydantic models: {missing_pydantic}")


if __name__ == "__main__":
    main()
