from enum import Enum
from typing import Optional

from sqlalchemy import insert

from db.models.table_reference import SQL_ALCHEMY_TABLE_REFERENCE
from db.queries.builder import QueryBuilderBase


def update_dictionary_enum_values(d: dict):
    """
    Update a dictionary's values such that any which are enums are converted to the enum value
    Only works for flat, one-level dictionaries
    :param d:
    :return:
    """
    return {
        key: (value.value if isinstance(value, Enum) else value)
        for key, value in d.items()
    }


class CreateEntryInTableQueryBuilder(QueryBuilderBase):
    """
    Creates a new entry in a table in the database, using the provided column value mappings

    :param table_name: The name of the table to create an entry in.
    :param column_value_mappings: A dictionary mapping column names to their new values.
    """

    def __init__(
        self,
        table_name: str,
        column_value_mappings: dict[str, str],
        column_to_return: Optional[str] = None,
    ):
        super().__init__()
        self.table_name = table_name
        self.column_value_mappings = column_value_mappings
        self.column_to_return = column_to_return

    def run(self):

        column_value_mappings = update_dictionary_enum_values(
            self.column_value_mappings
        )
        table = SQL_ALCHEMY_TABLE_REFERENCE[self.table_name]
        statement = insert(table.__table__).values(**column_value_mappings)

        if self.column_to_return is not None:
            column = getattr(table, self.column_to_return)
            statement = statement.returning(column)
        result = self.session.execute(statement)

        if self.column_to_return is not None:
            return result.fetchone()[0]
        return None
