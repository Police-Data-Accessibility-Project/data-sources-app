from typing import Sequence

from sqlalchemy import select, RowMapping

from db.models.implementations.core.permission import Permission
from db.queries.builder.core import QueryBuilderBase
from endpoints.v3.permissions.get.response import PermissionDescriptionMapping, GetPermissionListResponse


class GetPermissionMappingsQueryBuilder(QueryBuilderBase):

    def run(self) -> GetPermissionListResponse:
        query = (
            select(
                Permission.permission_name.label("permission"),
                Permission.description,
            )
        )
        mappings: Sequence[RowMapping] = self.mappings(query)
        description_mappings: list[PermissionDescriptionMapping] = [
            PermissionDescriptionMapping(**mapping)
            for mapping in mappings
        ]
        return GetPermissionListResponse(mappings=description_mappings)