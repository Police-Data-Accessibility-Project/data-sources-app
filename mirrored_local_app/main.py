"""
Starts a local instance of the application utilizing a database
mirrored from production.

"""

from middleware.util.env import get_env_variable
from mirrored_local_app.constants import DATA_DUMPER_PATH
from mirrored_local_app.helpers.docker import wait_for_pg_to_be_ready, is_docker_running, wait_for_health, start_docker_engine
from mirrored_local_app.docker_manager import DockerManager
from mirrored_local_app.models.docker import DockerInfo
from mirrored_local_app.models.docker_file import DockerfileInfo
from mirrored_local_app.models.volume import VolumeInfo
from mirrored_local_app.timestamp_checker import TimestampChecker
from root import ROOT_PATH


def main():
    docker_manager = DockerManager()
    # Ensure docker is running, and start if not
    if not is_docker_running():
        start_docker_engine()

    # Ensure Dockerfile for database is running, and if not, start it
    database_docker_info = DockerInfo(
        dockerfile_info=DockerfileInfo(
            image_tag="postgres:15",
        ),
        name="data_sources_app_db_host",
        ports={"5432/tcp": 5432},
        environment={
            "POSTGRES_PASSWORD": "ClandestineCornucopiaCommittee",
            "POSTGRES_USER": "test_data_sources_app_user",
            "POSTGRES_DB": "test_data_sources_app_db",
        },
    )
    container = docker_manager.run_container(database_docker_info)
    wait_for_pg_to_be_ready(container)

    # Start dockerfile for Datadumper
    data_dumper_docker_info = DockerInfo(
        dockerfile_info=DockerfileInfo(
            image_tag="datadumper",
            dockerfile_directory=DATA_DUMPER_PATH,
        ),
        volume_info=VolumeInfo(
            host_path="../local_database/DataDumper/dump", container_path="/dump"
        ),
        name="datadumper",
        environment={
            "DUMP_HOST": get_env_variable("DUMP_HOST"),
            "DUMP_USER": get_env_variable("DUMP_USER"),
            "DUMP_PASSWORD": get_env_variable("DUMP_PASSWORD"),
            "DUMP_NAME": get_env_variable("DUMP_DB_NAME"),
            "DUMP_PORT": get_env_variable("DUMP_PORT"),
            "RESTORE_HOST": "data_sources_app_db_host",
            "RESTORE_USER": "test_data_sources_app_user",
            "RESTORE_PORT": "5432",
            "RESTORE_DB_NAME": "test_data_sources_app_db",
            "RESTORE_PASSWORD": "ClandestineCornucopiaCommittee",
        },
        command="bash",
    )

    # If not last run within 24 hours, run dump operation in Datadumper
    # Check cache if exists and
    checker = TimestampChecker()
    container = docker_manager.run_container(data_dumper_docker_info)
    if checker.last_run_within_24_hours():
        print("Last run within 24 hours, skipping dump...")
    else:
        docker_manager.run_command("/usr/local/bin/dump.sh", container.id)
    docker_manager.run_command("/usr/local/bin/restore.sh", container.id)
    print("Stopping datadumper container")
    container.stop()
    checker.set_last_run_time()

    app_docker_info = DockerInfo(
        dockerfile_info=DockerfileInfo(
            image_tag="data_sources_app",
            dockerfile_directory=str(ROOT_PATH)
        ),
        name="data_sources_app_host",
        ports={"8000/tcp": 8000},
        environment={
            "DO_DATABASE_URL": get_env_variable("DO_DATABASE_URL"),
            "GH_CLIENT_ID": get_env_variable("GH_CLIENT_ID"),
            "GH_CLIENT_SECRET": get_env_variable("GH_CLIENT_SECRET"),
            "FLASK_APP_COOKIE_ENCRYPTION_KEY": get_env_variable(
                "FLASK_APP_COOKIE_ENCRYPTION_KEY"
            ),
            "JWT_SECRET_KEY": get_env_variable("JWT_SECRET_KEY"),
            "MAILGUN_KEY": get_env_variable("MAILGUN_KEY"),
            "WEBHOOK_URL": get_env_variable("WEBHOOK_URL"),
        },
    )
    container = docker_manager.run_container(app_docker_info)
    wait_for_health(container)


if __name__ == "__main__":
    main()
