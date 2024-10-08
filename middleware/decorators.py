from functools import wraps
from typing import Callable, Optional

from flask_restx import Namespace, Model
from flask_restx.reqparse import RequestParser
from marshmallow import Schema

from middleware.access_logic import get_authentication, AuthenticationInfo
from middleware.argument_checking_logic import check_for_mutually_exclusive_arguments
from middleware.enums import PermissionsEnum, AccessTypeEnum
from middleware.schema_and_dto_logic.dynamic_logic.dynamic_schema_documentation_construction import (
    get_restx_param_documentation,
)
from middleware.schema_and_dto_logic.non_dto_dataclasses import FlaskRestxDocInfo
from middleware.security import check_api_key, check_permissions
from resources.PsycopgResource import handle_exceptions
from resources.resource_helpers import (
    add_jwt_or_api_key_header_arg,
    add_jwt_header_arg,
    add_api_key_header_arg, ResponseInfo, create_response_dictionary, )
from resources.endpoint_schema_config import SchemaConfigs


def api_key_required(func):
    """
    The api_key_required decorator can be added to protect a route so that only authenticated users can access the information.
    To protect a route with this decorator, add @api_key_required on the line above a given route.
    The request header for a protected route must include an "Authorization" key with the value formatted as "Basic [api_key]".
    A user can get an API key by signing up and logging in.
    """

    @wraps(func)
    def decorator(*args, **kwargs):
        check_api_key()
        return func(*args, **kwargs)

    return decorator


def permissions_required(permissions: PermissionsEnum):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            check_permissions(permissions)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def authentication_required(
    allowed_access_methods: list[AccessTypeEnum],
    restrict_to_permissions: Optional[list[PermissionsEnum]] = None,
):
    """
    Checks if the user has access to the resource,
     and provides access info to the inner function

    Resource methods using this must include `access_info` in their kwargs.

    :param allowed_access_methods:
    :param restrict_to_permissions: Automatically abort if the user does not have the requisite permissions
    :return:
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            kwargs["access_info"] = get_authentication(
                allowed_access_methods, restrict_to_permissions
            )

            return func(*args, **kwargs)

        return wrapper

    return decorator


def endpoint_info(
    namespace: Namespace,
    auth_info: AuthenticationInfo,
    input_schema: Optional[Schema] = None,
    input_model: Optional[Model] = None,
    input_model_name: Optional[str] = None,
    **doc_kwargs
):
    """

    :param namespace: The namespace to add the endpoint to
    :param auth_info: info on how the endpoint is authenticated
    :param input_schema: info on the schema for the input. Mutually exclusive with input_schema
    :param input_model: info on the model for the input. Mutually exclusive with input_model
    :param doc_kwargs: Additional arguments for the endpoint's documentation
    :return:
    """

    # If input schema is defined, create parser and model using schema and namespace
    input_doc_info = _get_input_doc_info(
        namespace=namespace,
        input_schema=input_schema,
        input_model=input_model,
        input_model_name=input_model_name,
    )
    _add_auth_info_to_parser(auth_info=auth_info, parser=input_doc_info.parser)

    doc_kwargs["expect"] = [input_doc_info.model, input_doc_info.parser]

    def decorator(func: Callable):
        @wraps(func)
        @handle_exceptions
        @authentication_required(
            auth_info.allowed_access_methods, auth_info.restrict_to_permissions
        )
        @namespace.doc(**doc_kwargs)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator

def endpoint_info_2(
    namespace: Namespace,
    auth_info: AuthenticationInfo,
    schema_config: SchemaConfigs,
    response_info: ResponseInfo,
    **doc_kwargs
):
    # TODO: Replace original endpoint info with this, and rename to `endpoint_info`
    input_doc_info = get_restx_param_documentation(
        namespace=namespace,
        schema=schema_config.value.input_schema,
        model_name=f"{schema_config.name}_input",
    )
    _add_auth_info_to_parser(auth_info=auth_info, parser=input_doc_info.parser)

    _update_doc_kwargs(
        doc_kwargs,
        input_doc_info,
        namespace,
        response_info,
        schema_config.value.output_schema
    )

    def decorator(func: Callable):
        @wraps(func)
        @handle_exceptions
        @authentication_required(
            auth_info.allowed_access_methods, auth_info.restrict_to_permissions
        )
        @namespace.doc(**doc_kwargs)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def _update_doc_kwargs(
        doc_kwargs: dict,
        input_doc_info: FlaskRestxDocInfo,
        namespace: Namespace,
        response_info: ResponseInfo,
        output_schema: Schema
):
    if response_info.response_dictionary is None:
        output_model = _get_output_model(namespace, output_schema)
        doc_kwargs["responses"] = create_response_dictionary(
            success_message=response_info.success_message,
            success_model=output_model
        )
    else:
        doc_kwargs["responses"] = response_info.response_dictionary
    doc_kwargs["expect"] = [input_doc_info.model, input_doc_info.parser]


def _get_output_model(namespace: Namespace, output_schema: Schema) -> Optional[Model]:
    if output_schema is not None:
        return get_restx_param_documentation(
            namespace=namespace,
            schema=output_schema,
        ).model
    else:
        return None


def _add_auth_info_to_parser(auth_info: AuthenticationInfo, parser: RequestParser):
    # Depending on auth info, add authentication information to input parser
    jwt_allowed = AccessTypeEnum.JWT in auth_info.allowed_access_methods
    api_allowed = AccessTypeEnum.API_KEY in auth_info.allowed_access_methods

    if jwt_allowed and api_allowed:
        add_jwt_or_api_key_header_arg(parser)
    elif jwt_allowed:
        add_jwt_header_arg(parser)
    elif api_allowed:
        add_api_key_header_arg(parser)
    else:
        raise Exception("Must have at least one access method")


def _get_input_doc_info(
    namespace, input_schema, input_model=None, input_model_name: Optional[str] = None
) -> FlaskRestxDocInfo:
    check_for_mutually_exclusive_arguments(input_schema, input_model)
    if input_model is not None:
        return FlaskRestxDocInfo(
            model=input_model,
            parser=namespace.parser(),
        )
    if input_schema is None:
        return FlaskRestxDocInfo(
            model=None,
            parser=namespace.parser(),
        )

    # Assume input schema is defined
    return get_restx_param_documentation(
        namespace=namespace,
        schema=input_schema,
        model_name=(
            input_schema.__class__.__name__
            if input_model_name is None
            else input_model_name
        ),
    )
