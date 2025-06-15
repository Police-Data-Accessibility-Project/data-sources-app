from psycopg import sql

from middleware.enums import Relations


def get_columns_for_relation_query(relation: Relations) -> str:
    return (
        sql.SQL(
            """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = {relation_name}
        """
        )
        .format(relation_name=sql.Literal(relation.value))
        .as_string()
    )
