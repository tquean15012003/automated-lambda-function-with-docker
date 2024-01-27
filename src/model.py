from typing import Literal
from pydantic import BaseModel

class AnonymizeResult(BaseModel):
    data: str
    deanonymizer_mapping: dict
    status: Literal['success']

class DeanonymizeResult(BaseModel):
    data: str
    status: Literal['success']