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

@bp.route("/uboa-nav/query-users", methods=["GET", "POST"])
@auth_required()
@roles_accepted("administrator")
def query_users_and_render():
    """
    Query users and render.
    """
    current_app.logger.debug("Query users and render")
    if request.method == "POST":
        filters = request.form.to_dict(flat=False).copy()
        filters["offset"] = [""]
        users = query_users(filters)

        return render_template("users_management/users_nav.html", users=users, filters=filters)
    # end if
    return render_template("users_management/query_users.html")

@bp.route("/uboa-nav/query-users-pages", methods=["GET", "POST"])
@auth_required()
@roles_accepted("administrator")
def query_users_pages():
    """
    Query users using pages and render.
    """
    current_app.logger.debug("Query users using pages and render")
    filters = request.json
    users = query_users(filters)
    
    return render_template("users_management/users_nav.html", users=users, filters=filters)

def query_users(filters):
    """
    Query users.
    """
    current_app.logger.debug("Query users")

    kwargs = set_filters_for_query_users_or_roles(filters)
    users = query.get_users(**kwargs)

    return users

@bp.route("/uboa-nav/query-roles", methods=["GET", "POST"])
@auth_required()
@roles_accepted("administrator")
def query_roles_and_render():
    """
    Query roles and render.
    """
    current_app.logger.debug("Query roles and render")
    if request.method == "POST":
        filters = request.form.to_dict(flat=False).copy()
        filters["offset"] = [""]
        roles = query_roles(filters)

        return render_template("users_management/roles_nav.html", roles=roles, filters=filters)
    # end if
    return render_template("users_management/query_roles.html")

@bp.route("/uboa-nav/query-roles-pages", methods=["GET", "POST"])
@auth_required()
@roles_accepted("administrator")
def query_roles_pages():
    """
    Query roles using pages and render.
    """
    current_app.logger.debug("Query roles using pages and render")
    filters = request.json
    roles = query_roles(filters)
    
    return render_template("users_management/roles_nav.html", roles=roles, filters=filters)

def query_roles(filters):
    """
    Query roles.
    """
    current_app.logger.debug("Query roles")

    kwargs = set_filters_for_query_users_or_roles(filters)
    roles = query.get_roles(**kwargs)

    return roles

def set_filters_for_query_users_or_roles(filters):
    """
    Set filter for query users or query roles.
    """
    kwargs = {}

    if filters["email"][0] != "":
        op="notlike"
        if not "email_notlike_check" in filters:
            op="like"
        # end if
        kwargs["emails"] = {"filter": filters["email"][0], "op": filters["email_operator"][0]}
    # end if
    elif "emails" in filters and filters["emails"][0] != "":
        op="notin"
        if not "email_notin_check" in filters:
            op="in"
        # end if
        kwargs["emails"] = {"filter": [], "op": op}
        i = 0
        for email in filters["emails"]:
            kwargs["emails"]["filter"].append(email)
            i+=1
        # end for
    # end if
    
    if filters["username"][0] != "":
        op="notlike"
        if not "username_notlike_check" in filters:
            op="like"
        # end if
        kwargs["usernames"] = {"filter": filters["username"][0], "op": filters["username_operator"][0]}
    # end if
    elif "usernames" in filters and filters["usernames"][0] != "":
        op="notin"
        if not "username_notin_check" in filters:
            op="in"
        # end if
        kwargs["usernames"] = {"filter": [], "op": op}
        i = 0
        for username in filters["usernames"]:
            kwargs["usernames"]["filter"].append(username)
            i+=1
        # end for
    # end if
    
    if filters["group"][0] != "":
        op="notlike"
        if not "group_notlike_check" in filters:
            op="like"
        # end if
        kwargs["groups"] = {"filter": filters["group"][0], "op": filters["group_operator"][0]}
    # end if
    elif "groups" in filters and filters["groups"][0] != "":
        op="notin"
        if not "group_notin_check" in filters:
            op="in"
        # end if
        kwargs["groups"] = {"filter": [], "op": op}
        i = 0
        for group in filters["groups"]:
            kwargs["groups"]["filter"].append(group)
            i+=1
        # end for
    # end if
    
    if filters["role"][0] != "":
        op="notlike"
        if not "role_notlike_check" in filters:
            op="like"
        # end if
        kwargs["roles"] = {"filter": filters["role"][0], "op": filters["role_operator"][0]}
    # end if
    elif "roles" in filters and filters["roles"][0] != "":
        op="notin"
        if not "role_notin_check" in filters:
            op="in"
        # end if
        kwargs["roles"] = {"filter": [], "op": op}
        i = 0
        for role in filters["roles"]:
            kwargs["roles"]["filter"].append(role)
            i+=1
        # end for
    # end if

    if filters["active"][0] != "":
        kwargs["active"] = bool(util.strtobool(filters["active"][0]))
    # end if

    # Query restrictions
    if filters["order_by"][0] != "":
        descending = True
        if not "order_descending" in filters:
            descending = False
        # end if
        kwargs["order_by"] = {"field": filters["order_by"][0], "descending": descending}
    # end if

    if filters["limit"][0] != "":
        kwargs["limit"] = filters["limit"][0]
    # end if

    if filters["offset"][0] != "":
        kwargs["offset"] = filters["offset"][0]
    # end if

    return kwargs

