"""
Health monitoring section definition

Written by DEIMOS Space S.L. (dibb)

module vboa
"""
# Import python utilities
import sys
import json
import datetime
from dateutil import parser

# Import flask utilities
from flask import Blueprint, flash, g, current_app, redirect, render_template, request, url_for
from flask_debugtoolbar import DebugToolbarExtension
from flask import jsonify

# Import eboa utilities
from eboa.engine.query import Query
import eboa.engine.engine as eboa_engine
from eboa.engine.engine import Engine

bp = Blueprint("health", __name__, url_prefix="/health")
query = Query()
engine = Engine()

# Default configuration
window_delay=0
window_size=0.25
repeat_cycle=5

def get_start_stop_filters(window_size):

    start_filter = None
    stop_filter = None
    
    if request.method == "POST":

        if request.form["start"] != "":
            stop_filter = {
                "date": request.form["start"],
                "operator": ">"
            }
            if request.form["stop"] == "":
                start_filter = {
                    "date": (parser.parse(request.form["start"]) + datetime.timedelta(days=window_size)).isoformat(),
                    "operator": "<"
                }
            # end if            
        # end if

        if request.form["stop"] != "":
            start_filter = {
                "date": request.form["stop"],
                "operator": "<"
            }
            if request.form["start"] == "":
                stop_filter = {
                    "date": (parser.parse(request.form["stop"]) - datetime.timedelta(days=window_size)).isoformat(),
                    "operator": ">"
                }
            # end if
        # end if

    # end if

    return start_filter, stop_filter


@bp.route("/health", methods=["GET", "POST"])
def show_health():
    """
    Health monitoring view of the BOA.
    """
    current_app.logger.debug("Health monitoring view")

    template_name = request.args.get("template")

    # Initialize reporting period (now - window_size days, now)
    start_filter = {
        "date": (datetime.datetime.now() - datetime.timedelta(days=window_delay)).isoformat(),
        "operator": "<"
    }
    stop_filter = {
        "date": (datetime.datetime.now() - datetime.timedelta(days=(window_delay+window_size))).isoformat(),
        "operator": ">"
    }
    start_filter_calculated, stop_filter_calculated = get_start_stop_filters(window_size)

    if start_filter_calculated != None:
        start_filter = start_filter_calculated
    # end if

    if stop_filter_calculated != None:
        stop_filter = stop_filter_calculated
    # end if

    return query_health_and_render(start_filter, stop_filter, template_name = template_name)

@bp.route("/sliding_health_parameters", methods=["GET", "POST"])
def show_sliding_health_parameters():
    """
    Health monitoring view of the BOA.
    """
    current_app.logger.debug("Sliding health view with parameters")

    window_delay = float(request.args.get("window_delay"))
    window_size = float(request.args.get("window_size"))
    repeat_cycle = float(request.args.get("repeat_cycle"))
    template_name = request.args.get("template")
    
    start_filter = {
        "date": (datetime.datetime.now() - datetime.timedelta(days=window_delay)).isoformat(),
        "operator": "<"
    }
    stop_filter = {
        "date": (datetime.datetime.now() - datetime.timedelta(days=(window_delay+window_size))).isoformat(),
        "operator": ">"
    }

    sliding_window = {
        "window_delay": window_delay,
        "window_size": window_size,
        "repeat_cycle": repeat_cycle,
    }

    return query_health_and_render(start_filter, stop_filter, sliding_window, template_name = template_name)
    
@bp.route("/sliding_health", methods=["GET", "POST"])
def show_sliding_health():
    """
    Health monitoring view of the BOA.
    """
    current_app.logger.debug("Sliding health view")

    template_name = request.args.get("template")

    window_delay_parameter = None
    window_size_parameter = None
    repeat_cycle_parameter = None
    
    if request.method == "POST":

        if request.form["health_window_delay"] != "":
            window_delay_parameter = float(request.form["health_window_delay"])
        # end if

        if request.form["health_window_size"] != "":
            window_size_parameter = float(request.form["health_window_size"])
        # end if

        if request.form["health_repeat_cycle"] != "":
            repeat_cycle_parameter = float(request.form["health_repeat_cycle"])
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
        "operator": "<"
    }
    stop_filter = {
        "date": (datetime.datetime.now() - datetime.timedelta(days=(window_delay_parameter+window_size_parameter))).isoformat(),
        "operator": ">"
    }

    sliding_window = {
        "window_delay": window_delay_parameter,
        "window_size": window_size_parameter,
        "repeat_cycle": repeat_cycle_parameter,
    }

    return query_health_and_render(start_filter, stop_filter, sliding_window, template_name = template_name)

def query_health_and_render(start_filter = None, stop_filter = None, sliding_window = None, template_name = None):

    kwargs = {}

    # Start filter
    if start_filter:
        kwargs["start_filters"] = [{"date": start_filter["date"], "op": start_filter["operator"]}]
    # end if
    
    # Stop filter
    if stop_filter:
        kwargs["stop_filters"] = [{"date": stop_filter["date"], "op": stop_filter["operator"]}]
    # end if

    kwargs["gauge_names"] = {"filter": ["BOA_HEALTH"], "op": "in"}
    
    health_events = query.get_events(**kwargs)

    reporting_start = stop_filter["date"]
    reporting_stop = start_filter["date"]

    current_app.logger.debug(health_events)

    template = "boa_health/boa_health.html"
    if template_name != None:
        template = "boa_health/boa_health_" + template_name + ".html"
    # end if
    
    return render_template(template, health_events=health_events, request=request, reporting_start=reporting_start, reporting_stop=reporting_stop, sliding_window=sliding_window)
