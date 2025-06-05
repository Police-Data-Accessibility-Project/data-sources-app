from functools import partialmethod
from typing import Optional

from pydantic import BaseModel
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.base import ExecutableOption

from database_client.models.core import convert_to_column_reference
from middleware.enums import Relations


class SubqueryParameters(BaseModel):
    """
    Contains parameters for executing a subquery
    """

    relation_name: str
    linking_column: str
    columns: Optional[list[str]] = None
    alias_mappings: Optional[dict[str, str]] = None

    def set_columns(self, columns: list[str]) -> None:
        self.columns = columns

    def build_subquery_load_option(self, primary_relation: str) -> ExecutableOption:
        """Creates a SQLAlchemy ExecutableOption for subquerying.

        :param primary_relation:
        :return: ExecutableOption. Example: defaultload(DataSource.agencies).load_only(Agency.name)
        """
        column_references = convert_to_column_reference(
            columns=self.columns, relation=self.relation_name
        )
        linking_column_reference = convert_to_column_reference(
            columns=[self.linking_column], relation=primary_relation
        )

        return joinedload(*linking_column_reference).load_only(*column_references)


class SubqueryParameterManager:
    """
    Consolidates and manages the retrieval of subquery parameters
    """

    @staticmethod
    def get_subquery_params(
        relation: Relations,
        linking_column: str,
        columns: list[str] = None,
        alias_mappings: Optional[dict[str, str]] = None,
    ) -> SubqueryParameters:
        return SubqueryParameters(
            relation_name=relation.value,
            linking_column=linking_column,
            columns=columns,
            alias_mappings=alias_mappings,
        )

    agencies = partialmethod(
        get_subquery_params,
        relation=Relations.AGENCIES_EXPANDED,
        linking_column="agencies",
        columns=[
            "id",
            "name",
            "submitted_name",
            "state_name",
            "locality_name",
            "state_iso",
            "county_name",
            "agency_type",
            "jurisdiction_type",
            "homepage_url",
        ],
    )

    data_requests = partialmethod(
        get_subquery_params,
        relation=Relations.DATA_REQUESTS_EXPANDED,
        linking_column="data_requests",
    )

    @staticmethod
    def data_sources():
        return SubqueryParameterManager.get_subquery_params(
            relation=Relations.DATA_SOURCES_EXPANDED,
            linking_column="data_sources",
            columns=["id", "name"],
        )

    @staticmethod
    def locations():
        return SubqueryParameterManager.get_subquery_params(
            relation=Relations.LOCATIONS_EXPANDED,
            linking_column="locations",
            columns=[
                "type",
                "state_name",
                "state_iso",
                "county_fips",
                "county_name",
                "locality_name",
                "display_name",
            ],
            alias_mappings={"id": "location_id"},
        )
