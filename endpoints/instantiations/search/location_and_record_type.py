from flask import Response

from endpoints._helpers.response_info import ResponseInfo
from endpoints.instantiations.search.namespace import namespace_search
from endpoints.psycopg_resource import PsycopgResource
from endpoints.schema_config.enums import SchemaConfigs
from endpoints.schema_config.instantiations.search.location_and_record_type import (
    SearchLocationAndRecordTypeGetEndpointSchemaConfig,
)
from middleware.access_logic import AccessInfoPrimary
from middleware.authentication_info import API_OR_JWT_AUTH_INFO
from middleware.decorators import endpoint_info
from middleware.primary_resource_logic.search import search_wrapper


@namespace_search.route("/search-location-and-record-type")
class Search(PsycopgResource):
    """
    Provides a resource for performing searches in the database for data sources
    based on user-provided search terms and location.
    """

    @endpoint_info(
        namespace=namespace_search,
        auth_info=API_OR_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.SEARCH_LOCATION_AND_RECORD_TYPE_GET,
        response_info=ResponseInfo(success_message="Search successful."),
        description="Performs a search using the provided search terms and location.",
    )
    def get(self, access_info: AccessInfoPrimary) -> Response:
        """
        Performs a search using the provided search terms and location.

        Performs a search using the provided record type and location parameters.

        It attempts to find relevant data sources in the database.

        Source of truth for record types can be found at https://app.gitbook.com/o/-MXypK5ySzExtEzQU6se/s/-MXyolqTg_voOhFyAcr-/activities/data-dictionaries/record-types-taxonomy

        Returns:
        - A dictionary containing a message about the search results and the data found, if any.
        """
        return self.run_endpoint(
            wrapper_function=search_wrapper,
            access_info=access_info,
            schema_populate_parameters=SearchLocationAndRecordTypeGetEndpointSchemaConfig.get_schema_populate_parameters(),
        )
