import psycopg2.extensions

from RelationConfigurationManager import RelationConfigurationManager
from helper import (
    setup_connection,
    get_connection_string_from_argument,
    execute_query_with_connection,
)


def get_relations() -> list:
    """
    Load the list of relations from the relations.txt file
    :return:
    """
    relations = []
    with open("Relations.txt", "r") as f:
        for line in f:
            line = line.strip()
            if line:
                relations.append(line)
    return relations


def get_columns_for_relation(
    connection: psycopg2.extensions.connection, relation: str
) -> list[str]:
    """
    Query database for list of columns for relation
    :param relation:
    :return:
    """
    rows = execute_query_with_connection(
        connection=connection,
        query=f"""
        SELECT 
            column_name
        FROM 
            information_schema.columns
        WHERE 
            table_name = '{relation}'
        ORDER BY 
            ordinal_position;
        """,
        return_result=True,
    )
    return [row[0] for row in rows]


if __name__ == "__main__":
    connection_string = get_connection_string_from_argument()

    connection = setup_connection(connection_string)

    relation_configuration_manager = RelationConfigurationManager()

    relations = get_relations()
    for relation in relations:
        columns = get_columns_for_relation(connection, relation)

        if relation_configuration_manager.relation_configuration_exists(relation):
            relation_configuration = (
                relation_configuration_manager.get_relation_configuration(relation)
            )
            relation_configuration.update_columns(columns)
        else:
            relation_configuration_manager.make_relation_configuration(
                relation_name=relation, columns=columns
            )
        relation_configuration_manager.write_relation_configuration_csv(relation)
