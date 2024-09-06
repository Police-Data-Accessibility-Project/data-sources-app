"""
The base schema to use for get many requests,
to be inherited by other get many requests.
"""

from dataclasses import dataclass
from typing import Optional, Type, Callable

from marshmallow import Schema, fields, validate

from database_client.enums import SortOrder
from middleware.schema_and_dto_logic.custom_fields import DataField
from middleware.schema_and_dto_logic.custom_types import DTOTypes
from utilities.common import get_valid_enum_value

from utilities.enums import SourceMappingEnum


class GetManyBaseSchema(Schema):
    page = fields.Integer(
        required=True,
        description="The page number of the results to retrieve. Begins at 1.",
        source=SourceMappingEnum.QUERY_ARGS,
        validate=validate.Range(min=1),
        default=1,
    )
    sort_by = fields.Str(
        required=False,
        description="The field to sort the results by.",
        source=SourceMappingEnum.QUERY_ARGS,
    )
    sort_order = fields.Str(
        required=False,
        description="The order to sort the results by.",
        source=SourceMappingEnum.QUERY_ARGS,
        validate=validate.OneOf([e.value for e in SortOrder]),
        transformation_function=lambda value: get_valid_enum_value(SortOrder, value),
    )
    requested_columns = fields.Str(
        required=False,
        description="A comma-delimited list of the columns to return in the results. Defaults to all permitted if not provided.",
        source=SourceMappingEnum.QUERY_ARGS,
        transformation_function=lambda value: value.split(","),
    )


@dataclass
class GetManyBaseDTO:
    """
    A base data transfer object for GET requests returning a list of objects
    """

    page: int
    sort_by: Optional[str] = None
    sort_order: Optional[SortOrder] = None
    requested_columns: Optional[list[str]] = None


class EntryDataRequestSchema(Schema):
    entry_data = DataField(
        required=True,
        description="The entry data field for adding and updating entries",
        source=SourceMappingEnum.JSON,
    )


@dataclass
class DTOPopulateParameters:
    """
    Parameters for the dynamic DTO population function
    """

    dto_class: Type[DTOTypes]
    source: Optional[SourceMappingEnum] = None
    transformation_functions: Optional[dict[str, Callable]] = None
    attribute_source_mapping: Optional[dict[str, SourceMappingEnum]] = None
    # A schema to be used for validating the input of the class.
    validation_schema: Optional[Type[Schema]] = None


@dataclass
class EntryDataRequestDTO:
    """
    Contains data for creating or updating an entry
    """

    entry_data: dict

    @classmethod
    def get_dto_populate_parameters(cls) -> DTOPopulateParameters:
        return DTOPopulateParameters(
            dto_class=EntryDataRequestDTO,
            source=SourceMappingEnum.JSON,
            validation_schema=EntryDataRequestSchema,
        )
