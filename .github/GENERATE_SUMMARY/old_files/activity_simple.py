"""Simplified activity summary script"""
import cmipld
from cmipld.utils.ldparse import name_entry

def run(io, whoami, path, name, **kwargs):
    """Generate activity summary from project data"""
    try:
        # Get project data
        url = f"{io}/project/graph.jsonld"
        data = cmipld.get(url, depth=2)
        
        if not data or '@graph' not in data:
            print("activity: No project data found")
            return None
        
        # Find activity-list entry
        activity_entry = None
        for item in data['@graph']:
            if isinstance(item, dict) and item.get('id') == 'activity-list':
                activity_entry = item
                break
        
        if not activity_entry:
            print("activity: activity-list not found in project data")
            return None
        
        # Extract summary
        summary = name_entry(activity_entry)
        location = f"{path}/{name}_activity.json"
        
        return location, "activity", summary
        
    except Exception as e:
        print(f"Error in activity script: {e}")
        return None
