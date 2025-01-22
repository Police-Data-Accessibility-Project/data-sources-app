from alembic import command
from alembic.config import Config

from middleware.util import get_env_variable

if __name__ == "__main__":
    print("Applying migrations...")
    alembic_config = Config("alembic.ini")
    conn_string = get_env_variable("DO_DATABASE_URL")
    conn_string = conn_string.replace("postgresql", "postgresql+psycopg")
    alembic_config.set_main_option("sqlalchemy.url", conn_string)
    command.upgrade(alembic_config, "head")
    print("Migrations applied.")
