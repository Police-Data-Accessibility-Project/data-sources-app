from sqlalchemy.orm.collections import InstrumentedList

from db.models.implementations.core.data_source.expanded import DataSourceExpanded
from db.models.implementations.core.agency.core import Agency
from db.helpers_.result_formatter import ResultFormatter


def test_data_source_to_get_data_sources_output_no_agencies():

    data_source = DataSourceExpanded(
        id=1,
        name="Test Data Source",
    )
    agency = Agency(
        id=1,
        name="Test Agency",
    )
    data_source.agencies = InstrumentedList([agency])

    result = ResultFormatter.data_source_to_get_data_sources_output(
        data_source=data_source,
        data_sources_columns=["name"],
    )

    assert result["name"] == data_source.name
