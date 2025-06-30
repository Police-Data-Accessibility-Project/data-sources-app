from pydantic import BaseModel


class NotificationEmailContent(BaseModel):
    html_text: str
    base_text: str
