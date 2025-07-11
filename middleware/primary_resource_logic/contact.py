from middleware.common_response_formatting import message_response
from middleware.schema_and_dto.dtos.contact import (
    ContactFormPostDTO,
)
from middleware.third_party_interaction_logic.mailgun_.constants import CONTACT_EMAIL
from middleware.third_party_interaction_logic.mailgun_.send import send_via_mailgun


def submit_contact_form(db_client, dto: ContactFormPostDTO):
    send_via_mailgun(
        to_email=CONTACT_EMAIL,
        subject=f"PDAP contact form: {dto.type.value}",
        text=dto.message,
    )
    return message_response("Message sent.")
