import docker
from docker.errors import APIError, NotFound

from mirrored_local_app.models.docker import DockerInfo
from mirrored_local_app.models.docker_file import DockerfileInfo
from mirrored_local_app.helpers.path import get_absolute_path


class DockerManager:
    def __init__(self):
        self.client = docker.from_env()
        self.network_name = "my_network"
        self.network = self.start_network()

    def run_command(self, command: str, container_id: str):
        exec_id = self.client.api.exec_create(
            container_id, cmd=command, tty=True, stdin=False
        )
        output_stream = self.client.api.exec_start(exec_id=exec_id, stream=True)
        for line in output_stream:
            print(line.decode().rstrip())

    def start_network(self):
        try:
            self.client.networks.create(self.network_name, driver="bridge")
        except APIError as e:
            # Assume already exists
            print(e)
        return self.client.networks.get("my_network")

    def stop_network(self):
        self.client.networks.get("my_network").remove()

    def get_image(self, dockerfile_info: DockerfileInfo):
        if dockerfile_info.dockerfile_directory is not None:
            # Build image from Dockerfile
            self.client.images.build(
                path=get_absolute_path(dockerfile_info.dockerfile_directory),
                tag=dockerfile_info.image_tag,
            )
        else:
            # Pull or use existing image
            self.client.images.pull(dockerfile_info.image_tag)

    def run_container(
        self,
        docker_info: DockerInfo,
    ):
        print(f"Running container {docker_info.name}")
        try:
            container = self.client.containers.get(docker_info.name)
            if container.status == "running":
                print(f"Container '{docker_info.name}' is already running")
                return container
            print("Restarting container...")
            container.start()
            return container
        except NotFound:
            # Container does not exist; proceed to build/pull image and run
            pass

        self.get_image(docker_info.dockerfile_info)

        container = self.client.containers.run(
            image=docker_info.dockerfile_info.image_tag,
            volumes=(
                docker_info.volume_info.build_volumes()
                if docker_info.volume_info is not None
                else None
            ),
            command=docker_info.command,
            entrypoint=docker_info.entrypoint,
            detach=True,
            name=docker_info.name,
            ports=docker_info.ports,
            network=self.network_name,
            environment=docker_info.environment,
            stdout=True,
            stderr=True,
            tty=True,
            healthcheck=(
                docker_info.health_check_info.build_healthcheck()
                if docker_info.health_check_info is not None
                else None
            ),
        )
        return container
