from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel


class Filament(BaseModel):
    brand: str
    type: Literal["PLA", "PETG"]
    color: Optional[str] = None


class EvalueCalibration(Filament):
    e_value: float
    extruder_temp: float
    dt: datetime = None
