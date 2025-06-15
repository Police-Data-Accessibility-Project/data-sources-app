from typing import Optional

from pydantic import BaseModel

from middleware.enums import DataSourceCreationResponse
from middleware.schema_and_dto.dtos._helpers import (
    default_field_not_required,
    default_field_required,
)


class SourceCollectorPostResponseInnerDTO(BaseModel):
    url: Optional[str] = default_field_not_required(
        description="The URL of the created data source."
    )
    status: DataSourceCreationResponse = default_field_required(
        description="The status of the data source creation."
    )
    data_source_id: Optional[int] = default_field_not_required(
        description="The ID of the created data source, if successful.",
    )
    error: Optional[str] = default_field_not_required(
        description="The error message, if the data source creation failed.",
    )
