"""
The base schema to use for get many requests,
to be inherited by other get many requests.
"""

import ast
from dataclasses import dataclass
from typing import Optional

from marshmallow import Schema, fields, validate, validates_schema, ValidationError

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


@dataclass
class GetManyBaseDTO:
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


@dataclass
class GetByIDBaseDTO:
    resource_id: str


class EntryDataRequestSchema(Schema):
    entry_data = DataField(
        required=True,
        metadata={
            "source": SourceMappingEnum.JSON,
            "description": "The entry data field for adding and updating entries",
        },
    )


@dataclass
class EntryCreateUpdateRequestDTO:
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


@dataclass
class TypeaheadDTO:
    query: str


STATE_ISO_FIELD = fields.Str(
    required=False,
    allow_none=True,
    metadata={
        "description": "The 2 letter ISO code of the state.",
        "source": SourceMappingEnum.JSON,
    },
    validate=validate.Length(2),
)
COUNTY_FIPS_FIELD = fields.Str(
    required=False,
    allow_none=True,
    metadata={
        "description": "The unique 5-digit FIPS code of the county."
        "Does not apply to state or federal agencies.",
        "source": SourceMappingEnum.JSON,
    },
    validate=validate.Length(5),
)
LOCALITY_NAME_FIELD = fields.Str(
    required=False,
    allow_none=True,
    metadata={
        "description": "The name of the locality.",
        "source": SourceMappingEnum.JSON,
    },
)


class LocationInfoSchema(Schema):
    type = fields.Enum(
        required=True,
        enum=LocationType,
        by_value=fields.Str,
        metadata={
            "description": "The type of location. ",
            "source": SourceMappingEnum.JSON,
        },
    )
    state_iso = STATE_ISO_FIELD
    county_fips = COUNTY_FIPS_FIELD
    locality_name = LOCALITY_NAME_FIELD
    id = fields.Integer(
        metadata=get_json_metadata(
            description="The unique identifier of the location.",
        )
    )

    @validates_schema
    def validate_location_fields(self, data, **kwargs):
        location_type = data.get("type")

        if location_type == LocationType.STATE:
            if data.get("state_iso") is None:
                raise ValidationError("state_iso is required for location type STATE.")
            if (
                data.get("county_fips") is not None
                or data.get("locality_name") is not None
            ):
                raise ValidationError(
                    "county_fips and locality_name must be None for location type STATE."
                )

        elif location_type == LocationType.COUNTY:
            if data.get("county_fips") is None:
                raise ValidationError(
                    "county_fips is required for location type COUNTY."
                )
            if data.get("state_iso") is None:
                raise ValidationError("state_iso is required for location type COUNTY.")
            if data.get("locality_name"):
                raise ValidationError(
                    "locality_name must be None for location type COUNTY."
                )

        elif location_type == LocationType.LOCALITY:
            if data.get("locality_name") is None:
                raise ValidationError(
                    "locality_name is required for location type CITY."
                )
            if data.get("state_iso") is None:
                raise ValidationError("state_iso is required for location type CITY.")
            if data.get("county_fips") is None:
                raise ValidationError("county_fips is required for location type CITY.")


class LocationInfoExpandedSchema(LocationInfoSchema):
    state_name = fields.Str(
        required=True, metadata=get_json_metadata(description="The name of the state.")
    )
    county_name = fields.Str(
        required=True,
        allow_none=True,
        metadata=get_json_metadata(description="The name of the county."),
    )


@dataclass
class LocationInfoDTO:
    type: LocationType
    state_iso: str
    county_fips: Optional[str] = None
    locality_name: Optional[str] = None
