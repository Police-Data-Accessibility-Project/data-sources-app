from flask import Response

from middleware.column_permission.relation_role_parameters import RelationRoleParameters
from middleware.common_response_formatting import message_response
from middleware.custom_dataclasses import DeferredFunction
from middleware.dynamic_request_logic.supporting_classes import (
    MiddlewareParameters,
    PutPostBase,
    PostPutHandler,
    PutPostRequestInfo,
)


class PutHandler(PostPutHandler):
    def call_database_client_method(self, request: PutPostRequestInfo):
        self.mp.db_client_method(
            self.mp.db_client,
            column_edit_mappings=request.entry,
            entry_id=request.entry_id,
        )


class PutLogic(PutPostBase):
    def __init__(
        self,
        middleware_parameters: MiddlewareParameters,
        entry: dict,
        entry_id: str,
        pre_database_client_method_with_parameters: DeferredFunction | None = None,
        relation_role_parameters: RelationRoleParameters = RelationRoleParameters(),
    ):
        super().__init__(
            middleware_parameters=middleware_parameters,
            entry=entry,
            relation_role_parameters=relation_role_parameters,
            pre_database_client_method_with_parameters=pre_database_client_method_with_parameters,
        )
        self.entry_id = entry_id

    def call_database_client_method(self):
        self.mp.db_client_method(
            self.mp.db_client, column_edit_mappings=self.entry, entry_id=self.entry_id
        )

    def make_response(self) -> Response:
        return message_response(message=f"{self.mp.entry_name} updated.")


def put_entry(
    middleware_parameters: MiddlewareParameters,
    entry: dict,
    entry_id: str,
    pre_update_method_with_parameters: DeferredFunction | None = None,
    relation_role_parameters: RelationRoleParameters = RelationRoleParameters(),
) -> Response:
    put_logic = PutLogic(
        middleware_parameters=middleware_parameters,
        entry=entry,
        entry_id=int(entry_id),
        relation_role_parameters=relation_role_parameters,
        pre_database_client_method_with_parameters=pre_update_method_with_parameters,
    )
    return put_logic.execute()
