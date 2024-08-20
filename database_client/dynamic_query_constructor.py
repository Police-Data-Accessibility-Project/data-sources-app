import uuid
from collections import namedtuple
from datetime import datetime
from typing import Optional

from psycopg2 import sql

from database_client.constants import (
    AGENCY_APPROVED_COLUMNS,
    DATA_SOURCES_APPROVED_COLUMNS,
    ARCHIVE_INFO_APPROVED_COLUMNS,
    RESTRICTED_DATA_SOURCE_COLUMNS,
    RESTRICTED_COLUMNS,
)
from utilities.enums import RecordCategories

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
        archive_info_columns = DynamicQueryConstructor.create_table_columns(
            table="data_sources_archive_info", columns=ARCHIVE_INFO_APPROVED_COLUMNS
        )

        fields = DynamicQueryConstructor.build_fields(
            columns_only=data_sources_columns + archive_info_columns,
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
            INNER JOIN
                data_sources_archive_info ON data_sources.airtable_uid = data_sources_archive_info.airtable_uid
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
        archive_info_columns = DynamicQueryConstructor.create_table_columns(
            table="data_sources_archive_info", columns=ARCHIVE_INFO_APPROVED_COLUMNS
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
            columns_only=data_sources_columns
            + agencies_approved_columns
            + archive_info_columns,
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
            INNER JOIN
                data_sources_archive_info ON data_sources.airtable_uid = data_sources_archive_info.airtable_uid
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
        archive_info_columns = DynamicQueryConstructor.create_table_columns(
            table="data_sources_archive_info", columns=ARCHIVE_INFO_APPROVED_COLUMNS
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
            INNER JOIN
                data_sources_archive_info ON data_sources.airtable_uid = data_sources_archive_info.airtable_uid
            WHERE
                approval_status = 'needs identification'
        """
        ).format(fields=fields)
        return sql_query

    @staticmethod
    def zip_needs_identification_data_source_results(
        results: list[tuple],
    ) -> list[dict]:
        return [
            dict(
                zip(
                    DATA_SOURCES_APPROVED_COLUMNS + ARCHIVE_INFO_APPROVED_COLUMNS,
                    result,
                )
            )
            for result in results
        ]

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
        LIMIT 10;
        """
        ).format(
            search_term_prefix=sql.Literal(f"{search_term}%"),
            search_term_anywhere=sql.Literal(f"%{search_term}%"),
        )
        return query

    @staticmethod
    def create_search_query(
        state: str,
        record_categories: Optional[list[RecordCategories]] = None,
        county: Optional[str] = None,
        locality: Optional[str] = None,
    ) -> sql.Composed:

        base_query = sql.SQL(
            """
            SELECT
                data_sources.airtable_uid,
                data_sources.name AS data_source_name,
                data_sources.description,
                data_sources.record_type,
                data_sources.source_url,
                data_sources.record_format,
                data_sources.coverage_start,
                data_sources.coverage_end,
                data_sources.agency_supplied,
                agencies.name AS agency_name,
                agencies.municipality,
                agencies.state_iso
            FROM
                agency_source_link
            INNER JOIN
                data_sources ON agency_source_link.airtable_uid = data_sources.airtable_uid
            INNER JOIN
                agencies ON agency_source_link.agency_described_linked_uid = agencies.airtable_uid
            INNER JOIN
                state_names ON agencies.state_iso = state_names.state_iso
            INNER JOIN
                counties ON agencies.county_fips = counties.fips
        """
        )

        join_conditions = []
        where_conditions = [
            sql.SQL("LOWER(state_names.state_name) = LOWER({state_name})").format(
                state_name=sql.Literal(state)
            ),
            sql.SQL("data_sources.approval_status = 'approved'"),
            sql.SQL("data_sources.url_status NOT IN ('broken', 'none found')"),
        ]

        if record_categories is not None:
            join_conditions.append(
                sql.SQL(
                    """
                INNER JOIN
                    record_types ON data_sources.record_type_id = record_types.id
                INNER JOIN
                    record_categories ON record_types.category_id = record_categories.id
            """
                )
            )

            record_type_str_tup = tuple(
                [record_type.value for record_type in record_categories]
            )
            where_conditions.append(
                sql.SQL("record_categories.name in {record_types}").format(
                    record_types=sql.Literal(record_type_str_tup)
                )
            )

        if county is not None:
            where_conditions.append(
                sql.SQL("LOWER(counties.name) = LOWER({county_name})").format(
                    county_name=sql.Literal(county)
                )
            )

        if locality is not None:
            where_conditions.append(
                sql.SQL("LOWER(agencies.municipality) = LOWER({locality})").format(
                    locality=sql.Literal(locality)
                )
            )

        query = sql.Composed(
            [
                base_query,
                sql.SQL(" ").join(join_conditions),
                sql.SQL(" WHERE "),
                sql.SQL(" AND ").join(where_conditions),
            ]
        )

        return query

    @staticmethod
    def create_update_query(
        table_name: str,
        id_value: int,
        column_edit_mappings: dict[str, str],
        id_column_name: str
    ) -> sql.Composed:
        """
        Dynamically constructs an update query based on the provided mappings
        :param table_name: Name of the table to update
        :param id_value: The ID of the entry to update
        :param column_edit_mappings: A dictionary mapping column names to their new values
        :return: A composed SQL query ready for execution
        """

        # Start with the base update query
        base_query = sql.SQL("UPDATE {table} SET ").format(
            table=sql.Identifier(table_name)
        )

        # Generate the column assignments
        assignments = [
            sql.SQL("{column} = {value}").format(
                column=sql.Identifier(column_name),
                value=sql.Literal(column_value)
            )
            for column_name, column_value in column_edit_mappings.items()
        ]

        # Combine the base query with the assignments
        query = base_query + sql.SQL(", ").join(assignments)

        # Add the WHERE clause to specify the entry to update
        query += sql.SQL(" WHERE {id_column} = {id_value}").format(
            id_column=sql.Identifier(id_column_name),
            id_value=sql.Literal(id_value)
        )

        return query
