"""
Reporting control section definition

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

bp = Blueprint("reporting_control", __name__, url_prefix="/reporting_control")
query = Query()

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

@bp.route("/reporting_control", methods=["GET", "POST"])
@auth_required()
@roles_accepted("administrator", "service_administrator", "operator", "analyst", "operator_observer")
def show_reporting_control():
    """
    Reporting control view of the BOA.
    """
    current_app.logger.debug("Reporting control view")

    template_name = request.args.get("template")

    filters = {}
    filters["limit"] = ["100"]    
    if request.method == "POST":
        filters = request.form.to_dict(flat=False).copy()
    # end if
    filters["offset"] = [""]

    if "template" in filters:
        template_name = filters["template"][0]
    # end if

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
    filters["template_name"] = [template_name]    
    
    return query_reports_and_render(start_filter, stop_filter, template_name = template_name, filters = filters)

@bp.route("/reporting-control-pages", methods=["POST"])
@auth_required()
@roles_accepted("administrator", "service_administrator", "operator", "analyst", "operator_observer")
def query_reporting_control_pages():
    """
    Reporting control view of the BOA using pages.
    """
    current_app.logger.debug("Reporting control view using pages")
    filters = request.json
    start_filter, stop_filter = get_start_stop_filters(filters)

    template_name = filters["template_name"][0]
    
    return query_reports_and_render(start_filter, stop_filter, template_name = template_name, filters = filters)

@bp.route("/sliding_reporting_control_parameters", methods=["GET", "POST"])
@auth_required()
@roles_accepted("administrator", "service_administrator", "operator", "analyst", "operator_observer")
def show_sliding_reporting_control_parameters():
    """
    Reporting control view of the BOA.
    """
    current_app.logger.debug("Sliding reporting control view with parameters")

    window_delay = float(request.args.get("window_delay"))
    window_size = float(request.args.get("window_size"))
    repeat_cycle = float(request.args.get("repeat_cycle"))
    template_name = request.args.get("template")
    
    start_filter = {
        "date": (datetime.datetime.now() - datetime.timedelta(days=window_delay)).isoformat(),
        "operator": "<="
    }
    stop_filter = {
        "date": (datetime.datetime.now() - datetime.timedelta(days=(window_delay+window_size))).isoformat(),
        "operator": ">="
    }

    sliding_window = {
        "window_delay": window_delay,
        "window_size": window_size,
        "repeat_cycle": repeat_cycle,
    }

    return query_reports_and_render(start_filter, stop_filter, sliding_window, template_name = template_name)
    
@bp.route("/sliding_reporting_control", methods=["GET", "POST"])
@auth_required()
@roles_accepted("administrator", "service_administrator", "operator", "analyst", "operator_observer")
def show_sliding_reporting_control():
    """
    Reporting control view of the BOA.
    """
    current_app.logger.debug("Sliding reporting control view")

    template_name = request.args.get("template")

    window_delay_parameter = None
    window_size_parameter = None
    repeat_cycle_parameter = None
    
    if request.method == "POST":

        if request.form["reporting_control_window_delay"] != "":
            window_delay_parameter = float(request.form["reporting_control_window_delay"])
        # end if

        if request.form["reporting_control_window_size"] != "":
            window_size_parameter = float(request.form["reporting_control_window_size"])
        # end if

        if request.form["reporting_control_repeat_cycle"] != "":
            repeat_cycle_parameter = float(request.form["reporting_control_repeat_cycle"])
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

    return query_reports_and_render(start_filter, stop_filter, sliding_window, template_name = template_name)

def query_reports_and_render(start_filter = None, stop_filter = None, sliding_window = None, template_name = None, filters = None):

    kwargs = {}

    # Start filter
    kwargs["triggering_time_filters"] = [{"date": start_filter["date"], "op": start_filter["operator"]}]
    
    # Stop filter
    kwargs["triggering_time_filters"].append({"date": stop_filter["date"], "op": stop_filter["operator"]})

    # Set offset and limit for the query
    if filters and "offset" in filters and filters["offset"][0] != "":
        kwargs["offset"] = filters["offset"][0]
    # end if
    if filters and "limit" in filters and filters["limit"][0] != "":
        kwargs["limit"] = filters["limit"][0]
    # end if

    if template_name == "alerts":
        # Set order by ingestion_time descending
        kwargs["order_by"] = {"field": "ingestion_time", "descending": True}

        # Obtain report alerts and then the reports
        report_alerts = query.get_report_alerts(**kwargs)
        reports = query.get_reports(report_uuids = {"filter": [report_alert.report_uuid for report_alert in report_alerts], "op": "in"})
    elif template_name == "alerts_and_errors":
        # Set order by ingestion_time descending
        kwargs["order_by"] = {"field": "ingestion_time", "descending": True}

        # Obtain report alerts and then the reports
        report_alerts = query.get_report_alerts(**kwargs)
        reports_from_report_alerts = query.get_reports(report_uuids = {"filter": [report_alert.report_uuid for report_alert in report_alerts], "op": "in"})

        # Set order by ingestion_time descending
        kwargs["order_by"] = {"field": "triggering_time", "descending": True}

        # Obtain sources with errors
        kwargs["generation_error"] = {"filter": "true", "op": "=="}
        reports_from_report_errors = query.get_reports(**kwargs)

        reports = list(set(reports_from_report_alerts + reports_from_report_errors))
    else:
        if template_name == "errors":
            kwargs["generation_error"] = {"filter": "true", "op": "=="}
        # end if

        # Set order by ingestion_time descending
        kwargs["order_by"] = {"field": "triggering_time", "descending": True}
        reports = query.get_reports(**kwargs)
    # end if

    # Order reports by triggering time descending
    reports.sort(key=lambda x: x.triggering_time, reverse = True)
    
    reporting_start = stop_filter["date"]
    reporting_stop = start_filter["date"]

    template = "reporting_control/reporting_control.html"
    if template_name != None:
        template = "reporting_control/reporting_control_" + template_name + ".html"
    # end if
    
    return render_template(template, reports=reports, reporting_start=reporting_start, reporting_stop=reporting_stop, sliding_window=sliding_window, filters=filters)
