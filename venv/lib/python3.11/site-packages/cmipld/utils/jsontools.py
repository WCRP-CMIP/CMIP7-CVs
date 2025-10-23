from collections import OrderedDict

# Lazy load validate_json to avoid circular imports
_jval = None

def _get_validator():
    global _jval
    if _jval is None:
        from .validate_json import JSONValidator
        _jval = JSONValidator('./')
    return _jval

def validate_and_fix_json(*args, **kwargs):
    return _get_validator().validate_and_fix_json(*args, **kwargs)

def sort_json_keys(*args, **kwargs):
    return _get_validator().sort_json_keys(*args, **kwargs)

# class DotAccessibleDictOld:
#     def __init__(self, entries):
#         self.entries = dict(entries)
#         for key in self.entries.keys():
#             self.__dict__[key] = self.entries[key]
#             if '-' in key:
#                 self.__dict__[key.replace('-', '_')] = self.entries[key]


# class DotAccessible:
#     def __init__(self, **kwargs):
#         for key, value in kwargs.items():
#             setattr(self, key, value)

    # def __getattr__(self, name):
    #     if name in self.entries:
    #         return self.entries[name]
    #     else:
    #         raise AttributeError(f"'DotAccessibleDict' object has no attribute '{name}'")




    # def __str__(self):
    #     return str(self.entries.keys())
    
    
class DotAccessibleDict:
    def __init__(self, **kwargs):
        # Store the variables both as attributes and in the internal dictionary
        self._data = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __getitem__(self, key):
        # Allow dictionary-style access
        return self._data[key]

    def __setitem__(self, key, value):
        # Allow setting values both as attributes and in the dictionary
        self._data[key] = value
        setattr(self, key, value)

    def __repr__(self):
        # Pretty representation of the object
        return repr(self._data)

    def items(self):
        # Allow dict-like items() method
        return self._data.items()

    def keys(self):
        # Allow dict-like keys() method
        return self._data.keys()

    def values(self):
        # Allow dict-like values() method
        return self._data.values()

    def __str__(self):
        return str(self._data.keys())

def sorted_json(dct):
    """
    Sort a dictionary by keys and return an OrderedDict.

    Args:
    dct (dict): The input dictionary to be sorted.

    Returns:
    OrderedDict: A new OrderedDict with items sorted by keys.
    """
    if not isinstance(dct, dict):
        return dct

    od = OrderedDict()
    keys = ['@context', 'id', 'type']
    for i in keys:
        if i in dct:
            od[i] = dct[i]
    for key in sorted(dct.keys()):
        if key not in keys:
            od[key] = dct[key]

    return od

    # return sorted((k, v) for k, v in dct.items()))


def sorted_ctx(dct):
    """
    Sort a dictionary by keys and return an OrderedDict.

    Args:
    dct (dict): The input dictionary to be sorted.

    Returns:
    OrderedDict: A new OrderedDict with items sorted by keys.
    """
    assert isinstance(dct, dict)
    assert '@context' in dct

    ctxlist = []

    islist = True
    if not isinstance(dct['@context'], list):
        dct['@context'] = [dct['@context']]
        islist = False

    for dctx in dct['@context']:

        if isinstance(dctx, str):
            ctxlist.append(dctx)
            continue

        ctx = OrderedDict()

        # lddefinitions
        for ck, cv in sorted(dctx.items()):
            if ck[0] == '@':
                ctx[ck] = cv

        # ld objects
        for ck, cv in sorted(dctx.items()):
            if isinstance(cv, str) and cv[0] == '@':
                ctx[ck] = cv

        # prefix
        for ck, cv in sorted(dctx.items()):
            if ck[-1] == ':':
                ctx[ck] = cv

        # others

        # non context items
        for ck, cv in sorted(dctx.items()):
            if '@context' not in cv:
                ctx[ck] = cv

        # context items (links)
        for ck, cv in sorted(dctx.items()):
            if '@context' in cv:
                ctx[ck] = cv

        ctxlist.append(ctx)

    dct['@context'] = ctxlist

    dct['@embed'] = '@always'

    if not islist:
        dct['@context'] = dct['@context'][0]

    return dct
