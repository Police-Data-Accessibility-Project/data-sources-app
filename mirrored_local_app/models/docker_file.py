from pydantic import BaseModel


class DockerfileInfo(BaseModel):
    image_tag: str
    dockerfile_directory: str | None = None
