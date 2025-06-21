from typing import Optional, Union, Sequence

from sqlalchemy import RowMapping

from db.constants import PAGE_SIZE
from db.db_client_dataclasses import WhereMapping, OrderByParameters
from db.dynamic_query_constructor import DynamicQueryConstructor
from db.helpers import get_offset
from db.helpers_.result_formatting import format_with_metadata
from db.models.table_reference import convert_to_column_reference
from db.queries.builder import QueryBuilderBase
from db.subquery_logic import SubqueryParameters


class SelectFromRelationQueryBuilder(QueryBuilderBase):
    def __init__(
        self,
        relation_name: str,
        columns: list[str],
        where_mappings: Optional[Union[list[WhereMapping], dict]] = [True],
        limit: Optional[int] = PAGE_SIZE,
        page: Optional[int] = None,
        order_by: Optional[OrderByParameters] = None,
        subquery_parameters: Optional[list[SubqueryParameters]] = [],
        build_metadata: Optional[bool] = False,
        alias_mappings: Optional[dict[str, str]] = None,
        apply_uniqueness_constraints: Optional[bool] = True,
    ):
        super().__init__()
        self.relation_name = relation_name
        self.columns = columns
        self.where_mappings = where_mappings
        self.limit = limit
        self.page = page
        self.order_by = order_by
        self.subquery_parameters = subquery_parameters
        self.build_metadata = build_metadata
        self.alias_mappings = alias_mappings
        self.apply_uniqueness_constraints = apply_uniqueness_constraints

    def run(self) -> list[dict]:
        """
        Selects a single relation from the database
        """
        limit = min(self.limit, 100)
        where_mappings = self._create_where_mappings_instance_if_dictionary(
            self.where_mappings
        )
        offset = get_offset(self.page)
        column_references = convert_to_column_reference(
            columns=self.columns, relation=self.relation_name
        )
        query = DynamicQueryConstructor.create_selection_query(
            self.relation_name,
            column_references,
            where_mappings,
            limit,
            offset,
            self.order_by,
            self.subquery_parameters,
            self.alias_mappings,
        )
        if self.apply_uniqueness_constraints:
            raw_results = self.session.execute(query()).mappings().unique().all()
        else:
            raw_results = self.session.execute(query()).mappings().all()
        results = self._process_results(
            raw_results=raw_results,
        )

        return results

    def _process_results(
        self,
        raw_results: Sequence[RowMapping],
    ):
        table_key = self._build_table_key_if_results(raw_results)
        results = self._dictify_results(
            raw_results, self.subquery_parameters, table_key
        )
        results = self._optionally_build_metadata(
            self.build_metadata, self.relation_name, results, self.subquery_parameters
        )
        return results

    @staticmethod
    def _create_where_mappings_instance_if_dictionary(where_mappings):
        if isinstance(where_mappings, dict):
            where_mappings = WhereMapping.from_dict(where_mappings)
        return where_mappings

    @staticmethod
    def _optionally_build_metadata(
        build_metadata: bool, relation_name, results, subquery_parameters
    ):
        if build_metadata is True:
            results = format_with_metadata(
                results,
                relation_name,
                subquery_parameters,
            )
        return results

    def _dictify_results(
        self,
        raw_results: Sequence[RowMapping],
        subquery_parameters: Optional[list[SubqueryParameters]],
        table_key: str,
    ):
        if subquery_parameters and table_key:
            # Calls models.Base.to_dict() method
            results = []
            for result in raw_results:
                val: dict = result[table_key].to_dict(subquery_parameters)
                self._alias_subqueries(subquery_parameters, val)
                results.append(val)
        else:
            results = [dict(result) for result in raw_results]
        return results

    @staticmethod
    def _alias_subqueries(subquery_parameters, val: dict):
        for sp in subquery_parameters:
            if sp.alias_mappings is None:
                continue
            for entry in val[sp.linking_column]:
                keys = list(entry.keys())
                for key in keys:
                    if key in sp.alias_mappings:
                        alias = sp.alias_mappings[key]
                        entry[alias] = entry[key]
                        del entry[key]

    @staticmethod
    def _build_table_key_if_results(raw_results: Sequence[RowMapping]) -> str:
        table_key = ""
        if len(raw_results) > 0:
            table_key = [key for key in raw_results[0].keys()][0]
        return table_key
