#!/usr/bin/env python3
"""Create a CVs.json file."""
import json
import importlib.util
from pathlib import Path
import glob
from cmipld.utils.git.repo_info import cmip_info
from cmipld.utils.checksum import version


repo = cmip_info()
prefix = repo.whoami
print(prefix)

path = './'


def main():
    cv_files = sorted(glob.glob(f"{path}/{prefix}_*.json"))
    combined = {}
    
    for name in cv_files:
        try:
            data = json.load(open(name))
            mod_name = Path(name).stem.replace(f"{prefix}_", "")
            combined[mod_name] = data[mod_name]
        except Exception as e:
            print(f"❌ {name}: {e}")
    
    # Sort recursively
    combined = {k: dict(sorted(v.items())) if isinstance(v, dict) else v 
                for k, v in sorted(combined.items())}
    
    
    filename = f"{prefix}_CVs.json"
    combined = version(combined, 'CV', location=filename, repo=None)
    
    
    with open(filename, 'w') as f:
        json.dump(combined, f, indent=4)
    
    print(f"\n✅ Created CVs.json with keys: {list(combined.keys())}")


if __name__ == "__main__":
    main()