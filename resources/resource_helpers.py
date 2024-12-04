"""
Helper scripts for the Resource classes
"""

from http import HTTPStatus
from typing import Optional

from flask_restx import Namespace, Model, fields
from flask_restx.reqparse import RequestParser

from middleware.argument_checking_logic import check_for_mutually_exclusive_arguments


def add_api_key_header_arg(parser: RequestParser):
    parser.add_argument(
        "Authorization",
        type=str,
        required=True,
        location="headers",
        help="API key required to access this endpoint",
        default="Basic YOUR_API_KEY",
    )


def add_jwt_header_arg(
    parser: RequestParser,
    description: str = "Access token required to access this endpoint",
    default_name: str = "YOUR_ACCESS_TOKEN",
):
    parser.add_argument(
        "Authorization",
        type=str,
        required=True,
        location="headers",
        help=description,
        default=f"Bearer {default_name}",
    )


def add_password_reset_token_header_arg(
    parser: RequestParser,
):
    add_jwt_header_arg(
        parser=parser,
        description="Password Reset token required to access this endpoint",
        default_name="Bearer YOUR_PASSWORD_RESET_TOKEN",
    )


def add_validate_email_header_arg(
    parser: RequestParser,
):
    add_jwt_header_arg(
        parser=parser,
        description="Email validation token required to access this endpoint",
        default_name="Bearer YOUR_EMAIL_VALIDATION_TOKEN",
    )


def add_jwt_or_api_key_header_arg(parser: RequestParser):
    parser.add_argument(
        "Authorization",
        type=str,
        required=True,
        location="headers",
        help="API key or access token required to access this endpoint",
        default="Basic YOUR_API_KEY OR Bearer YOUR_ACCESS_TOKEN",
    )


def create_variable_columns_model(namespace: Namespace, name_snake_case: str) -> Model:
    """
    Creates a generic model for an entry with variable columns
    :param namespace:
    :param name:
    :return:
    """
    name_split = name_snake_case.split("_")
    name_camelcase = "".join([split[0].upper() + split[1:] for split in name_split])

    return namespace.model(
        name_camelcase,
        {
            "column_1": fields.String("Value for first column"),
            "column_2": fields.String("Value for second column"),
            "column_etc": fields.String("And so on..."),
        },
    )


def create_response_dictionary(
    success_message: str, success_model: Model = None
) -> dict:
    success_msg = "Success. " + success_message

    if success_model is not None:
        success_val = success_msg, success_model
    else:
        success_val = success_msg

    return {
        HTTPStatus.OK: success_val,
        HTTPStatus.INTERNAL_SERVER_ERROR: "Internal server error.",
        HTTPStatus.BAD_REQUEST: "Bad request. Missing or bad authentication or parameters",
        HTTPStatus.FORBIDDEN: "Unauthorized. Forbidden or invalid authentication.",
    }


def column_permissions_description(
    head_description: str,
    column_permissions_str_table: str,
    sub_description: str = "",
) -> str:
    """
    Creates a formatted description for column permissions
    :param head_description:
    :param sub_description:
    :param column_permissions_str_table:
    :return:
    """
    return f"""
    {head_description}

{sub_description}

## COLUMN PERMISSIONS    

{column_permissions_str_table}

    """


class ResponseInfo:
    """
    A configuration dataclasses for defining common information in a response
    """

    def __init__(
        self,
        success_message: Optional[str] = None,
        response_dictionary: Optional[dict] = None,
    ):
        check_for_mutually_exclusive_arguments(
            arg1=success_message, arg2=response_dictionary
        )

        self.success_message = success_message
        self.response_dictionary = response_dictionary
