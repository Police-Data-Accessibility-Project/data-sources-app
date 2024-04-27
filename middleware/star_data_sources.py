import psycopg2


class StarredDataSourceManager:
    """
    This class manages CRUD operations for the 'user_starred_data_sources' table in a PostgreSQL database.
    It requires a psycopg2 connection object to interact with the database.

    Attributes:
        conn (psycopg2.connect): A psycopg2 connection object to the PostgreSQL database.
    """

    def __init__(self, conn: psycopg2.connect):
        """
        Initializes the StarredDataSourceManager with a psycopg2 connection.

        Parameters:
            conn (psycopg2.connect): A connection to a PostgreSQL database.
        """
        self.conn = conn

    def create_star(self, user_id: int, data_source_uid: str) -> None:
        """
        Stars a data source for a user by creating an entry in the 'user_starred_data_sources' table.

        Parameters:
            user_id (int): ID of the user who is starring the data source.
            data_source_uid (str): UID of the data source being starred.
        """
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO public.user_starred_data_sources (user_id, data_source_uid, starred_at)
                VALUES (%s, %s, NOW());
                """,
                (user_id, data_source_uid),
            )
            self.conn.commit()

    def read_all_stars_for_user(self, user_id: int) -> list:
        """
        Retrieves all star entries for a specific user from the 'user_starred_data_sources' table.

        Parameters:
            user_id (int): ID of the user whose stars are to be retrieved.

        Returns:
            list: List of tuples, each containing all columns for each starred entry.
        """
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM public.user_starred_data_sources WHERE user_id = %s;",
                (user_id,),
            )
            return cur.fetchall()

    def delete_star(self, user_id: int, data_source_uid: str) -> None:
        """
        Removes a star from a data source for a user by deleting an entry from the 'user_starred_data_sources' table.

        Parameters:
            user_id (int): ID of the user.
            data_source_uid (str): UID of the data source.
        """
        with self.conn.cursor() as cur:
            cur.execute(
                "DELETE FROM public.user_starred_data_sources WHERE user_id = %s AND data_source_uid = %s;",
                (user_id, data_source_uid),
            )
            self.conn.commit()
