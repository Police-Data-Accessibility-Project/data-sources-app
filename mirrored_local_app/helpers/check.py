def check_for_absolute_path(path: str) -> str:
    if len(path) == 0:
        raise ValueError("Path is required")
    if path[0] != "/":
        raise ValueError("Container path must be absolute")
    return path
