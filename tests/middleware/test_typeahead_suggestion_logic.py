from unittest.mock import MagicMock

from tests.helpers.DynamicMagicMock import DynamicMagicMock


class GetTypeaheadSuggestionsMocks(DynamicMagicMock):
    get_typeahead_dict_results: MagicMock
    make_response: MagicMock
