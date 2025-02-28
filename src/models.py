from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, ConfigDict
from shapely.geometry import LineString

class OSMtoDBModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: int
    name: str = "LineString"
    kante: LineString

class BefahrungRequest(BaseModel):
    befahrung_id: int