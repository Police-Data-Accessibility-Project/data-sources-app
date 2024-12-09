from dataclasses import dataclass
from typing import Any

from marshmallow import Schema
from pydantic import BaseModel
from werkzeug.datastructures import FileStorage


@dataclass
class BatchRequestDTO:
    file: FileStorage
    csv_schema: Schema
    inner_dto_class: Any
