

from pydantic import BaseModel, field_validator
from pydantic import StrictStr, StrictBool, StrictFloat, conlist
from typing import Union, Optional
import json


from .stringcheck import hyphenate, maxlen, minlen

import re

# start with a letter, allow numbers and hyphens
idstr = re.compile(r'[a-z\d][a-z\d\-]+$')

max_id = 30


class id_field:

    id: StrictStr

    type_hyphen = field_validator('id', mode='after')(
        hyphenate)  # Directly apply hyphenate

    type_maxlength = field_validator('id', mode='after')(maxlen(max_id))

    type_minlength = field_validator('id', mode='after')(minlen(2))

    @field_validator('id', mode='after')
    @classmethod
    def id_allowed_char(cls, value):
        if idstr.fullmatch(value) == None:
            raise UnicodeError(
                f"Only use a-z, numbers, and '-' and lowercase characters only. \n [\"id\": \"{value}\"] has the invalid character: ({set(idstr.sub('',value))}).")
        return value
