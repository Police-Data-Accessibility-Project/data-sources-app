from flask_restx import Resource


class PsycopgResource(Resource):
    def __init__(self, *args, **kwargs):
        """
        Initializes the resource with a database connection.
        - kwargs (dict): Keyword arguments containing 'psycopg2_connection' for database connection.
        """
        super().__init__(*args, **kwargs)
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
