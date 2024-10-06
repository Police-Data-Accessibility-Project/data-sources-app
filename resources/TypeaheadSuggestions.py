from typing import Callable

from flask import Response

from config import limiter
from database_client.database_client import DatabaseClient
from middleware.primary_resource_logic.typeahead_suggestion_logic import (
    get_typeahead_results,
    TypeaheadLocationsOuterResponseSchema,
    TypeaheadAgenciesOuterResponseSchema,
)
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    TypeaheadSchema,
    TypeaheadDTO,
)
from middleware.schema_and_dto_logic.dynamic_schema_documentation_construction import (
    get_restx_param_documentation,
)
from middleware.schema_and_dto_logic.non_dto_dataclasses import SchemaPopulateParameters
from resources.PsycopgResource import handle_exceptions, PsycopgResource

from utilities.namespace import create_namespace, AppNamespaces

namespace_typeahead_suggestions = create_namespace(
    namespace_attributes=AppNamespaces.TYPEAHEAD
)

query_doc_info = get_restx_param_documentation(
    namespace=namespace_typeahead_suggestions,
    schema=TypeaheadSchema,
)

locations_doc_info = get_restx_param_documentation(
    namespace=namespace_typeahead_suggestions,
    schema=TypeaheadLocationsOuterResponseSchema,
)

agencies_doc_info = get_restx_param_documentation(
    namespace=namespace_typeahead_suggestions,
    schema=TypeaheadAgenciesOuterResponseSchema,
)


def get_typeahead_kwargs(db_client_method: Callable) -> dict:
    return {
        "wrapper_function": get_typeahead_results,
        "schema_populate_parameters": SchemaPopulateParameters(
            schema=TypeaheadSchema(),
            dto_class=TypeaheadDTO,
        ),
        "db_client_method": db_client_method,
    }


@namespace_typeahead_suggestions.route("/locations")
class TypeaheadLocations(PsycopgResource):

    @handle_exceptions
    @namespace_typeahead_suggestions.doc(
        description="Get suggestions for a typeahead query",
        expect=[query_doc_info.parser],
        responses={
            200: ("OK. Suggestions returned.", locations_doc_info.model),
            500: "Internal server error",
        },
    )
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
    @namespace_typeahead_suggestions.doc(
        description="Get suggestions for a typeahead query",
        expect=[query_doc_info.parser],
        responses={
            200: ("OK. Suggestions returned.", agencies_doc_info.model),
            500: "Internal server error",
        },
    )
    def get(self):
        return self.run_endpoint(
            **get_typeahead_kwargs(DatabaseClient.get_typeahead_agencies)
        )
