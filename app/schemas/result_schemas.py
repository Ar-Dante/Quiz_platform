from enum import Enum

from pydantic import BaseModel


class SaveFormat(str, Enum):
    json = "json"
    csv = "csv"


class GetResultsByFormat(BaseModel):
    save_format: SaveFormat


class AverageSystemModel(BaseModel):
    system_average_rating: float


class AverageCompanyModel(BaseModel):
    company_average_rating: float
