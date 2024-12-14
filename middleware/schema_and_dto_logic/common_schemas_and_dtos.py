"""
The base schema to use for get many requests,
to be inherited by other get many requests.
"""

import ast
from typing import Optional

from marshmallow import Schema, fields, validate
from pydantic import BaseModel

from database_client.enums import SortOrder, LocationType
from middleware.schema_and_dto_logic.custom_fields import DataField
from middleware.schema_and_dto_logic.non_dto_dataclasses import (
    SchemaPopulateParameters,
    DTOPopulateParameters,
)
from middleware.schema_and_dto_logic.util import get_json_metadata

from utilities.enums import SourceMappingEnum


class GetManyRequestsBaseSchema(Schema):
    page = fields.Integer(
        validate=validate.Range(min=1),
        load_default=1,
        metadata={
            "description": "The page number of the results to retrieve. Begins at 1.",
            "source": SourceMappingEnum.QUERY_ARGS,
        },
    )
    sort_by = fields.Str(
        required=False,
        metadata={
            "description": "The field to sort the results by.",
            "source": SourceMappingEnum.QUERY_ARGS,
        },
    )
    sort_order = fields.Enum(
        required=False,
        enum=SortOrder,
        by_value=fields.Str,
        load_default=SortOrder.DESCENDING,
        metadata={
            "source": SourceMappingEnum.QUERY_ARGS,
            "description": "The order to sort the results by.",
        },
    )
    requested_columns = fields.Str(
        required=False,
        metadata={
            "source": SourceMappingEnum.QUERY_ARGS,
            "transformation_function": lambda value: (
                ast.literal_eval(value) if value else None
            ),
            "description": "A comma-delimited list of the columns to return in the results. Defaults to all permitted if not provided.",
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
