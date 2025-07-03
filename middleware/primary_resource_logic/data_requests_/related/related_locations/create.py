from db.client.core import DatabaseClient
from middleware.column_permission.relation_role_parameters import RelationRoleParameters
from middleware.custom_dataclasses import DeferredFunction
from middleware.dynamic_request_logic.supporting_classes import MiddlewareParameters
from middleware.enums import Relations
from middleware.primary_resource_logic.data_requests_.related.related_locations._helpers import (
    CreateDataRequestRelatedLocationLogic,
)
from middleware.primary_resource_logic.data_requests_.helpers import (
    get_data_requests_relation_role,
)
from middleware.schema_and_dto.dtos.data_requests.by_id.locations import (
    RelatedLocationsByIDDTO,
)
from middleware.security.access_info.primary import AccessInfoPrimary


def create_data_request_related_location(
    db_client: DatabaseClient,
    access_info: AccessInfoPrimary,
    dto: RelatedLocationsByIDDTO,
):
    post_logic = CreateDataRequestRelatedLocationLogic(
        middleware_parameters=MiddlewareParameters(
            access_info=access_info,
            entry_name="Request-Location association",
            relation=Relations.LINK_LOCATIONS_DATA_REQUESTS.value,
            db_client_method=DatabaseClient.create_request_location_relation,
        ),
        entry=dto.get_where_mapping(),
        relation_role_parameters=RelationRoleParameters(
            relation_role_function_with_params=DeferredFunction(
                function=get_data_requests_relation_role,
                data_request_id=dto.resource_id,
                db_client=db_client,
            )
        ),
    )
    return post_logic.execute()
