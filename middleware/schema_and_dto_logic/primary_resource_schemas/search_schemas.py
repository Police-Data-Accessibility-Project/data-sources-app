from dataclasses import dataclass
from http import HTTPStatus
from typing import Optional

from marshmallow import Schema, fields, validates_schema, ValidationError
from pydantic import BaseModel, model_validator

from middleware.enums import OutputFormatEnum, RecordTypes
from middleware.flask_response_manager import FlaskResponseManager
from middleware.schema_and_dto_logic.schema_helpers import create_get_many_schema
from middleware.schema_and_dto_logic.util import get_json_metadata, get_query_metadata
from utilities.common import get_enums_from_string
from utilities.enums import RecordCategories, SourceMappingEnum, ParserLocation


def transform_record_categories(value: str) -> Optional[list[RecordCategories]]:
    if value is not None:
        return get_enums_from_string(RecordCategories, value, case_insensitive=True)
    return None


def transform_record_types(value: str) -> Optional[list[RecordTypes]]:
    if value is not None:
        return get_enums_from_string(RecordTypes, value, case_insensitive=True)
    return None


RECORD_CATEGORY_METADATA = {
    "transformation_function": transform_record_categories,
    "description": "The record categories of the search. If empty, all categories will be searched."
    "Multiple record categories can be provided as a comma-separated list, eg. 'Police & Public "
    "Interactions,Agency-published Resources'."
    "Allowable record categories include: \n  * "
    + "\n  * ".join([e.value for e in RecordCategories]),
    "source": SourceMappingEnum.QUERY_ARGS,
    "location": ParserLocation.QUERY.value,
}

RECORD_TYPE_METADATA = {
    "transformation_function": transform_record_types,
    "description": "The record types of the search. If empty, all types will be searched."
    "Multiple record types can be provided as a comma-separated list, eg. 'Accident Reports,"
    "Stops'. Mutually exclusive with `record_categories`.",
    "source": SourceMappingEnum.QUERY_ARGS,
    "location": ParserLocation.QUERY.value,
}


class FederalSearchRequestSchema(Schema):
    record_categories = fields.Str(
        required=False,
        load_default="All",
        metadata=RECORD_CATEGORY_METADATA,
    )
    page = fields.Int(
        required=False,
        load_default=1,
        metadata=get_query_metadata(
            "The page number of the results to retrieve. Begins at 1."
        ),
    )


class FederalSearchResponseInnerSchema(Schema):
    id = fields.Int(
        required=True,
        metadata=get_json_metadata("The ID of the search."),
    )
    agency_name = fields.Str(
        required=True,
        metadata=get_json_metadata("The name of the agency."),
    )
    data_source_name = fields.Str(
        required=True,
        metadata=get_json_metadata("The name of the data source."),
    )
    description = fields.Str(
        required=True,
        allow_none=True,
        metadata=get_json_metadata("The description of the search."),
    )
    record_type = fields.Str(
        required=True,
        metadata=get_json_metadata("The type of the record."),
    )
    source_url = fields.Str(
        required=True,
        metadata=get_json_metadata("The URL of the data source."),
    )
    record_formats = fields.List(
        fields.Str(
            required=True,
            metadata=get_json_metadata("The record formats of the search."),
        ),
        allow_none=True,
        metadata=get_json_metadata("The record formats of the search."),
    )
    coverage_start = fields.Str(
        required=True,
        allow_none=True,
        metadata=get_json_metadata("The start date of the search."),
    )
    coverage_end = fields.Str(
        required=True,
        metadata=get_json_metadata("The end date of the search."),
        allow_none=True,
    )
    agency_supplied = fields.Bool(
        required=True,
        metadata=get_json_metadata("Whether the agency supplied the data."),
    )
    jurisdiction_type = fields.Str(
        required=True,
        metadata=get_json_metadata("The type of the jurisdiction."),
    )


class FederalSearchResponseSchema(Schema):
    results = fields.List(
        fields.Nested(
            FederalSearchResponseInnerSchema(),
            metadata=get_json_metadata("The list of results"),
        ),
        required=True,
        metadata=get_json_metadata("The list of results"),
    )
    count = fields.Int(
        required=True,
        metadata=get_json_metadata("The number of results"),
    )


class SearchRequestSchema(Schema):
    location_id = fields.Int(
        required=False,
        metadata=get_query_metadata("The location ID of the search."),
    )
    record_categories = fields.Str(
        required=False,
        load_default="All",
        metadata=RECORD_CATEGORY_METADATA,
    )
    record_types = fields.Str(
        required=False,
        metadata=RECORD_TYPE_METADATA,
    )

    output_format = fields.Enum(
        required=False,
        enum=OutputFormatEnum,
        by_value=fields.Str,
        load_default=OutputFormatEnum.JSON.value,
        metadata={
            "description": "The output format of the search.",
            "source": SourceMappingEnum.QUERY_ARGS,
            "location": ParserLocation.QUERY.value,
        },
    )


