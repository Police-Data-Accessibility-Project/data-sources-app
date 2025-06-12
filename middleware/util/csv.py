import csv
from io import BytesIO, StringIO
from typing import Generator, Any

from werkzeug.datastructures import FileStorage


def bytes_to_text_iter(file: BytesIO | FileStorage) -> Generator[str, Any, None]:
    """
    Convert BytesIO file to text iterator
    """
    return (line.decode("utf-8") for line in file)


def read_from_csv(file: str | FileStorage | bytes) -> list[dict[str, Any]]:
    if isinstance(file, FileStorage):
        file = bytes_to_text_iter(file)
    elif isinstance(file, str):
        file = open(file, "r", newline="", encoding="utf-8")
    elif isinstance(file, bytes):
        content = file.decode("utf-8")
        file = StringIO(content)
    return list(csv.DictReader(file))
