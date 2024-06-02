# The below line is required to bypass the api_required decorator,
# and must be positioned prior to other imports in order to work.
from unittest.mock import patch, MagicMock
patch("middleware.security.api_required", lambda x: x).start()