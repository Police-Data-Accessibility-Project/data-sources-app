"""
Helper scripts for the Resource classes
"""
from http import HTTPStatus

from flask_restx import Namespace, Model, fields
from flask_restx.reqparse import RequestParser


def add_api_key_header_arg(parser: RequestParser):
    parser.add_argument(
        "Authorization",
        type=str,
        required=True,
        location="headers",
        help="API key required to access this endpoint",
        default="Basic YOUR_API_KEY",
    )


def add_jwt_header_arg(parser: RequestParser):
    parser.add_argument(
        "Authorization",
        type=str,
        required=True,
        location="headers",
        help="Access token required to access this endpoint",
        default="Bearer YOUR_ACCESS_TOKEN",
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


def create_id_and_message_model(namespace: Namespace) -> Model:
    return namespace.model(
        "IdAndMessage",
        {
            "id": fields.Integer(description="The id of the created entry"),
            "message": fields.String(
                description="The success message",
                example="Success. Entry created",
            ),
        },
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

def create_response_dictionary(success_message: str, success_model: Model = None) -> dict:
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
                description="Results for the county jurisdiction"
            ),
            "locality": fields.Nested(
                search_result_inner_wrapper_model,
                description="Results for the locality jurisdiction"
            ),
        }
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


def create_outer_model(namespace: Namespace, inner_model: Model, name: str) -> Model:
    return namespace.model(
        name,
        {
            "count": fields.Integer(
                required=True,
                description=f"Count of {inner_model.name} items",
                attribute="count",
            ),
            "data": fields.List(
                fields.Nested(
                    inner_model,
                    required=True,
                    description=f"List of {inner_model.name} items",
                ),
                attribute="data",
            ),
        },
    )
