from collections import namedtuple
from typing import Callable, Optional

from psycopg import sql
from sqlalchemy import select
from sqlalchemy.orm import load_only, InstrumentedAttribute, selectinload
from sqlalchemy.schema import Column

from database_client.db_client_dataclasses import (
    OrderByParameters,
    WhereMapping,
)
from database_client.models.implementations.core import (
    Agency,
    DataSourceExpanded,
    DataRequestExpanded,
)
from database_client.models.table_reference import (
    SQL_ALCHEMY_TABLE_REFERENCE,
    convert_to_column_reference,
)
from database_client.subquery_logic import SubqueryParameters
from middleware.enums import RecordTypes, Relations
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
    def agencies_get_load_options(
        requested_columns: Optional[list[str]] = None,
    ) -> list:
        load_options = [
            selectinload(Agency.data_sources).load_only(
                DataSourceExpanded.id, DataSourceExpanded.name
            ),
            selectinload(Agency.locations),
        ]

        if requested_columns is not None:
            column_references = convert_to_column_reference(
                columns=requested_columns, relation=Relations.AGENCIES.value
            )
            load_options.append(load_only(*column_references))

        return load_options

    @staticmethod
    def data_sources_get_load_options(
        data_sources_columns: list[str],
        data_requests_columns: list[str],
    ) -> list:
        load_options = [
            selectinload(DataSourceExpanded.agencies).selectinload(Agency.locations)
        ]

        data_sources_attributes = [
            getattr(DataSourceExpanded, column) for column in data_sources_columns
        ]
        load_options.append(load_only(*data_sources_attributes))

        data_requests_attributes = [
            getattr(DataRequestExpanded, column) for column in data_requests_columns
        ]
        load_options.append(
            selectinload(DataSourceExpanded.data_requests).load_only(
                *data_requests_attributes
            )
        )

        return load_options

    @staticmethod
    def get_sql_alchemy_order_by_clause(
        order_by: OrderByParameters, relation: str, default
    ):
        if order_by is not None:
            order_by_clause = order_by.build_order_by_clause(relation=relation)
        else:
            order_by_clause = default
        return order_by_clause

    @staticmethod
    def create_table_columns(table: str, columns: list[str]) -> list[TableColumn]:
        return [TableColumn(table, column) for column in columns]

    @staticmethod
    def generate_fuzzy_match_typeahead_locations_query(
        search_term: str,
    ) -> sql.Composed:
        query = sql.SQL(
            """
            SELECT 
                display_name,
                type,
                state_name,
                county_name,
                locality_name,
                location_id
            FROM typeahead_locations
            ORDER BY similarity(concat(locality_name, ' ', county_name, ' ', state_name), {search_term}) DESC
            LIMIT 10
            """
        ).format(search_term=sql.Literal(search_term))
        return query

    @staticmethod
    def generate_like_typeahead_locations_query(search_term: str) -> sql.Composed:
        query = sql.SQL(
            """
        WITH combined AS (
            SELECT 
                1 AS sort_order,
                display_name,
                type,
                state_name,
                county_name,
                locality_name,
                location_id
            FROM typeahead_locations
            WHERE search_name ILIKE {search_term_prefix}
            UNION ALL
            SELECT
                2 AS sort_order,
                display_name,
                type,
                state_name,
                county_name,
                locality_name,
                location_id
            FROM typeahead_locations
            WHERE search_name ILIKE {search_term_anywhere}
            AND search_name NOT ILIKE {search_term_prefix}
        )
        SELECT display_name, type, state_name, county_name, locality_name, location_id
        FROM (
            SELECT DISTINCT 
                sort_order,
                display_name,
                type,
                state_name,
                county_name,
                locality_name,
                location_id
            FROM combined
            ORDER BY sort_order, display_name
            LIMIT 10
        ) as results;
        """
        ).format(
            search_term_prefix=sql.Literal(f"{search_term}%"),
            search_term_anywhere=sql.Literal(f"%{search_term}%"),
        )
        return query

    @staticmethod
    def generate_new_typeahead_agencies_query(search_term: str):
        query = sql.SQL(
            """
        WITH combined AS (
            SELECT
                1 AS sort_order,
                id,
                name,
                jurisdiction_type,
                state_iso,
                municipality,
                county_name
            FROM typeahead_agencies
            WHERE name ILIKE {search_term}
            UNION ALL
            SELECT
                2 AS sort_order,
                id,
                name,
                jurisdiction_type,
                state_iso,
                municipality,
                county_name
            FROM typeahead_agencies
            WHERE name ILIKE {search_term_anywhere}
            AND name NOT ILIKE {search_term}
        )
        SELECT
            id,
            name as display_name,
            jurisdiction_type,
            state_iso,
            municipality as locality_name,
            county_name
        FROM (
            SELECT DISTINCT
                sort_order,
                id,
                name,
                jurisdiction_type,
                state_iso,
                municipality,
                county_name
            FROM combined
            ORDER BY sort_order, name
            LIMIT 10
        ) as results
        """
        ).format(
            search_term=sql.Literal(f"{search_term}%"),
            search_term_anywhere=sql.Literal(f"%{search_term}%"),
        )
        return query

    @staticmethod
    def create_federal_search_query(
        record_categories: Optional[list[RecordCategories]] = None,
        page: int = 1,
    ) -> sql.Composed:
        base_query = sql.SQL(
            """
            SELECT DISTINCT
                data_sources.id,
                data_sources.name AS data_source_name,
                data_sources.description,
                record_types.name AS record_type,
                data_sources.source_url,
                data_sources.record_formats,
                data_sources.coverage_start,
                data_sources.coverage_end,
                data_sources.agency_supplied,
                agencies.name AS agency_name,
                agencies.jurisdiction_type
            FROM
                LINK_AGENCIES_DATA_SOURCES AS agency_source_link
            INNER JOIN
                data_sources ON agency_source_link.data_source_id = data_sources.id
            INNER JOIN
                agencies ON agency_source_link.agency_id = agencies.id
            INNER JOIN 
                record_types on record_types.id = data_sources.record_type_id
            """
        )
        where_subclauses = [
            sql.SQL("agencies.jurisdiction_type = 'federal'"),
            sql.SQL("data_sources.approval_status = 'approved'"),
            sql.SQL("data_sources.url_status NOT IN ('broken', 'none found')"),
        ]

        if record_categories is not None:
            join_conditions = [
                sql.SQL(
                    """
                    INNER JOIN
                        record_categories ON record_types.category_id = record_categories.id
                    """
                )
            ]
            where_subclauses.append(
                sql.SQL("record_categories.name in ({record_categories})").format(
                    record_categories=sql.SQL(",").join(
                        sql.Literal(record_category.value)
                        for record_category in record_categories
                    )
                )
            )
        else:
            join_conditions = []

        query = sql.Composed(
            [
                base_query,
                sql.SQL(" ").join(join_conditions),
                DynamicQueryConstructor.build_full_where_clause(where_subclauses),
                sql.SQL("LIMIT 100 OFFSET {page}").format(
                    page=sql.Literal((page - 1) * 100)
                ),
            ]
        )

        return query

    @staticmethod
    def create_search_query(
        location_id: int,
        record_categories: Optional[list[RecordCategories]] = None,
        record_types: Optional[list[RecordTypes]] = None,
    ) -> sql.Composed:

        base_query = sql.SQL(
            """
            SELECT DISTINCT
                data_sources.id,
                data_sources.name AS data_source_name,
                data_sources.description,
                record_types.name AS record_type,
                data_sources.source_url,
                data_sources.record_formats,
                data_sources.coverage_start,
                data_sources.coverage_end,
                data_sources.agency_supplied,
                agencies.name AS agency_name,
                locations_expanded.locality_name as municipality,
                locations_expanded.state_iso,
                agencies.jurisdiction_type
            FROM
                LINK_AGENCIES_DATA_SOURCES AS agency_source_link
            INNER JOIN
                data_sources ON agency_source_link.data_source_id = data_sources.id
            INNER JOIN
                agencies ON agency_source_link.agency_id = agencies.id
            LEFT JOIN 
                link_agencies_locations LAL ON LAL.agency_id = agencies.id
            INNER JOIN
				locations_expanded on LAL.location_id = locations_expanded.id
            INNER JOIN 
                record_types on record_types.id = data_sources.record_type_id
            LEFT JOIN
                DEPENDENT_LOCATIONS DL1 ON DL1.DEPENDENT_LOCATION_ID = LOCATIONS_EXPANDED.ID
            LEFT JOIN 
                DEPENDENT_LOCATIONS DL2 ON DL2.PARENT_LOCATION_ID = LOCATIONS_EXPANDED.ID
        """
        )

        join_conditions = []
        where_subclauses = [
            sql.SQL(
                "(locations_expanded.id = {location_id} OR DL1.PARENT_LOCATION_ID = {location_id} OR DL2.DEPENDENT_LOCATION_ID = {location_id})"
            ).format(location_id=sql.Literal(location_id)),
            sql.SQL("data_sources.approval_status = 'approved'"),
            sql.SQL("data_sources.url_status NOT IN ('broken', 'none found')"),
        ]

        if record_categories is not None:
            join_conditions.append(
                sql.SQL(
                    """
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

        if record_types is not None:

            record_type_str_list = [[record_type.value for record_type in record_types]]
            where_subclauses.append(
                sql.SQL("record_types.name = ANY({record_types})").format(
                    record_types=sql.Literal(record_type_str_list)
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
    def build_full_where_clause(where_subclauses: list[sql.Composed]) -> sql.Composed:
        return sql.SQL(" WHERE ") + sql.SQL(" AND ").join(where_subclauses)

    @staticmethod
    def create_selection_query(
        relation: str,
        columns: list[Column],
        where_mappings: Optional[list[WhereMapping] | dict] = [True],
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[OrderByParameters] = None,
        subquery_parameters: Optional[list[SubqueryParameters]] = [],
        alias_mappings: Optional[dict[str, str]] = None,
    ) -> Callable:
        """
        Creates a SELECT query for a relation (table or view)
        that selects the given columns with the given where mappings
        :param columns: List of database column references. Example: [User.name, User.email]
        :param where_mappings: List of WhereMapping objects for conditional selection.
        :param limit:
        :param offset:
        :param order_by:
        :param subquery_parameters: List of SubqueryParameters objects for executing subqueries.
        :return:
        """
        if len(columns) == 0:
            raise ValueError("No columns provided")
        if type(where_mappings) == dict:
            where_mappings = [
                WhereMapping(
                    column=list(where_mappings.keys())[0],
                    value=list(where_mappings.values())[0],
                )
            ]
        if where_mappings != [True]:
            where_mappings = [
                mapping.build_where_clause(relation) for mapping in where_mappings
            ]
        if order_by is not None:
            order_by = order_by.build_order_by_clause(relation)
        load_options = []
        if subquery_parameters:
            for parameter in subquery_parameters:
                load_options.append(parameter.build_subquery_load_option(relation))
            load_options.append(load_only(*columns))
            primary_relation_columns = [SQL_ALCHEMY_TABLE_REFERENCE[relation]]
        else:
            primary_relation_columns = columns

        if alias_mappings is not None:
            primary_relation_columns = DynamicQueryConstructor.apply_alias_mappings(
                columns, alias_mappings
            )

        base_query = (
            lambda: select(*primary_relation_columns)
            .options(*load_options)
            .where(*where_mappings)
            .order_by(order_by)
            .limit(limit)
            .offset(offset)
        )
        return base_query

    @staticmethod
    def get_distinct_source_urls_query(url: str) -> sql.Composed:
        query = sql.SQL(
            """
            SELECT 
                original_url,
                rejection_note,
                approval_status
            FROM distinct_source_urls
            WHERE base_url = {url}
            """
        ).format(url=sql.Literal(url))
        return query

    @staticmethod
    def apply_alias_mappings(
        columns: list[InstrumentedAttribute], alias_mappings: dict[str, str]
    ):
        aliased_columns = []

        for column in columns:
            # Alias column if it exists in the alias mappings
            key = column.key
            if key in alias_mappings:
                aliased_columns.append(column.label(alias_mappings[key]))
            else:
                aliased_columns.append(column)

        return aliased_columns
