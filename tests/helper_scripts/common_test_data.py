from http import HTTPStatus
from collections import namedtuple

import psycopg

from database_client.database_client import DatabaseClient

ResponseTuple = namedtuple("ResponseTuple", ["response", "status_code"])

TEST_RESPONSE = ResponseTuple(
    response={"message": "Test Response"}, status_code=HTTPStatus.IM_A_TEAPOT
)


def insert_test_column_permission_data(db_client: DatabaseClient):
    try:
        db_client.execute_raw_sql(
            """
        DO $$
        DECLARE
            column_a_id INT;
            column_b_id INT;
            column_c_id INT;
        BEGIN
            INSERT INTO relation_column (relation, associated_column) VALUES ('test_relation', 'column_a') RETURNING id INTO column_a_id;
            INSERT INTO relation_column (relation, associated_column) VALUES ('test_relation', 'column_b') RETURNING id INTO column_b_id;
            INSERT INTO relation_column (relation, associated_column) VALUES ('test_relation', 'column_c') RETURNING id INTO column_c_id;

            INSERT INTO column_permission (rc_id, relation_role, access_permission) VALUES (column_a_id, 'STANDARD', 'READ');
            INSERT INTO column_permission (rc_id, relation_role, access_permission) VALUES (column_b_id, 'STANDARD', 'READ');
            INSERT INTO column_permission (rc_id, relation_role, access_permission) VALUES (column_c_id, 'STANDARD', 'NONE');

            INSERT INTO column_permission (rc_id, relation_role, access_permission) VALUES (column_a_id, 'OWNER', 'READ');
            INSERT INTO column_permission (rc_id, relation_role, access_permission) VALUES (column_b_id, 'OWNER', 'WRITE');
            INSERT INTO column_permission (rc_id, relation_role, access_permission) VALUES (column_c_id, 'OWNER', 'NONE');

            INSERT INTO column_permission (rc_id, relation_role, access_permission) VALUES (column_a_id, 'ADMIN', 'WRITE');
            INSERT INTO column_permission (rc_id, relation_role, access_permission) VALUES (column_b_id, 'ADMIN', 'WRITE');
            INSERT INTO column_permission (rc_id, relation_role, access_permission) VALUES (column_c_id, 'ADMIN', 'READ');

        END $$;
        """
        )
    except psycopg.errors.UniqueViolation:
        pass  # Already added
