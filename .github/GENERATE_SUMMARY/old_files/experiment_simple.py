"""Simplified experiment summary script"""
import cmipld
from cmipld.utils.ldparse import name_extract

def run(io, whoami, path, name, **kwargs):
    """Generate experiment summary from experiment data"""
    try:
        # Get experiment data
        url = f"{io}/experiment/graph.jsonld"
        data = cmipld.get(url, depth=1)
        
        if not data or '@graph' not in data:
            print("experiment: No experiment data found")
            return None
        
        # Extract summary using name_extract
        summary = name_extract(data['@graph'])
        location = f"{path}/{name}_experiment.json"
        
        return location, "experiment", summary
        
    except Exception as e:
        print(f"Error in experiment script: {e}")
        return None
