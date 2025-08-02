"""Universal project-based summary script generator"""
import cmipld
from cmipld.utils.ldparse import name_entry

def create_project_summary_script(entry_id, script_name=None):
    """Create a summary script for project-based entries"""
    if script_name is None:
        script_name = entry_id.replace('-list', '').replace('-', '_')
    
    def run(io, whoami, path, name, **kwargs):
        try:
            # Get project data
            url = f"{io}/project/graph.jsonld"
            data = cmipld.get(url, depth=2)
            
            if not data or '@graph' not in data:
                print(f"{script_name}: No project data found")
                return None
            
            # Find the specific entry
            target_entry = None
            for item in data['@graph']:
                if isinstance(item, dict) and item.get('id') == entry_id:
                    target_entry = item
                    break
            
            if not target_entry:
                print(f"{script_name}: {entry_id} not found in project data")
                return None
            
            # Extract summary
            summary = name_entry(target_entry)
            location = f"{path}/{name}_{script_name}.json"
            
            return location, script_name, summary
            
        except Exception as e:
            print(f"Error in {script_name} script: {e}")
            return None
    
    return run

# Pre-built run functions for common scripts
run = create_project_summary_script('frequency-list', 'frequency')
