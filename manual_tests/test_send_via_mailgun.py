from middleware.third_party_interaction_logic.mailgun_logic import send_via_mailgun
from middleware.util import get_env_variable


def test_send_via_mailgun():
    send_via_mailgun(
        to_email=get_env_variable("TEST_EMAIL_ADDRESS"),
        subject="This is a subject test",
        body="This is the body of the test"
    )