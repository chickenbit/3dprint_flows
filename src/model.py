from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel


class Filament(BaseModel):
    brand: str
    type: Literal["PLA", "PETG", "TPU"] = "PLA"
    color: Optional[str] = None


class EValueCalibration(Filament):
    e_value: float | None = None
    extruder_temp: float
    dt: datetime = None
