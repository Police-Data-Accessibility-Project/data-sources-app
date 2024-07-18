"""
Helper scripts for the Resource classes
"""

from flask_restx import Namespace, Model, fields
from flask_restx.reqparse import RequestParser


def add_api_key_header_arg(parser: RequestParser):
    parser.add_argument(
        "Authorization",
        type=str,
        required=True,
        location="headers",
        help="API key required to access this endpoint",
        default="Bearer YOUR_API_KEY",
    )


def create_user_model(namespace: Namespace) -> Model:
    return namespace.model(
        "User",
        {
            "email": fields.String(required=True, description="The email of the user"),
            "password": fields.String(
                required=True, description="The password of the user"
            ),
        },
    )
