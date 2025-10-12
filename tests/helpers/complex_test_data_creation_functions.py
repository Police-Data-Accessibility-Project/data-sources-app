import psycopg

from db.client.core import DatabaseClient


def create_data_source_entry_for_url_duplicate_checking(
    db_client: DatabaseClient,
) -> str:
    """
    Create an entry in `Data Sources` guaranteed to appear in the URL duplicate checking functionality
    :param db_client:
    :return:
    """
    submitted_name = "TEST URL DUPLICATE NAME"
    try:
        db_client._create_entry_in_table(
            table_name="data_sources",
            column_value_mappings={
                "name": submitted_name,
                "source_url": "https://duplicate-checker.com/",
            },
        )
        db_client.execute_raw_sql(
            """
            call refresh_distinct_source_urls();
        """
        )
    except psycopg.errors.UniqueViolation:
        pass  # Already added
    except Exception as e:
        # Rollback
        db_client.connection.rollback()
        raise e
