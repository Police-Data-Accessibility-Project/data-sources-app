from flask import Response

from endpoints._helpers.response_info import ResponseInfo
from endpoints.instantiations.search.namespace import namespace_search
from endpoints.psycopg_resource import PsycopgResource
from endpoints.schema_config.enums import SchemaConfigs
from middleware.access_logic import AccessInfoPrimary
from middleware.authentication_info import API_OR_JWT_AUTH_INFO
from middleware.decorators import endpoint_info
from middleware.primary_resource_logic.search import federal_search_wrapper


@namespace_search.route("/federal")
class SearchFederal(PsycopgResource):
    """
    A resource for performing searches in the database for Federal-level data sources
    """

    @endpoint_info(
        namespace=namespace_search,
        auth_info=API_OR_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.SEARCH_FEDERAL_GET,
        response_info=ResponseInfo(success_message="Search successful."),
        description="Performs a search using the provided search terms and location.",
    )
    def get(self, access_info: AccessInfoPrimary) -> Response:
        return self.run_endpoint(
            wrapper_function=federal_search_wrapper,
            schema_populate_parameters=SchemaConfigs.SEARCH_FEDERAL_GET.value.get_schema_populate_parameters(),
            access_info=access_info,
        )
