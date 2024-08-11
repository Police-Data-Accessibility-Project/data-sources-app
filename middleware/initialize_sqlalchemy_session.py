from sqlalchemy.orm import sessionmaker, scoped_session

from middleware.models import db


class SQLAlchemySession():

    def __init__(self):
        self.session = None
        self.initialize_sqlalchemy_session()

    def initialize_sqlalchemy_session(self):
        self.connection = db.engine.connect()
        self.transaction = self.connection.begin()
        self.session = scoped_session(sessionmaker(bind=self.connection))

        # Overwrite the db.session with the scoped session
        db.session = self.session

    def commit_and_close(self):
        self.session.commit()
        self.transaction.commit()
        self.close()
    
    def close(self):
        self.session.close()
        self.connection.close()

    def rollback_and_close(self):
        self.session.close()
        self.transaction.rollback()
        self.connection.close()