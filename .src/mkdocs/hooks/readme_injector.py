#!/usr/bin/env python3
"""
Hook to inject README.md content into index.md after the documentation tip.
"""

import os
from pathlib import Path

def on_page_markdown(markdown, page, config, files):
    """
    Hook that processes page markdown before it's converted to HTML.
    This runs for each page, but we only process index.md.
    """
    
    # Only process the main index page
    if page.file.src_path != 'index.md':
        return markdown
    
    # Look for the tip section
    tip_marker = '!!! tip "Documentation in progress"'
    
    if tip_marker not in markdown:
        return markdown
    
    # Try to find and read README.md from the project root
    docs_dir = Path(config['docs_dir'])
    project_root = docs_dir.parent
    readme_path = project_root / 'README.md'
    
    readme_content = ""
    if readme_path.exists():
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                readme_content = f.read().strip()
            print(f"✅ Injected README.md content ({len(readme_content)} chars) into index.md")
        except Exception as e:
            print(f"⚠️  Error reading README.md: {e}")
            readme_content = "*Could not load README.md content*"
    else:
        print(f"⚠️  README.md not found at {readme_path}")
        readme_content = "*README.md not found in project root*"
    
    # Find the tip section and inject README content after it
    lines = markdown.split('\n')
    new_lines = []
    in_tip_section = False
    tip_section_ended = False
    
    for line in lines:
        new_lines.append(line)
        
        # Detect start of tip section
        if tip_marker in line:
            in_tip_section = True
            continue
            
        # Detect end of tip section (next non-indented content or empty line followed by non-indented)
        if in_tip_section and not tip_section_ended:
            # If we hit a line that doesn't start with spaces (and isn't empty), tip section ended
            if line.strip() and not line.startswith('    '):
                # Insert README content before this line
                new_lines.insert(-1, '')  # Add empty line
                new_lines.insert(-1, '## Project Information')
                new_lines.insert(-1, '')
                new_lines.insert(-1, readme_content)
                new_lines.insert(-1, '')  # Add empty line after
                tip_section_ended = True
    
    # If we never found the end (file ends with tip section), add at the end
    if in_tip_section and not tip_section_ended:
        new_lines.append('')
        new_lines.append('## Project Information')
        new_lines.append('')
        new_lines.append(readme_content)
    
    return '\n'.join(new_lines)
