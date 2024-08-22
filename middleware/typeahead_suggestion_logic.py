from http import HTTPStatus

from flask import Response, make_response

from database_client.database_client import DatabaseClient


def get_typeahead_dict_results(
    suggestions: list[DatabaseClient.TypeaheadSuggestions],
) -> list[dict]:
    return [suggestion._asdict() for suggestion in suggestions]


def get_typeahead_suggestions_wrapper(
    db_client: DatabaseClient, query: str
) -> Response:
    suggestions = db_client.get_typeahead_suggestions(query)
    dict_results = get_typeahead_dict_results(suggestions)
    return make_response({"suggestions": dict_results}, HTTPStatus.OK)
