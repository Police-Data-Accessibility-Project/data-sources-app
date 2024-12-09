from dataclasses import asdict

from flask import Response, request

from database_client.database_client import DatabaseClient
from database_client.db_client_dataclasses import OrderByParameters
from database_client.subquery_logic import SubqueryParameterManager
from middleware.access_logic import AccessInfoPrimary
from middleware.custom_dataclasses import DeferredFunction
from middleware.dynamic_request_logic.delete_logic import delete_entry
from middleware.dynamic_request_logic.get_by_id_logic import get_by_id
from middleware.dynamic_request_logic.get_many_logic import get_many
from middleware.dynamic_request_logic.post_logic import post_entry, PostHandler
from middleware.dynamic_request_logic.put_logic import put_entry, PutHandler
from middleware.dynamic_request_logic.supporting_classes import (
    MiddlewareParameters,
    IDInfo,
    PutPostRequestInfo,
)
from middleware.location_logic import get_location_id
from middleware.schema_and_dto_logic.primary_resource_schemas.agencies_advanced_schemas import (
    AgenciesPutSchema,
)
from middleware.schema_and_dto_logic.primary_resource_dtos.agencies_dtos import (
    AgenciesPostDTO,
)
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    GetManyBaseDTO,
    GetByIDBaseDTO,
    LocationInfoDTO,
)
from middleware.enums import Relations, JurisdictionType
from middleware.util import dict_enums_to_values

SUBQUERY_PARAMS = [SubqueryParameterManager.data_sources()]


def get_agencies(
    db_client: DatabaseClient, access_info: AccessInfoPrimary, dto: GetManyBaseDTO
) -> Response:
    """
    Retrieves a paginated list of approved agencies from the database.

    :param db_client: The database client object.
    :param page: The page number of results to return.
    :return: A response object with the relevant agency information and status code.
    """
    return get_many(
        middleware_parameters=MiddlewareParameters(
            access_info=access_info,
            entry_name="agencies",
            relation=Relations.AGENCIES_EXPANDED.value,
            db_client_method=DatabaseClient.get_agencies,
            db_client_additional_args={
                "build_metadata": True,
                "order_by": OrderByParameters.construct_from_args(
                    sort_by=dto.sort_by, sort_order=dto.sort_order
                ),
            },
            subquery_parameters=SUBQUERY_PARAMS,
        ),
        page=dto.page,
    )


def get_agency_by_id(
    db_client: DatabaseClient, access_info: AccessInfoPrimary, dto: GetByIDBaseDTO
) -> Response:
    return get_by_id(
        middleware_parameters=MiddlewareParameters(
            access_info=access_info,
            entry_name="agency",
            relation=Relations.AGENCIES_EXPANDED.value,
            db_client_method=DatabaseClient.get_agencies,
            subquery_parameters=SUBQUERY_PARAMS,
        ),
        id=dto.resource_id,
    )


def validate_and_add_location_info(
    db_client: DatabaseClient, entry_data: dict, location_info: LocationInfoDTO
):
    """
    Checks that location provided is a valid one, and returns the associated location id
    In the case of a locality which does not yet exist, adds it and returns the location id
    :param db_client:
    :param entry_data: Modified in-place
    :param location_info:
    :return:
    """
    location_id = get_location_id(db_client, location_info)
    entry_data["location_id"] = location_id


class AgencyPostRequestInfo(PutPostRequestInfo):
    dto: AgenciesPostDTO


class AgencyPostHandler(PostHandler):

    def __init__(self):
        super().__init__(middleware_parameters=AGENCY_POST_MIDDLEWARE_PARAMETERS)

    def pre_execute(self, request: AgencyPostRequestInfo):
        validate_and_add_location_info(
            db_client=DatabaseClient(),
            entry_data=request.entry,
            location_info=request.dto.location_info,
        )


class AgencyPutHandler(PutHandler):

    def __init__(self):
        super().__init__(middleware_parameters=AGENCY_PUT_MIDDLEWARE_PARAMETERS)

    def pre_execute(self, request: PutPostRequestInfo):
        # The below values are probably incorrect, but serve as a placeholder
        entry_data = dict(request.dto.agency_info)
        request.entry = dict_enums_to_values(entry_data)
        location_info = request.dto.location_info
        if location_info is not None:
            validate_and_add_location_info(
                db_client=DatabaseClient(),
                entry_data=entry_data,
                location_info=location_info,
            )


AGENCY_POST_MIDDLEWARE_PARAMETERS = MiddlewareParameters(
    entry_name="agency",
    relation=Relations.AGENCIES.value,
    db_client_method=DatabaseClient.create_agency,
)


def create_agency(
    db_client: DatabaseClient,
    dto: AgenciesPostDTO,
    make_response: bool = True,
) -> Response:
    entry_data = dict(dto.agency_info)
    pre_insertion_function = optionally_get_location_info_deferred_function(
        db_client=db_client,
        jurisdiction_type=dto.agency_info.jurisdiction_type,
        entry_data=entry_data,
        location_info=dto.location_info,
    )

    return post_entry(
        middleware_parameters=AGENCY_POST_MIDDLEWARE_PARAMETERS,
        entry=entry_data,
        pre_insertion_function_with_parameters=pre_insertion_function,
        check_for_permission=False,
        make_response=make_response,
    )


def optionally_get_location_info_deferred_function(
    db_client: DatabaseClient,
    jurisdiction_type: JurisdictionType,
    entry_data: dict,
    location_info: LocationInfoDTO,
):
    if jurisdiction_type == JurisdictionType.FEDERAL:
        deferred_function = None
    else:
        deferred_function = DeferredFunction(
            function=validate_and_add_location_info,
            db_client=db_client,
            entry_data=entry_data,
            location_info=location_info,
        )
    return deferred_function


AGENCY_PUT_MIDDLEWARE_PARAMETERS = MiddlewareParameters(
    entry_name="agency",
    relation=Relations.AGENCIES.value,
    db_client_method=DatabaseClient.update_agency,
)


def update_agency(
    db_client: DatabaseClient,
    access_info: AccessInfoPrimary,
    agency_id: str,
) -> Response:
    AgenciesPutSchema().load(request.json)
    entry_data = request.json.get("agency_info")
    location_info = request.json.get("location_info")
    if location_info is not None:
        jurisdiction_type = entry_data.get("jurisdiction_type")
        deferred_function = optionally_get_location_info_deferred_function(
            db_client=db_client,
            jurisdiction_type=jurisdiction_type,
            entry_data=entry_data,
            location_info=location_info,
        )
    else:
        deferred_function = None

    return put_entry(
        middleware_parameters=MiddlewareParameters(
            access_info=access_info,
            entry_name="agency",
            relation=Relations.AGENCIES.value,
            db_client_method=DatabaseClient.update_agency,
        ),
        entry=entry_data,
        entry_id=int(agency_id),
        pre_update_method_with_parameters=deferred_function,
    )


def delete_agency(
    db_client: DatabaseClient, access_info: AccessInfoPrimary, agency_id: str
) -> Response:
    return delete_entry(
        middleware_parameters=MiddlewareParameters(
            access_info=access_info,
            entry_name="agency",
            relation=Relations.AGENCIES.value,
            db_client_method=DatabaseClient.delete_agency,
        ),
        id_info=IDInfo(id_column_value=int(agency_id)),
    )
