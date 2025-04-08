"""
This contains common endpoint calls which are used across
multiple integration tests
"""

import uuid
from collections import namedtuple

from flask.testing import FlaskClient

from resources.endpoint_schema_config import SchemaConfigs
from tests.helper_scripts.common_test_data import get_test_name
from tests.helper_scripts.constants import DATA_SOURCES_BASE_ENDPOINT
from tests.helper_scripts.run_and_validate_request import run_and_validate_request

CreatedDataSource = namedtuple(
    "CreatedDataSource", [
        "id",
        "name",
        "url"
    ]
)
