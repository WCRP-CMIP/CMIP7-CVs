

from pydantic import BaseModel, field_validator
from pydantic import StrictStr, StrictBool, StrictFloat
from typing import Union, Optional, List
import json
from datetime import datetime


# class date_field:
#     date: str

#     @validator('date')


def validate_date(value):
    # Try parsing the date in different formats
    for fmt in ("%Y-%m-%d", "%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Invalid date format for value: {value}")
