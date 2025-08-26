from datetime import datetime

from db.client.core import DatabaseClient
from db.db_client_dataclasses import WhereMapping
from middleware.constants import DATETIME_FORMAT
from middleware.enums import Relations
from tests.helpers.helper_classes.test_data_creator.db_client_.core import TestDataCreatorDBClient


def test_update_last_cached(
    test_data_creator_db_client: TestDataCreatorDBClient,
    live_database_client: DatabaseClient,
):
    tdc = test_data_creator_db_client
    # Add a new data source to the database
    ds_info = tdc.data_source()
    # Update the data source's last_cached value with the DatabaseClient method
    new_last_cached = datetime.now().strftime(DATETIME_FORMAT)
    live_database_client.update_last_cached(
        data_source_id=ds_info.id, last_cached=new_last_cached
    )

    # Fetch the data source from the database to confirm the change
    result = live_database_client._select_from_relation(
        relation_name=Relations.DATA_SOURCES_ARCHIVE_INFO.value,
        columns=["last_cached"],
        where_mappings=[WhereMapping(column="data_source_id", value=ds_info.id)],
    )[0]

    assert result["last_cached"].strftime(DATETIME_FORMAT) == new_last_cached
