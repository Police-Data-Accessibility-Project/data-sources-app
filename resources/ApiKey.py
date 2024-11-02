from flask import Response
from flask_restx import fields

from middleware.primary_resource_logic.login_queries import create_api_key_for_user
from middleware.primary_resource_logic.user_queries import UserRequestDTO
from middleware.schema_and_dto_logic.dynamic_logic.model_helpers_with_schemas import (
    create_user_model,
)
from utilities.namespace import create_namespace, AppNamespaces

from resources.PsycopgResource import PsycopgResource, handle_exceptions
from utilities.enums import SourceMappingEnum
from middleware.schema_and_dto_logic.non_dto_dataclasses import DTOPopulateParameters

namespace_api_key = create_namespace(namespace_attributes=AppNamespaces.AUTH)

api_key_model = namespace_api_key.model(
    "ApiKey",
    {
        "api_key": fields.String(
            required=True,
            description="The generated API key",
            example="2bd77a1d7ef24a1dad3365b8a5c6994e",
        ),
    },
)

user = create_user_model(namespace_api_key)

API_KEY_ROUTE = "/api-key"


@namespace_api_key.route(API_KEY_ROUTE)
@namespace_api_key.expect(user)
@namespace_api_key.doc(
    description="Generates an API key for authenticated users.",
    responses={
        200: "Success",
        401: "Invalid email or password",
        500: "Internal server error.",
    },
)
class ApiKey(PsycopgResource):
    """Represents a resource for generating an API key for authenticated users."""

    @handle_exceptions
    @namespace_api_key.response(200, "Success", model=api_key_model)
    def post(self) -> Response:
        """
        Authenticates a user based on provided credentials and generates an API key.

        Reads the 'email' and 'password' from the JSON body of the request, validates the user,
        and if successful, generates and returns a new API key.

        If the email and password match a row in the database, a new API key is created using uuid.uuid4().hex, updated in for the matching user in the users table, and the API key is sent to the user.

        Returns:
        - dict: A dictionary containing the generated API key, or None if an error occurs.
        """
        return self.run_endpoint(
            wrapper_function=create_api_key_for_user,
            dto_populate_parameters=DTOPopulateParameters(
                source=SourceMappingEnum.JSON,
                dto_class=UserRequestDTO,
            ),
        )
