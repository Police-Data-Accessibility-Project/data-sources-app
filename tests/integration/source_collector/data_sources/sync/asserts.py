def assert_data_sources_each_have_one_agency(results: dict):
    for data_source in results["data_sources"]:
        assert len(data_source["agency_ids"]) == 1


def assert_expected_data_sources_count(results, count: int):
    assert len(results["data_sources"]) == count
