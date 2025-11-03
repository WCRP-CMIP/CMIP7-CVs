import cmipld,os
from cmipld.utils.ldparse import cvjson_validation_key
me = __file__.split('/')[-1].replace('.py','')


print('RUN LD2GRAPH FIRST')
graph = os.popen('ld2graph experiment').read()
print(graph)




def ld2cmip6(validation_key, ui_label, description, activity, 
                 parent_experiment, tier, model_realms, 
                 start="", end="", min_years=0, parent_activity=None, **kwargs):
    """Convert form data to experiment JSON format."""

    model_realms = model_realms if isinstance(model_realms, list) else [model_realms]

    required = [m for m in model_realms if m.get('is_required')]
    optional = [m for m in model_realms if not m.get('is_required')]
    

    return {
        validation_key: {
            "activity": cvjson_validation_key(activity),
            "additional_allowed_model_components": cvjson_validation_key(optional),
            "description": description,
            "end": end,
            "experiment": ui_label,
            "experiment_id": validation_key,
            "min_number_yrs_per_sim": min_years,
            "parent_activity_id": cvjson_validation_key(parent_activity) if parent_activity else [],
            "parent_experiment_id": cvjson_validation_key(parent_experiment),
            "required_model_components":cvjson_validation_key(required),
            "start": start,
            "tier": tier
        }
    }
    
    

def run(io, whoami, path, name, **kwargs):
    data = cmipld.get('cmip7:experiment/graph.jsonld', depth=2)

    summary = {}
    for i in data['@graph']:
        summary.update(ld2cmip6(**i))
        
    summary = dict(sorted(summary.items()))
        
    # update the name to use the id field
    me2 = me + '_id'
    return f"{path}/{name}_{me2}.json", me2, summary
