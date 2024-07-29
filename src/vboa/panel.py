"""
VBOA inital panel section definition

Written by DEIMOS Space S.L. (dibb)

module vboa
"""
# Import flask utilities
from flask import Blueprint, render_template

# Import vboa security
from vboa.security import auth_required, roles_accepted

bp = Blueprint("panel", __name__)

version="1.0"

@bp.route("/")
@auth_required()
@roles_accepted("administrator", "service_administrator", "operator", "analyst", "operator_observer", "observer")
def index():
    """
    Show initial panel.
    """

    return render_template("panel/index.html")
