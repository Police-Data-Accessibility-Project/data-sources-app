from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest, Forbidden, Conflict

from db.client.core import DatabaseClient
from endpoints.instantiations.data_requests_.related_sources.queries.add_link import \
    DataRequestRelatedSourceAddLinkQueryBuilder
from endpoints.instantiations.data_requests_.related_sources.queries.data_request_exists import \
    DataRequestExistsQueryBuilder
from endpoints.instantiations.data_requests_.related_sources.queries.data_source_exists import \
    DataSourceExistsQueryBuilder
from middleware.common_response_formatting import message_response
from middleware.primary_resource_logic.data_requests_.helpers import check_has_admin_or_owner_role, is_creator_or_admin
from middleware.schema_and_dto.dtos.data_requests.by_id.source import (
    RelatedSourceByIDDTO,
)
from middleware.security.access_info.primary import AccessInfoPrimary


def create_data_request_related_source(
    db_client: DatabaseClient,
    access_info: AccessInfoPrimary,
    dto: RelatedSourceByIDDTO
):

    # Check if user is either an owner or admin
    if not is_creator_or_admin(
        access_info=access_info,
        data_request_id=int(dto.resource_id),
        db_client=db_client,
    ):
        raise Forbidden(
            "User does not have permission to perform this action."
        )

    # Check if data request exists, raise request not found error otherwise (bad request)
    request_exists: bool = db_client.run_query_builder(
        DataRequestExistsQueryBuilder(
            data_request_id=int(dto.resource_id)
        )
    )
    if not request_exists:
        raise BadRequest("Request not found")

    # Check if data source exists, raise source not found error otherwise (bad request)
    source_exists: bool = db_client.run_query_builder(
        DataSourceExistsQueryBuilder(
            data_source_id=int(dto.data_source_id)
        )
    )
    if not source_exists:
        raise BadRequest("Source not found")

    # Add request-source association if it doesn't exist
    try:
        db_client.run_query_builder(
            DataRequestRelatedSourceAddLinkQueryBuilder(
                data_request_id=int(dto.resource_id),
                data_source_id=int(dto.resource_id),
            )
        )
    except IntegrityError:
        raise Conflict("Request-Source association already exists.")

    return message_response(
        message="Data source successfully associated with request.",
    )



