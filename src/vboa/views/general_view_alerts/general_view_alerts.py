"""
General view of alerts section definition

Written by DEIMOS Space S.L. (jubv)

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

bp = Blueprint("general-view-alerts", __name__, url_prefix="/general-view-alerts")
query = Query()
engine = Engine()

# Default configuration
window_delay=0
window_size=0.25
repeat_cycle=5

def get_start_stop_filters(filters):

    start_filter = None
    stop_filter = None
    
    if request.method == "POST":
        if filters["start"][0] != "":
            stop_filter = {
                "date": filters["start"][0],
                "operator": ">="
            }
            if filters["stop"][0] == "":
                start_filter = {
                    "date": (parser.parse(filters["start"][0]) + datetime.timedelta(days=window_size)).isoformat(),
                    "operator": "<="
                }
            # end if            
        # end if

        if filters["stop"][0] != "":
            start_filter = {
                "date": filters["stop"][0],
                "operator": "<="
            }
            if filters["start"][0] == "":
                stop_filter = {
                    "date": (parser.parse(filters["stop"][0]) - datetime.timedelta(days=window_size)).isoformat(),
                    "operator": ">="
                }
            # end if
        # end if

    # end if

    return start_filter, stop_filter

@bp.route("/", methods=["GET", "POST"])
def show_general_view_alerts():
    """
    General view of alerts view of the BOA.
    """
    current_app.logger.debug("General view of alerts view")
    
    filters = {}
    filters["limit"] = ["100"]
    if request.method == "POST":
        filters = request.form.to_dict(flat=False).copy()
    # end if
    filters["offset"] = [""]

    # Initialize reporting period (now - window_size days, now)
    start_filter = {
        "date": (datetime.datetime.now() - datetime.timedelta(days=window_delay)).isoformat(),
        "operator": "<="
    }
    stop_filter = {
        "date": (datetime.datetime.now() - datetime.timedelta(days=(window_delay+window_size))).isoformat(),
        "operator": ">="
    }
    start_filter_calculated, stop_filter_calculated = get_start_stop_filters(filters)
    
    if start_filter_calculated != None:
        start_filter = start_filter_calculated
    # end if

    if stop_filter_calculated != None:
        stop_filter = stop_filter_calculated
    # end if

    filters["start"] = [stop_filter["date"]]
    filters["stop"] = [start_filter["date"]]   
    
    return query_and_render(start_filter, stop_filter, filters = filters)

@bp.route("/general-view-alerts-pages", methods=["POST"])
def query_general_view_alerts_pages():
    """
    General view of alerts view of the BOA using pages.
    """
    current_app.logger.debug("General view of alerts view using pages")
    filters = request.json
    start_filter, stop_filter = get_start_stop_filters(filters)
    
    return query_and_render(start_filter, stop_filter, filters = filters)

@bp.route("/sliding-general-view-alerts-parameters", methods=["GET", "POST"])
def show_sliding_general_view_alerts_parameters():
    """
    General view of alerts view of the BOA.
    """
    current_app.logger.debug("Sliding general view of alerts view with parameters")

    window_delay = float(request.args.get("window_delay"))
    window_size = float(request.args.get("window_size"))
    repeat_cycle = float(request.args.get("repeat_cycle"))
    
    start_filter = {
        "date": (datetime.datetime.now() - datetime.timedelta(days=window_delay)).isoformat(),
        "operator": "<="
    }
    stop_filter = {
        "date": (datetime.datetime.now() - datetime.timedelta(days=(window_delay + window_size))).isoformat(),
        "operator": ">="
    }

    sliding_window = {
        "window_delay": window_delay,
        "window_size": window_size,
        "repeat_cycle": repeat_cycle,
    }

    return query_and_render(start_filter, stop_filter, sliding_window)
    
@bp.route("/sliding-general-view-alerts", methods=["GET", "POST"])
def show_sliding_general_view_alerts():
    """
    General view of alerts view of the BOA.
    """
    current_app.logger.debug("Sliding general view of alerts view")

    window_delay_parameter = None
    window_size_parameter = None
    repeat_cycle_parameter = None
    
    if request.method == "POST":

        if request.form["general_view_alerts_window_delay"] != "":
            window_delay_parameter = float(request.form["general_view_alerts_window_delay"])
        # end if

        if request.form["general_view_alerts_window_size"] != "":
            window_size_parameter = float(request.form["general_view_alerts_window_size"])
        # end if

        if request.form["general_view_alerts_repeat_cycle"] != "":
            repeat_cycle_parameter = float(request.form["general_view_alerts_repeat_cycle"])
        # end if

    # end if

    if not window_delay_parameter:
        window_delay_parameter = window_delay
    # end if

    if not window_size_parameter:
        window_size_parameter = window_size
    # end if

    if not repeat_cycle_parameter:
        repeat_cycle_parameter = repeat_cycle
    # end if

    start_filter = {
        "date": (datetime.datetime.now() - datetime.timedelta(days=window_delay_parameter)).isoformat(),
        "operator": "<="
    }
    stop_filter = {
        "date": (datetime.datetime.now() - datetime.timedelta(days=(window_delay_parameter+window_size_parameter))).isoformat(),
        "operator": ">="
    }

    sliding_window = {
        "window_delay": window_delay_parameter,
        "window_size": window_size_parameter,
        "repeat_cycle": repeat_cycle_parameter,
    }

    return query_and_render(start_filter, stop_filter, sliding_window)

def query_and_render(start_filter = None, stop_filter = None, sliding_window = None, filters = None):

    kwargs = {}

    # Start filter
    kwargs["notification_time_filters"] = [{"date": start_filter["date"], "op": start_filter["operator"]}]
    
    # Stop filter
    kwargs["notification_time_filters"].append({"date": stop_filter["date"], "op": stop_filter["operator"]})

    # Avoid showing the sources related to the ingestion of health data
    kwargs["dim_signatures"] = {"filter": ["BOA_HEALTH"], "op": "notin"}

    # Set offset and limit for the query
    if filters and "offset" in filters and filters["offset"][0] != "":
        kwargs["offset"] = filters["offset"][0]
    # end if
    if filters and "limit" in filters and filters["limit"][0] != "":
        kwargs["limit"] = filters["limit"][0]
    # end if

    # Set order by ingestion_time descending
    kwargs["order_by"] = {"field": "notification_time", "descending": False}

    # Obtain source alerts and then the sources
    source_alerts = query.get_source_alerts(**kwargs)
    
    # Remove filter by DIM signature
    del kwargs["dim_signatures"]

    # Obtain report alerts and then the reports
    report_alerts = query.get_report_alerts(**kwargs)

    # Obtain event alerts and then the events
    event_alerts = query.get_event_alerts(**kwargs)

    # Obtain annotation alerts and then the annotations
    annotation_alerts = query.get_annotation_alerts(**kwargs)

    # Obtain explicit ref alerts and then the explicit refs
    er_alerts = query.get_explicit_ref_alerts(**kwargs)
    
    reporting_start = stop_filter["date"]
    reporting_stop = start_filter["date"]

    template = "general_view_alerts/general_view_alerts.html"

    return render_template(template, source_alerts=source_alerts, event_alerts=event_alerts, annotation_alerts=annotation_alerts, report_alerts=report_alerts, er_alerts=er_alerts, reporting_start=reporting_start, reporting_stop=reporting_stop, sliding_window=sliding_window, filters=filters)
