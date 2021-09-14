"""
Profile settings view

Written by DEIMOS Space S.L.

module vboa
"""

# Import flask utilities
from flask import Blueprint, render_template, request

# Import uboa utilities
import uboa.engine.engine as uboa_engine
from uboa.engine.query import Query
from uboa.engine.engine import Engine

# Import vboa security
from vboa.security import auth_required, roles_accepted

bp = Blueprint("user-profile", __name__, url_prefix="/user-profile")
query = Query()
engine = Engine()

@bp.route("/", methods=["GET"])
@auth_required()
def navigate():
    """
    Initial panel for the user profile settings.
    """
    username = request.args.get("user")
    user = query.get_users(usernames={"filter": username, "op": "=="})

    return render_template("user_profile/user_profile.html", user = user[0])