@bp.route("/uboa-nav/query-users-by-group/<string:group>")
@auth_required()
@roles_accepted("administrator")
def query_user_by_group(group):
    """
    Query users belonging to the group.
    """
    current_app.logger.debug("Query user by group")
    users = query.get_users(groups={"filter": group, "op": "=="})

    filters = {}
    filters["offset"] = [""]
    filters["limit"] = ["100"]
    
    return render_template("users_management/users_nav.html", users=users, filters=filters)

@bp.route("/uboa-nav/query-users-by-role/<string:role>")
@auth_required()
@roles_accepted("administrator")
def query_user_by_role(role):
    """
    Query users belonging to the role.
    """
    current_app.logger.debug("Query user by role")
    users = query.get_users(roles={"filter": role, "op": "=="})

    filters = {}
    filters["offset"] = [""]
    filters["limit"] = ["100"]
    
    return render_template("users_management/users_nav.html", users=users, filters=filters)

@bp.route("/uboa-nav/query-jsonify-<string:filter>")
@auth_required()
@roles_accepted("administrator")
def query_jsonify_filter(filter):
    """
    Query all the emails, usernames or groups
    """
    current_app.logger.debug("Query all the emails, usernames or groups")

    # Get limit and offset values
    limit = request.args.get("limit")
    offset = request.args.get("offset")
    search = request.args.get("search")

    # Set the filters for the query
    kwargs = {}
    kwargs["limit"] = limit
    kwargs["offset"] = offset   
    
    if filter == "emails":
        kwargs["emails"] = {"filter": search, "op": "=="}
    elif filter == "usernames":
        kwargs["usernames"] = {"filter": search, "op": "=="}
    elif filter == "groups":
        kwargs["groups"] = {"filter": "%" + search + "%", "op": "like"}

    users = query.get_users(**kwargs)
    jsonified_users = [user.jsonify() for user in users]
    return jsonify(jsonified_users)

@bp.route("/uboa-nav/query-jsonify-roles")
@auth_required()
@roles_accepted("administrator")
def query_jsonify_roles():
    """
    Query all the roles
    """
    current_app.logger.debug("Query all the roles")

    # Get limit and offset values
    limit = request.args.get("limit")
    offset = request.args.get("offset")
    search = request.args.get("search")

    # Set the filters for the query
    kwargs = {}
    kwargs["limit"] = limit
    kwargs["offset"] = offset   
    kwargs["roles"] = {"filter": "%" + search + "%", "op": "like"}
    
    roles = query.get_roles(**kwargs)
    jsonified_roles = [role.jsonify() for role in roles]
    return jsonify(jsonified_roles)

@bp.route("/uboa-nav/query-jsonify-user-roles/<uuid:user_uuid>")
@auth_required()
@roles_accepted("administrator")
def query_jsonify_user_roles(user_uuid):
    """
    Query roles related to the user with the corresponding received UUID.
    """
    current_app.logger.debug("Query roles corresponding to the user with the specified UUID " + str(user_uuid))
    users = query.get_users(user_uuids = {"filter": [user_uuid], "op": "in"})
    jsonified_roles = [user_roles.jsonify() for user in users for user_roles in user.roles]
    return jsonify(jsonified_roles)

@bp.route("/uboa-nav/prepare-deletion-of-users", methods=["POST"])
@auth_required()
@roles_accepted("administrator")
def prepare_deletion_of_users():
    """
    Prepare deletion of selected users.
    """
    current_app.logger.debug("Prepare deletion of selected users")
    filters = request.json

    users_from_uuids = query.get_users(user_uuids = {"filter": filters["users"], "op": "in"})
    users = query.get_users(usernames = {"filter": [user.username for user in users_from_uuids], "op": "in"})

    return render_template("users_management/deletion_of_users.html", users=users)

@bp.route("/uboa-nav/delete-users", methods=["POST"])
@auth_required()
@roles_accepted("administrator")
def delete_users():
    """
    Delete selected users.
    """
    current_app.logger.debug("Delete selected users")
    filters = request.json
    
    query.get_users(user_uuids = {"filter": filters["users"], "op": "in"}, delete=True)

    return render_template("users_management/query_users.html")