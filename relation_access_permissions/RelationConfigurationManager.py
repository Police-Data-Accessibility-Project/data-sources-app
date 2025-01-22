import os
from dataclasses import dataclass
from enum import Enum
import pandas as pd


class AccessPermission(Enum):
    READ = "READ"
    WRITE = "WRITE"
    NONE = "NONE"


def get_full_path(path: str) -> str:
    return os.path.join(os.path.dirname(__file__), path)


RELATION_CONFIGURATIONS_DIR = "relation_configurations"


@dataclass
class RelationColumn:
    column_name: str
    # Access permission in format of {role: AccessPermission}
    access_permissions: dict[str, AccessPermission]


class RelationConfiguration:
    relation_name: str
    columns: list[RelationColumn]
    columns: dict[str, RelationColumn]

    def __init__(self, relation_name: str, columns: list[RelationColumn]):
        self.relation_name = relation_name
        self.columns = {}
        for column in columns:
            self.add_column(column)

    def add_column(self, column: RelationColumn):
        self.columns[column.column_name] = column

    def remove_column(self, column_name: str):
        self.columns.pop(column_name)

    def get_column_names(self) -> list[str]:
        return list(self.columns.keys())

    def update_columns(self, new_columns: list[str]):
        self.remove_columns_not_in(new_columns)
        self.add_new_columns(new_columns)

    def remove_columns_not_in(self, new_columns: list[str]):
        existing_columns = self.get_column_names()
        columns_to_remove = [
            column for column in existing_columns if column not in new_columns
        ]
        for column in columns_to_remove:
            self.remove_column(column)

    def add_new_columns(self, new_columns: list[str]):
        for column in new_columns:
            if not self.column_exists(column):
                relation_column = RelationColumn(
                    column_name=column, access_permissions={}
                )
                self.add_column(relation_column)

    def column_exists(self, column_name: str):
        return column_name in self.columns

    def get_all_roles(self) -> list[str]:
        roles = set()
        for column in self.columns.values():
            for role in column.access_permissions.keys():
                roles.add(role)
        return list(roles)


class RelationConfigurationManager:

    def __init__(self):
        self.relation_configurations = {}
        self.load_relation_configuration_csvs()

    def get_all_relation_configuration_filenames(self) -> list[str]:
        """
        Assumptions:
        * The relation_configurations directory contains only csv files
        :return: A list of all filenames in the directory
        """
        return os.listdir(get_full_path(RELATION_CONFIGURATIONS_DIR))

    def load_relation_configuration_csvs(self):
        for filename in self.get_all_relation_configuration_filenames():
            df = pd.read_csv(get_full_path(f"{RELATION_CONFIGURATIONS_DIR}/{filename}"))
            relation_name = filename.replace(".csv", "")
            relation_columns = []
            for row_index, row in df.iterrows():
                column_name = row["column_name"]
                access_permissions = {}
                for col_name, value in row.items():
                    if col_name == "column_name":
                        continue
                    try:
                        access_permission = AccessPermission(value)
                    except ValueError:
                        access_permission = AccessPermission.NONE
                    access_permissions[str(col_name)] = access_permission
                    relation_columns.append(
                        RelationColumn(
                            column_name=column_name,
                            access_permissions=access_permissions,
                        )
                    )

            self.relation_configurations[relation_name] = RelationConfiguration(
                relation_name=relation_name, columns=relation_columns
            )

    def get_relation_configuration(self, relation_name: str) -> RelationConfiguration:
        return self.relation_configurations[relation_name]

    def relation_configuration_exists(self, relation_name):
        return relation_name in self.relation_configurations

    def make_relation_configuration(self, relation_name: str, columns: list[str]):
        relation_columns = []
        for column in columns:
            relation_column = RelationColumn(column_name=column, access_permissions={})
            relation_columns.append(relation_column)

        self.relation_configurations[relation_name] = RelationConfiguration(
            relation_name=relation_name, columns=relation_columns
        )

    def write_relation_configuration_csv(self, relation_name: str):
        relation_configuration = self.relation_configurations[relation_name]
        roles = relation_configuration.get_all_roles()
        df = pd.DataFrame(columns=["column_name"] + roles)
        new_rows = []
        for column in self.relation_configurations[relation_name].columns.values():
            new_row = {"column_name": column.column_name}
            for role in roles:
                new_row[role] = column.access_permissions.get(
                    role, AccessPermission.NONE
                ).value
            new_rows.append(new_row)
        df_extended = pd.DataFrame(columns=["column_name"] + roles, data=new_rows)
        out_df = pd.concat([df, df_extended], ignore_index=True)

        out_df.to_csv(
            get_full_path(f"{RELATION_CONFIGURATIONS_DIR}/{relation_name}.csv"),
            index=False,
        )
