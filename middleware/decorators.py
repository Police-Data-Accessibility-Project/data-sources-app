import functools
from functools import wraps
from typing import Callable, Optional, Any, Type

from flask_restx import Namespace, Model
from flask_restx.reqparse import RequestParser
from marshmallow import Schema

from middleware.access_logic import get_authentication, AuthenticationInfo
from middleware.argument_checking_logic import check_for_mutually_exclusive_arguments
from middleware.enums import PermissionsEnum, AccessTypeEnum
from middleware.schema_and_dto_logic.dynamic_schema_documentation_construction import (
    get_restx_param_documentation,
)
from middleware.schema_and_dto_logic.non_dto_dataclasses import FlaskRestxDocInfo
from middleware.security import check_api_key, check_permissions
from resources.PsycopgResource import handle_exceptions
from resources.resource_helpers import (
    add_jwt_or_api_key_header_arg,
    add_jwt_header_arg,
    add_api_key_header_arg,
)


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
    input_schema: Optional[Type[Schema]] = None,
    input_model: Optional[Model] = None,
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
    )
    _add_auth_info_to_parser(auth_info=auth_info, parser=input_doc_info.parser)

    doc_kwargs["expect"] = [input_doc_info.model, input_doc_info.parser]

    def decorator(func: Callable):
        @wraps(func)
        @handle_exceptions
        @authentication_required(auth_info.allowed_access_methods, auth_info.restrict_to_permissions)
        @namespace.doc(**doc_kwargs)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator



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


def _get_input_doc_info(namespace, input_schema, input_model=None) -> FlaskRestxDocInfo:
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
        schema_class=input_schema,
        model_name=input_schema.__name__,
    )
