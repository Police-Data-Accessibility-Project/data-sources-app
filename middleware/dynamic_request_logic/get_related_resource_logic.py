from typing import Optional

from flask import Response

from database_client.database_client import DatabaseClient
from database_client.db_client_dataclasses import WhereMapping
from database_client.enums import RelationRoleEnum, ColumnPermissionEnum
from database_client.subquery_logic import SubqueryParameterManager
from middleware.column_permission_logic import get_permitted_columns
from middleware.dynamic_request_logic.common_functions import check_for_id
from middleware.dynamic_request_logic.supporting_classes import IDInfo
from middleware.enums import Relations
from middleware.flask_response_manager import FlaskResponseManager
from middleware.schema_and_dto_logic.common_schemas_and_dtos import GetByIDBaseDTO
from dataclasses import dataclass


@dataclass
class GetRelatedResourcesParameters:
    db_client: DatabaseClient
    dto: GetByIDBaseDTO
    db_client_method: callable
    primary_relation: Relations
    related_relation: Relations
    linking_column: str
    metadata_count_name: str
    resource_name: str = "resource"


def get_related_resource(
    get_related_resources_parameters: GetRelatedResourcesParameters,
    permitted_columns: Optional[list] = None,
) -> Response:
    # Technically, it'd make more sense as "grrp", but "gerp" rolls off the tongue better
    gerp = get_related_resources_parameters
    check_for_id(
        table_name=gerp.primary_relation.value,
        id_info=IDInfo(
            id_column_value=int(gerp.dto.resource_id),
        ),
        db_client=gerp.db_client,
    )
    if permitted_columns is None:
        permitted_columns = get_permitted_columns(
            db_client=gerp.db_client,
            relation=gerp.related_relation.value,
            role=RelationRoleEnum.STANDARD,
            column_permission=ColumnPermissionEnum.READ,
        )
    subquery_parameters = [
        SubqueryParameterManager.get_subquery_params(
            relation=gerp.related_relation,
            linking_column=gerp.linking_column,
            columns=permitted_columns,
        )
    ]
    where_mappings = [
        WhereMapping(
            column="id",
            value=int(gerp.dto.resource_id),
        )
    ]
    results = gerp.db_client_method(
        gerp.db_client,
        columns=["id"],
        where_mappings=where_mappings,
        subquery_parameters=subquery_parameters,
        build_metadata=True,
    )

    _format_results(gerp, results)

    return FlaskResponseManager.make_response(
        data=results,
    )


def _format_results(gerp: GetRelatedResourcesParameters, results: dict):
    metadata = results["metadata"]
    metadata["count"] = metadata[gerp.metadata_count_name]
    metadata.pop(gerp.metadata_count_name)
    if metadata["count"] == 0:
        results["data"] = []
    else:
        results["data"] = results["data"][0][gerp.linking_column]
    results["metadata"] = metadata
    results.update(
        {
            "message": f"Related {gerp.resource_name} found.",
        }
    )
