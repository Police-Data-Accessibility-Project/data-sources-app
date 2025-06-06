from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Union, Any

from flask import Response
from pydantic import BaseModel

from database_client.client import DatabaseClient
from database_client.enums import RelationRoleEnum
from database_client.subquery_logic import SubqueryParameters
from middleware.access_logic import AccessInfoPrimary
from middleware.column_permission_logic import (
    RelationRoleParameters,
    check_has_permission_to_edit_columns,
)
from middleware.custom_dataclasses import DeferredFunction
from middleware.util.dynamic import execute_if_not_none


@dataclass
class MiddlewareParameters:
    """
    Contains parameters for the middleware functions
    """

    relation: str
    db_client_method: callable
    access_info: Optional[AccessInfoPrimary] = None
    db_client: DatabaseClient = DatabaseClient()
    # Additional arguments for the Database Client method beyond those provided in the given method
    db_client_additional_args: dict = field(default_factory=dict)
    entry_name: str = "entry"
    subquery_parameters: list[SubqueryParameters] = field(default_factory=list)


class IDInfo:

    def __init__(
        self,
        id_column_name: str = "id",
        id_column_value: Optional[Union[str, int]] = None,
        additional_where_mappings: Optional[dict] = None,
    ):
        self.id_column_name = id_column_name
        self.where_mappings = additional_where_mappings or {}
        if id_column_value is not None:
            self.where_mappings[id_column_name] = id_column_value


class PutPostRequestInfo(BaseModel):
    """
    A DTO for the post/put request

    :param request_id: the id of the request
    :param entry: the entry information for the request
    :param entry_id: the id of the entry to be updated, OR the id of the entry created
    :param error_message: the error message, if any
    """

    request_id: int = 1
    entry: dict
    dto: Optional[Any] = None
    entry_id: Optional[int] = None
    error_message: Optional[str] = None


class BulkPostResponse(BaseModel):
    request_id: int = 1
    entry_id: Optional[int] = None
    error_message: Optional[str] = None


class PostPutHandler(ABC):

    def __init__(
        self,
        middleware_parameters: MiddlewareParameters,
    ):
        self.mp = middleware_parameters

    def pre_execute(self, request: PutPostRequestInfo):
        return

    @abstractmethod
    def call_database_client_method(self, request: PutPostRequestInfo):
        raise NotImplementedError

    def execute(
        self,
        request: PutPostRequestInfo,
    ):
        self.pre_execute(request=request)
        result = self.call_database_client_method(request=request)
        self.post_execute(request=request)
        return result

    def post_execute(self, request: PutPostRequestInfo):
        return

    def mass_execute(self, requests: list[PutPostRequestInfo]):
        for request in requests:
            try:
                self.execute(request=request)
            except Exception as e:
                request.error_message = str(e)


class PutPostBase(ABC):

    def __init__(
        self,
        middleware_parameters: MiddlewareParameters,
        entry: dict,
        relation_role_parameters: RelationRoleParameters = RelationRoleParameters(),
        pre_database_client_method_with_parameters: Optional[DeferredFunction] = None,
        check_for_permission: bool = True,
    ):
        self.mp = middleware_parameters
        self.entry = entry
        self.relation_role_parameters = relation_role_parameters
        self.pre_database_client_method_with_parameters = (
            pre_database_client_method_with_parameters
        )
        self.check_for_permission = check_for_permission

    def pre_database_client_method_logic(self):
        execute_if_not_none(self.pre_database_client_method_with_parameters)

    @abstractmethod
    def call_database_client_method(self):
        raise NotImplementedError

    def check_can_edit_columns(self, relation_role: RelationRoleEnum):
        check_has_permission_to_edit_columns(
            relation=self.mp.relation,
            role=relation_role,
            columns=list(self.entry.keys()),
        )

    @abstractmethod
    def make_response(self) -> Response:
        raise NotImplementedError

    def execute(self, make_response: bool = True) -> Response:
        if self.check_for_permission:
            relation_role = (
                self.relation_role_parameters.get_relation_role_from_parameters(
                    access_info=self.mp.access_info
                )
            )
            self.check_can_edit_columns(relation_role)
        self.pre_database_client_method_logic()
        self.call_database_client_method()
        self.post_database_client_method_logic()
        if make_response:
            return self.make_response()

    def post_database_client_method_logic(self):
        return
