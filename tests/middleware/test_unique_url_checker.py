import pytest

from middleware.primary_resource_logic.unique_url_checker import normalize_url


@pytest.mark.parametrize(
    "url",
    (
        "http://duplicate-checker.com/",
        "https://www.duplicate-checker.com",
        "http://www.duplicate-checker.com/",
    ),
)
def test_normalize_url(url):
    expected_url = "duplicate-checker.com"

    assert normalize_url(url) == expected_url
