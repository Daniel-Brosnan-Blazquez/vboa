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
    Query events.
    """
    if request.method == "POST":
        current_app.logger.info("form inputs: {}".format(request.form))
        current_app.logger.info("start: {}".format(request.form.getlist("start")))
        query = Query()
        kwargs = {}
        if request.form["source_like"] != "":
            kwargs["source_like"] = {"str": request.form["source_like"], "op": "like"}
        # end if
        if request.form["er_like"] != "":
            kwargs["explicit_ref_like_like"] = {"str": request.form["er_like"], "op": "like"}
        # end if
        if request.form["gauge_name_like"] != "":
            kwargs["gauge_name_like"] = {"str": request.form["gauge_name_like"], "op": "like"}
        # end if
        if request.form["gauge_system_like"] != "":
            kwargs["gauge_system_like"] = {"str": request.form["gauge_system_like"], "op": "like"}
        # end if
        if request.form["start"] != "":
            kwargs["start_filters"] = []
            i = 0
            operators = request.form.getlist("start_operator")
            for start in request.form.getlist("start"):
                kwargs["start_filters"].append({"date": start, "op": operators[i]})
                i+=1
            # end for
        # end if
        if request.form["stop"] != "":
            kwargs["stop_filters"] = []
            i = 0
            operators = request.form.getlist("stop_operator")
            for stop in request.form.getlist("stop"):
                kwargs["stop_filters"].append({"date": stop, "op": operators[i]})
                i+=1
            # end for
        # end if
        if request.form["ingestion_time"] != "":
            kwargs["ingestion_time_filters"] = []
            i = 0
            operators = request.form.getlist("ingestion_time_operator")
            for ingestion_time in request.form.getlist("ingestion_time"):
                kwargs["ingestion_time_filters"].append({"date": ingestion_time, "op": operators[i]})
                i+=1
            # end for
        # end if
        current_app.logger.info("kwargs: {}".format(kwargs))
        events = query.get_events_join(**kwargs)
        current_app.logger.info("events: {}".format(events))
    # end if
    return render_template("eboa_nav/eboa_nav.html")


