from db.client.core import DatabaseClient
from middleware.column_permission.core import RelationRoleParameters
from middleware.custom_dataclasses import DeferredFunction
from middleware.dynamic_request_logic.put import put_entry
from middleware.dynamic_request_logic.supporting_classes import MiddlewareParameters
from middleware.enums import Relations
from middleware.primary_resource_logic.data_requests_.constants import RELATION
from middleware.primary_resource_logic.data_requests_.helpers import get_data_requests_relation_role
from middleware.schema_and_dto.dtos.data_requests.put import DataRequestsPutDTO, DataRequestsPutOuterDTO
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.util.type_conversion import dataclass_to_filtered_dict


def optionally_update_github_issue_info(
    db_client: DatabaseClient, entry_data: DataRequestsPutDTO, data_request_id: int
):
    d = {}
    if entry_data.github_issue_url is not None:
        d["github_issue_url"] = entry_data.github_issue_url
    if entry_data.github_issue_number is not None:
        d["github_issue_number"] = entry_data.github_issue_number
    if len(d) > 0:
        db_client._update_entry_in_table(
            table_name=Relations.DATA_REQUESTS_GITHUB_ISSUE_INFO.value,
            entry_id=data_request_id,
            id_column_name="data_request_id",
            column_edit_mappings=d,
        )


def update_data_request_wrapper(
    db_client: DatabaseClient,
    dto: DataRequestsPutOuterDTO,
    data_request_id: int,
    access_info: AccessInfoPrimary,
):
    """
    Update data requests
    :param db_client:
    :param access_info:
    :return:
    """
    entry_dict = created_filtered_entry_dict(dto)
    return put_entry(
        middleware_parameters=MiddlewareParameters(
            access_info=access_info,
            entry_name="Data request",
            relation=RELATION,
            db_client_method=DatabaseClient.update_data_request,
        ),
        entry=entry_dict,
        entry_id=data_request_id,
        relation_role_parameters=RelationRoleParameters(
            relation_role_function_with_params=DeferredFunction(
                function=get_data_requests_relation_role,
                data_request_id=data_request_id,
                db_client=db_client,
            )
        ),
        pre_update_method_with_parameters=DeferredFunction(
            function=optionally_update_github_issue_info,
            db_client=db_client,
            entry_data=dto.entry_data,
            data_request_id=data_request_id,
        ),
    )


def created_filtered_entry_dict(dto: DataRequestsPutOuterDTO) -> dict:
    entry_dict = dataclass_to_filtered_dict(dto.entry_data)
    if "github_issue_url" in entry_dict:
        del entry_dict["github_issue_url"]
    if "github_issue_number" in entry_dict:
        del entry_dict["github_issue_number"]
    return entry_dict
