from marshmallow import fields

from middleware.schema_and_dto.schemas.agencies.get.base import AgenciesGetSchema
from endpoints.instantiations.data_requests_._shared.schemas.base import (
    DataRequestsSchema,
)
from middleware.schema_and_dto.schemas.data_sources.expanded import (
    DataSourceExpandedSchema,
)
from middleware.schema_and_dto.util import get_json_metadata


class DataSourceGetSchema(DataSourceExpandedSchema):
    """
    The schema for getting a single data source.
    Include the base schema as well as data from connected tables, including agencies and record types.
    """

    agencies = fields.List(
        fields.Nested(
            AgenciesGetSchema(
                only=[
                    "id",
                    "name",
                    "submitted_name",
                    "agency_type",
                    "jurisdiction_type",
                    "homepage_url",
                    "locations",
                    "state_name",
                    "state_iso",
                    "locality_name",
                    "county_name",
                    "county_fips",
                ],
            ),
            metadata=get_json_metadata("The agencies associated with the data source."),
        ),
        allow_none=True,
        metadata=get_json_metadata("The agencies associated with the data source."),
    )
    data_requests = fields.List(
        fields.Nested(
            nested=DataRequestsSchema(),
            metadata=get_json_metadata(
                "The data requests associated with the data source."
            ),
        ),
        allow_none=True,
        metadata=get_json_metadata(
            "The data requests associated with the data source."
        ),
    )
