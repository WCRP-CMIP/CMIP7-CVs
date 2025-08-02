import cmipld
import json

me = __file__.split('/')[-1].replace('.py','')

def run(io, whoami, path, name, **kwargs):
    """Debug script to see what IDs are available in project data"""
    try:
        data = cmipld.get(f"{io}/project/graph.jsonld", depth=2)["@graph"]
        
        # Extract all IDs that are available
        available_ids = [item.get('id') for item in data if item.get('id')]
        
        print(f"Available IDs in project data:")
        for id_val in sorted(available_ids):
            print(f"  - {id_val}")
        
        # Check specifically for nominal-resolution variations
        nominal_variations = [id_val for id_val in available_ids if 'nominal' in id_val.lower()]
        print(f"\nNominal resolution related IDs:")
        for id_val in nominal_variations:
            print(f"  - {id_val}")
        
        # Return a simple debug summary
        summary = {"available_ids": available_ids, "nominal_ids": nominal_variations}
        return f"{path}/{name}_debug_ids.json", "debug_ids", summary
        
    except Exception as e:
        print(f"Error in debug script: {e}")
        return None
