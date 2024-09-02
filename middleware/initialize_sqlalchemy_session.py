import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.orm import sessionmaker

from middleware.util import get_env_variable


class DatabaseInitializationError(Exception):
    """
    Custom Exception to be raised when psycopg connection initialization fails.
    """

    def __init__(self, message="Failed to initialize sqlalchemy session."):
        self.message = message
        super().__init__(self.message)


class DatabaseSessionSingleton:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            if not cls._instance:
                cls._instance = super(DatabaseSessionSingleton, cls).__new__(cls)
                cls._instance._session = None
        return cls._instance

    def get_session(self) -> SQLAlchemySession:
        if self._session is None:# or self._session.closed != 0:
            self._session = self._initialize_sqlalchemy_session()
        return self._session

    def _initialize_sqlalchemy_session(self) -> SQLAlchemySession:
        """
        Initializes a connection to a PostgreSQL database using psycopg with connection parameters
        obtained from an environment variable. If the connection fails, it raises a DatabaseInitializationError.

        The function sets keepalive parameters to maintain the connection active during periods of inactivity.

        :return: A psycopg connection object if successful.
        """
        try: 
            do_database_url = get_env_variable("DO_DATABASE_URL")
            do_database_url = "postgresql+psycopg" + do_database_url[10:]

            engine = create_engine(do_database_url, echo=True)
            Session = sessionmaker(bind=engine)
            return Session()
            
            '''return psycopg.connect(
                DO_DATABASE_URL,
                keepalives=1,
                keepalives_idle=30,
                keepalives_interval=10,
                keepalives_count=5,
            )'''

        except sqlalchemy.exc.SQLAlchemyError as e:
            raise DatabaseInitializationError(e) from e


def initialize_sqlalchemy_session() -> SQLAlchemySession:
    """
    Initializes a connection to a PostgreSQL database using psycopg with connection parameters
    obtained from an environment variable. If the connection fails, it returns a default dictionary
    indicating no data sources are available.

    The function sets keepalive parameters to maintain the connection active during periods of inactivity.

    :return: A psycopg connection object if successful, or a dictionary with a count of 0 and an empty data list upon failure.
    """
    return DatabaseSessionSingleton().get_session()


