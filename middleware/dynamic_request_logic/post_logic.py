from http import HTTPStatus
from typing import Optional, Callable, Type

import psycopg.errors
from flask import Response

from middleware.column_permission_logic import (
    RelationRoleParameters,
)
from middleware.common_response_formatting import created_id_response
from middleware.custom_dataclasses import DeferredFunction
from middleware.dynamic_request_logic.supporting_classes import (
    MiddlewareParameters,
    PutPostBase,
)
from middleware.flask_response_manager import FlaskResponseManager
from middleware.util_dynamic import execute_if_not_none


class PostLogic(PutPostBase):

    def __init__(
        self,
        middleware_parameters: MiddlewareParameters,
        entry: dict,
        relation_role_parameters: RelationRoleParameters = RelationRoleParameters(),
        pre_database_client_method_with_parameters: Optional[DeferredFunction] = None,
    ):
        super().__init__(
            middleware_parameters=middleware_parameters,
            entry=entry,
            relation_role_parameters=relation_role_parameters,
            pre_database_client_method_with_parameters=pre_database_client_method_with_parameters,
        )
        self.id_val = None


    def call_database_client_method(self):
        try:
            self.id_val = self.mp.db_client_method(
                self.mp.db_client, column_value_mappings=self.entry
            )
        except psycopg.errors.UniqueViolation:
            FlaskResponseManager.abort(
                code=HTTPStatus.CONFLICT,
                message=f"{self.mp.entry_name} already exists.",
            )

    def make_response(self) -> Response:
        return created_id_response(
            new_id=str(self.id_val), message=f"{self.mp.entry_name} created."
        )


def post_entry(
    middleware_parameters: MiddlewareParameters,
    entry: dict,
    pre_insertion_function_with_parameters: Optional[DeferredFunction] = None,
    relation_role_parameters: RelationRoleParameters = RelationRoleParameters(),
    post_logic_class: Optional[Type[PostLogic]] = PostLogic,
) -> Response:

    post_logic = post_logic_class(
        middleware_parameters=middleware_parameters,
        entry=entry,
        pre_database_client_method_with_parameters=pre_insertion_function_with_parameters,
        relation_role_parameters=relation_role_parameters,
    )
    return post_logic.execute()


def try_to_add_entry(middleware_parameters: MiddlewareParameters, entry: dict) -> str:
    """
    Try to add an entry to the database, aborting if the entry already exists
    :param middleware_parameters:
    :param entry:
    :return:
    """
    try:
        return middleware_parameters.db_client_method(
            middleware_parameters.db_client, column_value_mappings=entry
        )
    except psycopg.errors.UniqueViolation:
        FlaskResponseManager.abort(
            code=HTTPStatus.CONFLICT,
            message=f"{middleware_parameters.entry_name} ({entry}) already exists.",
        )
