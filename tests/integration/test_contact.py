from unittest.mock import MagicMock

from middleware.enums import ContactFormMessageType
from middleware.util.type_conversion import get_enum_values
from tests.helpers.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)


def test_contact(test_data_creator_flask: TestDataCreatorFlask, monkeypatch):
    tdc = test_data_creator_flask

    mock_send_via_mailgun = MagicMock()

    monkeypatch.setattr(
        "middleware.primary_resource_logic.contact.send_via_mailgun",
        mock_send_via_mailgun,
    )

    for val in get_enum_values(ContactFormMessageType):
        tdc.request_validator.post(
            endpoint="contact/form-submit",
            headers=tdc.get_admin_tus().api_authorization_header,
            json={
                "email": "xHbR3@example.com",
                "type": val,
                "message": "This is a test message",
            },
        )

        mock_send_via_mailgun.assert_called_with(
            to_email="contact@pdap.io",
            subject=f"PDAP contact form: {val}",
            text="This is a test message",
        )
