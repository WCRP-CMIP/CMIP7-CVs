

from pydantic import BaseModel, field_validator
from pydantic import StrictStr, StrictBool, StrictFloat, conlist
from typing import Union, Optional
import json


minlen = 50


class description_field:

    description: StrictStr

    @field_validator('description', mode='after')
    @classmethod
    def description_minlen(cls, value):
        if len(value) <= minlen:
            raise UnicodeError(
                f"Description length == {len(value)}. This is less than the minimum character length of {minlen}. `{value}`")
        return value
