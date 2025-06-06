"""
The base schema to use for get many requests,
to be inherited by other get many requests.
"""

import ast
from typing import Optional

from marshmallow import Schema, fields
from pydantic import BaseModel, Field

from db.constants import PAGE_SIZE
from db.enums import SortOrder, LocationType
from middleware.schema_and_dto_logic.common_fields import (
    PAGE_FIELD,
    SORT_ORDER_FIELD,
)
from middleware.schema_and_dto_logic.custom_fields import DataField
from middleware.schema_and_dto_logic.dynamic_logic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
    MetadataInfo,
)
from middleware.schema_and_dto_logic.non_dto_dataclasses import (
    SchemaPopulateParameters,
    DTOPopulateParameters,
)
from utilities.enums import SourceMappingEnum


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


class GetByIDBaseDTO(BaseModel):
    resource_id: str = Field(
        description="The ID of the object to retrieve.",
        json_schema_extra=MetadataInfo(required=True, source=SourceMappingEnum.PATH),
    )


GetByIDBaseSchema = generate_marshmallow_schema(GetByIDBaseDTO)


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


class TypeaheadDTO(BaseModel):
    query: str = Field(
        description="The search query to get suggestions for.",
        json_schema_extra=MetadataInfo(
            source=SourceMappingEnum.QUERY_ARGS, required=True
        ),
    )


TypeaheadQuerySchema = generate_marshmallow_schema(TypeaheadDTO)


class LocationInfoDTO(BaseModel):
    type: LocationType
    state_iso: str
    county_fips: Optional[str] = None
    locality_name: Optional[str] = None


class EmailOnlyDTO(BaseModel):
    email: str = Field(
        description="The user's email address",
        json_schema_extra=MetadataInfo(required=True),
    )


EmailOnlySchema = generate_marshmallow_schema(EmailOnlyDTO)
