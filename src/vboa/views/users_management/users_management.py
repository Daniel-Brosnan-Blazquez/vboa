"""
Users management section definition

Written by DEIMOS Space S.L.

module vboa
"""
# Import python utilities
import sys
import json
from distutils import util
import shlex
from subprocess import Popen, PIPE

# Import flask utilities
from flask import Blueprint, flash, g, current_app, redirect, render_template, request, url_for, send_from_directory
from flask_debugtoolbar import DebugToolbarExtension
from flask import jsonify

# Import eboa utilities
from uboa.engine.query import Query
import uboa.engine.engine as uboa_engine
from uboa.engine.engine import Engine

# Import auxiliary functions
from eboa.triggering.eboa_triggering import get_triggering_conf
from vboa.functions import set_specific_alert_filters

# Import vboa security
from vboa.security import auth_required, roles_accepted

bp = Blueprint("users-management", __name__, url_prefix="/users-management")
query = Query()
engine = Engine()

@bp.route("/uboa-nav", methods=["GET"])
@auth_required()
@roles_accepted("administrator")
def navigate():
    """
    Initial panel for the UBOA navigation functionality.
    """
    return render_template("users_management/query_users.html")