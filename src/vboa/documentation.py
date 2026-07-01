"""
VBOA documentation section definition

Written by Daniel Brosnan Blázquez

module vboa
"""
# Import flask utilities
from flask import Blueprint, render_template

# Import vboa security
from vboa.security import auth_required, roles_accepted

bp = Blueprint("documentation", __name__)

version="1.0"

@bp.route("/documentation-eboa")
@auth_required()
@roles_accepted("administrator", "service_administrator", "operator", "analyst", "operator_observer", "observer")
def documentation_eboa():
    """
    Show EBOA documentation page.
    """

    return render_template("documentation/eboa.html")

@bp.route("/documentation-eboa-faq")
@auth_required()
@roles_accepted("administrator", "service_administrator", "operator", "analyst", "operator_observer", "observer")
def documentation_eboa_faq():
    """
    Show EBOA FAQ documentation page.
    """

    return render_template("documentation/eboa_faq.html")

@bp.route("/documentation-vboa")
@auth_required()
@roles_accepted("administrator", "service_administrator", "operator", "analyst", "operator_observer", "observer")
def documentation_vboa():
    """
    Show VBOA documentation page.
    """

    return render_template("documentation/vboa.html")

@bp.route("/documentation-vboa-faq")
@auth_required()
@roles_accepted("administrator", "service_administrator", "operator", "analyst", "operator_observer", "observer")
def documentation_vboa_faq():
    """
    Show VBOA FAQ documentation page.
    """

    return render_template("documentation/vboa_faq.html")

@bp.route("/documentation-boa-tailoring")
@auth_required()
@roles_accepted("administrator", "service_administrator", "operator", "analyst", "operator_observer", "observer")
def documentation_boa_tailoring():
    """
    Show BOA tailoring documentation page.
    """

    return render_template("documentation/boa_tailoring.html")
