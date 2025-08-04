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

# Source paths - check template sources first, then static versions
js_source_template = project_root / ".src" / "mkdocs" / "scripts" / "embed.js.jinja"
js_source_generated = project_root / ".src" / "mkdocs" / "scripts" / "embed.js"
js_source_static = docs_path / "scripts" / "embed.js"

css_source_template = project_root / ".src" / "mkdocs" / "stylesheets" / "extra.css.jinja"
css_source_generated = project_root / ".src" / "mkdocs" / "stylesheets" / "extra.css"
css_source_static = docs_path / "stylesheets" / "extra.css"

print(f"Docs path: {docs_path}", file=sys.stderr)
print(f"Project root: {project_root}", file=sys.stderr)

# Copy JavaScript file - check template, generated, then static
js_copied = False
for js_source, source_type in [(js_source_template, "template"), (js_source_generated, "generated"), (js_source_static, "static")]:
    if js_source.exists() and not js_copied:
        print(f"✅ Found embed.js ({source_type}), copying to generated files", file=sys.stderr)
        print(f"   Source: {js_source}", file=sys.stderr)
        
        with open(js_source, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        with mkdocs_gen_files.open("scripts/embed.js", "w") as f:
            f.write(js_content)
        
        print(f"✅ Copied embed.js from {source_type} source", file=sys.stderr)
        js_copied = True
        break

if not js_copied:
    print(f"⚠️  embed.js not found at any source location", file=sys.stderr)
    print(f"   Checked: {js_source_template}", file=sys.stderr)
    print(f"   Checked: {js_source_generated}", file=sys.stderr)
    print(f"   Checked: {js_source_static}", file=sys.stderr)

# Copy CSS file - check template, generated, then static
css_copied = False
for css_source, source_type in [(css_source_template, "template"), (css_source_generated, "generated"), (css_source_static, "static")]:
    if css_source.exists() and not css_copied:
        print(f"✅ Found extra.css ({source_type}), copying to generated files", file=sys.stderr)
        print(f"   Source: {css_source}", file=sys.stderr)
        
        with open(css_source, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        with mkdocs_gen_files.open("stylesheets/extra.css", "w") as f:
            f.write(css_content)
        
        print(f"✅ Copied extra.css from {source_type} source", file=sys.stderr)
        css_copied = True
        break

if not css_copied:
    print(f"⚠️  extra.css not found at any source location", file=sys.stderr)
    print(f"   Checked: {css_source_template}", file=sys.stderr)
    print(f"   Checked: {css_source_generated}", file=sys.stderr)
    print(f"   Checked: {css_source_static}", file=sys.stderr)

print("="*60, file=sys.stderr)
