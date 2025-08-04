#!/usr/bin/env python3
"""
Robust src-data processor with extensive path checking
"""

import os
import sys
from pathlib import Path
import mkdocs_gen_files
import re
import json

section = re.compile(r"</{0,1}section[^>]*>", re.IGNORECASE)

print("\n" + "="*60, file=sys.stderr)
print("SRC-DATA PROCESSOR - ROBUST VERSION", file=sys.stderr)
print("="*60, file=sys.stderr)

# Get the actual working directory and script location
cwd = Path.cwd()
script_file = Path(__file__) if '__file__' in globals() else None

print(f"Working directory: {cwd}", file=sys.stderr)
if script_file:
    print(f"Script location: {script_file}", file=sys.stderr)
    print(f"Script parent: {script_file.parent}", file=sys.stderr)

# Try multiple strategies to find src-data
search_paths = [
    # Relative to current working directory
    cwd / "src-data",
    cwd.parent / "src-data",
    cwd.parent.parent / "src-data",
    
    # Absolute paths
    Path("src-data").resolve(),
    Path("../src-data").resolve(),
    Path("../../src-data").resolve(),
    
    # Relative to script location (if known)
]

if script_file:
    search_paths.extend([
        script_file.parent.parent.parent / "src-data",
        script_file.parent.parent.parent.parent / "src-data",
    ])

# Remove duplicates while preserving order
seen = set()
unique_paths = []
for path in search_paths:
    if path not in seen:
        seen.add(path)
        unique_paths.append(path)

print(f"\nSearching for src-data in {len(unique_paths)} locations:", file=sys.stderr)

src_data_path = None
for i, path in enumerate(unique_paths, 1):
    exists = path.exists()
    is_dir = path.is_dir() if exists else False
    print(f"  {i}. {path}: ", end="", file=sys.stderr)
    
    if exists and is_dir:
        print("✅ FOUND!", file=sys.stderr)
        src_data_path = path
        break
    elif exists and not is_dir:
        print("❌ exists but is a file", file=sys.stderr)
    else:
        print("❌ not found", file=sys.stderr)

if not src_data_path:
    print("\n❌ No src-data directory found!", file=sys.stderr)
    print("\nCreating placeholder documentation...", file=sys.stderr)
    
    # Create placeholder so navigation doesn't break
    with mkdocs_gen_files.open("src-data-docs/not-found.md", "w") as f:
        f.write("""# Data Content Not Found

The `src-data` directory was not found in any of the expected locations.

## Expected Structure

Your project should have a `src-data` directory at the root level:

```
your-project/
├── mkdocs.yml
├── docs/
├── src-data/          <-- This directory is missing
│   ├── subfolder1/
│   │   ├── README.md
│   │   └── files...
│   └── subfolder2/
│       └── files...
└── ...
```

## Checked Locations

The processor checked the following locations:
""")
        for path in unique_paths:
            f.write(f"- `{path}`\n")
    
    print("="*60, file=sys.stderr)
    sys.exit(0)

# Found src-data, now process it
print(f"\n✅ Processing src-data at: {src_data_path}", file=sys.stderr)

# List all items in src-data
all_items = list(src_data_path.iterdir())
print(f"\nFound {len(all_items)} items in src-data:", file=sys.stderr)
for item in all_items:
    if item.is_dir():
        print(f"  📁 {item.name}/ (directory)", file=sys.stderr)
    else:
        print(f"  📄 {item.name} (file)", file=sys.stderr)

