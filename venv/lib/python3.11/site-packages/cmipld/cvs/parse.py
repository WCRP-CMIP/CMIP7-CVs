
from collections import OrderedDict
import cmipld

# def name_description(data,key='name',value='description'):
#     return dict([(x[key],x[value]) for x in data])

# def key_only(data,key='name',default='missing'):
#     if isinstance(data[0],str):
#         # if single value do not fetch key
#         return data
#     return sorted(list(set([x.get(key,default) for x in data if x])))


##################################
### MIP Table fns      ###########
##################################

def mip_cmor_tables_source_type(data):
    return data.key_only('name')


def mip_cmor_tables_frequency(data):
    return data.key_value('name', 'description')


def mip_cmor_tables_realm(data):
    return data.key_value('name', 'description')


def mip_cmor_tables_grid_label(data):
    return data.key_value('name', 'description')


def cmip6plus_activity_id(data):
    return data.key_value('name', 'description')


def cmip6plus_sub_experiment_id(data):
    return data.key_value('name', 'description')


##################################
### CMIP fns            ###########
##################################

def cmip6plus_organisations(data):

    # data = [d['organisation_id'] for d in data if d['organisation_id']['cmip_acronym']]

    data.clean(['rmnull'])

    # # return filter(lambda x: 'cmip_acronym' in x, data)
    # data.print

    return cmipld.key_value(data.value_only('organisation_id'), key='cmip_acronym', value='name')


def cmip6plus_descriptors(data):
    data = data.json

    for i in data['index']:
        if isinstance(data['index'][i], str):
            data['index'][i] = [data['index'][i]]

    for i in 'tracking_id license'.split():
        if isinstance(data[i], str):
            data[i] = [data[i]]

    data.update(data['index'])
    del data['index']
    data['DRS'] = data['drs']
    data['Conventions'] = data['conventions']
    print(data['mip_era'])
    data['mip_era'] = data['mip_era']['name']
    data['product'] = data['product']['kind']

    del data['drs'], data['conventions'], data['@context']
    return data


def cmip6plus_source_id(data):
    data = data.json

    sid = OrderedDict()
    for source in sorted(data, key=lambda x: x['source_id']):
        # ideally organisation
        source['institution_id'] = [
            source['organisation_id'].get('cmip_acronym', '')]
        del source['organisation_id']

        source["activity_participation"] = cmipld.value_only(
            source.get("activity_participation", []), 'name')

        source['license'].update(source['license'].get('kind', {}))

        if not isinstance(source['cohort'], list):
            source['cohort'] = [source['cohort']]

        source['source'] = f"{source['source_id']} ({source['release_year']}): \n  "

        #    combine the model-components
        for i in source['model_component']:
            try:
                source['source'] += f"{i['name']} ({i['realm']['name']})\n  "
            except Exception as e:

                print('Missing', i, source['source_id'])

                print(e)

        # del source['license']['kind']
        # del source['license']['conditions']

        del source['model_component']
        sid[source['source_id']] = source

    return sid


def cmip6plus_native_nominal_resolution(data):
    data = data.json

    return list(set([f"{x['nominal_resolution'].get('value',x['nominal_resolution'])}{x['nominal_resolution'].get('unit',{}).get('si','km')}" for x in data]))


def cmip6plus_experiment_id(data):
    data = data.json

    eid = OrderedDict()
    for e in sorted(data, key=lambda x: x['experiment_id']):

        for i in ['additional_allowed', 'required']:
            if isinstance(e['model_components'][i], str):
                e['model_components'][i] = [e['model_components'][i]]

            e[f'{i}_model_components'] = e['model_components'][i]

        del e['model_components']

        # to list
        e['activity_id'] = cmipld.key_only([e['activity_id']])

        for i in e['parent']:
            e['parent_'+i] = [e['parent'][i]]

        e['sub_experiment_id'] = [
            e['sub_experiment_id'].get('name', 'missing')]

        del e['parent']

        eid[e['experiment_id']] = e

    return eid


##################################
### Main processing function #####
##################################
local_globals = globals()


async def process(prefix, file, data=None, clean=None):
    name = f'{prefix}_{file}'.replace('-', '_')
    # prepare for use.

    if clean:
        # print('clean', clean)
        data.clean(clean)
    else:
        data.clean_cv
    if name in local_globals:
        data.data = local_globals[name](data)
    else:
        print('no parsing function found', name)

    return data.json
