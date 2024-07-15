from flask import Response
from flask_restx import fields

from middleware.security import api_required
from middleware.quick_search_query import quick_search_query_wrapper
from resources.DataSources import namespace_data_source

from utilities.namespace import create_namespace
from resources.PsycopgResource import PsycopgResource

namespace_quick_search = create_namespace()

data_item_model = namespace_quick_search.model('DataItem', {
    'airtable_uid': fields.String(required=True, description='Airtable UID of the record'),
    'agency_name': fields.String(description='Name of the agency'),
    'municipality': fields.String(description='Name of the municipality'),
    'state_iso': fields.String(description='ISO code of the state'),
    'data_source_name': fields.String(description='Name of the data source'),
    'description': fields.String(description='Description of the record'),
    'record_type': fields.String(description='Type of the record'),
    'source_url': fields.String(description='URL of the data source'),
    'record_format': fields.String(description='Format of the record'),
    'coverage_start': fields.String(description='Coverage start date'),
    'coverage_end': fields.String(description='Coverage end date'),
    'agency_supplied': fields.String(description='If the record is supplied by the agency')
})

# Define the main model
main_model = namespace_quick_search.model('MainModel', {
    'count': fields.Integer(required=True, description='Count of data items', attribute='count'),
    'data': fields.List(fields.Nested(data_item_model, required=True, description='List of data items'), attribute='data')
})

@namespace_quick_search.route("/quick-search/<search>/<location>")
class QuickSearch(PsycopgResource):
    """
    Provides a resource for performing quick searches in the database for data sources
    based on user-provided search terms and location.
    """

    # api_required decorator requires the request"s header to include an "Authorization" key with the value formatted as "Bearer [api_key]"
    # A user can get an API key by signing up and logging in (see User.py)
    @api_required
    @namespace_quick_search.response(200, "Success", main_model)
    @namespace_data_source.response(500, "Internal server error")
    @namespace_data_source.response(400, "Bad request; missing or bad API key")
    @namespace_data_source.response(403, "Forbidden; invalid API key")
    @namespace_data_source.doc(
        description="Retrieves all data sources needing identification.",
        security="apikey",
    )
    @namespace_quick_search.param(
        name="search",
        description="The search term provided by the user. Checks partial matches on any of the following properties on the data_source table: \"name\", \"description\", \"record_type\", and \"tags\". The search term is case insensitive and will match singular and pluralized versions of the term.",
        _in="path"
    )
    @namespace_quick_search.param(
        name="location",
        description="The location provided by the user. Checks partial matches on any of the following properties on the agencies table: \"county_name\", \"state_iso\", \"municipality\", \"agency_type\", \"jurisdiction_type\", \"name\"",
        _in="path"
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
        with self.setup_database_client() as db_client:
            response = quick_search_query_wrapper(search, location, db_client)
        return response
