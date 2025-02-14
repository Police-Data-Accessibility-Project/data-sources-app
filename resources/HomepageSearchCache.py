from flask_restx import fields

from middleware.access_logic import AccessInfoPrimary
from middleware.decorators import authentication_required
from middleware.enums import AccessTypeEnum, PermissionsEnum
from middleware.primary_resource_logic.homepage_search_cache import (
    get_agencies_without_homepage_urls,
    update_search_cache,
    SearchCacheEntry,
)
from resources.PsycopgResource import PsycopgResource, handle_exceptions
from resources.resource_helpers import add_jwt_header_arg
from utilities.namespace import create_namespace
from utilities.enums import SourceMappingEnum
from middleware.schema_and_dto_logic.non_dto_dataclasses import DTOPopulateParameters

namespace_homepage_search_cache = create_namespace()

post_model = namespace_homepage_search_cache.model(
    "Update Search Cache",
    {
        "search_results": fields.List(
            fields.String,
            description="The list of search results to add to the cache",
        ),
        "agency_airtable_uid": fields.String(
            description="The Airtable UID of the agency",
        ),
    },
)
parser = namespace_homepage_search_cache.parser()
add_jwt_header_arg(parser)

get_result_model = namespace_homepage_search_cache.model(
    "Get Homepage Search Cache Result",
    {
        "submitted_name": fields.String(description="The submitted name of the agency"),
        "jurisdiction_type": fields.String(
            description="The jurisdiction type of the agency"
        ),
        "state_iso": fields.String(description="The ISO code of the state"),
        "municipality": fields.String(description="The municipality of the agency"),
        "county_name": fields.String(description="The name of the county"),
        "airtable_uid": fields.String(description="The Airtable UID of the agency"),
        "count_data_sources": fields.Integer(description="The count of data sources"),
        "no_web_presence": fields.Boolean(
            description="Indicates if the agency has no web presence"
        ),
    },
)


@namespace_homepage_search_cache.route("/homepage-search-cache")
class HomepageSearchCache(PsycopgResource):

    @handle_exceptions
    @authentication_required(
        allowed_access_methods=[AccessTypeEnum.JWT],
        restrict_to_permissions=[PermissionsEnum.DB_WRITE],
    )
    @namespace_homepage_search_cache.expect(parser)
    @namespace_homepage_search_cache.doc(
        description="Get agencies without homepage urls",
        responses={
            200: ("Success. Returns agencies without homepage urls.", get_result_model),
            500: "Internal server error.",
            403: "Unauthorized. Forbidden or an invalid API key.",
            400: "Bad request. Missing or bad API key",
        },
    )
    def get(self, access_info: AccessInfoPrimary):
        """
        Retrieve 100 agencies without homepage urls
        :return:
        """
        return self.run_endpoint(wrapper_function=get_agencies_without_homepage_urls)

    @handle_exceptions
    @authentication_required(
        allowed_access_methods=[AccessTypeEnum.JWT],
        restrict_to_permissions=[PermissionsEnum.DB_WRITE],
    )
    @namespace_homepage_search_cache.expect(parser, post_model)
    @namespace_homepage_search_cache.doc(
        description="Update search cache",
        responses={
            200: "Success. Search Cache Updated.",
            500: "Internal server error.",
            403: "Unauthorized. Forbidden or an invalid API key.",
            400: "Bad request. Missing or bad API key",
        },
    )
    def post(self, access_info: AccessInfoPrimary):
        """
        Update search cache
        :return:
        """
        return self.run_endpoint(
            wrapper_function=update_search_cache,
            dto_populate_parameters=DTOPopulateParameters(
                dto_class=SearchCacheEntry,
                source=SourceMappingEnum.JSON,
            ),
        )
