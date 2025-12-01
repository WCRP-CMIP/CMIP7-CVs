from glob import glob
import cmipld,os
from cmipld.utils.ldparse import cvjson_validation_key
me = __file__.split('/')[-1].replace('.py','')


print('RUN LD2GRAPH FIRST')
graph = os.popen('ld2graph experiment').read()
print(graph)




def ld2cmip6(validation_key, ui_label, description, activity, 
                 parent_experiment, tier, model_realms_required,model_realms_additional_allowed, 
                 start="", end="", min_years=0, parent_activity=None, **kwargs):
    """Convert form data to experiment JSON format."""


    return {
        validation_key: {
            "activity_id": cvjson_validation_key(activity),
            "additional_allowed_model_components": cvjson_validation_key(model_realms_additional_allowed),
            "description": description,
            # "end": end,
            "experiment": ui_label,
            "experiment_id": validation_key,
            # "min_number_yrs_per_sim": min_years,
            "parent_activity_id": cvjson_validation_key(parent_activity) if parent_activity else [],
            "parent_experiment_id": cvjson_validation_key(parent_experiment),
            "required_model_components":cvjson_validation_key(model_realms_required),
            # "start": start,
            # "tier": tier
        }
    }
    
    

def run(io, whoami, path, name, **kwargs):
    data = cmipld.get('cmip7:experiment/graph.jsonld', depth=1)

    summary = {}
    failed = []

    nokeys =[]

    for i in data:
        try:
            i = cmipld.get(f"cmip7:experiment/{i.get('@id')}.json", depth=2)
        except Exception as e:
            print(f"Error fetching data for {i.get('@id')}: {e}")
            failed.append(i)
            continue
    # for i in glob('experiment/*.json'):
    #     i = cmipld.get(f"file://{os.path.abspath(i)}", depth=2)



        try:
            
            summary.update(ld2cmip6(**i))
        except Exception as e:
            print(f"Error processing item {i.keys()}: {e}" )
            failed.append(i)
            nokeys.append(i)
        

    for i in failed:
        print(f"Failed item: {i['@id']}")


    summary = dict(sorted(summary.items()))
    

    for i in nokeys:
        print(f"Missing: {i['@id']},{i}")

        
    # update the name to use the id field
    me2 = me + '_id'
    return f"{path}/{whoami}_{me2}.json", me2, summary
