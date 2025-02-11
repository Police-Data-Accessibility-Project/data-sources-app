from sqlalchemy import CursorResult

from tests.alembic.AlembicRunner import AlembicRunner


def test_submitted_name(alembic_runner: AlembicRunner):
    alembic_runner.upgrade("12cf56cbebb7")
    alembic_runner.execute(
        """
        INSERT INTO AGENCIES (
        submitted_name,
        state_iso,
        jurisdiction_type
        ) VALUES (
        'Test Name',
        'TX',
        'state'
        );    
    """
    )

    results = alembic_runner.execute(
        """
        SELECT name, submitted_name FROM AGENCIES;
    """
    )

    assert results[0][0] == "Test Name - TX"
    assert results[0][1] == "Test Name"

    def refresh_materialized_view():
        alembic_runner.execute(
            """
            REFRESH MATERIALIZED VIEW TYPEAHEAD_AGENCIES;
        """
        )

    refresh_materialized_view()
    results = alembic_runner.execute(
        """
        SELECT name FROM typeahead_agencies;
    """
    )
    assert results[0][0] == "Test Name - TX"

    alembic_runner.upgrade("8ba99f12446d")
    results = alembic_runner.execute(
        """
        SELECT name FROM AGENCIES;
    """
    )
    assert results[0][0] == "Test Name"

    refresh_materialized_view()
    results = alembic_runner.execute(
        """
        SELECT name FROM typeahead_agencies;
    """
    )
    assert results[0][0] == "Test Name"



