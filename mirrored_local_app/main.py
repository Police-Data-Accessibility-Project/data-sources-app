"""
Starts a local instance of the application utilizing a database
mirrored from production.

"""
from local_database.constants import RESTORE_SH_DOCKER_PATH, DUMP_SH_DOCKER_PATH
from mirrored_local_app.DockerContainer import DockerContainer
from mirrored_local_app.constants import DATABASE_DOCKER_INFO, DATA_DUMPER_DOCKER_INFO
from mirrored_local_app.docker_manager import DockerManager
from mirrored_local_app.timestamp_checker import TimestampChecker


def main():
    docker_manager = DockerManager()
    db_container = docker_manager.run_container(DATABASE_DOCKER_INFO)
    db_container.wait_for_pg_to_be_ready()


    # Start dockerfile for Datadumper

    # If not last run within 24 hours, run dump operation in Datadumper
    checker = TimestampChecker()
    data_dump_container: DockerContainer = docker_manager.run_container(DATA_DUMPER_DOCKER_INFO)
    _run_dump_if_longer_than_24_hours(checker, data_dump_container)
    _run_database_restore(data_dump_container)
    print("Stopping datadumper container")
    data_dump_container.stop()
    checker.set_last_run_time()
    #
    # container = docker_manager.run_container(APP_DOCKER_INFO)
    # wait_for_health(container)



def _run_database_restore(data_dump_container: DockerContainer) -> None:
    data_dump_container.run_command(
        RESTORE_SH_DOCKER_PATH,
    )


def _run_dump_if_longer_than_24_hours(
    checker: TimestampChecker,
    data_dump_container: DockerContainer
) -> None:
    if checker.last_run_within_24_hours():
        print("Last run within 24 hours, skipping dump...")
        return
    data_dump_container.run_command(
        DUMP_SH_DOCKER_PATH,
    )

if __name__ == "__main__":
    main()
