from pydantic import BaseModel, model_validator


# TODO: Delete
class SourceManagerSyncInnerResponse(BaseModel):
    id: int
    success: bool
    error: str | None = None

    @model_validator(mode="after")
    def check_error(self):
        if self.success and self.error is not None:
            raise ValueError("Error should be None if success is True")
        if not self.success and self.error is None:
            raise ValueError("Error should not be None if success is False")
        return self


class SourceManagerSyncOuterResponse(BaseModel):
    results: list[SourceManagerSyncInnerResponse]
