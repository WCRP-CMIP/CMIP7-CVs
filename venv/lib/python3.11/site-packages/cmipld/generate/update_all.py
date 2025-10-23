#!/bin/python3

import glob
import os
import tqdm


def main():
    """Main function for update_all command"""
    
    # Update contexts - this will call the Python function directly
    print("Updating contexts...")
    try:
        from .update_ctx import main as update_ctx_main
        update_ctx_main()
    except ImportError:
        # Fallback to os.system for backward compatibility
        os.system('update_ctx')
    
    # os.system('update_schema')
    # os.system('update_issues')
    
    # Validate JSON-LD files - use shell wrapper
    print("Validating JSON-LD files...")
    try:
        from ..utils.shell_wrappers import run_shell_script
        run_shell_script('validjsonld', ['.'])
    except ImportError:
        # Fallback to os.system for backward compatibility
        os.system('validjsonld')
    
    # Generate graphs for all src-data directories
    print("Generating graphs...")
    for i in tqdm.tqdm(glob.glob('src-data/*/')):
        try:
            from ..utils.shell_wrappers import run_shell_script
            run_shell_script('ld2graph', [i])
        except ImportError:
            # Fallback to os.system for backward compatibility
            os.system('ld2graph '+i)
    
    print("Update complete!")


if __name__ == '__main__':
    main()
