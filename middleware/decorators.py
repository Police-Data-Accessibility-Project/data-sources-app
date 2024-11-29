from functools import wraps
from http import HTTPStatus
from typing import Callable, Optional

from flask_restx import Namespace, Model
from flask_restx.reqparse import RequestParser
from marshmallow import Schema

from middleware.access_logic import (
    get_authentication,
    AuthenticationInfo,
    ParserDeterminator,
)
from middleware.argument_checking_logic import check_for_mutually_exclusive_arguments
from middleware.enums import PermissionsEnum, AccessTypeEnum
from middleware.schema_and_dto_logic.dynamic_logic.dynamic_schema_documentation_construction import (
    get_restx_param_documentation,
)
from middleware.schema_and_dto_logic.non_dto_dataclasses import FlaskRestxDocInfo
from middleware.security import check_permissions
from middleware.primary_resource_logic.api_key_logic import check_api_key
from resources.PsycopgResource import handle_exceptions
from resources.resource_helpers import (
    add_jwt_or_api_key_header_arg,
    add_jwt_header_arg,
    add_api_key_header_arg,
    ResponseInfo,
    create_response_dictionary,
    add_password_reset_token_header_arg,
    add_validate_email_header_arg,
)
from resources.endpoint_schema_config import SchemaConfigs, OutputSchemaManager


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
    no_auth: bool = False,
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
                allowed_access_methods, restrict_to_permissions, no_auth=no_auth
            )

            return func(*args, **kwargs)

        return wrapper

    return decorator


def endpoint_info(
    namespace: Namespace,
    auth_info: AuthenticationInfo,
    schema_config: SchemaConfigs,
    response_info: ResponseInfo,
    **doc_kwargs,
):
    """
    A more sophisticated form of `endpoint_info`, with more robust
    schema and response definition.
    Designed to eventually replace all instances of endpoint_info
    """
    if schema_config.value.input_schema is not None:
        input_doc_info = get_restx_param_documentation(
            namespace=namespace,
            schema=schema_config.value.input_schema,
            model_name=f"{schema_config.name}_{namespace.name}_input",
        )
    else:
        input_doc_info = FlaskRestxDocInfo(model=None, parser=namespace.parser())

    if input_doc_info is not None:
        _add_auth_info_to_parser(auth_info=auth_info, parser=input_doc_info.parser)

    _update_doc_kwargs(
        doc_kwargs=doc_kwargs,
        input_doc_info=input_doc_info,
        namespace=namespace,
        response_info=response_info,
        output_schema_manager=schema_config.value.output_schema_manager,
    )

    def decorator(func: Callable):
        @wraps(func)
        @handle_exceptions
        @authentication_required(
            allowed_access_methods=auth_info.allowed_access_methods,
            restrict_to_permissions=auth_info.restrict_to_permissions,
            no_auth=auth_info.no_auth,
        )
        @namespace.doc(**doc_kwargs)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def _update_doc_kwargs(
    doc_kwargs: dict,
    input_doc_info: Optional[FlaskRestxDocInfo],
    namespace: Namespace,
    response_info: ResponseInfo,
    output_schema_manager: OutputSchemaManager,
):
    _update_responses(
        doc_kwargs=doc_kwargs,
        namespace=namespace,
        response_info=response_info,
        output_schema_manager=output_schema_manager,
    )

    if input_doc_info is None:
        return
    doc_kwargs["expect"] = [input_doc_info.model, input_doc_info.parser]


def _update_responses(
    doc_kwargs: dict,
    namespace: Namespace,
    response_info: ResponseInfo,
    output_schema_manager: OutputSchemaManager,
):

    if response_info.response_dictionary is None:
        primary_output_model = _get_output_model(
            namespace=namespace,
            output_schema=output_schema_manager.get_output_schema(HTTPStatus.OK),
        )
        response_dictionary = create_response_dictionary(
            success_message=response_info.success_message,
            success_model=primary_output_model,
        )
    else:
        for status_code, schema in output_schema_manager.get_output_schemas().items():
            model = _get_output_model(namespace=namespace, output_schema=schema)

            if model is not None:
                response_info.response_dictionary[status_code] = (
                    response_info.response_dictionary[status_code],
                    model,
                )

        response_dictionary = response_info.response_dictionary

    doc_kwargs["responses"] = response_dictionary


def _get_output_model(namespace: Namespace, output_schema: Schema) -> Optional[Model]:
    if output_schema is not None:
        return get_restx_param_documentation(
            namespace=namespace,
            schema=output_schema,
            model_name=f"{namespace.name}_{output_schema.__class__.__name__}_output",
        ).model
    else:
        return None


ACCESS_TYPE_HEADER_ARG_FUNC_MAP = {
    AccessTypeEnum.JWT: add_jwt_header_arg,
    AccessTypeEnum.API_KEY: add_api_key_header_arg,
    AccessTypeEnum.RESET_PASSWORD: add_password_reset_token_header_arg,
    AccessTypeEnum.VALIDATE_EMAIL: add_validate_email_header_arg,
}


def _add_auth_info_to_parser(auth_info: AuthenticationInfo, parser: RequestParser):
    if auth_info.no_auth:
        return

    pd = ParserDeterminator(auth_info.allowed_access_methods)

    if pd.is_access_type_allowed(AccessTypeEnum.JWT) and pd.is_access_type_allowed(
        AccessTypeEnum.API_KEY
    ):
        add_jwt_or_api_key_header_arg(parser)
        return
    for access_type in auth_info.allowed_access_methods:
        header_arg_function = ACCESS_TYPE_HEADER_ARG_FUNC_MAP[access_type]
        header_arg_function(parser)
        return
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
