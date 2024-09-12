from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Union

from flask import Response

from database_client.database_client import DatabaseClient
from database_client.enums import RelationRoleEnum
from middleware.access_logic import AccessInfo
from middleware.column_permission_logic import (
    RelationRoleParameters,
    check_has_permission_to_edit_columns,
)


@dataclass
class MiddlewareParameters:
    """
    Contains parameters for the middleware functions
    """

    access_info: AccessInfo
    relation: str
    db_client_method: callable
    db_client: DatabaseClient = DatabaseClient()
    # Additional arguments for the Database Client method beyond those provided in the given method
    db_client_additional_args: dict = field(default_factory=dict)
    entry_name: str = "entry"


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


class PutPostBase(ABC):

    def __init__(
        self,
        middleware_parameters: MiddlewareParameters,
        entry: dict,
        relation_role_parameters: RelationRoleParameters = RelationRoleParameters(),
    ):
        self.mp = middleware_parameters
        self.entry = entry
        self.relation_role_parameters = relation_role_parameters

    def pre_database_client_method_logic(self):
        pass

    @abstractmethod
    def call_database_client_method(self):
        raise NotImplementedError

    def check_for_permission(self, relation_role: RelationRoleEnum):
        check_has_permission_to_edit_columns(
            db_client=self.mp.db_client,
            relation=self.mp.relation,
            role=relation_role,
            columns=list(self.entry.keys()),
        )

    @abstractmethod
    def make_response(self) -> Response:
        raise NotImplementedError

    def execute(self) -> Response:

        relation_role = self.relation_role_parameters.get_relation_role_from_parameters(
            access_info=self.mp.access_info
        )
        self.check_for_permission(relation_role)
        self.pre_database_client_method_logic()
        self.call_database_client_method()
        return self.make_response()

