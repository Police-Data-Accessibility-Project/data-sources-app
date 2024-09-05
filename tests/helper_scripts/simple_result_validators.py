def has_expected_keys(result_keys: list, expected_keys: list) -> bool:
    """
    Check that given result includes expected keys.

    :param result:
    :param expected_keys:
    :return: True if has expected keys, false otherwise
    """
    return not set(expected_keys).difference(result_keys)


def check_response_status(response, status_code):
    assert (
        response.status_code == status_code
    ), f"Expected status code {status_code}, got {response.status_code}: {response.text}"


def assert_is_oauth_redirect_link(text: str):
    assert "https://github.com/login/oauth/authorize?response_type=code" in text, (
        "Expected OAuth authorize link, got: " + text
    )
