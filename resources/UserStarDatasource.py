from flask import request

from middleware.security import api_required
from resources.PsycopgResource import PsycopgResource, handle_exceptions
from middleware.star_data_sources import (
    StarredDataSourceManager,
)


class UserStarDatasource(PsycopgResource):
    """
    Flask-Restful resource for handling CRUD operations on the 'user_starred_data_sources' table.
    Inherits from PsycopgResource which provides a psycopg2 database connection.
    """

    def __init__(self, **kwargs):
        """
        Initialize the UserStarDatasource resource with a StarredDataSourceManager instance.
        """
        super().__init__(**kwargs)
        self.data_manager = StarredDataSourceManager(self.psycopg2_connection)

    @api_required
    @handle_exceptions
    def post(self) -> tuple[dict, int]:
        """
        Handles the creation of a new user star entry.
        Expects 'user_id' and 'data_source_uid' in the request body.
        """
        user_id = request.json["user_id"]
        data_source_uid = request.json["data_source_uid"]
        self.data_manager.create_star(user_id, data_source_uid)
        return {"message": "Starred successfully"}, 201

    @api_required
    @handle_exceptions
    def get(self, user_id: int) -> tuple[dict, int]:
        """
        Retrieves all starred data sources for a given user ID.
        """
        data = self.data_manager.read_all_stars_for_user(user_id)
        if data:
            return {"data": data}, 200
        else:
            return {"message": "No starred data sources found"}, 404

    @api_required
    @handle_exceptions
    def delete(self) -> tuple[dict, int]:
        """
        Removes a star from a data source for a user.
        Expects 'user_id' and 'data_source_uid' in the request body to identify the star to remove.
        """
        user_id = request.json["user_id"]
        data_source_uid = request.json["data_source_uid"]
        self.data_manager.delete_star(user_id, data_source_uid)
        return {"message": "Unstarred successfully"}, 200
