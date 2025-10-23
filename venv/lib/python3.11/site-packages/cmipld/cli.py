# cmipld/cli.py
"""
Simple CLI entry points for shell scripts
"""
import subprocess
import sys
from pathlib import Path

def get_script_path(script_name):
    """Get the path to a shell script in the package"""
    # First try the bin directory in the package
    bin_dir = Path(__file__).parent / "bin"
    script_path = bin_dir / script_name
    
    if script_path.exists():
        return str(script_path)
    
    # If that doesn't work, the script might not exist
    print(f"Error: Script {script_name} not found in {bin_dir}", file=sys.stderr)
    sys.exit(1)

def run_script(script_name):
    """Run a shell script with all command line arguments"""
    script_path = get_script_path(script_name)
    
    # Make sure the script is executable
    try:
        import os
        os.chmod(script_path, 0o755)
    except (OSError, PermissionError):
        pass  # Ignore permission errors
    
    # Execute the shell script with all original arguments
    result = subprocess.run(["bash", script_path] + sys.argv[1:])
    sys.exit(result.returncode)

# Entry points for each script
def ld2graph():
    """Create graph.jsonld from directory of JSON-LD files"""
    run_script("ld2graph")

def validjsonld():
    """Validate JSON-LD files in directory"""
    run_script("validjsonld")

def dev():
    """Quick git development workflow"""
    run_script("dev")

def rmbak():
    """Remove .bak files recursively"""
    run_script("rmbak")

def rmgraph():
    """Remove graph.json files recursively"""
    run_script("rmgraph")

def coauthor_file():
    """Add co-author to git commit for specific file"""
    run_script("coauthor_file")

def cmipld_help():
    """Show help for all CMIP-LD commands"""
    run_script("cmipld-help")
