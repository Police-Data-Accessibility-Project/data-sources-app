import argparse
import subprocess


DATA_DUMPER_ARGS = [
    "docker",
    "compose",
    "-f",
    "DataDumper/docker-compose.yml",
    "run",
    "--rm",
    "pg_dump",
    "bash",
]


def execute_script(script_path, args):
    """Executes a Bash script with optional arguments."""
    try:
        command = ["bash", script_path] + args
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("Output:\n", result.stdout)
        if result.stderr:
            print("Errors:\n", result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error executing {script_path}: {e}")


def spin_up_local_database():
    result = subprocess.run(
        [
            "docker",
            "compose",
            "-f",
            "docker-compose.yml",
            "up",
            "-d",
        ],
        capture_output=True,
        text=True,
    )
    print(result)


def dump_from_database():
    result = subprocess.run(
        [*DATA_DUMPER_ARGS, "/usr/local/bin/dump.sh"], capture_output=True, text=True
    )
    print(result)


def restore_to_local_database():
    result = subprocess.run(
        [*DATA_DUMPER_ARGS, "/usr/local/bin/restore.sh"], capture_output=True, text=True
    )
    print(result)


def main():
    parser = argparse.ArgumentParser(
        description="Execute a Bash script with arguments."
    )
    parser.add_argument(
        "--restore_only",
        action="store_true",
        help="Only restore and not dump the database. Saves time in dump stage.",
    )

    args = parser.parse_args()

    restore_only = args.restore_only

    if restore_only:
        print("Restoring DB")
    else:
        print("Dumping and restoring DB")

    spin_up_local_database()
    if not restore_only:
        dump_from_database()
    restore_to_local_database()

    # TODO: Add alembic?


if __name__ == "__main__":
    main()
