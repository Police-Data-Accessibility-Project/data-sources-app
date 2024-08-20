Integration tests in this case usually (but not always) involve an end-to-end test of an API call.

In some cases, integration tests involve the calling of other complex functionality that is not otherwise tested in integration tests.

For example, `test_check_api_key` is functionality present in the `@api_key_required` decorator which is used by a number of endpoints, and which has multiple logical outcomes depending on whether the provided API Key is valid or not. However, because it would be redundant to test all of these logical outcomes in every endpoint which uses this wrapper (because each test for expected behavior of an invalid API key would be the same), they are all tested in the `test_check_api_key` integration tests.