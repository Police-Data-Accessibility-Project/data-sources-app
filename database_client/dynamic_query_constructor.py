import uuid
from collections import namedtuple
from datetime import datetime
from typing import Callable, Optional

from psycopg import sql
from sqlalchemy import select
from sqlalchemy.schema import Column
from sqlalchemy.sql.expression import UnaryExpression

from database_client.constants import (
    AGENCY_APPROVED_COLUMNS,
    DATA_SOURCES_APPROVED_COLUMNS,
    ARCHIVE_INFO_APPROVED_COLUMNS,
    RESTRICTED_DATA_SOURCE_COLUMNS,
    RESTRICTED_COLUMNS,
)
from database_client.db_client_dataclasses import OrderByParameters
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
                agencies.state_iso,
                agencies.jurisdiction_type
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
        where_subclauses = [
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

            record_type_str_list = [
                [record_type.value for record_type in record_categories]
            ]
            where_subclauses.append(
                sql.SQL("record_categories.name = ANY({record_types})").format(
                    record_types=sql.Literal(record_type_str_list)
                )
            )

        if county is not None:
            where_subclauses.append(
                sql.SQL("LOWER(counties.name) = LOWER({county_name})").format(
                    county_name=sql.Literal(county)
                )
            )

        if locality is not None:
            where_subclauses.append(
                sql.SQL("LOWER(agencies.municipality) = LOWER({locality})").format(
                    locality=sql.Literal(locality)
                )
            )

        query = sql.Composed(
            [
                base_query,
                sql.SQL(" ").join(join_conditions),
                DynamicQueryConstructor.build_full_where_clause(where_subclauses),
            ]
        )

        return query

    @staticmethod
    def create_update_query(
        table_name: str,
        id_value: int,
        column_edit_mappings: dict[str, str],
        id_column_name: str,
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
                column=sql.Identifier(column_name), value=sql.Literal(column_value)
            )
            for column_name, column_value in column_edit_mappings.items()
        ]

        # Combine the base query with the assignments
        query = base_query + sql.SQL(", ").join(assignments)

        # Add the WHERE clause to specify the entry to update
        query += sql.SQL(" WHERE {id_column} = {id_value}").format(
            id_column=sql.Identifier(id_column_name), id_value=sql.Literal(id_value)
        )

        return query

    @staticmethod
    def create_insert_query(
        table_name: str,
        column_value_mappings: dict[str, str],
        column_to_return: Optional[str] = None,
    ) -> sql.Composed:
        """
        Dynamically constructs an insert query based on the provided mappings
        :param table_name: Name of the table to insert into
        :param column_value_mappings: A dictionary mapping column names to their values
        :return: A composed SQL query ready for execution
        """

        # Start with the base insert query
        base_query = sql.SQL("INSERT INTO {table} ").format(
            table=sql.Identifier(table_name)
        )

        # Generate the column assignments
        columns = sql.SQL(", ").join(
            [
                sql.Identifier(column_name)
                for column_name in column_value_mappings.keys()
            ]
        )

        # Generate the value assignments
        values = sql.SQL(", ").join(
            [
                sql.Literal(column_value)
                for column_value in column_value_mappings.values()
            ]
        )

        # Combine the base query with the assignments
        query = base_query + sql.SQL("({columns}) VALUES ({values})").format(
            columns=columns, values=values
        )

        if column_to_return is not None:
            query += sql.SQL(" RETURNING {column_to_return}").format(
                column_to_return=sql.Identifier(column_to_return)
            )

        return query

    @staticmethod
    def build_full_where_clause(where_subclauses: list[sql.Composed]) -> sql.Composed:
        return sql.SQL(" WHERE ") + sql.SQL(" AND ").join(where_subclauses)

    @staticmethod
    def create_single_relation_selection_query(
        columns: list[Column],
        where_mappings: Optional[list[bool]] = [True],
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[UnaryExpression] = None,
    ) -> Callable:
        """
        Creates a SELECT query for a single relation (table or view)
        that selects the given columns with the given where mappings
        :param columns: List of database column references. Example: [User.name, User.email]
        :param where_mappings: List of booleans for conditional selection.
        :param limit:
        :param offset:
        :param order_by: Database column reference with SQLAlchemy UnaryExpression determining order. Example: Agency.name.desc()
        :return:
        """
        base_query = (
            lambda: select(*columns)
            .where(*where_mappings)
            .order_by(order_by)
            .limit(limit)
            .offset(offset)
        )
        return base_query

    @staticmethod
    def build_where_subclauses_from_mappings(not_where_mappings, where_mappings):
        where_clauses = []
        if where_mappings is not None:
            # Create list of where clauses
            where_clauses.extend(
                DynamicQueryConstructor.get_where_eq_clauses(where_mappings)
            )
        if not_where_mappings is not None:
            # Create list of not where clauses
            where_clauses.extend(
                DynamicQueryConstructor.get_where_neq_clauses(not_where_mappings)
            )
        return where_clauses

    @staticmethod
    def get_offset_clause(offset):
        return sql.SQL(" OFFSET {offset}").format(offset=sql.Literal(offset))

    @staticmethod
    def get_limit_clause(limit):
        return sql.SQL(" LIMIT {limit}").format(limit=sql.Literal(limit))

    @staticmethod
    def get_where_neq_clauses(not_where_mappings):
        where_neq_clauses = [
            sql.SQL(" ({column} != {value} or {column} is null) ").format(
                column=sql.Identifier(column), value=sql.Literal(value)
            )
            for column, value in not_where_mappings.items()
        ]
        return where_neq_clauses

    @staticmethod
    def get_where_eq_clauses(where_mappings):
        where_eq_clauses = [
            sql.SQL(" {column} = {value} ").format(
                column=sql.Identifier(column), value=sql.Literal(value)
            )
            for column, value in where_mappings.items()
        ]
        return where_eq_clauses

    @staticmethod
    def get_select_clause(columns, relation):
        base_query = sql.SQL("SELECT {columns} FROM {relation}").format(
            columns=sql.SQL(", ").join([sql.Identifier(column) for column in columns]),
            relation=sql.Identifier(relation),
        )
        return base_query

    @staticmethod
    def get_column_permissions_as_permission_table_query(
        relation: str, relation_roles: list[str]
    ) -> sql.Composed:

        max_case_queries = []
        for role in relation_roles:
            max_case_query = sql.SQL(
                " MAX(CASE WHEN CP.relation_role = {role} THEN CP.ACCESS_PERMISSION ELSE NULL END) AS {role_alias} "
            ).format(role=sql.Literal(role), role_alias=sql.Identifier(role))
            max_case_queries.append(max_case_query)

        query = sql.SQL(
            """
        SELECT
            RC.ASSOCIATED_COLUMN,
            {max_case_queries}
        FROM
            PUBLIC.COLUMN_PERMISSION CP
        INNER JOIN PUBLIC.relation_column RC ON CP.rc_id = RC.id
        WHERE
            RC.relation = {relation}
        GROUP BY
            RC.ASSOCIATED_COLUMN, rc.id
        ORDER BY
            RC.id;
        
        """
        ).format(
            max_case_queries=sql.SQL(", ").join(max_case_queries),
            relation=sql.Literal(relation),
        )
        return query

    @staticmethod
    def get_order_by_clause(order_by: OrderByParameters):
        return sql.SQL(
            """
            ORDER BY {column} {order}
            """
        ).format(
            column=sql.Identifier(order_by.sort_by),
            order=sql.SQL(order_by.sort_order.value),
        )
