"""
EBOA navigation section definition

Written by DEIMOS Space S.L. (dibb)

module vboa
"""
# Import python utilities
import sys
import json
# Import flask utilities
from flask import Blueprint, flash, g, current_app, redirect, render_template, request, url_for
from flask_debugtoolbar import DebugToolbarExtension
from flask import jsonify

# Import eboa utilities
from eboa.engine.query import Query
from eboa.engine.engine import Engine

bp = Blueprint("eboa_nav", __name__, url_prefix="/eboa_nav")

@bp.route("/", methods=["GET"])
def navigate():
    """
    Initial panel for the EBOA navigation functionality.
    """
    return render_template("eboa_nav/query_events.html")

@bp.route("/query-events", methods=["GET", "POST"])
def query_events_and_render():
    """
    Query events and render.
    """
    current_app.logger.debug("Query events and render")
    if request.method == "POST":
        events = query_events()
        show = {}
        show["timeline"]=True
        if not "show_timeline" in request.form:
            show["timeline"] = False
        # end if

        return render_template("eboa_nav/events_nav.html", events=events, show=show)
    # end if
    return render_template("eboa_nav/query_events.html")

def query_events():
    """
    Query events.
    """
    current_app.logger.debug("Query events")

    query = Query()
    kwargs = {}
    if request.form["source_like"] != "":
        kwargs["source_like"] = {"str": request.form["source_like"], "op": "like"}
    # end if
    if "sources" in request.form and request.form["sources"] != "":
        kwargs["sources"] = {"list": [], "op": "in"}
        i = 0
        for source in request.form.getlist("sources"):
            kwargs["sources"]["list"].append(source)
            i+=1
        # end for
    # end if
    if request.form["er_like"] != "":
        kwargs["explicit_ref_like"] = {"str": request.form["er_like"], "op": "like"}
    # end if
    if "ers" in request.form and request.form["ers"] != "":
        kwargs["ers"] = {"list": [], "op": "in"}
        i = 0
        for source in request.form.getlist("ers"):
            kwargs["ers"]["list"].append(source)
            i+=1
        # end for
    # end if
    if request.form["gauge_name_like"] != "":
        kwargs["gauge_name_like"] = {"str": request.form["gauge_name_like"], "op": "like"}
    # end if
    if "gauge_names" in request.form and request.form["gauge_names"] != "":
        kwargs["gauge_names"] = {"list": [], "op": "in"}
        i = 0
        for source in request.form.getlist("gauge_names"):
            kwargs["gauge_names"]["list"].append(source)
            i+=1
        # end for
    # end if
    if request.form["gauge_system_like"] != "":
        kwargs["gauge_system_like"] = {"str": request.form["gauge_system_like"], "op": "like"}
    # end if
    if "gauge_systems" in request.form and request.form["gauge_systems"] != "":
        kwargs["gauge_systems"] = {"list": [], "op": "in"}
        i = 0
        for source in request.form.getlist("gauge_systems"):
            kwargs["gauge_systems"]["list"].append(source)
            i+=1
        # end for
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
    events = query.get_events_join(**kwargs)

    return events

@bp.route("/query-event-links/<uuid:event_uuid>")
def query_event_links_and_render(event_uuid):
    """
    Query events linked to the event corresponding to the UUID received and render.
    """
    current_app.logger.debug("Query event links and render")
    links = query_event_links(event_uuid)
    events = links["prime_events"] + [link["event"] for link in links["events_linking"]] + [link["event"] for link in links["linked_events"]]

    return render_template("eboa_nav/linked_events_nav.html", links=links, events=events)

def query_event_links(event_uuid):
    """
    Query events linked to the event corresponding to the UUID received.
    """
    current_app.logger.debug("Query event links")
    query = Query()
    links = query.get_linked_events_details(event_uuid=event_uuid, back_ref = True)
    
    return links

@bp.route("/query-sources", methods=["GET", "POST"])
def query_sources_and_render():
    """
    Query sources amd render.
    """
    current_app.logger.debug("Query sources and render")
    if request.method == "POST":
        sources = query_sources()
        show = {}
        show["validity_timeline"]=True
        if not "show_validity_timeline" in request.form:
            show["validity_timeline"] = False
        # end if
        show["generation_to_ingestion_timeline"]=True
        if not "show_generation_to_ingestion_timeline" in request.form:
            show["generation_to_ingestion_timeline"] = False
        # end if
        show["number_events_xy"]=True
        if not "show_number_events_xy" in request.form:
            show["number_events_xy"] = False
        # end if
        show["ingestion_duration_xy"]=True
        if not "show_ingestion_duration_xy" in request.form:
            show["ingestion_duration_xy"] = False
        # end if
        show["generation_time_to_ingestion_time_xy"]=True
        if not "show_generation_time_to_ingestion_time_xy" in request.form:
            show["generation_time_to_ingestion_time_xy"] = False
        # end if

        return render_template("eboa_nav/sources_nav.html", sources=sources, show=show)
    # end if

    return render_template("eboa_nav/query_sources.html")

