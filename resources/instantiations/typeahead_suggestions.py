from typing import Callable

from flask import Response

from config import limiter
from database_client.database_client import DatabaseClient
from middleware.access_logic import AccessInfoPrimary
from middleware.authentication_info import NO_AUTH_INFO
from middleware.decorators import endpoint_info
from middleware.primary_resource_logic.typeahead_suggestion_logic import (
    get_typeahead_results,
)
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    TypeaheadQuerySchema,
    TypeaheadDTO,
)
from middleware.schema_and_dto_logic.non_dto_dataclasses import SchemaPopulateParameters
from resources.PsycopgResource import PsycopgResource
from resources.endpoint_schema_config import SchemaConfigs
from resources.resource_helpers import ResponseInfo

from utilities.namespace import create_namespace, AppNamespaces

namespace_typeahead_suggestions = create_namespace(
    namespace_attributes=AppNamespaces.TYPEAHEAD
)


def get_typeahead_kwargs(db_client_method: Callable) -> dict:
    return {
        "wrapper_function": get_typeahead_results,
        "schema_populate_parameters": SchemaPopulateParameters(
            schema=TypeaheadQuerySchema(),
            dto_class=TypeaheadDTO,
        ),
        "db_client_method": db_client_method,
    }


@namespace_typeahead_suggestions.route("/locations")
class TypeaheadLocations(PsycopgResource):

    @endpoint_info(
        namespace=namespace_typeahead_suggestions,
        description="Get suggestions for a typeahead query",
        schema_config=SchemaConfigs.TYPEAHEAD_LOCATIONS,
        auth_info=NO_AUTH_INFO,
        response_info=ResponseInfo(
            response_dictionary={
                200: "OK. Suggestions returned.",
                500: "Internal server error",
            }
        ),
    )
    @limiter.limit("10/second")
    def get(self, access_info: AccessInfoPrimary) -> Response:
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

    @limiter.limit("10/second")
    @endpoint_info(
        namespace=namespace_typeahead_suggestions,
        description="Get suggestions for a typeahead query",
        schema_config=SchemaConfigs.TYPEAHEAD_AGENCIES,
        auth_info=NO_AUTH_INFO,
        response_info=ResponseInfo(
            response_dictionary={
                200: "OK. Suggestions returned.",
                500: "Internal server error",
            }
        ),
    )
    def get(self, access_info: AccessInfoPrimary) -> Response:
        return self.run_endpoint(
            **get_typeahead_kwargs(DatabaseClient.get_typeahead_agencies)
        )
