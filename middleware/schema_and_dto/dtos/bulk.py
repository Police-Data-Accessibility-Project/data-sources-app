from dataclasses import dataclass
from typing import Any

from marshmallow import Schema
from pydantic import BaseModel
from werkzeug.datastructures import FileStorage


class BulkRequestDTO(BaseModel):

    class Config:
        arbitrary_types_allowed = True

    file: FileStorage
    csv_schema: Schema
    inner_dto_class: Any
