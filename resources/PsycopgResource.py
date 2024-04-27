import functools

from flask_restful import Resource


def handle_exceptions(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            self.psycopg2_connection.rollback()
            print(str(e))
            return {"message": str(e)}, 500

    return wrapper


class PsycopgResource(Resource):
    def __init__(self, **kwargs):
        """
        Initializes the resource with a database connection.
        - kwargs (dict): Keyword arguments containing 'psycopg2_connection' for database connection.
        """
        self.psycopg2_connection = kwargs["psycopg2_connection"]

    def get(self):
        """
        Base implementation of GET. Override in subclasses as needed.
        """
        raise NotImplementedError("This method should be overridden by subclasses")

    def post(self):
        """
        Base implementation of POST. Override in subclasses as needed.
        """
        raise NotImplementedError("This method should be overridden by subclasses")
