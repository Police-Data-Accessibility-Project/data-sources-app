from db.client.core import DatabaseClient
from db.enums import ApprovalStatus
from middleware.enums import Relations
from tests.helpers.helper_classes.test_data_creator.db_client_.core import TestDataCreatorDBClient


def test_get_data_sources_to_archive(
    test_data_creator_db_client: TestDataCreatorDBClient,
    live_database_client: DatabaseClient,
):
    data_source_id = test_data_creator_db_client.data_source(
        approval_status=ApprovalStatus.APPROVED
    ).id
    live_database_client._update_entry_in_table(
        table_name=Relations.DATA_SOURCES_ARCHIVE_INFO.value,
        entry_id=data_source_id,
        id_column_name="data_source_id",
        column_edit_mappings={
            "update_frequency": "Monthly",
        },
    )
    results = live_database_client.get_data_sources_to_archive()
    assert len(results) > 0
