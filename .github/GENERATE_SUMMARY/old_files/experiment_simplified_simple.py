"""Simplified experiment simplified summary script"""
import cmipld
from cmipld.utils.ldparse import name_extract, key_extract

def run(io, whoami, path, name, **kwargs):
    """Generate simplified experiment summary with specific fields"""
    try:
        # Get experiment data with context framing
        url = f"{io}/experiment/graph.jsonld"
        ctx = f"{io}/experiment/_context_"
        
        try:
            # Try JSON-LD framing first
            frame = {"@context": ctx, "@type": "wcrp:experiment"}
            data = cmipld.jsonld.frame(url, frame)
            graph_data = data.get("@graph", [])
        except Exception as frame_error:
            print(f"JSON-LD framing failed, falling back to simple get: {frame_error}")
            # Fallback to simple get
            data = cmipld.get(url, depth=1)
            graph_data = data.get('@graph', []) if data else []
        
        if not graph_data:
            print("experiment_simplified: No experiment data found")
            return None
        
        # Extract summary and filter to specific fields
        full_summary = name_extract(graph_data)
        summary = {
            k: key_extract(v, ['long-label', 'description']) 
            for k, v in full_summary.items()
        }
        
        location = f"{path}/{name}_experiment_simplified.json"
        return location, "experiment_simplified", summary
        
    except Exception as e:
        print(f"Error in experiment_simplified script: {e}")
        return None
