"""
These include helpers for constructing models and parsers
That rely on schemas

They are isolated from other code to prevent circular imports.
"""

from flask_restx import Namespace, Model

from middleware.primary_resource_logic.user_queries import UserRequestSchema
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    EntryDataRequestSchema,
)
from middleware.schema_and_dto_logic.dynamic_schema_documentation_construction import (
    get_restx_param_documentation,
)
from middleware.schema_and_dto_logic.response_schemas import (
    IDAndMessageSchema,
    GetManyResponseSchema,
    EntryDataResponseSchema,
)


def create_user_model(namespace: Namespace) -> Model:
    doc_info = get_restx_param_documentation(
        namespace,
        UserRequestSchema,
        model_name="UserEmailAndPassword",
    )
    return doc_info.model


def create_entry_data_request_model(namespace: Namespace) -> Model:
    doc_info = get_restx_param_documentation(
        namespace,
        EntryDataRequestSchema,
    )
    return doc_info.model


def create_entry_data_response_model(
    namespace: Namespace, entry_data_response_schema=EntryDataResponseSchema
) -> Model:
    doc_info = get_restx_param_documentation(
        namespace,
        schema=entry_data_response_schema,
    )
    return doc_info.model


def create_id_and_message_model(namespace: Namespace) -> Model:
    doc_info = get_restx_param_documentation(
        namespace,
        IDAndMessageSchema,
    )
    return doc_info.model


def create_get_many_response_model(
    namespace: Namespace, get_many_response_schema=GetManyResponseSchema
) -> Model:
    doc_info = get_restx_param_documentation(
        namespace=namespace,
        schema=get_many_response_schema,
    )
    return doc_info.model


class CRUDModels:
    """
    A model that initializes and returns all standard models for CRUD operations
    """

    def __init__(
        self, namespace: Namespace, get_many_response_schema=GetManyResponseSchema
    ):
        self.entry_data_request_model = create_entry_data_request_model(namespace)
        self.entry_data_response_model = create_entry_data_response_model(namespace)
        self.id_and_message_model = create_id_and_message_model(namespace)
        self.get_many_response_model = create_get_many_response_model(
            namespace, get_many_response_schema
        )
