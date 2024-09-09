from flask import Response

from middleware.column_permission_logic import RelationRoleParameters, check_has_permission_to_edit_columns
from middleware.common_response_formatting import message_response
from middleware.dynamic_request_logic.supporting_classes import MiddlewareParameters, PutPostBase


class PutLogic(PutPostBase):

    def __init__(
        self,
        middleware_parameters: MiddlewareParameters,
        entry: dict,
        entry_id: str,
        relation_role_parameters: RelationRoleParameters = RelationRoleParameters(),
    ):
        super().__init__(
            middleware_parameters=middleware_parameters,
            entry=entry,
            relation_role_parameters=relation_role_parameters,
        )
        self.entry_id = entry_id

    def call_database_client_method(self):
        self.mp.db_client_method(
            self.mp.db_client,
            column_edit_mappings=self.entry,
            entry_id=self.entry_id
        )

    def make_response(self) -> Response:
        return message_response(message=f"{self.mp.entry_name} updated.")

def put_entry(
    middleware_parameters: MiddlewareParameters,
    entry: dict,
    entry_id: str,
    relation_role_parameters: RelationRoleParameters = RelationRoleParameters(),
) -> Response:

    put_logic = PutLogic(
        middleware_parameters=middleware_parameters,
        entry=entry,
        entry_id=entry_id,
        relation_role_parameters=relation_role_parameters,
    )
    return put_logic.execute()

    # mp = middleware_parameters
    # relation_role = relation_role_parameters.get_relation_role_from_parameters(
    #     access_info=mp.access_info,
    # )
    # check_has_permission_to_edit_columns(
    #     db_client=mp.db_client,
    #     relation=mp.relation,
    #     role=relation_role,
    #     columns=list(entry.keys()),
    # )
    # mp.db_client_method(
    #     mp.db_client,
    #     column_edit_mappings=entry,
    #     entry_id=entry_id,
    # )
    # return message_response(message=f"{mp.entry_name} updated.")
