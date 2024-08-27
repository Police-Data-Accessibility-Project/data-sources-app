from flask import Response
from flask_restx import fields

from middleware.decorators import api_key_required
from middleware.quick_search_query import quick_search_query_wrapper
from resources.DataSources import namespace_data_source
from resources.resource_helpers import add_api_key_header_arg, create_search_model

from utilities.namespace import create_namespace
from resources.PsycopgResource import PsycopgResource

namespace_quick_search = create_namespace()

search_result_outer_model = create_search_model(namespace_quick_search)

authorization_parser = namespace_quick_search.parser()
add_api_key_header_arg(authorization_parser)


@namespace_quick_search.route("/quick-search/<search>/<location>")
class QuickSearch(PsycopgResource):
    """
    Provides a resource for performing quick searches in the database for data sources
    based on user-provided search terms and location.
    """

    # api_required decorator requires the request"s header to include an "Authorization" key with the value formatted as "Bearer [api_key]"
    # A user can get an API key by signing up and logging in (see User.py)
    @api_key_required
    @namespace_quick_search.response(200, "Success", search_result_outer_model)
    @namespace_data_source.response(500, "Internal server error")
    @namespace_data_source.response(400, "Bad request; missing or bad API key")
    @namespace_data_source.response(403, "Forbidden; invalid API key")
    @namespace_data_source.doc(
        description="Retrieves all data sources needing identification.",
    )
    @namespace_quick_search.expect(authorization_parser)
    @namespace_quick_search.param(
        name="search",
        description='The search term provided by the user. Checks partial matches on any of the following properties on the data_source table: "name", "description", "record_type", and "tags". The search term is case insensitive and will match singular and pluralized versions of the term.',
        _in="path",
    )
    @namespace_quick_search.param(
        name="location",
        description='The location provided by the user. Checks partial matches on any of the following properties on the agencies table: "county_name", "state_iso", "municipality", "agency_type", "jurisdiction_type", "name"',
        _in="path",
    )
    def get(self, search: str, location: str) -> Response:
        """
        Performs a quick search using the provided search terms and location. It attempts to find relevant
        data sources in the database. If no results are found initially, it re-initializes the database
        connection and tries again.

        Parameters:
        - search (str): The search term provided by the user.
        - location (str): The location provided by the user.

        Returns:
        - A dictionary containing a message about the search results and the data found, if any.
        """
        return self.run_endpoint(quick_search_query_wrapper, arg1=search, arg2=location)

