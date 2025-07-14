import uuid
from typing import Optional

import psycopg
from flask.testing import FlaskClient

from db.client.core import DatabaseClient
from db.enums import RequestUrgency
from middleware.enums import JurisdictionType, AgencyType
from middleware.schema_and_dto.schemas.agencies.info.post import (
    AgencyInfoPostSchema,
)
from tests.helper_scripts.common_test_data import get_test_name
from tests.helper_scripts.constants import (
    DATA_REQUESTS_BASE_ENDPOINT,
)
from tests.helper_scripts.helper_classes.SchemaTestDataGenerator import (
    generate_test_data_from_schema,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request
from tests.helper_scripts.test_dataclasses import TestDataRequestInfo


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
                "rejection_note": "Test rejection note",
                "approval_status": "rejected",
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
