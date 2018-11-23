"""
EBOA navigation section definition

Written by DEIMOS Space S.L. (dibb)

module vboa
"""
import sys
# Import flask utilities
from flask import Blueprint, flash, g, current_app, redirect, render_template, request, url_for
from flask_debugtoolbar import DebugToolbarExtension

# Import eboa utilities
from eboa.engine.query import Query

bp = Blueprint("eboa_nav", __name__, url_prefix="/eboa_nav")

@bp.route("/", methods=["GET"])
def navigate():
    """
    Initial panel for the EBOA navigation functionality.
    """
    return render_template("eboa_nav/query_events.html")

@bp.route("/query-events", methods=["GET", "POST"])
def query_events():
    """
    Query events.
    """
    current_app.logger.debug("Query events")
    if request.method == "POST":
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
        show = {}
        show["timeline"]=True
        if not "show_timeline" in request.form:
            show["timeline"] = False
        # end if
        events = query.get_events_join(**kwargs)
        return render_template("eboa_nav/events_nav.html", events=events, show=show)
    # end if
    return render_template("eboa_nav/query_events.html")

@bp.route("/query-event-links/<uuid:event_uuid>")
def query_event_links(event_uuid):
    """
    Query events linked to the event corresponding to the UUID received.
    """
    current_app.logger.debug("Query event links")
    query = Query()
    links = query.get_linked_events_details(event_uuid=event_uuid, back_ref = True)
    events = links["prime_events"] + [link["event"] for link in links["events_linking"]] + [link["event"] for link in links["linked_events"]]
    return render_template("eboa_nav/linked_events_nav.html", links=links, events=events)


@bp.route("/query-sources", methods=["GET", "POST"])
def query_sources():
    """
    Query sources.
    """
    current_app.logger.debug("Query sources")
    if request.method == "POST":
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
        sources = query.get_sources_join(**kwargs)
        return render_template("eboa_nav/sources_nav.html", sources=sources, show=show)
    # end if
    return render_template("eboa_nav/query_sources.html")


@bp.route("/query-source/<uuid:source_uuid>")
def query_source(source_uuid):
    """
    Query source corresponding to the UUID received.
    """
    current_app.logger.debug("Query source")
    query = Query()
    source = query.get_sources(processing_uuids={"list": [source_uuid], "op": "in"})
    return render_template("eboa_nav/sources_nav.html", sources=source)


