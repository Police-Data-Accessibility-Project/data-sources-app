from pydantic import BaseModel, Field


class UserPutDTO(BaseModel):
    old_password: str = Field(description="The old password of the user.")
    new_password: str = Field(description="The new password of the user.")
