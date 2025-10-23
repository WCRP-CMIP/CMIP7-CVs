
from pydantic import BaseModel, field_validator
from pydantic import StrictStr, StrictBool, StrictFloat
from typing import Union, Optional
import json

from .ror import ror_field


from ..components import id_field, type_field


class institution(BaseModel, id_field, type_field, ror_field):

    @field_validator('type', mode='after')
    @classmethod
    def type_contains(cls, value):
        assert 'wcrp:organisation' in value
        assert 'wcrp:institution' in value
        assert 'wcrp:consortium' not in value
        return value

    def json(self):
        return self.model_json_dump()

# Example usage
# a = EMD(**{'num':'1','id':'ts-t'})
