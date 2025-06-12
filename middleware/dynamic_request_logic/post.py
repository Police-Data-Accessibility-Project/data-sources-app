from http import HTTPStatus
from typing import Optional, Type, Any

import psycopg.errors
import sqlalchemy
from flask import Response
from werkzeug.exceptions import Conflict, BadRequest, InternalServerError

from middleware.column_permission_logic import (
    RelationRoleParameters,
)
from middleware.common_response_formatting import created_id_response
from middleware.custom_dataclasses import DeferredFunction
from middleware.dynamic_request_logic.supporting_classes import (
    MiddlewareParameters,
    PutPostBase,
    PostPutHandler,
    PutPostRequestInfo,
)


class PostHandler(PostPutHandler):

    def call_database_client_method(self, request: PutPostRequestInfo):
        """
        Runs the database client method
        and sets the request entry id in-place with the result
        """
        request.entry_id = self.mp.db_client_method(
            self.mp.db_client, column_value_mappings=request.entry
        )


class PostLogic(PutPostBase):

    def __init__(
        self,
        middleware_parameters: MiddlewareParameters,
        entry: dict,
        relation_role_parameters: RelationRoleParameters = RelationRoleParameters(),
        pre_database_client_method_with_parameters: Optional[DeferredFunction] = None,
        check_for_permission: bool = True,
    ):
        super().__init__(
            middleware_parameters=middleware_parameters,
            entry=entry,
            relation_role_parameters=relation_role_parameters,
            pre_database_client_method_with_parameters=pre_database_client_method_with_parameters,
            check_for_permission=check_for_permission,
        )
        self.id_val = None

    def call_database_client_method(self):
        try:
            self.id_val = self.mp.db_client_method(
                self.mp.db_client, column_value_mappings=self.entry
            )
        except sqlalchemy.exc.IntegrityError as e:
            if e.orig.sqlstate == "23505":
                raise Conflict(f"{self.mp.entry_name} already exists.")
            if e.orig.sqlstate == "23503":
                raise BadRequest(f"{self.mp.entry_name} not found.")
            raise InternalServerError(f"Error creating {self.mp.entry_name}.")

    def make_response(self) -> Response:
        return created_id_response(
            new_id=str(self.id_val), message=f"{self.mp.entry_name} created."
        )


def post_entry_with_handler(
    handler: PostHandler,
    dto: Any,
):
    request = PutPostRequestInfo(entry=dict(dto), dto=dto)
    handler.mass_execute([request])
    if request.error_message is not None:
        raise BadRequest(request.error_message)

    return created_id_response(
        new_id=str(request.entry_id), message=f"{handler.mp.entry_name} created."
    )


def post_entry(
    middleware_parameters: MiddlewareParameters,
    entry: dict,
    pre_insertion_function_with_parameters: Optional[DeferredFunction] = None,
    relation_role_parameters: RelationRoleParameters = RelationRoleParameters(),
    post_logic_class: Optional[Type[PostLogic]] = PostLogic,
    check_for_permission: bool = True,
    make_response: bool = True,
) -> Response:

    post_logic = post_logic_class(
        middleware_parameters=middleware_parameters,
        entry=entry,
        pre_database_client_method_with_parameters=pre_insertion_function_with_parameters,
        relation_role_parameters=relation_role_parameters,
        check_for_permission=check_for_permission,
    )
    return post_logic.execute(make_response=make_response)


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
        raise Conflict(f"{middleware_parameters.entry_name} ({entry}) already exists.")
