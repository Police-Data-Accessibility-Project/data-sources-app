from pydantic import BaseModel

from mirrored_local_app.models.docker_file import DockerfileInfo
from mirrored_local_app.models.health_check import HealthCheckInfo
from mirrored_local_app.models.volume import VolumeInfo


class DockerInfo(BaseModel):
    dockerfile_info: DockerfileInfo
    volume_info: VolumeInfo | None = None
    name: str
    ports: dict | None = None
    environment: dict | None
    command: str | None = None
    entrypoint: list[str] | None = None
    health_check_info: HealthCheckInfo | None = None
