

from pydantic import BaseModel, field_validator
from pydantic import StrictStr, StrictBool, StrictFloat, conlist
from typing import Union, Optional


json_data = {'FieldKey: values ...}

# if we have external functions. 
from external_fn import check2


class JSONField1:

    FieldKey1: str
    '''
    This contains the test funcitons
    '''

    # classic embedding
    @field_validator('FieldKey', mode='after')  
    @classmethod
    def check1(cls,value):
        if value != x:
            raise Error('this is wrong because...')
        return value

    
    # using reusable function
    check2 = field_validator('FieldKey', mode='before')(hyphenate)  # Directly apply hyphenate
    


# repeat for all relevant fields. 

JSONField1.testfunction1 = lambda x: assert x > 3 

# overwrite an existing test funciton


''' 
Global test on whole generated json
'''


class FullTest(Basemodel, JsonField1, JsonField2... ):

    ''' Enter the keys and types as per the usual pydantic tests '''

    # if not specified in an imported class specify here
    FieldKey3: str
    FieldKey4: int




# usage

dataobject = FullTest(**jsondata)





