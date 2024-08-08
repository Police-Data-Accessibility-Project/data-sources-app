from flask import Response, request

from middleware.search_logic import search_wrapper
from middleware.security import api_required
from resources.PsycopgResource import PsycopgResource
from resources.resource_helpers import add_api_key_header_arg, create_search_model
from utilities.common import get_enums_from_string
from utilities.enums import RecordCategories
from utilities.namespace import create_namespace, AppNamespaces

namespace_search = create_namespace(namespace_attributes=AppNamespaces.SEARCH)

request_parser = namespace_search.parser()
add_api_key_header_arg(request_parser)
request_parser.add_argument(
    "state",
    type=str,
    location="args",
    required=True,
    help="The state of the search. Must be an exact match.",
)

request_parser.add_argument(
    "county",
    type=str,
    location="args",
    required=False,
    help="The county of the search. If empty, all counties for the given state will be searched. Must be an exact "
         "match.",
)

request_parser.add_argument(
    "locality",
    type=str,
    location="args",
    required=False,
    help="The locality of the search. If empty, all localities for the given county will be searched. Must be an "
         "exact match.",
)

request_parser.add_argument(
    "record_categories",
    type=str,
    location="args",
    required=False,
    help="The record categories of the search. If empty, all categories will be searched. Must be an exact match."
         "Allowable record categories include: " + ", ".join([e.value for e in RecordCategories]),
)
# TODO: Check that this description looks as expected.

search_model = create_search_model(namespace_search)


@namespace_search.route("/search-location-and-record-type")
class Search(PsycopgResource):
    """
    Provides a resource for performing searches in the database for data sources
    based on user-provided search terms and location.
    """

    @api_required
    @namespace_search.expect(request_parser)
    @namespace_search.response(200, "Success", search_model)
    @namespace_search.response(500, "Internal server error")
    @namespace_search.response(400, "Bad request; missing or bad API key")
    @namespace_search.response(403, "Forbidden; invalid API key")
    def get(self) -> Response:
        """
        Performs a search using the provided search terms and location.

        Performs a search using the provided record type and location parameters.
        It attempts to find relevant data sources in the database.

        Record Types:
        - "Police & Public Interactions"
        - "Info about Officers"
        - "Info about Agencies"
        - "Agency-published Resources"
        - "Jails & Courts"

        Source of truth for record types can be found at https://app.gitbook.com/o/-MXypK5ySzExtEzQU6se/s/-MXyolqTg_voOhFyAcr-/activities/data-dictionaries/record-types-taxonomy

        Returns:
        - A dictionary containing a message about the search results and the data found, if any.
        """
        state = request.args.get("state")
        county = request.args.get("county")
        locality = request.args.get("locality")
        record_category_raw = request.args.get("record_category")
        if record_category_raw is not None:
            record_categories = get_enums_from_string(
                RecordCategories,
                record_category_raw,
                case_insensitive=True
            )
        else:
            record_categories = None

        with self.setup_database_client() as db_client:
            response = search_wrapper(
                db_client=db_client,
                record_categories=record_categories,
                state=state,
                county=county,
                locality=locality,
            )
        return response