class SearchResultsInnerSchema(Schema):
    id = fields.Int(
        required=True,
        metadata=get_json_metadata("The ID of the search."),
    )
    agency_name = fields.Str(
        required=True,
        metadata=get_json_metadata("The name of the agency."),
    )
    municipality = fields.Str(
        required=True,
        allow_none=True,
        metadata=get_json_metadata("The name of the municipality."),
    )
    state_iso = fields.Str(
        required=True,
        metadata=get_json_metadata("The ISO code of the state."),
    )
    data_source_name = fields.Str(
        required=True,
        metadata=get_json_metadata("The name of the data source."),
    )
    description = fields.Str(
        required=True,
        allow_none=True,
        metadata=get_json_metadata("The description of the search."),
    )
    record_type = fields.Str(
        required=True,
        metadata=get_json_metadata("The type of the record."),
    )
    source_url = fields.Str(
        required=True,
        metadata=get_json_metadata("The URL of the data source."),
    )
    record_formats = fields.List(
        fields.Str(
            required=True,
            metadata=get_json_metadata("The record formats of the search."),
        ),
        allow_none=True,
        metadata=get_json_metadata("The record formats of the search."),
    )
    coverage_start = fields.Str(
        required=True,
        allow_none=True,
        metadata=get_json_metadata("The start date of the search."),
    )
    coverage_end = fields.Str(
        required=True,
        metadata=get_json_metadata("The end date of the search."),
        allow_none=True,
    )
    agency_supplied = fields.Bool(
        required=True,
        metadata=get_json_metadata("Whether the agency supplied the data."),
    )
    jurisdiction_type = fields.Str(
        required=True,
        metadata=get_json_metadata("The type of the jurisdiction."),
    )


class SearchResultsOuterSchema(Schema):
    results = fields.List(
        fields.Nested(
            SearchResultsInnerSchema(),
            metadata=get_json_metadata("The list of results"),
        ),
        required=True,
        metadata=get_json_metadata("The list of results"),
    )
    count = fields.Int(
        required=True,
        metadata=get_json_metadata("The number of results"),
    )


class SearchResponseJurisdictionsWrapperSchema(Schema):
    federal = fields.Nested(
        SearchResultsOuterSchema(),
        metadata=get_json_metadata("Results for the federal jurisdiction."),
    )
    state = fields.Nested(
        SearchResultsOuterSchema(),
        metadata=get_json_metadata("Results for the state jurisdiction."),
    )
    county = fields.Nested(
        SearchResultsOuterSchema(),
        metadata=get_json_metadata("Results for the county jurisdiction."),
    )
    locality = fields.Nested(
        SearchResultsOuterSchema(),
        metadata=get_json_metadata("Results for the locality jurisdiction."),
    )


class SearchResponseSchema(Schema):
    data = fields.Nested(
        SearchResponseJurisdictionsWrapperSchema(),
        metadata=get_json_metadata("The list of results"),
    )
    count = fields.Int(
        metadata=get_json_metadata("The number of results"),
    )


class FollowSearchResponseSchema(Schema):
    state_name = fields.Str(
        required=True,
        metadata=get_json_metadata("The state of the search."),
    )
    county_name = fields.Str(
        required=False,
        allow_none=True,
        metadata=get_json_metadata(
            "The county of the search. If empty, all counties for the given state will be searched."
        ),
    )
    locality_name = fields.Str(
        required=False,
        allow_none=True,
        metadata=get_json_metadata(
            "The locality of the search. If empty, all localities for the given county will be searched."
        ),
    )
    location_id = fields.Int(
        required=True,
        metadata=get_json_metadata("The location ID of the search."),
    )


GetUserFollowedSearchesSchema = create_get_many_schema(
    data_list_schema=FollowSearchResponseSchema,
    description="The searches that the user follows.",
)


class FederalSearchRequestDTO(BaseModel):
    record_categories: Optional[list[RecordCategories]] = None
    page: Optional[int] = None


class SearchRequestsDTO(BaseModel):
    location_id: int
    record_categories: Optional[list[RecordCategories]] = None
    record_types: Optional[list[RecordTypes]] = None
    output_format: Optional[OutputFormatEnum] = None

    @model_validator(mode="after")
    def check_exclusive_fields(self):

        if self.record_categories is not None and self.record_types is not None:
            if self.record_categories == [RecordCategories.ALL]:
                self.record_categories = None
                return

            FlaskResponseManager.abort(
                message="Only one of 'record_categories' or 'record_types' should be provided.",
                code=HTTPStatus.BAD_REQUEST,
            )
            raise ValueError(
                "Only one of 'record_categories' or 'record_types' should be provided, not both."
            )