def query_sources():
    """
    Query sources.
    """
    current_app.logger.debug("Query sources")
    query = Query()
    kwargs = {}
    if request.form["source_like"] != "":
        kwargs["name_like"] = {"str": request.form["source_like"], "op": "like"}
    # end if
    if request.form["dim_signature_like"] != "":
        kwargs["dim_signature_like"] = {"str": request.form["dim_signature_like"], "op": "like"}
    # end if
    if request.form["validity_start"] != "":
        kwargs["validity_start_filters"] = []
        i = 0
        operators = request.form.getlist("validity_start_operator")
        for start in request.form.getlist("validity_start"):
            kwargs["validity_start_filters"].append({"date": start, "op": operators[i]})
            i+=1
        # end for
    # end if
    if request.form["validity_stop"] != "":
        kwargs["validity_stop_filters"] = []
        i = 0
        operators = request.form.getlist("validity_stop_operator")
        for stop in request.form.getlist("validity_stop"):
            kwargs["validity_stop_filters"].append({"date": stop, "op": operators[i]})
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
    if request.form["generation_time"] != "":
        kwargs["generation_time_filters"] = []
        i = 0
        operators = request.form.getlist("generation_time_operator")
        for generation_time in request.form.getlist("generation_time"):
            kwargs["generation_time_filters"].append({"date": generation_time, "op": operators[i]})
            i+=1
        # end for
    # end if
    sources = query.get_sources_join(**kwargs)

    return sources

@bp.route("/query-jsonify-sources")
def query_jsonify_sources():
    """
    Query all the sources.
    """
    current_app.logger.debug("Query source")
    query = Query()
    sources = query.get_sources()
    jsonified_sources = [source.jsonify() for source in sources]
    return jsonify(jsonified_sources)

@bp.route("/query-source/<uuid:source_uuid>")
def query_source(source_uuid):
    """
    Query source corresponding to the UUID received.
    """
    current_app.logger.debug("Query source")
    query = Query()
    source = query.get_sources(processing_uuids={"list": [source_uuid], "op": "in"})
    return render_template("eboa_nav/sources_nav.html", sources=source)

@bp.route("/query-jsonify-gauges")
def query_jsonify_gauges():
    """
    Query all the gauges.
    """
    current_app.logger.debug("Query gauge")
    query = Query()
    gauges = query.get_gauges()
    jsonified_gauges = [gauge.jsonify() for gauge in gauges]
    return jsonify(jsonified_gauges)

@bp.route("/query-jsonify-keys")
def query_jsonify_keys():
    """
    Query all the keys.
    """
    current_app.logger.debug("Query event keys")
    query = Query()
    keys = query.get_event_keys()
    jsonified_keys = [key.jsonify() for key in keys]
    return jsonify(jsonified_keys)

@bp.route("/query-jsonify-ers")
def query_jsonify_ers():
    """
    Query all the ers.
    """
    current_app.logger.debug("Query explicit references")
    query = Query()
    ers = query.get_event_ers()
    jsonified_ers = [er.jsonify() for er in ers]
    return jsonify(jsonified_ers)

@bp.route("/query-jsonify-dim-signatures")
def query_jsonify_dim_signatures():
    """
    Query all the DIM signatures.
    """
    current_app.logger.debug("Query DIM signatures")
    query = Query()
    dim_signatures = query.get_dim_signatures()
    jsonified_dim_signatures = [dim_signature.jsonify() for dim_signature in dim_signatures]
    return jsonify(jsonified_dim_signatures)

@bp.route("/treat-data", methods = ["POST"])
def treat_data():
    """
    Send data to the EBOA to be treated
    """
    current_app.logger.debug("Treat data")
    if request.headers['Content-Type'] != 'application/json':
        raise
    # end if

    data = request.get_json()
    engine = Engine()
    exit_status = engine.treat_data(data)
    exit_information = {
        "exit_status": str(exit_status)
    }
    return jsonify(exit_information)
