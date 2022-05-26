"""
Earth observation section definition

Written by DEIMOS Space S.L. (dibb)

module vboa
"""
# Import python utilities
import sys
import json
import datetime
from dateutil import parser
import os

# Import flask utilities
from flask import Blueprint, flash, g, current_app, redirect, render_template, request, url_for
from flask_debugtoolbar import DebugToolbarExtension
from flask import jsonify

# Import eboa utilities
from eboa.engine.query import Query
import eboa.engine.engine as eboa_engine
from eboa.engine.engine import Engine

# Import SQLAlchemy exceptions
from sqlalchemy.orm.exc import DetachedInstanceError

# Import vboa security
from vboa.security import auth_required, roles_accepted

# Import TLE functions
import tle2czml
import pytz

bp = Blueprint("earth-observation", __name__, url_prefix="/earth-observation")
query = Query()

@bp.route("/navigation", methods=["GET", "POST"])
@auth_required()
@roles_accepted("administrator", "service_administrator", "operator", "analyst", "operator_observer")
def show_navigation():
    """
    Navigation view for Earth observation in BOA.
    """
    current_app.logger.debug("Navigation for Earth observation view")

    return render_template("earth_observation/navigation.html")

@bp.route("/get-czml-orbit", methods=["POST"])
@auth_required()
@roles_accepted("administrator", "service_administrator", "operator", "analyst", "operator_observer")
def get_czml_orbit():
    """
    Get czml orbit from the received TLE and start and stop values
    """

    # Obtain parameters
    filters = request.json
    tle = filters["tle"]
    start = parser.parse(filters["start"])
    stop = parser.parse(filters["stop"])

    czml = json.loads(tle2czml.tle2czml.tles_to_czml(tle, start_time=start.replace(tzinfo=pytz.UTC), end_time=stop.replace(tzinfo=pytz.UTC), silent=True))

    result = {
        "czml": czml,
        "start": start.isoformat(),
        "stop": stop.isoformat(),
        "filters": filters
    }
    
    return jsonify(result)
