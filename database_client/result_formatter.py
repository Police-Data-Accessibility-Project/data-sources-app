from collections import namedtuple
from typing import Any

from sqlalchemy import RowMapping

from database_client.constants import (
    DATA_SOURCES_MAP_COLUMN,
)
from database_client.subquery_logic import SubqueryParameters
from utilities.common import convert_dates_to_strings, format_arrays


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
        # TODO: Rename to a more general title
        zipped_results = [
            dict(zip(columns, result)) for result in tuples
        ]
        formatted_results = []
        for zipped_result in zipped_results:
            zipped_result = convert_dates_to_strings(zipped_result)
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
        formatted_results = []
        for row_mapping in row_mappings:
            formatted_result = {}
            key = list(row_mapping.keys())[0]
            row_object = row_mapping[key]
            for column in primary_columns:
                formatted_result[column] = getattr(row_object, column)
            for subquery_parameter in subquery_parameters:
                relationship_entities = getattr(row_object, subquery_parameter.linking_column)
                subquery_results = []
                for relationship_entity in relationship_entities:
                    subquery_result = {}
                    for column in subquery_parameter.columns:
                        subquery_result[column] = getattr(relationship_entity, column)
                    subquery_results.append(subquery_result)
                formatted_result[subquery_parameter.linking_column] = subquery_results
            formatted_results.append(formatted_result)
        return formatted_results




def dictify_namedtuple(result: list[namedtuple]) -> list[dict[str, Any]]:
    return [result._asdict() for result in result]
