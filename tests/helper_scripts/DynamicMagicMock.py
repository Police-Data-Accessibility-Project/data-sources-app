from unittest.mock import patch, MagicMock


class DynamicMagicMock:
    """
    A helper class to create a large number of MagicMock objects dynamically,
    with optional patching of specific attributes and setting of return values.

    Example Usage:
    --------------
    class UpdateArchivesDataMocks(DynamicMagicMock):
        archives_put_broken_as_of_results: MagicMock
        archives_put_last_cached_results: MagicMock
        make_response: MagicMock

    patch_root = "middleware.archives_queries"

    return_values = {
        'archives_put_last_cached_results': 'mocked cursor',
        'make_response': 12345
    }

    mock = UpdateArchivesDataMocks(patch_root, return_values)

    Features:
    ---------
    - Dynamically creates MagicMock objects for each annotated attribute.
    - Patches specified attributes using provided patch paths.
    - Allows optional setting of return values for MagicMock objects.
    - Provides a method to stop all active patches when done.

    Methods:
    --------
    - __init__(self, patch_root: str, mocks_to_patch: list = None, return_values=None): Initializes the class.
    - __post_init__(self, mocks_to_patch: list = None, return_values=None): Builds the MagicMock objects.
    - build_mocks_with_dynamic_patching(self, mocks_to_patch: list, return_values: dict): Builds the MagicMock objects with dynamic patching.


    """

    def __init__(self, patch_root: str = "", return_values=None):
        self._patch_root = patch_root
        self.__post_init__(return_values)

    def __post_init__(self,return_values=None) -> None:
        self._patchers = {}
        if return_values is None:
            return_values = {}
        self.build_mocks_with_dynamic_patching(return_values)

    def build_mocks_with_dynamic_patching(self, return_values: dict):
        for attribute, attr_type in self.__annotations__.items():
            mock = self.create_dynamic_patch(attribute)
            self.mock_return_value_if_specified(attribute, mock, return_values)
            setattr(self, attribute, mock)

    def create_dynamic_patch(self, attribute: str) -> MagicMock:
        """
        Note that this assumes that the name of the attribute is an exact match
         to the function being patched following the patch root
        :param attribute:
        :return:
        """
        patcher = patch(f"{self._patch_root}.{attribute}", new_callable=MagicMock)
        self._patchers[attribute] = patcher
        mock = patcher.start()
        return mock

    def mock_return_value_if_specified(self, attribute: str, mock: MagicMock, return_values: dict):
        if attribute in return_values:
            mock.return_value = return_values[attribute]

    def __getattr__(self, name: str) -> MagicMock:
        """
        Create additional MagicMock objects if not already created
        :param name:
        :return:
        """
        mock = MagicMock()
        setattr(self, name, mock)
        return mock

    def stop_patches(self):
        """
        Stop all active patches.
        """
        for patcher in self._patchers.values():
            patcher.stop()
