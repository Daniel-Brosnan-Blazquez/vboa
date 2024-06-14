"""
API for querying BOA

Written by DEIMOS Space S.L. (dibb)

module vboa
"""
# Import python utilities
import shutil
import traceback

# Import flask utilities
from flask import Blueprint, request, make_response

# Import eboa utilities
from eboa.engine.query import Query
from eboa.engine import export as eboa_export

bp = Blueprint("query", __name__, url_prefix="/query")
query = Query()

@bp.route("/", methods=["GET"])
def perform_query():
    """
    API for querying BOA.
    """

    if not "Content-Type" in request.headers or request.headers["Content-Type"] != "application/json":
        status = 400
        response_json = {
            "response": {
                "status": status,
                "message": "The method /query needs to receive the JSON data with the relevant query parameters"
            },
            "data": {}
        }
        response = make_response(response_json, status)
        response.mimetype = "application/json"
    else:
        data = {}
        query_parameters = request.get_json()

        try:
            if "events" in query_parameters.keys():
                events = query.get_events(**query_parameters["events"])
                eboa_export.export_events(data, events, group = "events", include_ers = True, include_annotations = True)
            # end if
        except Exception as e:
            status = 400
            response_json = {
                "response": {
                    "status": status,
                    "message": f"The method /query needs to receive correct filters. The exception raised was: {str(e)}. The traceback generated was: {traceback.format_exc()}"
                },
                "data": {}
            }
            response = make_response(response_json, status)
            response.mimetype = "application/json"
        else:
            status = 200
            response_json = {
                "response": {
                    "status": status,
                    "message": "Query solved"
                },
                "data": data
            }
            response = make_response(response_json, status)
            response.mimetype = "application/json"
        # end try
    # end if
    
    return response
