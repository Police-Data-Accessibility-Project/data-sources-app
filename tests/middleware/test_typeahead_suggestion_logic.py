from http import HTTPStatus
from unittest.mock import MagicMock

from database_client.database_client import DatabaseClient

from tests.helper_scripts.DynamicMagicMock import DynamicMagicMock


class GetTypeaheadSuggestionsMocks(DynamicMagicMock):
    get_typeahead_dict_results: MagicMock
    make_response: MagicMock

