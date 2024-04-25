def save_search(used_id: str, search_query: str) -> str:
    """
    Save a search query associated with the user
    and return a permanent id for the search url
    :param used_id:
    :param search_query:
    :return:
    """
    raise NotImplementedError()


def get_saved_searches(used_id: str, limit: int) -> list:
    """
    Retrieve saved searches for user up to limit
    :param used_id:
    :param limit:
    :return:
    """
    raise NotImplementedError()


def execute_search(search_id: str) -> list:
    """
    Execute a saved search by the search id
    :param search_id:
    :return:
    """
    raise NotImplementedError()
