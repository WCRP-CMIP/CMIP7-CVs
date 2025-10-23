from cmipld.utils.ldparse import *


def license(data):
    return data['license']


def organisation(data):
    # return 'None if this is missing' Does not break CVs.
    return [name_entry(o['organisation'], 'ui-label') if isinstance(o['organisation'], dict) else {o['organisation']: None} for o in data]


functionlist = {}

##################################
# Literals
##################################

literals = ['tracking-id', 'drs', 'index',
            'required_global_attributes', 'repo']

for name in literals:
    field = name.replace('-', '_')

    def literal_wrapper(data, field=field):
        return data[field]
    functionlist[name] = literal_wrapper


##################################
# Name: Description pairs.
##################################

name_description = ['realm', 'frequency', 'grid_label',
                    'nominal', 'sub_experiment', 'tables']

for name in name_description:
    field = name.replace('-', '_')

    def nd_wrapper(data, field=field):
        return sorted(name_entry(data))
    functionlist[name] = nd_wrapper


##################################
# Label Extraction
##################################

'''
All of the following names formulate a function of the format

def <name> (data):
    return get_entry(data[<name>])

This function saves us having to hard code them all. 

# ids are specified with a '-' as not to affect path parsing, 
# however keys are not allowed '-' and must contain '_' instead.
'''

# List of function names
named_entry_feed = ['mip_era', 'activity', 'product', 'tables']
# 'tables',

for field in named_entry_feed:
    functionlist[field] = lambda data, field=field: rmkeys(
        get_entry(data[field], entry='validation-key'))

# save the functions to the local global list
locals().update(functionlist)


# end named field


def experiment(data):
    dummy = {}

    for e in data:

        e['additional_allowed_model_components'] = [
            i for i in e['model_realms'] if not i['is_required']]
        e['required_model_components'] = [
            i for i in e['model_realms'] if i['is_required']]

        # e['model_components_additional_allowed'] = [i for i in e['model_realms'] if not i['is_required']]
        # e['model_components_required'] = [i for i in e['model_realms'] if i['is_required']]

        for name in ['activity', 'parent_experiment', 'additional_allowed_model_components', 'required_model_components']:
            e[name] = name_entry(e[name])

        dummy[e['validation-key']] = rmkeys(e, ['id', 'type', 'model_realms'])

        # 'sub_experiment',

    return dummy


def source(data):

    license_keep = ['validation-key', 'url',
                    'exceptions_contact', 'source_specific_info']
    dummy = {}
    for s in data:
        s['license'] = s['license'][0]
        s['license'] = key_extract(s['license'], license_keep)

        s['organisation'] = name_entry('ui-label')
        # {k.split('/')[-1]:v for k,v in s['organisation']},

        s['institution'] = s['organisation']

        s['model_component'] = [key_extract(
            x, ['realm', 'description', 'validation-key', 'native-nominal-resolution']) for x in s['model_component']]

        s['source'] = ''
        for mc in s['model_component']:
            s['source'] += f"{mc['validation-key']} ({mc['realm']}); "

        s = rmkeys(s, ['id', 'type', 'organisation', 'model_component'])

        dummy[s['validation-key']] = s

    return dummy
