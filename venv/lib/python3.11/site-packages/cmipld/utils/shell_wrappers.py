# cmipld/utils/shell_wrappers.py
"""
Python wrappers for shell scripts to make them available after pip install
"""

import os
import subprocess
import sys
from pathlib import Path

def get_script_path(script_name):
    """Get the path to a shell script in the cmipld package"""
    # Get the directory where this module is located
    cmipld_dir = Path(__file__).parent.parent
    script_path = cmipld_dir / "scripts" / script_name
    
    if not script_path.exists():
        # Try alternative locations
        alt_locations = [
            cmipld_dir / "scripts" / "directory-utilities" / script_name,
            cmipld_dir / "scripts" / "jsonld-util" / script_name,
            cmipld_dir / "scripts" / "development" / script_name,
        ]
        
        for alt_path in alt_locations:
            if alt_path.exists():
                script_path = alt_path
                break
        else:
            raise FileNotFoundError(f"Script {script_name} not found in cmipld scripts directory")
    
    return str(script_path)

def run_shell_script(script_name, args=None):
    """Run a shell script with optional arguments"""
    script_path = get_script_path(script_name)
    
    # Make sure the script is executable (important after pip install)
    try:
        os.chmod(script_path, 0o755)
    except (OSError, PermissionError):
        pass  # Ignore permission errors, bash should still work
    
    cmd = ['bash', script_path]
    if args:
        cmd.extend(args)
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}: {e}")
        if e.stderr:
            print(e.stderr, file=sys.stderr)
        return e.returncode
    except FileNotFoundError as e:
        print(f"Error: Could not find bash or script {script_name}: {e}")
        return 1

def ld2graph_main():
    """Entry point for ld2graph command"""
    if len(sys.argv) < 2:
        print("Usage: ld2graph <directory>", file=sys.stderr)
        sys.exit(1)
    
    directory = sys.argv[1]
    return run_shell_script('ld2graph', [directory])

def validjsonld_main():
    """Entry point for validjsonld command"""
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    return run_shell_script('validjsonld', args)

def dev_main():
    """Entry point for dev command"""
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    return run_shell_script('dev', args)

def rmbak_main():
    """Entry point for rmbak command"""
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    return run_shell_script('rmbak', args)

def rmgraph_main():
    """Entry point for rmgraph command"""
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    return run_shell_script('rmgraph', args)

def coauthor_file_main():
    """Entry point for coauthor_file command"""
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    return run_shell_script('coauthor_file', args)

if __name__ == "__main__":
    # This allows the module to be run directly for testing
    if len(sys.argv) > 1:
        script_name = sys.argv[1]
        args = sys.argv[2:]
        run_shell_script(script_name, args)
    else:
        print("Usage: python -m cmipld.utils.shell_wrappers <script_name> [args...]")
