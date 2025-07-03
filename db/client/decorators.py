"""
Decorators used exclusively by the Database Client
"""

from functools import wraps

from psycopg.rows import RowFactory, dict_row

from db.helpers_.psycopg import initialize_psycopg_connection


def session_manager(method):
    @wraps(method)
    def wrapper(self: "DatabaseClient", *args, **kwargs):
        self.session = self.session_maker()
        try:
            result = method(self, *args, **kwargs)
            self.session.flush()
            self.session.commit()
            return result
        except Exception as e:
            self.session.rollback()
            raise e
        finally:
            self.session.close()
            self.session = None

    return wrapper


def session_manager_v2(method: callable) -> callable:
    @wraps(method)
    def wrapper(self: "DatabaseClient", *args, **kwargs):
        session = self.session_maker()
        try:
            result = method(self, session, *args, **kwargs)
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()  # Ensures the session is cleaned up

    return wrapper


def cursor_manager(row_factory: RowFactory = dict_row):
    """Decorator method for managing a cursor object.
    The cursor is closed after the method concludes its execution.

    :param row_factory: Row factory for the cursor, defaults to dict_row
    """

    def decorator(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            # Open a new cursor
            # If connection is closed, reopen
            if self.connection.closed != 0:
                self.connection = initialize_psycopg_connection()
            self.cursor = self.connection.cursor(row_factory=row_factory)
            try:
                # Execute the method
                result = method(self, *args, **kwargs)
                # Commit the transaction if no exception occurs
                self.connection.commit()
                return result
            except Exception as e:
                # Rollback in case of an error
                self.connection.rollback()
                raise e
            finally:
                # Close the cursor
                self.cursor.close()
                self.cursor = None

        return wrapper

    return decorator
