import pytest

from tests.integration.auth.signup.helpers import SignupTestHelper


@pytest.fixture
def helper(test_data_creator_flask, mocker):
    return SignupTestHelper(test_data_creator_flask, mocker)
