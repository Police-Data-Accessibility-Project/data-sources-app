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
    default_name: str = "YOUR_ACCESS_TOKEN"
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
        default_name="YOUR_PASSWORD_RESET_TOKEN",
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


def create_jwt_tokens_model(namespace: Namespace) -> Model:
    return namespace.model(
        "JWTTokens",
        {
            "access_token": fields.String(
                required=True, description="The access token of the user"
            ),
            "refresh_token": fields.String(
                required=True, description="The refresh token of the user"
            ),
        },
    )


def create_search_model(namespace: Namespace) -> Model:
    search_result_inner_model = namespace.model(
        "SearchResultInner",
        {
            "airtable_uid": fields.String(
                required=True, description="Airtable UID of the record"
            ),
            "agency_name": fields.String(description="Name of the agency"),
            "municipality": fields.String(description="Name of the municipality"),
            "state_iso": fields.String(description="ISO code of the state"),
            "data_source_name": fields.String(description="Name of the data source"),
            "description": fields.String(description="Description of the record"),
            "record_type": fields.String(description="Type of the record"),
            "source_url": fields.String(description="URL of the data source"),
            "record_format": fields.String(description="Format of the record"),
            "coverage_start": fields.String(description="Coverage start date"),
            "coverage_end": fields.String(description="Coverage end date"),
            "agency_supplied": fields.String(
                description="If the record is supplied by the agency"
            ),
            "jurisdiction_type": fields.String(
                description="Type of jursidiction for agency"
            ),
        },
    )

    search_result_inner_wrapper_model = namespace.model(
        "SearchResultInnerWrapper",
        {
            "count": fields.Integer(
                required=True,
                description="Count of SearchResultInnerWrapper items",
                attribute="count",
            ),
            "results": fields.List(
                fields.Nested(
                    search_result_inner_model,
                    description="List of results for the given jurisdiction",
                )
            ),
        },
    )

    search_result_jurisdictions_wrapper_model = namespace.model(
        name="SearchResultJurisdictionsWrapper",
        model={
            "federal": fields.Nested(
                search_result_inner_wrapper_model,
                description="Results for the federal jurisdiction",
            ),
            "state": fields.Nested(
                search_result_inner_wrapper_model,
                description="Results for the state jurisdiction",
            ),
            "county": fields.Nested(
                search_result_inner_wrapper_model,
                description="Results for the county jurisdiction",
            ),
            "locality": fields.Nested(
                search_result_inner_wrapper_model,
                description="Results for the locality jurisdiction",
            ),
        },
    )

    search_result_outer_model = namespace.model(
        "SearchResultOuter",
        {
            "count": fields.Integer(
                required=True,
                description="Count of SearchResultInner items",
                attribute="count",
            ),
            "data": fields.Nested(
                attribute="data",
                model=search_result_jurisdictions_wrapper_model,
            ),
        },
    )

    return search_result_outer_model


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
