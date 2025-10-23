#!/usr/bin/env python3
"""
Generate summary runner with data normalization

Usage: python generate_summary.py <script_directory>
"""

import cmipld
import os
import glob
import importlib.util
import tqdm
from cmipld.utils.git.repo_info import cmip_info
from cmipld.utils.server_tools.offline import LD_server
from cmipld.utils.checksum import version


def normalize_jsonld_data(data):
    """Convert expanded JSON-LD to simple key-value format"""
    if not isinstance(data, dict):
        return data
    
    normalized = {}
    
    for key, value in data.items():
        # Convert @id to id
        if key == '@id':
            normalized['id'] = value.split('/')[-1] if isinstance(value, str) else value
            continue
        
        # Skip @type for now
        if key == '@type':
            continue
            
        # Extract simple key name from URL
        if isinstance(key, str) and key.startswith('http'):
            simple_key = key.split('/')[-1]
        else:
            simple_key = key
        
        # Handle different value formats
        if isinstance(value, list) and len(value) == 1:
            item = value[0]
            
            # Handle @value wrapper
            if isinstance(item, dict) and '@value' in item:
                normalized[simple_key] = item['@value']
            
            # Handle @list wrapper
            elif isinstance(item, dict) and '@list' in item:
                list_items = item['@list']
                # Extract @value from each list item
                if isinstance(list_items, list):
                    simple_list = []
                    for list_item in list_items:
                        if isinstance(list_item, dict) and '@value' in list_item:
                            simple_list.append(list_item['@value'])
                        else:
                            simple_list.append(list_item)
                    normalized[simple_key] = simple_list
                else:
                    normalized[simple_key] = list_items
            else:
                normalized[simple_key] = item
        else:
            normalized[simple_key] = value
    
    return normalized


def write(location, me, data):
    """Write summary with proper version header"""
    summary = version(data, me, location.split("/")[-1])

    if os.path.exists(location):
        old = cmipld.utils.io.jr(location)
        if old.get('Header', {}).get('checksum') == summary.get('Header', {}).get('checksum'):
            print(f"📄 {me}: No update needed (unchanged)")
            return 'no update - file already exists'

    cmipld.utils.io.jw(summary, location)
    print(f"💾 {me}: Written to {location}")


def run_script(script_path, repo_info):
    """Run script with data normalization"""
    try:
        spec = importlib.util.spec_from_file_location("module.name", script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Monkey patch cmipld.get to normalize data
        original_get = cmipld.get
        
        def normalizing_get(url, **kwargs):
            """Get data and normalize JSON-LD format"""
            data = original_get(url, **kwargs)
            
            if isinstance(data, dict) and '@graph' in data:
                # Normalize each item in the graph
                normalized_graph = []
                for item in data['@graph']:
                    normalized_item = normalize_jsonld_data(item)
                    normalized_graph.append(normalized_item)
                data['@graph'] = normalized_graph
            
            return data
        
        # Temporarily replace cmipld.get
        cmipld.get = normalizing_get
        
        try:
            processed = module.run(**repo_info)
            
            if processed and len(processed) == 3:
                write(*processed)
                return True
            else:
                print(f"❌ {os.path.basename(script_path)}: No output")
                return False
        finally:
            # Restore original get function
            cmipld.get = original_get

    except Exception as e:
        print(f"❌ {os.path.basename(script_path)}: {e}")
        return False


def main():
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: generate_summary <script_directory>")
        sys.exit(1)
    
    script_dir = sys.argv[1]
    
    print("🔍 Getting repository information...")
    repo = cmip_info()
    
    print("🖥️  Setting up local LD server...")
    
    # Server setup matching your pattern
    directory_path = repo.path
    location = directory_path.split('src-data')[0] + 'src-data' if 'src-data' in directory_path else os.path.join(directory_path, 'src-data')
    prefix = repo.whoami
    
    local = [(location, cmipld.mapping[prefix], prefix)]
    server = LD_server(copy=local, use_ssl=False)
    
    try:
        base_url = server.start_server(port=8081)
        print(f"✅ LD server started at {base_url}")
        
        # Find scripts
        scripts = [s for s in glob.glob(f"{script_dir}/*.py") 
                   if not os.path.basename(s).startswith('x_')]
        
        print(f"🚀 Running {len(scripts)} summary scripts...\n")
        
        # Run each script
        success = 0
        for script in tqdm.tqdm(scripts):
            if run_script(script, dict(repo)):
                success += 1
        
        print(f"\n✅ Summary: {success}/{len(scripts)} scripts successful")
    
    finally:
        print("🛑 Stopping LD server...")
        server.stop_server()


if __name__ == "__main__":
    main()
