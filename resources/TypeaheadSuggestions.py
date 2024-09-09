from typing import Callable

from flask import Response, request
from flask_restx import fields, reqparse

from config import limiter
from database_client.database_client import DatabaseClient
from middleware.primary_resource_logic.typeahead_suggestion_logic import (
    get_typeahead_results,
)
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    TypeaheadSchema,
    TypeaheadDTO,
)
from middleware.schema_and_dto_logic.non_dto_dataclasses import SchemaPopulateParameters
from resources.PsycopgResource import handle_exceptions, PsycopgResource
from resources.resource_helpers import create_outer_model

from utilities.namespace import create_namespace, AppNamespaces

namespace_typeahead_suggestions = create_namespace(
    namespace_attributes=AppNamespaces.TYPEAHEAD
)

request_parser = reqparse.RequestParser()
request_parser.add_argument(
    "query",
    type=str,
    location="args",
    required=True,
    help="The typeahead query to get suggestions for, such as `Pitts`",
)


typeahead_suggestions_inner_model = namespace_typeahead_suggestions.model(
    "TypeaheadSuggestionsInner",
    {
        "display_name": fields.String(
            required=True,
            description="The display name of the suggestion",
            example="Pittsburgh",
        ),
        "type": fields.String(
            required=True,
            description="The type of suggestion. Either `State`, `County` or `Locality`",
            example="Locality",
        ),
        "state": fields.String(
            required=True,
            description="The state of the suggestion",
            example="Pennsylvania",
        ),
        "county": fields.String(
            required=True,
            description="The county of the suggestion",
            example="Allegheny",
        ),
        "locality": fields.String(
            required=True,
            description="The locality of the suggestion",
            example="Pittsburgh",
        ),
    },
)

typeahead_suggestions_outer_model = create_outer_model(
    namespace_typeahead_suggestions,
    typeahead_suggestions_inner_model,
    "TypeaheadSuggestionsOuter",
)


def get_typeahead_kwargs(db_client_method: Callable) -> dict:
    return {
        "wrapper_function": get_typeahead_results,
        "schema_populate_parameters": SchemaPopulateParameters(
            schema_class=TypeaheadSchema,
            dto_class=TypeaheadDTO,
        ),
        "db_client_method": db_client_method,
    }


@namespace_typeahead_suggestions.route("/locations")
class TypeaheadLocations(PsycopgResource):

    @handle_exceptions
    @namespace_typeahead_suggestions.expect(request_parser)
    @namespace_typeahead_suggestions.response(
        200, "OK", typeahead_suggestions_outer_model
    )
    @namespace_typeahead_suggestions.response(500, "Internal server error")
    @limiter.limit("10/second")
    def get(self) -> Response:
        """
        Get suggestions for a typeahead query
        Queries the database for typeahead suggestions of locations

        **Returns**
            - a list of location suggestions
        """
        return self.run_endpoint(
            **get_typeahead_kwargs(DatabaseClient.get_typeahead_locations)
        )


@namespace_typeahead_suggestions.route("/agencies")
class TypeaheadAgencies(PsycopgResource):

    @handle_exceptions
    @limiter.limit("10/second")
    def get(self):
        return self.run_endpoint(
            **get_typeahead_kwargs(DatabaseClient.get_typeahead_agencies)
        )
