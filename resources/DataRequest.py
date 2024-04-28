from flask import request

from middleware.data_requests import DataRequestsManager
from middleware.security import api_required
from resources.PsycopgResource import PsycopgResource, handle_exceptions


# TODO: Should I include type checking for the request body?
class DataRequest(PsycopgResource):
    """
    Flask-Restful resource for handling CRUD operations on the 'data_requests' table.
    Inherits from PsycopgResource which provides a psycopg2 database connection.
    """

    def __init__(self, **kwargs):
        """
        Initialize the DataRequest resource with a DataRequestsManager instance.
        """
        super().__init__(**kwargs)
        self.data_manager = DataRequestsManager(self.psycopg2_connection)

    @api_required
    @handle_exceptions
    def post(self) -> tuple[dict, int]:
        """
        Handles the creation of a new data request.
        Expects 'submission_notes' and 'submitter_contact_info' in the request body.
        """
        submission_notes = request.json["submission_notes"]
        submitter_contact_info = request.json["submitter_contact_info"]
        record_id = self.data_manager.create_request(
            submission_notes, submitter_contact_info
        )
        return {"message": "Created successfully", "id": record_id}, 201

    @api_required
    @handle_exceptions
    def get(self) -> tuple[dict, int]:
        """
        Retrieves a data request by ID.
        """
        request_id = request.json["request_id"]
        data = self.data_manager.read_request(request_id)
        if data:
            return {"data": data}, 200
        else:
            return {"message": "Data request not found"}, 404

    @api_required
    @handle_exceptions
    def put(self) -> tuple[dict, int]:
        """
        Updates an existing data request.
        Expects any of the updatable fields in the request body.
        """
        request_id = request.json["request_id"]
        updates = request.json
        self.data_manager.update_request(request_id, **updates)
        return {"message": "Updated successfully"}, 200

    @api_required
    @handle_exceptions
    def delete(self) -> tuple[dict, int]:
        """
        Deletes a data request by ID.
        """
        request_id = request.json["request_id"]
        self.data_manager.delete_request(request_id)
        return {"message": "Deleted successfully"}, 200
