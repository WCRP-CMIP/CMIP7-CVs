from pydantic import field_validator
import re
import cmipld

owner = 'ror-community'
repo = 'ror-records'

# tag = cmipld.utils.git.get_tags(owner,repo)[0]['name']
# rors = [i['name'].replace('.json','') for i in cmipld.utils.git.get_contents(owner,repo,tag)]

# Regex pattern for ROR key validation
ror_pattern = re.compile(r'^\d{2}\w{5}\d{2}$')


class ror_field:

    ror: str

    @field_validator('ror', mode='after')
    @classmethod
    def ror_length(cls, value):
        assert len(value) == 9, f'ROR key "{value}" must be 9 characters long'
        return value

    @field_validator('ror', mode='after')
    @classmethod
    def ror_validate(cls, value: str) -> str:
        if not isinstance(value, str) or not ror_pattern.fullmatch(value):
            raise ValueError(
                f'Invalid ROR key format: "{value}". Expected format: "https://ror.org/0XXXXXXYY"'
            )
        return value

    # just a test, may need a bit of updating.

    # @field_validator('ror', mode='after')
    # @classmethod
    # def ror_exists(cls, value: str) -> str:
    #     if value not in rors:
    #         raise FileExistsError(f'ROR key "{value}" not found in the ROR records of latest tag: {tag}')
    #     return value
