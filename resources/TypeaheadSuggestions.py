from flask import Response, request

from middleware.typeahead_suggestion_logic import get_typeahead_suggestions_wrapper
from resources.PsycopgResource import handle_exceptions, PsycopgResource


class TypeaheadSuggestions(PsycopgResource):

    @handle_exceptions
    def get(self) -> Response:
        data = request.get_json()
        with self.setup_database_client() as db_client:
            response = get_typeahead_suggestions_wrapper(db_client, data.get("query"))
        return response
