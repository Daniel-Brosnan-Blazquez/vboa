"""
API for getting metrics from BOA

Written by DEIMOS Space S.L. (dibb)

module vboa
"""
# Import python utilities
import shutil

# Import flask utilities
from flask import Blueprint, make_response

bp = Blueprint("metrics", __name__, url_prefix="/metrics")

@bp.route("/", methods=["GET"])
def provide_metrics():
    """
    API for getting metrics from BOA.
    """

    metrics_to_publish_file_path = "/metrics/metrics_to_publish.txt"

    metrics_file_path = "/metrics/metrics.txt"

    shutil.move(metrics_to_publish_file_path, metrics_file_path)

    # Read metrics
    with open(metrics_file_path, "r+") as metrics_file:
        metrics = metrics_file.read()
    # end with

    response = make_response(metrics, 200)
    response.mimetype = "text/plain"
    
    return response
