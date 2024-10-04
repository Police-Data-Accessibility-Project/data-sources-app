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
    def convert_data_source_matches(
        data_source_output_columns: list[str], results: list[tuple]
    ) -> list[dict]:
        """
        Combine a list of output columns with a list of results,
        and produce a list of dictionaries where the keys correspond
        to the output columns and the values correspond to the results
        :param data_source_output_columns:
        :param results:
        :return:
        """
        # TODO: Rename to a more general title
        data_source_matches = [
            dict(zip(data_source_output_columns, result)) for result in results
        ]
        data_source_matches_converted = []
        for data_source_match in data_source_matches:
            data_source_match = convert_dates_to_strings(data_source_match)
            data_source_matches_converted.append(format_arrays(data_source_match))
        return data_source_matches_converted

    @staticmethod
    def zip_get_datas_sources_for_map_results(results: list[tuple]) -> list[dict]:
        return ResultFormatter.convert_data_source_matches(
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
