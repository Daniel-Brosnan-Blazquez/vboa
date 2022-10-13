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

# Import EBOA Earth observation libraries
import eboa.ingestion.orbit as eboa_orbit
import eboa.ingestion.swath as eboa_swath

# Import utilities for Earth observation analysis
import geopy.distance

bp = Blueprint("earth-observation", __name__, url_prefix="/earth-observation")
query = Query()

# Global variables
orbit = None
semimajor = None

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

    # Stablish orbit
    global orbit
    orbit = eboa_orbit.get_orbit(tle)

    # Stablish semimajor
    global semimajor
    semimajor = eboa_orbit.get_semimajor(tle)

    # Obtain CZML
    czml = json.loads(tle2czml.tle2czml.tles_to_czml(tle, start_time=start.replace(tzinfo=pytz.UTC), end_time=stop.replace(tzinfo=pytz.UTC), silent=True))

    result = {
        "czml": czml,
        "start": start.isoformat(),
        "stop": stop.isoformat(),
        "filters": filters
    }
    
    return jsonify(result)

@bp.route("/get-footprint", methods=["POST"])
@auth_required()
@roles_accepted("administrator", "service_administrator", "operator", "analyst", "operator_observer")
def get_footprint():
    """
    Get czml orbit from the received TLE and start and stop values
    """

    # Obtain parameters
    filters = request.json
    roll = float(filters["roll"])
    pitch = float(filters["pitch"])
    yaw = float(filters["yaw"])
    footprint_start = filters["footprint_start"]
    footprint_duration = float(filters["footprint_duration"])
    footprint_aperture = float(filters["footprint_aperture"])
    footprint_alpha = footprint_aperture / 2

    # Default value of alpha angle for NAOS
    # alpha = 0.705176738839256

    footprint_stop = parser.parse(filters["footprint_start"]) + datetime.timedelta(seconds=footprint_duration)

    footprint = eboa_swath.get_footprint(footprint_start, footprint_stop.isoformat(), footprint_alpha, semimajor = semimajor, satellite_orbit = orbit,
                             roll = roll, pitch = pitch, yaw = yaw)


    # Convert satellite footprint to an array [lon1, lat1, ..., lonN, latN] and calculate footprint
    satellite_footprints = []
    swath = "N/A"
    if len(footprint["satellite_footprints"]) > 0 and len(footprint["satellite_footprints"][0].split(",")) > 0:
        for satellite_footprint in footprint["satellite_footprints"]:
            satellite_footprints.append([coordinate  for coordinates in satellite_footprint.split(",") for coordinate in coordinates.split(" ") + ["0.0"]])
        # end for

        # Calculate swath
        coords_1 = (satellite_footprint[-5], satellite_footprint[-6])
        coords_2 = (satellite_footprint[-2], satellite_footprint[-3])
        swath = geopy.distance.geodesic(coords_1, coords_2).km
    # end if
    
    result = {
        "footprints": satellite_footprints,
        "swath": swath
    }
    
    return jsonify(result)
