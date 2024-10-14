from dataclasses import dataclass
from typing import Optional

from marshmallow import Schema, fields, validates_schema, ValidationError

from middleware.schema_and_dto_logic.schema_helpers import create_get_many_schema
from middleware.schema_and_dto_logic.util import get_json_metadata
from utilities.common import get_enums_from_string
from utilities.enums import RecordCategories, SourceMappingEnum, ParserLocation


def transform_record_categories(value: str) -> Optional[list[RecordCategories]]:
    if value is not None:
        return get_enums_from_string(RecordCategories, value, case_insensitive=True)
    return None


class SearchRequestSchema(Schema):
    state = fields.Str(
        required=True,
        metadata={
            "description": "The state of the search.",
            "source": SourceMappingEnum.QUERY_ARGS,
            "location": ParserLocation.QUERY.value,
        },
    )
    record_categories = fields.Str(
        required=False,
        metadata={
            "transformation_function": transform_record_categories,
            "description": "The record categories of the search. If empty, all categories will be searched."
                           "Multiple record categories can be provided as a comma-separated list, eg. 'Police & Public "
                           "Interactions,Agency-published Resources'."
                           "Allowable record categories include: \n  * "
                           + "\n  * ".join([e.value for e in RecordCategories]),
            "source": SourceMappingEnum.QUERY_ARGS,
            "location": ParserLocation.QUERY.value,
        },
    )
    county = fields.Str(
        required=False,
        metadata={
            "description": "The county of the search. If empty, all counties for the given state will be searched.",
            "source": SourceMappingEnum.QUERY_ARGS,
            "location": ParserLocation.QUERY.value,
        },
    )
    locality = fields.Str(
        required=False,
        metadata={
            "description": "The locality of the search. If empty, all localities for the given county will be searched.",
            "source": SourceMappingEnum.QUERY_ARGS,
            "location": ParserLocation.QUERY.value,
        },
    )

    @validates_schema
    def validate_location_info(self, data, **kwargs):
        if data.get("locality") and not data.get("county"):
            raise ValidationError("If locality is provided, county must also be provided.")


class FollowSearchResponseSchema(Schema):
    state = fields.Str(
        required=True,
        metadata=get_json_metadata(
            "The state of the search."),
    )
    county = fields.Str(
        required=False,
        metadata=get_json_metadata("The county of the search. If empty, all counties for the given state will be searched."),
    )
    locality = fields.Str(
        required=False,
        metadata=get_json_metadata("The locality of the search. If empty, all localities for the given county will be searched."),
    )

GetUserFollowedSearchesSchema = create_get_many_schema(
    data_list_schema=FollowSearchResponseSchema(),
    description="The searches that the user follows.",
)


@dataclass
class SearchRequests:
    state: str
    record_categories: Optional[list[RecordCategories]] = None
    county: Optional[str] = None
    locality: Optional[str] = None