# Get subdirectories only
subdirs = [d for d in src_data_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
print(f"\nFound {len(subdirs)} subdirectories to process:", file=sys.stderr)

if not subdirs:
    print("⚠️  No subdirectories found in src-data!", file=sys.stderr)
    with mkdocs_gen_files.open("src-data-docs/empty.md", "w") as f:
        f.write("""# Data Content - Empty

The `src-data` directory exists but contains no subdirectories.

Please create subdirectories in `src-data/` with your data files.
""")
    sys.exit(0)

# Process each subdirectory
output_base = "src-data-docs"
sections = []

# Create index
print("\nCreating index page...", file=sys.stderr)
index_content = """# Data Content Documentation

This section contains documentation extracted from the `src-data` folder.

## Available Sections

| Section | Description | Files |
|---------|-------------|-------|
"""

# Function to create a plotly data file for the wind rose
def create_wind_rose_data(section_names, file_counts):
    """Create a wind rose visualization with file counts as bar heights."""
    # Create data for each section
    data = []
    
    # Calculate the width based on number of sections
    num_sections = len(section_names) if section_names else 1
    # Generate theta values properly spaced around the circle
    theta_values = [i * (360 / num_sections) for i in range(num_sections)]
    
    # Set bar width as a fraction of the angular spacing
    section_width = 360 / num_sections
    bar_width = min(section_width * 0.9, 120)  # 90% of section width, max 120 degrees
    
    # Create color scale based on file counts
    max_count = max(file_counts) if file_counts else 1
    min_count = min(file_counts) if file_counts else 0
    
    # Create bars for each section
    for i, (theta, section_name, file_count) in enumerate(zip(theta_values, section_names, file_counts)):
        
        # Define base colors
        base_colors = [
            "rgb(70, 102, 178)",   # Blue
            "rgb(52, 168, 83)",    # Green
            "rgb(142, 68, 173)",   # Purple
            "rgb(230, 126, 34)",   # Orange
            "rgb(217, 79, 79)"     # Red
        ]
        
        # Select a color for this section
        base_color = base_colors[i % len(base_colors)]
        
        # Split file count into segments of 5 files each
        # Calculate how many complete segments of 5 and a possible remainder
        full_segments = file_count // 5
        remainder = file_count % 5
        
        # Create r values for each segment (stacked)
        r_values = []
        
        # Add full segments of 5 files each
        for seg in range(full_segments):
            r_values.append(5)  # Each full segment is 5 files high
        
        # Add the remainder segment if there is one
        if remainder > 0:
            r_values.append(remainder)
            
        # Create arrays for theta, width, and text - same length as r_values
        num_segments = len(r_values)
        theta_values_repeated = [theta] * num_segments
        width_values = [bar_width] * num_segments
        text_values = [section_name] * num_segments
        
        # Generate colors with increasing opacity for each segment
        # Each higher segment gets a more opaque color
        opacities = [0.2 + (0.8 * seg / max(1, num_segments - 1)) for seg in range(num_segments)]
        
        # Format the colors properly based on the base color
        # Extract RGB components from the base color string
        rgb_parts = base_color.replace('rgb(', '').replace(')', '').split(',')
        colors = [f"rgba({rgb_parts[0]}, {rgb_parts[1]}, {rgb_parts[2]}, {opacity})" for opacity in opacities]
        
        # Create barpolar trace with stacked bands
        data.append({
            "type": "barpolar",
            "r": r_values,  # Heights of each segment
            "theta": theta_values_repeated,
            "width": width_values,
            "name": section_name,
            "text": text_values,
            "hoverinfo": "text+r",
            "hovertemplate": f"<b>{section_name}</b><br>Files: {file_count}<extra></extra>",
            "marker": {
                "color": colors,
                "line": {
                    "width": 0.5,
                    "color": "rgba(255, 255, 255, 0.3)"
                }
            },
            "showlegend": False
        })
    
    return {
        "data": data,
        "layout": {
            "title": {
                "text": "Data Content Directory Structure",
                "font": {"size": 20, "color": "#333333"}
            },
            "polar": {
                "radialaxis": {
                    "visible": True,
                    "range": [0, max_count * 1.05],  # Tighter range to ensure no overflow
                    "showticklabels": True,
                    "ticksuffix": " files",
                    "tickangle": 45,
                    "showline": True,
                    "linecolor": "rgba(0,0,0,0.2)"
                },
                "angularaxis": {
                    "direction": "clockwise",
                    "showticklabels": True,
                    "tickvals": theta_values,  # Use our calculated theta values
                    "ticktext": section_names,  # Display section names at these points
                    "tickfont": {"size": 12, "weight": "bold"}
                },
                "bargap": 0.03  # Reduced gap between bars for a more solid look
            },
            "showlegend": False,
            "margin": {"l": 60, "r": 60, "t": 80, "b": 60},
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "autosize": True,
            "height": 500,
            "width": 700
        }
    }

# Function to create a pie chart data file
def create_pie_chart_data(labels, values, title):
    """Create a pie chart visualization."""
    # Generate colors with better distribution and contrast
    # Using fixed color scale for better appearance
    color_scale = [
        "#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A", 
        "#19D3F3", "#FF6692", "#B6E880", "#FF97FF", "#FECB52"
    ]
    
    # Repeat colors if needed
    colors = [color_scale[i % len(color_scale)] for i in range(len(labels))]
    
    return {
        "data": [
            {
                "type": "pie",
                "labels": labels,
                "values": values,
                "textinfo": "label+percent",
                "textposition": "auto",  # Automatic positioning for better readability
                "insidetextorientation": "radial",
                "marker": {
                    "colors": colors,
                    "line": {
                        "color": "#FFFFFF",
                        "width": 1
                    }
                },
                "hoverinfo": "label+value+percent",
                "hole": 0.4,
                "sort": False  # Keep original order
            }
        ],
        "layout": {
            "title": {
                "text": title,
                "font": {"size": 18}
            },
            "showlegend": True,
            "legend": {
                "orientation": "h",
                "yanchor": "bottom",
                "y": -0.2,
                "xanchor": "center",
                "x": 0.5
            },
            "margin": {"t": 50, "b": 80, "l": 20, "r": 20},
            "autosize": True,
            "height": 500,
            "width": 700,
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)"
        }
    }

# Function to create plotly code block without using curly braces directly
def create_plotly_block(file_path):
    """Create a plotly code block with file_path reference."""
    # Use triple quotes to avoid issues with nested quotes
    open_curly = "{"
    close_curly = "}"
    # Return the plotly code block with the file path and responsive config
    return f"""```plotly
{open_curly}
  "file_path": "{file_path}",
  "config": {open_curly}
    "responsive": true,
    "displayModeBar": true,
    "displaylogo": false
  {close_curly}
{close_curly}
```"""

