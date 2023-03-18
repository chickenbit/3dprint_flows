from typing import Literal, Optional
from pydantic import BaseModel


class FilamentModel(BaseModel):
    brand: str
    type: Literal["PLA", "PETG"]
    color: Optional[str] = None
