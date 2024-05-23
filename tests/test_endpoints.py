import pytest
from unittest.mock import patch
from app import app, SearchTokens


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_search_tokens_get_called(client):
    with patch.object(SearchTokens, "get", return_value="Mocked response") as mock_get:
        response = client.get("/search-tokens")
        assert response.status_code == 200
        mock_get.assert_called_once()


def test_search_tokens_put_not_allowed(client):
    response = client.put("/search-tokens")
    assert response.status_code == 405  # 405 Method Not Allowed


def test_search_tokens_post_not_allowed(client):
    response = client.post("/search-tokens")
    assert response.status_code == 405  # 405 Method Not Allowed


def test_search_tokens_delete_not_allowed(client):
    response = client.delete("/search-tokens")
    assert response.status_code == 405  # 405 Method Not Allowed
