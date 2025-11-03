#!/usr/bin/env python3
"""Create a CVs.json file."""
import json
import importlib.util
from pathlib import Path
import glob
from cmipld.utils.git.repo_info import cmip_info
from cmipld.utils.checksum import version


repo = cmip_info()
print(repo.name)

path = './'


def main():
    cv_files = sorted(glob.glob(f"{path}/{repo.name}_*.json"))
    combined = {}
    
    for name in cv_files:
        try:
            data = json.load(open(name))
            mod_name = Path(name).stem.replace(f"{repo.name}_", "")
            combined[mod_name] = data[mod_name]
        except Exception as e:
            print(f"❌ {name}: {e}")
    
    # Sort recursively
    combined = {k: dict(sorted(v.items())) if isinstance(v, dict) else v 
                for k, v in sorted(combined.items())}
    
    
    combined = version(combined, 'CVs', location='./', repo=None)
    
    
    with open(f"CV_{repo.name}.json", 'w') as f:
        json.dump(combined, f, indent=4)
    
    print(f"\n✅ Created CVs.json with keys: {list(combined.keys())}")


if __name__ == "__main__":
    main()