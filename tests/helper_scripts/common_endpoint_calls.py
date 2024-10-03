"""
This contains common endpoint calls which are used across
multiple integration tests
"""
import uuid
from collections import namedtuple

from flask.testing import FlaskClient

from tests.helper_scripts.constants import DATA_SOURCES_BASE_ENDPOINT
from tests.helper_scripts.run_and_validate_request import run_and_validate_request

CreatedDataSource = namedtuple("CreatedDataSource", ["id", "name"])

def create_data_source_with_endpoint(
    flask_client: FlaskClient,
    jwt_authorization_header: dict,
) -> CreatedDataSource:
    """
    Creates a data source with the given endpoint
    :param flask_client:
    :param jwt_authorization_header:
    :return:
    """
    cds = CreatedDataSource(
        name=uuid.uuid4().hex,
        id=uuid.uuid4().hex,
    )
    json = run_and_validate_request(
        flask_client=flask_client,
        http_method="post",
        endpoint=DATA_SOURCES_BASE_ENDPOINT,
        headers=jwt_authorization_header,
        json={
            "entry_data": {
                "name": cds.name,
                "airtable_uid": cds.id,
                "source_url": "http://src1.com",
            }
        },
    )

    return cds
