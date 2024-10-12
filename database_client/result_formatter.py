from collections import namedtuple
from typing import Any, Optional

from sqlalchemy import RowMapping
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.inspection import inspect

from database_client.constants import (
    DATA_SOURCES_MAP_COLUMN,
    METADATA_METHOD_NAMES,
)
from database_client.db_client_dataclasses import WhereMapping
from database_client.models import SQL_ALCHEMY_TABLE_REFERENCE
from database_client.subquery_logic import SubqueryParameters
from utilities.common import format_arrays

class SubqueryResultFormatter:
    def __init__(self, row_mappings: list[RowMapping], primary_columns: list[str], subquery_parameters: list[SubqueryParameters]):
        self.row_mappings = row_mappings
        self.primary_columns = primary_columns
        self.subquery_parameters = subquery_parameters

    def format_results(self) -> list[dict]:
        formatted_results = []
        for row_mapping in self.row_mappings:
            formatted_result = self._format_row(row_mapping)
            formatted_results.append(formatted_result)
        return formatted_results

    def _format_row(self, row_mapping: RowMapping) -> dict:
        formatted_result = {}
        key = list(row_mapping.keys())[0]
        row_object = row_mapping[key]
        self._add_primary_columns(formatted_result, row_object)
        self._add_subquery_parameters(formatted_result, row_object)
        return formatted_result

    def _add_primary_columns(self, formatted_result: dict, row_object: Any) -> None:
        for column in self.primary_columns:
            formatted_result[column] = getattr(row_object, column)

    def _add_subquery_parameters(self, formatted_result: dict, row_object: Any) -> None:
        for subquery_parameter in self.subquery_parameters:
            relationship_entities = getattr(row_object, subquery_parameter.linking_column)
            subquery_results = [
                {column: getattr(relationship_entity, column) for column in subquery_parameter.columns}
                for relationship_entity in relationship_entities
            ]
            formatted_result[subquery_parameter.linking_column] = subquery_results

class ResultFormatter:
    """
    Formats results for specific database queries
    Coupled with the DatabaseClient class, whose outputs are formatted here
    """

    @staticmethod
    def tuples_to_column_value_dict(
        columns: list[str], tuples: list[tuple]
    ) -> list[dict]:
        """
        Combine a list of output columns with a list of results,
        and produce a list of dictionaries where the keys correspond
        to the output columns and the values correspond to the results
        :param columns:
        :param tuples:
        :return:
        """
        zipped_results = [
            dict(zip(columns, result)) for result in tuples
        ]
        formatted_results = []
        for zipped_result in zipped_results:
            formatted_results.append(format_arrays(zipped_result))
        return formatted_results

    @staticmethod
    def zip_get_datas_sources_for_map_results(results: list[tuple]) -> list[dict]:
        return ResultFormatter.tuples_to_column_value_dict(
            DATA_SOURCES_MAP_COLUMN, results
        )

    @staticmethod
    def format_result_with_subquery_parameters(
        row_mappings: list[RowMapping],
        primary_columns: list[str],
        subquery_parameters: list[SubqueryParameters]
    ) -> list[dict]:
        srf = SubqueryResultFormatter(
            row_mappings=row_mappings,
            primary_columns=primary_columns,
            subquery_parameters=subquery_parameters)
        return srf.format_results()

    @staticmethod
    def format_with_metadata(
        data: list[dict],
        relation_name: str,
        subquery_parameters: Optional[list[SubqueryParameters]] = [],
    ) -> dict[str, Any]:
        metadata_dict = {}
        relation_reference = SQL_ALCHEMY_TABLE_REFERENCE[relation_name]

        # Iterate through all properties of the Table
        for name, descriptor in inspect(
            relation_reference
        ).all_orm_descriptors.items():
            if type(descriptor) == hybrid_method and name in METADATA_METHOD_NAMES:
                # Retrieve and call the metadata method
                metadata_result = getattr(relation_reference, name)(
                    data=data,
                    subquery_parameters=subquery_parameters,
                )
                if metadata_result is not None:
                    metadata_dict.update(metadata_result)
        
        return {
            "metadata": metadata_dict,
            "data": data,
        }


def dictify_namedtuple(result: list[namedtuple]) -> list[dict[str, Any]]:
    return [result._asdict() for result in result]
