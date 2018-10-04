"""
EBOA navigation section definition

Written by DEIMOS Space S.L. (dibb)

module vboa
"""
import sys
# Import flask utilities
from flask import Blueprint, flash, g, current_app, redirect, render_template, request, url_for
from flask_debugtoolbar import DebugToolbarExtension

# Import forms
from vboa.forms.query_events import QueryEvents

# Import eboa utilities
from eboa.engine.query import Query

bp = Blueprint("eboa_nav", __name__, url_prefix="/eboa_nav")

@bp.route("/", methods=["GET", "POST"])
def query_events():
    """
    Show initial panel.
    """
    if request.method == "POST":
        current_app.logger.info("form inputs: {}".format(request.form))
        current_app.logger.info("start: {}".format(request.form.getlist("start")))
        query = Query()
        kwargs = {}
        if request.form["gauge_name_like"] != "":
            kwargs["gauge_name_like"] = {"str": request.form["gauge_name_like"], "op": "like"}
        # end if
        if request.form["gauge_system_like"] != "":
            kwargs["gauge_system_like"] = {"str": request.form["gauge_system_like"], "op": "like"}
        # end if
        if request.form["source_like"] != "":
            kwargs["source_like"] = {"str": request.form["source_like"], "op": "like"}
        # end if
        if request.form["explicit_ref_like_like"] != "":
            kwargs["explicit_ref_like_like"] = {"str": request.form["explicit_ref_like_like"], "op": "like"}
        # end if
        current_app.logger.info("starts: {}".format(request.form.getlist("start")))
        # if request.form["start"] != "":
        #     kwargs["start_filters"] = []
        #     for start in request.form.getlist("start"):
        #     kwargs["start_filters"].append({"date": request.form["start"], "op": request.form["start_operator"]})
        # # end if
        # current_app.logger.info("kwargs: {}".format(kwargs)))
        # events = query.get_events_join(gauge_name_like = ,
        #                                gauge_name_like = {"str": request.form["gauge_name_like"], "op": "like"},
        #                                start_filters = [{"date": request.form["start"], "op": request.form["start_operator"]}],
        #                                stop_filters = [{"date": request.form["stop"], "op": request.form["stop_operator"]}],
        #                                stop_filters = [{"date": request.form["stop"], "op": request.form["stop_operator"]}])
    # end if
    return render_template("eboa_nav/eboa_nav.html")


