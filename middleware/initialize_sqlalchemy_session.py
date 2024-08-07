from sqlalchemy.orm import sessionmaker, scoped_session

from middleware.models import db


def initialize_sqlalchemy_session():
    connection = db.engine.connect()
    transaction = connection.begin()
    session = scoped_session(sessionmaker(bind=connection))

    # Overwrite the db.session with the scoped session
    db.session = session
    
    try:
        yield session
    except Exception as e:
        transaction.rollback()
        raise e
    finally:
        session.close()
        connection.close()