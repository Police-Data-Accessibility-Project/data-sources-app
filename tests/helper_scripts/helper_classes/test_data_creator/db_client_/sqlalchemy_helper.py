from sqlalchemy import delete, select, and_

from db.client.core import DatabaseClient
from db.models.implementations.core.notification.queue.data_request import (
    DataRequestUserNotificationQueue,
)
from db.models.implementations.core.notification.queue.data_source import (
    DataSourceUserNotificationQueue,
)
from db.models.table_reference import SQL_ALCHEMY_TABLE_REFERENCE
from middleware.enums import Relations


class TDCSQLAlchemyHelper:

    def __init__(self):
        self.db_client = DatabaseClient()

    def delete_like(
        self,
        table_name: str,
        like_column_name: str,
        like_text: str,
    ):
        table = SQL_ALCHEMY_TABLE_REFERENCE[table_name]
        column = getattr(table, like_column_name)
        query = delete(table).where(column.like(like_text))
        self.db_client.execute_sqlalchemy(lambda: query)

    def get_county_id(self, county_name: str, state_iso: str = "PA") -> int:
        state_id = self.get_state_id(state_iso=state_iso)
        table = SQL_ALCHEMY_TABLE_REFERENCE[Relations.COUNTIES.value]
        state_id_column = getattr(table, "state_id")
        county_name_column = getattr(table, "name")
        county_id_column = getattr(table, "id")
        query = select(county_id_column).where(
            and_(county_name_column == county_name, state_id_column == state_id)
        )
        result = self.db_client.execute_sqlalchemy(lambda: query)
        return [row[0] for row in result][0]

    def get_state_id(self, state_iso: str) -> int:
        table = SQL_ALCHEMY_TABLE_REFERENCE[Relations.US_STATES.value]
        column_name = getattr(table, "state_iso")
        column_id = getattr(table, "id")
        query = select(column_id).where(column_name == state_iso)
        result = self.db_client.execute_sqlalchemy(lambda: query)
        results = [result[0] for result in result]
        if len(results) == 0:
            raise Exception(f"Could not find state with iso {state_iso}")
        return results[0]
