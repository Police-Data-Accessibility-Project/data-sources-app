from db.client.core import DatabaseClient
from middleware.custom_dataclasses import DeferredFunction
from middleware.dynamic_request_logic.delete import delete_entry
from middleware.dynamic_request_logic.supporting_classes import MiddlewareParameters, IDInfo
from middleware.enums import Relations
from middleware.primary_resource_logic.data_requests_.helpers import is_creator_or_admin
from middleware.schema_and_dto.dtos.data_requests.by_id.locations import RelatedLocationsByIDDTO
from middleware.security.access_info.primary import AccessInfoPrimary


def delete_data_request_related_location(
    db_client: DatabaseClient,
    access_info: AccessInfoPrimary,
    dto: RelatedLocationsByIDDTO,
):
    return delete_entry(
        middleware_parameters=MiddlewareParameters(
            access_info=access_info,
            entry_name="Request-Location association",
            relation=Relations.LINK_LOCATIONS_DATA_REQUESTS.value,
            db_client_method=DatabaseClient.delete_request_location_relation,
        ),
        id_info=IDInfo(
            additional_where_mappings=dto.get_where_mapping(),
        ),
        permission_checking_function=DeferredFunction(
            is_creator_or_admin,
            access_info=access_info,
            data_request_id=dto.resource_id,
            db_client=db_client,
        ),
    )
