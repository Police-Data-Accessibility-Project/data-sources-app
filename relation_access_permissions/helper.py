import argparse

import psycopg2


def execute_query_with_connection(
    connection: psycopg2.extensions.connection, query: str, return_result=False
):
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        if return_result:
            result = cursor.fetchall()
            cursor.close()
            return result
        else:
            cursor.close()
    except Exception as error:
        print(f"Error executing query '{query}': {type(error).__name__}")
        connection.rollback()
        connection.close()
        exit(1)


def setup_connection(connection_string: str) -> psycopg2.extensions.connection:
    return psycopg2.connect(connection_string)


def get_connection_string_from_argument() -> str:
    """
    Get connection string from command line argument
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--connection_string",
        type=str,
        help="Database connection string",
        required=True,
    )
    args = parser.parse_args()
    return args.connection_string
