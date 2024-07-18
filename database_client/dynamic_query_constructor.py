import uuid
from collections import namedtuple
from datetime import datetime
from typing import Optional

from psycopg2 import sql

from database_client.constants import (
    AGENCY_APPROVED_COLUMNS,
    DATA_SOURCES_APPROVED_COLUMNS,
    RESTRICTED_DATA_SOURCE_COLUMNS,
    RESTRICTED_COLUMNS,
)

TableColumn = namedtuple("TableColumn", ["table", "column"])
TableColumnAlias = namedtuple("TableColumnAlias", ["table", "column", "alias"])


class DynamicQueryConstructor:
    """
    This is a class for constructing more complex queries
    where writing out the entire query is either impractical or unfeasible.
    Coupled with the DatabaseClient class, which utilizes the queries constructed here
    """

    @staticmethod
    def build_fields(
        columns_only: list[TableColumn],
        columns_and_alias: Optional[list[TableColumnAlias]] = None,
    ):
        # Process columns without alias
        fields_only = [
            sql.SQL("{}.{}").format(sql.Identifier(table), sql.Identifier(column))
            for table, column in columns_only
        ]

        if columns_and_alias:
            # Process columns with alias
            fields_with_alias = [
                sql.SQL("{}.{} AS {}").format(
                    sql.Identifier(col.table),
                    sql.Identifier(col.column),
                    sql.Identifier(col.alias),
                )
                for col in columns_and_alias
            ]
        else:
            fields_with_alias = []

        # Combine both lists
        all_fields = fields_only + fields_with_alias

        # Join fields to create the final fields SQL
        fields_sql = sql.SQL(", ").join(all_fields)

        return fields_sql

    @staticmethod
    def create_table_columns(table: str, columns: list[str]) -> list[TableColumn]:
        return [TableColumn(table, column) for column in columns]

    @staticmethod
    def build_get_approved_data_sources_query() -> sql.Composed:
        data_sources_columns = DynamicQueryConstructor.create_table_columns(
            table="data_sources", columns=DATA_SOURCES_APPROVED_COLUMNS
        )

        fields = DynamicQueryConstructor.build_fields(
            columns_only=data_sources_columns,
            columns_and_alias=[
                TableColumnAlias(table="agencies", column="name", alias="agency_name")
            ],
        )
        sql_query = sql.SQL(
            """
            SELECT
                {fields}
            FROM
                agency_source_link
            INNER JOIN
                data_sources ON agency_source_link.airtable_uid = data_sources.airtable_uid
            INNER JOIN
                agencies ON agency_source_link.agency_described_linked_uid = agencies.airtable_uid
            WHERE
                data_sources.approval_status = 'approved'
        """
        ).format(fields=fields)
        return sql_query

    @staticmethod
    def build_data_source_by_id_results_query() -> sql.Composed:
        data_sources_columns = DynamicQueryConstructor.create_table_columns(
            table="data_sources", columns=DATA_SOURCES_APPROVED_COLUMNS
        )
        agencies_approved_columns = DynamicQueryConstructor.create_table_columns(
            table="agencies", columns=AGENCY_APPROVED_COLUMNS
        )
        alias_columns = [
            TableColumnAlias(table="agencies", column="name", alias="agency_name"),
            TableColumnAlias(
                table="agencies", column="airtable_uid", alias="agency_id"
            ),
            TableColumnAlias(
                table="data_sources", column="airtable_uid", alias="data_source_id"
            ),
        ]
        fields = DynamicQueryConstructor.build_fields(
            columns_only=data_sources_columns + agencies_approved_columns,
            columns_and_alias=alias_columns,
        )
        sql_query = sql.SQL(
            """
            SELECT
                {fields}
            FROM
                agency_source_link
            INNER JOIN
                data_sources ON agency_source_link.airtable_uid = data_sources.airtable_uid
            INNER JOIN
                agencies ON agency_source_link.agency_described_linked_uid = agencies.airtable_uid
            WHERE
                data_sources.approval_status = 'approved' AND data_sources.airtable_uid = %s
        """
        ).format(fields=fields)
        return sql_query

    @staticmethod
    def build_needs_identification_data_source_query():
        data_sources_columns = DynamicQueryConstructor.create_table_columns(
            table="data_sources", columns=DATA_SOURCES_APPROVED_COLUMNS
        )
        fields = DynamicQueryConstructor.build_fields(
            columns_only=data_sources_columns,
        )
        sql_query = sql.SQL(
            """
            SELECT
                {fields}
            FROM
                data_sources
            WHERE
                approval_status = 'needs identification'
        """
        ).format(fields=fields)
        return sql_query

    @staticmethod
    def zip_needs_identification_data_source_results(
        results: list[tuple],
    ) -> list[dict]:
        return [dict(zip(DATA_SOURCES_APPROVED_COLUMNS, result)) for result in results]

    @staticmethod
    def create_data_source_update_query(
        data: dict, data_source_id: str
    ) -> sql.Composed:
        """
        Creates a query to update a data source in the database.

        :param data: A dictionary containing the updated data source details.
        :param data_source_id: The ID of the data source to be updated.
        """
        data_to_update = []
        for key, value in data.items():
            if key in RESTRICTED_DATA_SOURCE_COLUMNS:
                continue
            data_to_update.append(
                sql.SQL("{} = {}").format(sql.Identifier(key), sql.Literal(value))
            )

        data_to_update_sql = sql.SQL(", ").join(data_to_update)

        query = sql.SQL(
            """
            UPDATE data_sources 
            SET {data_to_update}
            WHERE airtable_uid = {data_source_id}
        """
        ).format(
            data_to_update=data_to_update_sql,
            data_source_id=sql.Literal(data_source_id),
        )

        return query

    @staticmethod
    def create_new_data_source_query(data: dict) -> sql.Composed:
        """
        Creates a query to add a new data source to the database.

        :param data: A dictionary containing the data source details.
        """
        columns = []
        values = []
        for key, value in data.items():
            if key not in RESTRICTED_COLUMNS:
                columns.append(sql.Identifier(key))
                values.append(sql.Literal(value))

        now = datetime.now().strftime("%Y-%m-%d")
        airtable_uid = str(uuid.uuid4())

        columns.extend(
            [
                sql.Identifier("approval_status"),
                sql.Identifier("url_status"),
                sql.Identifier("data_source_created"),
                sql.Identifier("airtable_uid"),
            ]
        )
        values.extend(
            [
                sql.Literal(False),
                sql.Literal(["ok"]),
                sql.Literal(now),
                sql.Literal(airtable_uid),
            ]
        )

        query = sql.SQL("INSERT INTO data_sources ({}) VALUES ({}) RETURNING *").format(
            sql.SQL(", ").join(columns), sql.SQL(", ").join(values)
        )

        return query


    @staticmethod
    def generate_new_typeahead_suggestion_query(search_term: str):
        query = sql.SQL(
            """
        WITH combined AS (
            SELECT 
                1 AS sort_order,
                display_name,
                type,
                state,
                county,
                locality
            FROM typeahead_suggestions
            WHERE display_name ILIKE {search_term_prefix}
            UNION ALL
            SELECT
                2 AS sort_order,
                display_name,
                type,
                state,
                county,
                locality
            FROM typeahead_suggestions
            WHERE display_name ILIKE {search_term_anywhere}
            AND display_name NOT ILIKE {search_term_prefix}
        )
        SELECT DISTINCT 
            sort_order,
            display_name,
            type,
            state,
            county,
            locality
        FROM combined
        ORDER BY sort_order, display_name
        LIMIT 4;
        """
        ).format(
            search_term_prefix=sql.Literal(f"{search_term}%"),
            search_term_anywhere=sql.Literal(f"%{search_term}%"),
        )
        return query
