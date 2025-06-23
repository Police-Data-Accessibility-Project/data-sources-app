"""Integration tests for /archives endpoint"""

import datetime

from db.enums import ApprovalStatus
from middleware.enums import Relations
from tests.helper_scripts.helper_classes.TestDataCreatorDBClient import (
    TestDataCreatorDBClient,
)
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)

from tests.helper_scripts.run_and_validate_request import run_and_validate_request
from tests.integration.test_check_database_health import wipe_database

ENDPOINT = "/api/archives"


def test_archives_get(
    test_data_creator_db_client: TestDataCreatorDBClient,
    test_data_creator_flask: TestDataCreatorFlask,
):
    """
    Test that GET call to /archives endpoint successfully retrieves a non-zero amount of data
    """
    tdc = test_data_creator_flask
    wipe_database(tdc.db_client)
    tus = tdc.standard_user()
    data_source_id = test_data_creator_db_client.data_source(
        approval_status=ApprovalStatus.APPROVED, source_url="http://example.com"
    ).id
    tdc.db_client._update_entry_in_table(
        table_name=Relations.DATA_SOURCES_ARCHIVE_INFO.value,
        entry_id=data_source_id,
        id_column_name="data_source_id",
        column_edit_mappings={
            "update_frequency": "Monthly",
            "last_cached": datetime.datetime(year=2020, month=3, day=4),
        },
    )
    response_json = tdc.request_validator.archives_get(
        headers=tus.api_authorization_header,
    )

    assert len(response_json) == 1, "Endpoint should return more than 0 results"
    assert response_json[0]["id"] is not None

    # Run test that filters on update frequency
    response_json = tdc.request_validator.archives_get(
        headers=tus.api_authorization_header,
        update_frequency="Monthly",
    )
    assert len(response_json) == 1, "Endpoint should return more than 0 results"

    response_json = tdc.request_validator.archives_get(
        headers=tus.api_authorization_header,
        update_frequency="Annually",
    )
    assert len(response_json) == 0

    # Run test that filters on update last archived before

    response_json = tdc.request_validator.archives_get(
        headers=tus.api_authorization_header,
        last_archived_before=datetime.datetime(year=2020, month=3, day=5),
    )
    assert len(response_json) == 1

    response_json = tdc.request_validator.archives_get(
        headers=tus.api_authorization_header,
        last_archived_before=datetime.datetime(year=2020, month=3, day=4),
    )
    assert len(response_json) == 0


def test_archives_put(
    test_data_creator_flask: TestDataCreatorFlask,
):
    """tes
    Test that PUT call to /archives endpoint successfully updates the data source with last_cached and broken_source_url_as_of fields
    """
    tdc = test_data_creator_flask
    data_source_id = tdc.data_source().id
    last_cached = datetime.datetime(year=2020, month=3, day=4)
    test_user_admin = tdc.get_admin_tus()

    test_user_admin.jwt_authorization_header["Content-Type"] = "application/json"
    run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="put",
        endpoint=ENDPOINT,
        headers=test_user_admin.jwt_authorization_header,
        json={
            "id": data_source_id,
            "last_cached": str(last_cached),
        },
    )

    row = tdc.db_client.execute_raw_sql(
        query="""
        SELECT last_cached, broken_source_url_as_of 
        FROM data_sources 
        INNER JOIN data_sources_archive_info ON data_sources.id = data_sources_archive_info.data_source_id 
        WHERE data_sources.id = %s
        """,
        vars_=(int(data_source_id),),
    )
    assert row[0]["last_cached"] == last_cached
    assert row[0]["broken_source_url_as_of"] is None
