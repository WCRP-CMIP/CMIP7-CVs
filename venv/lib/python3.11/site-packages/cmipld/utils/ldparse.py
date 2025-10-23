from collections import OrderedDict
rmld = ['id', 'type', '@context']


def get_entry(data, entry='validation-key'):
    if isinstance(data, dict):
        if 'id' in data:
            return [data[entry]]
        else:
            data = list(data.values())
    return [i.get(entry) for i in data if entry in i]


def name_entry(data, value='description', key='validation-key'):
    if isinstance(data, list):
        return sortd({entry[key]: entry[value] for entry in data if key in entry})

    elif isinstance(data, dict):
        if 'id' in data:
            return sortd({data[key]: data[value]})
        else:
            return sortd({entry: data[entry][value] for entry in data})


def key_extract(data, keep_list):
    return sortd({k: data[k] for k in keep_list if k in data})


def keypathstrip(data):
    return sortd({k.split('/')[-1]: v for k, v in data.items()})


def rmkeys(data, keys=rmld):
    for ky in keys:
        if ky in data:
            del data[ky]
        return data


def name_extract(data, fields=None, key='validation-key'):

    assert isinstance(data, list) or isinstance(
        data, dict), 'data must be a list or dict'
    if fields is None:
        fields = [i for i in data[0].keys() if i not in rmld]
    if isinstance(data, dict):
        if 'id' in data:
            return {data[key]: data}
        else:
            data = list(data.values())
    return sortd({entry[key]: {k: entry[k] for k in fields if k in entry} for entry in data if key in entry})


def sortd(d):
    return OrderedDict(sorted(d.items()))
