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


def add_refresh_jwt_header_arg(
    parser: RequestParser,
):
    add_jwt_header_arg(
        parser=parser,
        description="Refresh token required to access this endpoint",
        default_name="YOUR_REFRESH_TOKEN",
    )


def add_password_reset_token_header_arg(
    parser: RequestParser,
):
    add_jwt_header_arg(
        parser=parser,
        description="Password Reset token required to access this endpoint",
        default_name="YOUR_PASSWORD_RESET_TOKEN",
    )


def add_validate_email_header_arg(
    parser: RequestParser,
):
    add_jwt_header_arg(
        parser=parser,
        description="Email validation token required to access this endpoint",
        default_name="YOUR_EMAIL_VALIDATION_TOKEN",
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
