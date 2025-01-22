from alembic import op

from relation_access_permissions.RelationConfigurationManager import (
    RelationConfiguration,
    RelationConfigurationManager,
)


def insert_relation_columns_to_db(relation_configuration: RelationConfiguration):
    relation_name = relation_configuration.relation_name
    columns = relation_configuration.get_column_names()
    for column in columns:
        op.execute(
            f"""
            INSERT INTO relation_column (relation, associated_column)
            VALUES ('{relation_name}', '{column}');
            COMMIT;
            """,
        )


def insert_column_permissions_to_db(relation_configuration: RelationConfiguration):
    relation_name = relation_configuration.relation_name
    columns = relation_configuration.columns.values()
    for column in columns:
        for role, access_permission in column.access_permissions.items():
            op.execute(
                f"""
                INSERT INTO column_permission (rc_id, relation_role, access_permission)
                SELECT rc.id, '{role.strip()}', '{access_permission.value}'
                FROM
                    relation_column rc
                WHERE
                    relation = '{relation_name}' AND
                    associated_column = '{column.column_name}';
                COMMIT;
                """,
            )


def upload_relation_configurations_to_db_alembic():
    relation_configuration_manager = RelationConfigurationManager()
    relation_configurations = relation_configuration_manager.relation_configurations
    for relation_configuration in relation_configurations.values():
        insert_relation_columns_to_db(relation_configuration)
        insert_column_permissions_to_db(relation_configuration)