# Create assets directory if it doesn't exist
try:
    mkdocs_gen_files.open("assets/.gitkeep", "w").write("")
    print("✅ Created assets directory", file=sys.stderr)
except Exception as e:
    print(f"⚠️ Could not create assets directory: {e}", file=sys.stderr)

# Process each directory
for subdir in sorted(subdirs):
    folder_name = subdir.name
    print(f"\n📂 Processing '{folder_name}'...", file=sys.stderr)
    
    # Count files
    files = [f for f in subdir.iterdir() if f.is_file() and not f.name.startswith('.')]
    file_count = len(files)
    print(f"   Found {file_count} files", file=sys.stderr)
    
    # Look for README
    readme_path = subdir / "README.md"
    readme_content = f"# {folder_name.title()}\n\nDocumentation for {folder_name}."
    
    if readme_path.exists():
        try:
            with open(readme_path, 'r', encoding='utf-8', newline=None) as f:
                readme_content = f.read()
                readme_content = section.sub('', readme_content)
        except Exception as e:
            print(f"   ❌ Error reading README.md: {e}", file=sys.stderr)
    
    # Create main page
    with mkdocs_gen_files.open(f"{output_base}/{folder_name}.md", "w") as f:
        f.write(readme_content)
    print(f"   ✅ Created {folder_name}.md", file=sys.stderr)
    
    # Create contents page
    contents = f"""# {folder_name.title()} - Contents

## Files in this section

| File | Size | Type |
|------|------|------|
"""
    
    for file in sorted(files):
        size = file.stat().st_size
        size_str = f"{size:,} bytes"
        file_type = file.suffix or "no extension"
        contents += f"| {file.name} | {size_str} | {file_type} |\n"
    
    # Create file type counts for visualization
    file_extensions = {}
    for file in files:
        ext = file.suffix.lower() if file.suffix else "no extension"
        file_extensions[ext] = file_extensions.get(ext, 0) + 1
    
    # Sort by count for better visualization
    sorted_extensions = sorted(file_extensions.items(), key=lambda x: x[1], reverse=True)
    
    # Prepare pie chart data
    ext_names = [ext[1:] if ext.startswith('.') else ext for ext, _ in sorted_extensions]
    ext_counts = [count for _, count in sorted_extensions]
    
    # Create the pie chart data file
    pie_chart_data = create_pie_chart_data(
        ext_names, 
        ext_counts, 
        f"File Types in {folder_name.title()}"
    )
    pie_chart_file = f"pie_chart_{folder_name}.json"
    
    # Write the pie chart data file
    with mkdocs_gen_files.open(f"assets/{pie_chart_file}", "w") as f:
        f.write(json.dumps(pie_chart_data, indent=2))
    
    # Create the wind rose data for this folder
    folder_wind_rose_data = create_wind_rose_data([folder_name], [file_count])
    folder_wind_rose_file = f"wind_rose_{folder_name}.json"
    
    # Write the wind rose data file
    with mkdocs_gen_files.open(f"assets/{folder_wind_rose_file}", "w") as f:
        f.write(json.dumps(folder_wind_rose_data, indent=2))
    
    # Add visualizations using plotly plugin
    contents += f"""
## File Type Distribution

{create_plotly_block(f"../assets/{pie_chart_file}")}

## Directory Visualization

{create_plotly_block(f"../assets/{folder_wind_rose_file}")}
"""
    
    with mkdocs_gen_files.open(f"{output_base}/{folder_name}_contents.md", "w") as f:
        f.write(contents)
    print(f"   ✅ Created {folder_name}_contents.md", file=sys.stderr)
    
    # Add to index
    desc = f"{file_count} files"
    index_content += f"| [{folder_name}]({folder_name}.md) | {desc} | [View contents]({folder_name}_contents.md) |\n"
    sections.append(folder_name)

# Add wind-rose plot for all directories
# Calculate file counts for each directory
file_counts = [len([f for f in (src_data_path / s).iterdir() if f.is_file() and not f.name.startswith('.')]) for s in sections]

# Create the main wind rose data
main_wind_rose_data = create_wind_rose_data(sections, file_counts)

# Write the main wind rose data file
main_wind_rose_file = "wind_rose_all_dirs.json"
with mkdocs_gen_files.open(f"assets/{main_wind_rose_file}", "w") as f:
    f.write(json.dumps(main_wind_rose_data, indent=2))

# Add main visualization to index with plotly plugin
index_content += f"""

## Directory Structure Visualization

{create_plotly_block(f"../assets/{main_wind_rose_file}")}
"""

# Write index
with mkdocs_gen_files.open(f"{output_base}/index.md", "w") as f:
    f.write(index_content)

print(f"\n✅ Successfully processed {len(sections)} sections", file=sys.stderr)
print(f"Sections: {sections}", file=sys.stderr)
print("="*60, file=sys.stderr)

# Also create a marker file to verify gen-files is working
with mkdocs_gen_files.open("src-data-marker.md", "w") as f:
    f.write("# Data Content Marker\n\nThis file confirms gen-files processed src-data.")
