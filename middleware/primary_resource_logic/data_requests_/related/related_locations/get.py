from flask import Response

from db.client.core import DatabaseClient
from middleware.dynamic_request_logic.get.related_resource import get_related_resource, GetRelatedResourcesParameters
from middleware.enums import Relations
from middleware.schema_and_dto.dtos.common.base import GetByIDBaseDTO


def get_data_request_related_locations(
    db_client: DatabaseClient, dto: GetByIDBaseDTO
) -> Response:
    return get_related_resource(
        get_related_resources_parameters=GetRelatedResourcesParameters(
            dto=dto,
            db_client_method=DatabaseClient.get_data_requests,
            primary_relation=Relations.DATA_REQUESTS,
            related_relation=Relations.LOCATIONS_EXPANDED,
            linking_column="locations",
            metadata_count_name="locations_count",
            resource_name="locations",
        ),
        permitted_columns=[
            "id",
            "state_name",
            "state_iso",
            "county_name",
            "county_fips",
            "locality_name",
            "type",
        ],
        alias_mappings={"id": "location_id"},
    )
