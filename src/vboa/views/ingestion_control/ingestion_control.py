"""
Ingestion control section definition

Written by DEIMOS Space S.L. (dibb)

module vboa
"""
# Import python utilities
import sys
import json
import datetime
from dateutil import parser
import os
import tempfile
import shutil

# Import flask utilities
from flask import Blueprint, current_app, render_template, request, redirect, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from flask_debugtoolbar import DebugToolbarExtension

# Import eboa utilities
from eboa.engine.query import Query
import eboa.engine.engine as eboa_engine
from eboa.engine.engine import Engine
import eboa.triggering.eboa_triggering as eboa_triggering

# Import SQLAlchemy exceptions
from sqlalchemy.orm.exc import DetachedInstanceError

# Import vboa security
from vboa.security import auth_required, roles_accepted

# Import service management
import vboa.service_management as service_management

bp = Blueprint("ingestion_control", __name__, url_prefix="/ingestion_control")
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

@bp.route("/ingestion_control", methods=["GET", "POST"])
@auth_required()
@roles_accepted("administrator", "service_administrator", "operator", "analyst", "operator_observer")
def show_ingestion_control():
    """
    Ingestion control view of the BOA.
    """
    current_app.logger.debug("Ingestion control view")

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
    
    return query_sources_and_render(start_filter, stop_filter, template_name = template_name, filters = filters)

@bp.route("/ingestion-control-pages", methods=["POST"])
@auth_required()
@roles_accepted("administrator", "service_administrator", "operator", "analyst", "operator_observer")
def query_ingestion_control_pages():
    """
    Ingestion control view of the BOA using pages.
    """
    current_app.logger.debug("Ingestion control view using pages")
    filters = request.json
    start_filter, stop_filter = get_start_stop_filters(filters)

    template_name = filters["template_name"][0]
    
    return query_sources_and_render(start_filter, stop_filter, template_name = template_name, filters = filters)

@bp.route("/sliding_ingestion_control_parameters", methods=["GET", "POST"])
@auth_required()
@roles_accepted("administrator", "service_administrator", "operator", "analyst", "operator_observer")
def show_sliding_ingestion_control_parameters():
    """
    Ingestion control view of the BOA.
    """
    current_app.logger.debug("Sliding ingestion control view with parameters")

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

    return query_sources_and_render(start_filter, stop_filter, sliding_window, template_name = template_name)
    
@bp.route("/sliding_ingestion_control", methods=["GET", "POST"])
@auth_required()
@roles_accepted("administrator", "service_administrator", "operator", "analyst", "operator_observer")
def show_sliding_ingestion_control():
    """
    Ingestion control view of the BOA.
    """
    current_app.logger.debug("Sliding ingestion control view")

    template_name = request.args.get("template")

    window_delay_parameter = None
    window_size_parameter = None
    repeat_cycle_parameter = None
    
    if request.method == "POST":

        if request.form["ingestion_control_window_delay"] != "":
            window_delay_parameter = float(request.form["ingestion_control_window_delay"])
        # end if

        if request.form["ingestion_control_window_size"] != "":
            window_size_parameter = float(request.form["ingestion_control_window_size"])
        # end if

        if request.form["ingestion_control_repeat_cycle"] != "":
            repeat_cycle_parameter = float(request.form["ingestion_control_repeat_cycle"])
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

    return query_sources_and_render(start_filter, stop_filter, sliding_window, template_name = template_name)

