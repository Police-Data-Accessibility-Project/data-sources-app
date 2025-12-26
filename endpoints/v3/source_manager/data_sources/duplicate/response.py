from pydantic import BaseModel, Field


class SourceManagerDataSourcesDuplicateResponse(BaseModel):
    results: dict[str, bool] = Field(
        description="A dictionary of provided URLs and whether they are duplicates or not.",
        examples=[
            {
                "www.unique-url": False,
                "www.duplicate-url": True,
            }
        ]
    )