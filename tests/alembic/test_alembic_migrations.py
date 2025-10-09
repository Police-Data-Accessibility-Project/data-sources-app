import logging


from tests.alembic.AlembicRunner import AlembicRunner


def test_revision_upgrade_downgrade(alembic_runner: AlembicRunner):
    logging.disable(logging.NOTSET)
    alembic_runner.upgrade("head")
    logging.disable(logging.CRITICAL)
