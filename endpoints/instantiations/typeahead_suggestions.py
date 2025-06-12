from typing import Callable

from flask import Response

from config import limiter
from db.client.core import DatabaseClient
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.security.auth.info.instantiations import NO_AUTH_INFO
from middleware.decorators.decorators import endpoint_info
from middleware.primary_resource_logic.typeahead_suggestion import (
    get_typeahead_results,
)
from middleware.schema_and_dto.schemas.typeahead.request import (
    TypeaheadQuerySchema,
)
from middleware.schema_and_dto.dtos.typeahead import TypeaheadDTO
from middleware.schema_and_dto.non_dto_dataclasses import SchemaPopulateParameters
from endpoints.psycopg_resource import PsycopgResource
from endpoints.schema_config.enums import SchemaConfigs
from endpoints._helpers.response_info import ResponseInfo

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
