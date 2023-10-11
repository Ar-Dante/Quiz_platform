from enum import Enum

from pydantic import BaseModel


class SaveFormat(str, Enum):
    json = "json"
    csv = "csv"


class GetResults(BaseModel):
    save_format: SaveFormat
