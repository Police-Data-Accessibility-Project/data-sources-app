import platform
import subprocess
import sys
import time

import docker
from docker.errors import DockerException

from docker.models.containers import Container


def wait_for_pg_to_be_ready(container: Container):
    for i in range(30):
        exit_code, output = container.exec_run("pg_isready")
        print(output)
        if exit_code == 0:
            return
        time.sleep(1)
    raise Exception("Timed out waiting for postgres to be ready")


def is_docker_running():
    try:
        client = docker.from_env()
        client.ping()
        return True
    except DockerException as e:
        print(f"Docker is not running: {e}")
        return False


def wait_for_health(container, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        container.reload()  # Refresh container state
        state = container.attrs.get("State")
        print(state)
        health = container.attrs.get("State", {}).get("Health", {})
        status = health.get("Status")
        print(f"Health status: {status}")
        if status == "healthy":
            print("Postgres is healthy.")
            return
        elif status == "unhealthy":
            raise Exception("Postgres container became unhealthy.")
        time.sleep(1)
    raise TimeoutError("Timed out waiting for Postgres to become healthy.")


def start_docker_engine():
    system = platform.system()

    match system:
        case "Windows":
            # Use PowerShell to start Docker Desktop on Windows
            subprocess.run(
                ["powershell", "-Command", "Start-Process 'Docker Desktop' -Verb RunAs"]
            )
        case "Darwin":
            # MacOS: Docker Desktop must be started manually or with open
            subprocess.run(["open", "-a", "Docker"])
        case "Linux":
            # Most Linux systems use systemctl to manage Docker
            subprocess.run(["sudo", "systemctl", "start", "docker"])
        case _:
            print(f"Unsupported OS: {system}")
            sys.exit(1)
