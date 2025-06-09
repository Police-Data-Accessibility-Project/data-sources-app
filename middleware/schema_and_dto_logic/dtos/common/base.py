import ast
from typing import Optional

from marshmallow import Schema, fields
from pydantic import BaseModel, Field

from db.constants import PAGE_SIZE
from db.enums import SortOrder
from middleware.schema_and_dto_logic.dynamic_logic.pydantic_to_marshmallow.core import (
    MetadataInfo,
)
from middleware.schema_and_dto_logic.schemas.common.fields import (
    PAGE_FIELD,
    SORT_ORDER_FIELD,
)
from utilities.enums import SourceMappingEnum


class GetManyBaseDTO(BaseModel):
    """
    A base data transfer object for GET requests returning a list of objects
    """

    page: int
    sort_by: Optional[str] = None
    sort_order: Optional[SortOrder] = None
    requested_columns: Optional[list[str]] = None
    limit: Optional[int] = PAGE_SIZE


class GetByIDBaseDTO(BaseModel):
    resource_id: str = Field(
        description="The ID of the object to retrieve.",
        json_schema_extra=MetadataInfo(required=True, source=SourceMappingEnum.PATH),
    )


class GetManyRequestsBaseSchema(Schema):
    page = PAGE_FIELD
    sort_by = fields.Str(
        required=False,
        metadata={
            "description": "The field to sort the results by.",
            "source": SourceMappingEnum.QUERY_ARGS,
        },
    )
    sort_order = SORT_ORDER_FIELD
    requested_columns = fields.Str(
        required=False,
        metadata={
            "source": SourceMappingEnum.QUERY_ARGS,
            "transformation_function": lambda value: (
                ast.literal_eval(value) if value else None
            ),
            "description": "A comma-delimited list of the columns to return in the results. "
            "Defaults to all permitted if not provided."
            "Note that these columns must be in URL-encoded format."
            "\nFor example, for `name` and `id`: '/api/data-sources?page=1&requested_columns=%5B%27name%27%2C+%27id%27%5D'",
        },
    )
    limit = fields.Integer(
        required=False,
        load_default=100,
        metadata={
            "source": SourceMappingEnum.QUERY_ARGS,
            "description": "The maximum number of results to return. Defaults to 100 if not provided.",
        },
    )
