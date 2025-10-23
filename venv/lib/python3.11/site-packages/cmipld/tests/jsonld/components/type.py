

from pydantic import BaseModel, field_validator
from pydantic import StrictStr, StrictBool, StrictFloat
from typing import Union, Optional, List
import json

from .stringcheck import hyphenate, maxlen


import re


typestr = re.compile(r'[a-z\-:\d]+')
max_type = 50


class type_field:

    # set field type
    type: Union[str, list[str]]

    type_hyphen = field_validator('type', mode='after')(
        hyphenate)  # Directly apply hyphenate

    type_maxlength = field_validator('type', mode='after')(maxlen(max_type))

    @field_validator('type', mode='after')
    @classmethod
    def type_allowed_char(cls, value):
        for i in value:

            if typestr.fullmatch(i) == None:
                raise UnicodeError(
                    f"Types must only have a-z, lowercase letters and colons (:) to separate the prefixes from the type. Full urls should be provided within the context for clarity. [\"id\": \"{i}\"] has the invalid character: ({set(typestr.sub('',i))}).")
        return value

    @field_validator('type', mode='before')
    @classmethod
    def types_allowed(cls, value):
        ''' 
        # to change the default allowed types use the following in your main code

        def allowed_types(value):
            assert value in ['type1','type2','type3']
            return value

        types_field.types_allowed = allowed_types

        '''
        # this passes by default, we can change this in the main code (see docstring above)
        return value
