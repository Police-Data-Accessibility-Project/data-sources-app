from datetime import datetime


def get_datetime_now() -> str:
    return datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
