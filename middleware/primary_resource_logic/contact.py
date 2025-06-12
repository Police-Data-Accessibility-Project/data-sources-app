from middleware.common_response_formatting import message_response
from middleware.flask_response_manager import FlaskResponseManager
from middleware.schema_and_dto.dtos.contact import (
    ContactFormPostDTO,
)
from middleware.third_party_interaction_logic.mailgun import send_via_mailgun


def submit_contact_form(db_client, dto: ContactFormPostDTO):
    send_via_mailgun(
        to_email="contact@pdap.io",
        subject=f"PDAP contact form: {dto.type.value}",
        text=dto.message,
    )
    return message_response("Message sent.")
