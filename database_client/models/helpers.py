from sqlalchemy import Column

from database_client.models.table_reference import SQL_ALCHEMY_TABLE_REFERENCE


def convert_to_column_reference(columns: list[str], relation: str) -> list[Column]:
    """Converts a list of column strings to SQLAlchemy column references.

    :param columns: List of column strings.
    :param relation: Relation string.
    :return:
    """
    try:
        relation_reference = SQL_ALCHEMY_TABLE_REFERENCE[relation]
    except KeyError:
        raise ValueError(
            f"SQL Model does not exist in SQL_ALCHEMY_TABLE_REFERENCE: {relation}"
        )

    def get_attribute(column: str) -> Column:
        try:
            return getattr(relation_reference, column)
        except AttributeError:
            raise AttributeError(
                f'Column "{column}" does not exist in SQLAlchemy Table Model for "{relation}"'
            )

    return [get_attribute(column) for column in columns]
