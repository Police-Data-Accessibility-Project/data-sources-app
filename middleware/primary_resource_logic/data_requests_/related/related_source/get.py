from db.client.core import DatabaseClient
from middleware.dynamic_request_logic.get.related_resource import get_related_resource, GetRelatedResourcesParameters
from middleware.enums import Relations
from middleware.schema_and_dto.dtos.common.base import GetByIDBaseDTO


def get_data_request_related_sources(db_client: DatabaseClient, dto: GetByIDBaseDTO):

    return get_related_resource(
        get_related_resources_parameters=GetRelatedResourcesParameters(
            dto=dto,
            db_client_method=DatabaseClient.get_data_requests,
            primary_relation=Relations.DATA_REQUESTS,
            related_relation=Relations.DATA_SOURCES_EXPANDED,
            linking_column="data_sources",
            metadata_count_name="data_sources_count",
            resource_name="sources",
        )
    )
