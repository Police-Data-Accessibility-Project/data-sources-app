from endpoints.instantiations.auth_.signup.middleware import send_signup_link
from middleware.util.env import get_env_variable


def test_send_signup_link():
    send_signup_link(
        email=get_env_variable("TEST_EMAIL_ADDRESS"),
        token="TEST_TOKEN",
    )
