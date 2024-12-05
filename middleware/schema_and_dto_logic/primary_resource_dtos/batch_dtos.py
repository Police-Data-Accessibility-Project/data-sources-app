from dataclasses import dataclass
from io import BytesIO
from typing import Any

from marshmallow import Schema
from pydantic import BaseModel
from werkzeug.datastructures import FileStorage


@dataclass
class BatchRequestDTO:
    file: FileStorage
    csv_schema: Schema


class BatchPutEntryDTO(BaseModel):
    id: int  # The id of the entry to be updated
    entries: dict[str, Any]
