from middleware.util.env import get_env_variable
from mirrored_local_app.models.docker import DockerInfo
from mirrored_local_app.models.docker_file import DockerfileInfo
from mirrored_local_app.models.health_check import HealthCheckInfo
from mirrored_local_app.models.volume import VolumeInfo
from root import ROOT_PATH

DATA_DUMPER_PATH = str(ROOT_PATH / "local_database" / "DataDumper")

APP_DOCKER_INFO = DockerInfo(
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

DATA_DUMPER_DOCKER_INFO = DockerInfo(
        dockerfile_info=DockerfileInfo(
            image_tag="datadumper",
            dockerfile_directory=DATA_DUMPER_PATH,
        ),
        volume_info=VolumeInfo(
            host_path=f"{DATA_DUMPER_PATH}/dump",
            container_path="/dump"
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

DATABASE_DOCKER_INFO = DockerInfo(
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
        health_check_info=HealthCheckInfo(
            test=["pg_isready", "-U", "test_source_collector_user", "-h", "127.0.0.1", "-p", "5432"],
            interval=1,
            timeout=3,
            retries=30,
            start_period=2
        )
    )