"""
VBOA inital panel section definition

Written by DEIMOS Space S.L. (dibb)

module vboa
"""
# Import python utilities
import os
from tempfile import mkstemp
import datetime

# Import BOA scheduler
import sboa.scheduler.boa_scheduler as boa_scheduler

# Import flask utilities
from flask import Blueprint, flash, g, redirect, render_template, request, url_for, jsonify

# Import rboa engine
import rboa.engine.engine as rboa_engine
from rboa.engine.engine import Engine

# Import vboa security
from vboa.security import auth_required, roles_accepted

bp = Blueprint("screenshots", __name__)

version="1.0"

###
# Screenshots
###
@bp.route("/save-screenshot", methods=["POST"])
def save_screenshot():
    """
    Save screenshot.
    """

    html = request.json["html"]
    name = request.json["name"]
    group = request.json["group"]
    group_description = request.json["group_description"]

    (_, html_file_path) = mkstemp()
    f= open(html_file_path,"w+")
    f.write(html)
    f.close()
    
    creation_date = datetime.datetime.now().isoformat()
    metadata = {"operations": [{
        "mode": "insert",
        "report": {"name": name,
                   "group": group,
                   "group_description": group_description,
                   "path": html_file_path,
                   "compress": "true",
                   "generation_mode": "MANUAL",
                   "validity_start": creation_date,
                   "validity_stop": creation_date,
                   "triggering_time": creation_date,
                   "generation_start": creation_date,
                   "generation_stop": creation_date,
                   "generator": os.path.basename(__file__),
                   "generator_version": version
        }
    }]
    }

    failures = []
    successes = []
    
    try:
        engine_rboa = Engine()
        returned_statuses = engine_rboa.treat_data(metadata, name)
        engine_rboa.close_session()

        failures = [returned_status for returned_status in returned_statuses if not returned_status["status"] in [rboa_engine.exit_codes["OK"]["status"]]]
        successes = [returned_status for returned_status in returned_statuses if returned_status["status"] in [rboa_engine.exit_codes["OK"]["status"]]]

    except Exception as e:
        failures = [-1]
    # end try

    if len(failures) > 0:
        result = {
            "status": -1,
            "message": "The screenshot could not be saved. The operation returned the exit code: {}".format(failures[0])
        }
    else:
        result = {
            "status": 0,
            "message": "The screenshot has been saved successfully"
        }
    # end if
        
        
    return jsonify(result)
