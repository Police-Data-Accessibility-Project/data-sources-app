import subprocess


def run_command_checked(command: list[str] or str, shell=False):
    result = subprocess.run(
        command, check=True, capture_output=True, text=True, shell=shell
    )
    return result
