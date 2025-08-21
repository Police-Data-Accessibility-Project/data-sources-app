import os

from alembic import command
from alembic.config import Config

from middleware.util.env import get_env_variable
from root import ROOT_PATH


def apply_migrations():
    print("Applying migrations...")
    print(ROOT_PATH / "alembic.ini")
    alembic_config = Config(ROOT_PATH / "alembic.ini")
    alembic_config.set_main_option(
        "sqlalchemy.url", get_env_variable("DO_DATABASE_URL")
    )
    command.upgrade(alembic_config, "head")
    print("Migrations applied.")


if __name__ == "__main__":
    apply_migrations()
