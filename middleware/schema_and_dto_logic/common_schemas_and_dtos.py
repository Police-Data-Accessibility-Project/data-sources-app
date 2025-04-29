"""
The base schema to use for get many requests,
to be inherited by other get many requests.
"""

import ast
from typing import Optional

from marshmallow import Schema, fields, validate
from pydantic import BaseModel

from database_client.constants import PAGE_SIZE
from database_client.enums import SortOrder, LocationType
from middleware.schema_and_dto_logic.common_fields import (
    PAGE_FIELD,
    SORT_ORDER_FIELD,
    SORT_BY_FIELD,
)
from middleware.schema_and_dto_logic.custom_fields import DataField
from middleware.schema_and_dto_logic.non_dto_dataclasses import (
    SchemaPopulateParameters,
    DTOPopulateParameters,
)
from middleware.schema_and_dto_logic.util import get_json_metadata

from utilities.enums import SourceMappingEnum


class GetManyRequestsBaseSchema(Schema):
    page = PAGE_FIELD
    sort_by = SORT_BY_FIELD
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


class GetManyBaseDTO(BaseModel):
    """
    A base data transfer object for GET requests returning a list of objects
    """

    page: int
    sort_by: Optional[str] = None
    sort_order: Optional[SortOrder] = None
    requested_columns: Optional[list[str]] = None
    limit: Optional[int] = PAGE_SIZE


GET_MANY_SCHEMA_POPULATE_PARAMETERS = SchemaPopulateParameters(
    schema=GetManyRequestsBaseSchema(),
    dto_class=GetManyBaseDTO,
)


class GetByIDBaseSchema(Schema):
    resource_id = fields.Str(
        required=True,
        metadata={
            "source": SourceMappingEnum.PATH,
            "description": "The ID of the object to retrieve.",
        },
    )


class GetByIDBaseDTO(BaseModel):
    resource_id: str


class EntryDataRequestSchema(Schema):
    entry_data = DataField(
        required=True,
        metadata={
            "source": SourceMappingEnum.JSON,
            "description": "The entry data field for adding and updating entries",
        },
    )


class EntryCreateUpdateRequestDTO(BaseModel):
    """
    Contains data for creating or updating an entry
    """

    entry_data: dict

    @classmethod
    def get_dto_populate_parameters(cls) -> DTOPopulateParameters:
        return DTOPopulateParameters(
            dto_class=EntryCreateUpdateRequestDTO,
            source=SourceMappingEnum.JSON,
            validation_schema=EntryDataRequestSchema,
        )


class TypeaheadQuerySchema(Schema):
    query = fields.Str(
        required=True,
        metadata={
            "source": SourceMappingEnum.QUERY_ARGS,
            "description": "The search query to get suggestions for.",
        },
    )


class TypeaheadDTO(BaseModel):
    query: str


class LocationInfoDTO(BaseModel):
    type: LocationType
    state_iso: str
    county_fips: Optional[str] = None
    locality_name: Optional[str] = None


class EmailOnlySchema(Schema):
    email = fields.Email(
        required=True,
        metadata=get_json_metadata(description="The user's email address"),
    )


class EmailOnlyDTO(BaseModel):
    email: str