def query_sources_and_render(start_filter = None, stop_filter = None, sliding_window = None, template_name = None, filters = None):

    kwargs = {}

    # Start filter
    kwargs["reception_time_filters"] = [{"date": start_filter["date"], "op": start_filter["operator"]}]
    
    # Stop filter
    kwargs["reception_time_filters"].append({"date": stop_filter["date"], "op": stop_filter["operator"]})

    # Avoid showing the sources related to the ingestion of health data
    kwargs["dim_signatures"] = {"filter": ["BOA_HEALTH"], "op": "notin"}

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

        # Obtain source alerts and then the sources
        source_alerts = query.get_source_alerts(**kwargs)
        sources = query.get_sources(source_uuids = {"filter": [source_alert.source_uuid for source_alert in source_alerts], "op": "in"})
    elif template_name == "alerts_and_errors":
        # Set order by ingestion_time descending
        kwargs["order_by"] = {"field": "ingestion_time", "descending": True}

        # Obtain source alerts and then the sources
        source_alerts = query.get_source_alerts(**kwargs)
        sources_from_source_alerts = query.get_sources(source_uuids = {"filter": [source_alert.source_uuid for source_alert in source_alerts], "op": "in"})

        # Set order by ingestion_time descending
        kwargs["order_by"] = {"field": "reception_time", "descending": True}

        # Obtain sources with errors
        kwargs["ingestion_error"] = {"filter": "true", "op": "=="}
        sources_from_source_errors = query.get_sources(**kwargs)

        sources = list(set(sources_from_source_alerts + sources_from_source_errors))
    else:
        if template_name == "errors":
            kwargs["ingestion_error"] = {"filter": "true", "op": "=="}
        # end if

        # Set order by reception_time descending
        kwargs["order_by"] = {"field": "reception_time", "descending": True}
        sources = query.get_sources(**kwargs)
    # end if

    # Order sources by reception time descending
    sources.sort(key=lambda x: x.reception_time, reverse = True)
    
    reporting_start = stop_filter["date"]
    reporting_stop = start_filter["date"]

    template = "ingestion_control/ingestion_control.html"
    if template_name != None:
        template = "ingestion_control/ingestion_control_" + template_name + ".html"
    # end if

    return render_template(template, sources=sources, reporting_start=reporting_start, reporting_stop=reporting_stop, sliding_window=sliding_window, filters=filters)

@bp.route("/manual-ingestion", methods=["GET"])
@auth_required()
@roles_accepted("administrator", "service_administrator")
def show_manual_ingestion():
    """
    Initial panel for manually ingest products.
    """
    return render_template("ingestion_control/manual_ingestion.html")

@bp.route("/manual-ingestion/ingest-files", methods=["POST"])
@auth_required()
@roles_accepted("administrator", "service_administrator")
def manual_ingestion_files():
    """
    Ingest the selected files
    """
    current_app.logger.debug("Prepare ingestion of selected files")

    # Create intermediate destination folder
    os.makedirs("/inputs/.boa_manual_ingestion", exist_ok=True)
    
    # Save files to /tmp
    files = request.files.getlist("files")
    for file in files:
        # Save file into a temporary file
        tmp_file = tempfile.mkstemp()
        tmp_file_path = tmp_file[1]
        file.save(tmp_file_path)

        # Move file to the inputs folder so that ORC will get it
        filename = secure_filename(file.filename)
        intermediate_file_path = os.path.join("/inputs/.boa_manual_ingestion", filename)
        final_file_path = os.path.join("/inputs", filename)

        # First move file to intermediate folder to avoid cross-device link failure
        shutil.move(tmp_file_path, intermediate_file_path)
        os.rename(intermediate_file_path, final_file_path)

    # end for

    return {"status": "OK"}

@bp.route("/download-triggering", methods=["GET"])
@auth_required()
@roles_accepted("administrator", "service_administrator")
def download_triggering():
    """
    Method to allow the download of the triggering configuration
    """
    current_app.logger.debug("Download triggering configuration")

    return send_from_directory("/resources_path", "triggering.xml", as_attachment=True)

@bp.route("/download-orc-config", methods=["GET"])
@auth_required()
@roles_accepted("administrator", "service_administrator")
def download_orc_config():
    """
    Method to allow the download of the ORC configuration
    """
    current_app.logger.debug("Download ORC configuration")

    # Get path to ORC configuration
    status = service_management.execute_command("orcValidateConfig -C")
    assert status["return_code"] == 0
    path_to_orc_config = status["output"]
    
    return send_from_directory(path_to_orc_config, "orchestratorConfigFile.xml", as_attachment=True)

