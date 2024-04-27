import psycopg2
from psycopg2 import sql


class DataRequestsManager:
    """
    This class manages CRUD operations for the 'data_requests' table in a PostgreSQL database.
    It requires a psycopg2 connection object to interact with the database.

    Attributes:
        conn (psycopg2.connect): A psycopg2 connection object to the PostgreSQL database.
    """

    def __init__(self, conn: psycopg2.connect):
        """
        Initializes the DataRequestsManager with a psycopg2 connection.

        Parameters:
            conn (psycopg2.connect): A connection to a PostgreSQL database.
        """
        self.conn = conn

    def create_request(self, submission_notes: str, submitter_contact_info: str) -> int:
        """
        Creates a new entry in the data_requests table.

        Parameters:
            submission_notes (str): Notes regarding the submission.
            submitter_contact_info (str): Contact information of the submitter.

        Returns:
            int: The id of the newly created record.
        """
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO public.data_requests (submission_notes, submitter_contact_info, date_created)
                VALUES (%s, %s, NOW()) RETURNING id;
                """,
                (submission_notes, submitter_contact_info),
            )
            self.conn.commit()
            return cur.fetchone()[0]

    def read_request(self, request_id: int) -> tuple:
        """
        Reads a specific entry from the data_requests table.

        Parameters:
            request_id (int): The ID of the request to retrieve.

        Returns:
            tuple: All columns of the entry as a tuple.
        """
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM public.data_requests WHERE id = %s;", (request_id,)
            )
            return cur.fetchone()

    def update_request(self, request_id: int, **kwargs) -> None:
        """
        Updates specified fields of an existing entry in the data_requests table.

        Parameters:
            request_id (int): The ID of the request to update.
            **kwargs: Variable keyword arguments corresponding to column names and their new values.
        """
        with self.conn.cursor() as cur:
            query = sql.SQL("UPDATE public.data_requests SET {} WHERE id = %s").format(
                sql.SQL(", ").join(
                    [sql.SQL("{} = %s").format(sql.Identifier(k)) for k in kwargs]
                )
            )
            params = list(kwargs.values()) + [request_id]
            cur.execute(query, params)
            self.conn.commit()

    def delete_request(self, request_id: int) -> int:
        """
        Deletes a specific entry from the data_requests table.

        Parameters:
            request_id (int): The ID of the request to delete.
        """
        with self.conn.cursor() as cur:
            cur.execute(
                "DELETE FROM public.data_requests WHERE id = %s;", (request_id,)
            )
            self.conn.commit()
