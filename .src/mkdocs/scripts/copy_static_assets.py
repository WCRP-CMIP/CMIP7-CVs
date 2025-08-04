#!/usr/bin/env python3
"""
Copy static assets (JS and CSS) to the site
"""

import os
import sys
from pathlib import Path
import mkdocs_gen_files
import shutil

print("="*60, file=sys.stderr)
print("COPYING STATIC ASSETS", file=sys.stderr)
print("="*60, file=sys.stderr)

# Get the docs directory
docs_path = Path(mkdocs_gen_files.config.docs_dir)
project_root = docs_path.parent

# Source paths (in the docs folder)
js_source = docs_path / "scripts" / "embed.js"
css_source = docs_path / "stylesheets" / "extra.css"

print(f"Docs path: {docs_path}", file=sys.stderr)
print(f"JS source: {js_source}", file=sys.stderr)
print(f"CSS source: {css_source}", file=sys.stderr)

# Copy JavaScript file if it exists
if js_source.exists():
    print(f"✅ Found embed.js, copying to generated files", file=sys.stderr)
    with open(js_source, 'r', encoding='utf-8') as f:
        js_content = f.read()
    
    with mkdocs_gen_files.open("scripts/embed.js", "w") as f:
        f.write(js_content)
    
    print(f"✅ Copied embed.js", file=sys.stderr)
else:
    print(f"⚠️  embed.js not found at {js_source}", file=sys.stderr)

# Copy CSS file if it exists
if css_source.exists():
    print(f"✅ Found extra.css, copying to generated files", file=sys.stderr)
    with open(css_source, 'r', encoding='utf-8') as f:
        css_content = f.read()
    
    with mkdocs_gen_files.open("stylesheets/extra.css", "w") as f:
        f.write(css_content)
    
    print(f"✅ Copied extra.css", file=sys.stderr)
else:
    print(f"⚠️  extra.css not found at {css_source}", file=sys.stderr)

print("="*60, file=sys.stderr)
