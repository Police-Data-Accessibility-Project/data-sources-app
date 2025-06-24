from typing import Optional

from db.db_client_dataclasses import WhereMapping, OrderByParameters
from db.enums import (
    ColumnPermissionEnum,
)
from middleware.primary_resource_logic.data_requests_.constants import RELATION
from middleware.primary_resource_logic.data_requests_.helpers import (
    get_data_requests_subquery_params,
)
from middleware.column_permission.core import (
    get_permitted_columns,
)
from middleware.schema_and_dto.dtos.common.base import (
    GetManyBaseDTO,
)


def get_data_requests_with_permitted_columns(
    db_client,
    relation_role,
    dto: GetManyBaseDTO,
    where_mappings: Optional[list[WhereMapping]] = [True],
    build_metadata: Optional[bool] = False,
) -> list[dict]:

    columns = get_permitted_columns(
        relation=RELATION,
        role=relation_role,
        user_permission=ColumnPermissionEnum.READ,
    )
    data_requests = db_client.get_data_requests(
        columns=columns,
        where_mappings=where_mappings,
        order_by=OrderByParameters.construct_from_args(dto.sort_by, dto.sort_order),
        subquery_parameters=get_data_requests_subquery_params(),
        build_metadata=build_metadata,
        limit=dto.limit,
    )
    return data_requests
