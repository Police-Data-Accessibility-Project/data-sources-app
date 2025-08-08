from unittest.mock import MagicMock

from tests.helpers.DynamicMagicMock import DynamicMagicMock


class GetAPIKeyFromRequestHeaderMock(DynamicMagicMock):
    get_authorization_header_from_request: MagicMock
    get_api_key_from_authorization_header: MagicMock
