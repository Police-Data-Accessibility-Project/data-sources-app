from flask import Response, request

from middleware.search_logic import (
    search_wrapper,
    SearchRequests,
    transform_record_categories,
)
from middleware.decorators import api_key_required
from resources.PsycopgResource import PsycopgResource
from resources.resource_helpers import add_api_key_header_arg, create_search_model
from utilities.populate_dto_with_request_content import (
    populate_dto_with_request_content,
    SourceMappingEnum,
)
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
    help="The state of the search.",
)

request_parser.add_argument(
    "county",
    type=str,
    location="args",
    required=False,
    help="The county of the search. If empty, all counties for the given state will be searched.",
)

request_parser.add_argument(
    "locality",
    type=str,
    location="args",
    required=False,
    help="The locality of the search. If empty, all localities for the given county will be searched.",
)

request_parser.add_argument(
    "record_categories",
    type=str,
    location="args",
    required=False,
    help="The record categories of the search. If empty, all categories will be searched.\n"
    "Multiple record categories can be provided as a comma-separated list, eg. 'Police & Public Interactions,Agency-published Resources'.\n"
    "Allowable record categories include: \n  * "
    + "\n  * ".join([e.value for e in RecordCategories]),
)
# TODO: Check that this description looks as expected.

search_model = create_search_model(namespace_search)


@namespace_search.route("/search-location-and-record-type")
class Search(PsycopgResource):
    """
    Provides a resource for performing searches in the database for data sources
    based on user-provided search terms and location.
    """

    @api_key_required
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
        dto = populate_dto_with_request_content(
            object_class=SearchRequests,
            transformation_functions={"record_categories": transform_record_categories},
            source=SourceMappingEnum.ARGS,
        )
        with self.setup_database_client() as db_client:
            response = search_wrapper(db_client=db_client, dto=dto)
        return response
