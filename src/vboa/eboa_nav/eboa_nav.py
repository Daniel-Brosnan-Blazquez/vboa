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
import eboa.engine.engine as eboa_engine
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
        op="notlike"
        if not "source_notlike_check" in request.form:
            op="like"
        # end if
        kwargs["source_like"] = {"str": request.form["source_like"], "op": op}
    # end if
    if "sources" in request.form and request.form["sources"] != "":
        op="notin"
        if not "source_notin_check" in request.form:
            op="in"
        # end if
        kwargs["sources"] = {"list": [], "op": op}
        i = 0
        for source in request.form.getlist("sources"):
            kwargs["sources"]["list"].append(source)
            i+=1
        # end for
    # end if
    if request.form["er_like"] != "":
        op="notlike"
        if not "er_notlike_check" in request.form:
            op="like"
        # end if
        kwargs["explicit_ref_like"] = {"str": request.form["er_like"], "op": op}
    # end if
    if "ers" in request.form and request.form["ers"] != "":
        op="notin"
        if not "er_notin_check" in request.form:
            op="in"
        # end if
        kwargs["ers"] = {"list": [], "op": op}
        i = 0
        for source in request.form.getlist("ers"):
            kwargs["ers"]["list"].append(source)
            i+=1
        # end for
    # end if
    if request.form["gauge_name_like"] != "":
        op="notlike"
        if not "gauge_name_notlike_check" in request.form:
            op="like"
        # end if
        kwargs["gauge_name_like"] = {"str": request.form["gauge_name_like"], "op": op}
    # end if
    if "gauge_names" in request.form and request.form["gauge_names"] != "":
        op="notin"
        if not "gauge_name_notin_check" in request.form:
            op="in"
        # end if
        kwargs["gauge_names"] = {"list": [], "op": op}
        i = 0
        for source in request.form.getlist("gauge_names"):
            kwargs["gauge_names"]["list"].append(source)
            i+=1
        # end for
    # end if
    if request.form["gauge_system_like"] != "":
        op="notlike"
        if not "gauge_system_notlike_check" in request.form:
            op="like"
        # end if
        kwargs["gauge_system_like"] = {"str": request.form["gauge_system_like"], "op": op}
    # end if
    if "gauge_systems" in request.form and request.form["gauge_systems"] != "":
        op="notin"
        if not "gauge_system_notin_check" in request.form:
            op="in"
        # end if
        kwargs["gauge_systems"] = {"list": [], "op": op}
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

    kwargs = {}
    if request.form["key_like"] != "":
        op="notlike"
        if not "key_notlike_check" in request.form:
            op="like"
        # end if
        kwargs["key_like"] = {"str": request.form["key_like"], "op": op}
    # end if
    if "keys" in request.form and request.form["keys"] != "":
        op="notin"
        if not "key_notin_check" in request.form:
            op="in"
        # end if
        kwargs["keys"] = {"list": [], "op": op}
        i = 0
        for key in request.form.getlist("keys"):
            kwargs["keys"]["list"].append(key)
            i+=1
        # end for
    # end if

    if request.form["key_like"] != "" or ("keys" in request.form and request.form["keys"] != ""):
        event_uuids = {"list": [event.event_uuid for event in events], "op": "in"}
        kwargs["event_uuids"] = event_uuids
        event_keys = query.get_event_keys(**kwargs)
        event_uuids_from_keys = {"list": [event_key.event_uuid for event_key in event_keys], "op": "in"}
        events = query.get_events(event_uuids = event_uuids_from_keys)
    # end if

    kwargs = {}
    if request.form["value_name_like"] != "":
        i = 0
        operators = request.form.getlist("value_operator")
        value_types = request.form.getlist("value_type")
        values = request.form.getlist("value")
        for value_name_like in request.form.getlist("value_name_like"):
            event_uuids = {"list": [event.event_uuid for event in events], "op": "in"}
            values_name_type_like = [{"name_like": value_name_like, "type": value_types[i]}]
            value_filters = [{"value": values[i], "type": value_types[i], "op": operators[i]}]
            events = query.get_events_join(values_name_type_like = values_name_type_like, value_filters = value_filters, event_uuids = event_uuids)
            i+=1
        # end for
    # end if

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

@bp.route("/query-annotations", methods=["GET", "POST"])
def query_annotations_and_render():
    """
    Query annotations and render.
    """
    current_app.logger.debug("Query annotations and render")
    if request.method == "POST":
        annotations = query_annotations()
        show = {}
        show["timeline"]=True
        if not "show_timeline" in request.form:
            show["timeline"] = False
        # end if

        return render_template("eboa_nav/annotations_nav.html", annotations=annotations, show=show)
    # end if
    return render_template("eboa_nav/query_annotations.html")

def query_annotations():
    """
    Query annotations.
    """
    current_app.logger.debug("Query annotations")

    query = Query()
    kwargs = {}
    if request.form["source_like"] != "":
        op="notlike"
        if not "source_notlike_check" in request.form:
            op="like"
        # end if
        kwargs["source_like"] = {"str": request.form["source_like"], "op": op}
    # end if
    if "sources" in request.form and request.form["sources"] != "":
        op="notin"
        if not "source_notin_check" in request.form:
            op="in"
        # end if
        kwargs["sources"] = {"list": [], "op": op}
        i = 0
        for source in request.form.getlist("sources"):
            kwargs["sources"]["list"].append(source)
            i+=1
        # end for
    # end if
    if request.form["er_like"] != "":
        op="notlike"
        if not "er_notlike_check" in request.form:
            op="like"
        # end if
        kwargs["explicit_ref_like"] = {"str": request.form["er_like"], "op": op}
    # end if
    if "ers" in request.form and request.form["ers"] != "":
        op="notin"
        if not "er_notin_check" in request.form:
            op="in"
        # end if
        kwargs["ers"] = {"list": [], "op": op}
        i = 0
        for source in request.form.getlist("ers"):
            kwargs["ers"]["list"].append(source)
            i+=1
        # end for
    # end if
    if request.form["annotation_name_like"] != "":
        op="notlike"
        if not "annotation_name_notlike_check" in request.form:
            op="like"
        # end if
        kwargs["name_like"] = {"str": request.form["annotation_name_like"], "op": op}
    # end if
    if "annotation_names" in request.form and request.form["annotation_names"] != "":
        op="notin"
        if not "annotation_name_notin_check" in request.form:
            op="in"
        # end if
        kwargs["names"] = {"list": [], "op": op}
        i = 0
        for source in request.form.getlist("annotation_names"):
            kwargs["names"]["list"].append(source)
            i+=1
        # end for
    # end if
    if request.form["annotation_system_like"] != "":
        op="notlike"
        if not "annotation_system_notlike_check" in request.form:
            op="like"
        # end if
        kwargs["system_like"] = {"str": request.form["annotation_system_like"], "op": op}
    # end if
    if "annotation_systems" in request.form and request.form["annotation_systems"] != "":
        op="notin"
        if not "annotation_system_notin_check" in request.form:
            op="in"
        # end if
        kwargs["systems"] = {"list": [], "op": op}
        i = 0
        for source in request.form.getlist("annotation_systems"):
            kwargs["systems"]["list"].append(source)
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
    annotations = query.get_annotations_join(**kwargs)

    return annotations

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
        op="notlike"
        if not "source_notlike_check" in request.form:
            op="like"
        # end if
        kwargs["name_like"] = {"str": request.form["source_like"], "op": op}
    # end if
    if request.form["dim_signature_like"] != "":
        op="notlike"
        if not "dim_signature_notlike_check" in request.form:
            op="like"
        # end if
        kwargs["dim_signature_like"] = {"str": request.form["dim_signature_like"], "op": op}
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
    if request.form["ingestion_duration"] != "":
        kwargs["ingestion_duration_filters"] = []
        i = 0
        operators = request.form.getlist("ingestion_duration_operator")
        for ingestion_duration in request.form.getlist("ingestion_duration"):
            kwargs["ingestion_duration_filters"].append({"float": float(ingestion_duration), "op": operators[i]})
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
    if request.form["processor_like"] != "":
        op="notlike"
        if not "processor_notlike_check" in request.form:
            op="like"
        # end if
        kwargs["processor_like"] = {"str": request.form["processor_like"], "op": op}
    # end if
    if "processors" in request.form and request.form["processors"] != "":
        op="notin"
        if not "processor_notin_check" in request.form:
            op="in"
        # end if
        kwargs["processors"] = {"list": [], "op": op}
        i = 0
        for source in request.form.getlist("processors"):
            kwargs["processors"]["list"].append(source)
            i+=1
        # end for
    # end if

    sources = query.get_sources_join(**kwargs)

    return sources

@bp.route("/query-source/<uuid:source_uuid>")
def query_source(source_uuid):
    """
    Query source corresponding to the UUID received.
    """
    current_app.logger.debug("Query source")
    query = Query()
    source = query.get_sources(source_uuids={"list": [source_uuid], "op": "in"})
    return render_template("eboa_nav/sources_nav.html", sources=source)

@bp.route("/query-sources-by-dim/<uuid:dim_signature_uuid>")
def query_sources_by_dim(dim_signature_uuid):
    """
    Query sources associated to the DIM signature corresponding to the UUID received.
    """
    current_app.logger.debug("Query sources by DIM signature")
    query = Query()
    sources = query.get_sources(dim_signature_uuids={"list": [dim_signature_uuid], "op": "in"})
    return render_template("eboa_nav/sources_nav.html", sources=sources)

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

@bp.route("/get-source-status")
def get_source_status():
    """
    Get the source statuses defined in the EBOA component.
    """
    current_app.logger.debug("Get source statuses")
    return jsonify(eboa_engine.exit_codes)

@bp.route("/query-gauges", methods=["GET", "POST"])
def query_gauges_and_render():
    """
    Query gauges amd render.
    """
    current_app.logger.debug("Query gauges and render")
    if request.method == "POST":
        gauges = query_gauges()

        return render_template("eboa_nav/gauges_nav.html", gauges=gauges)
    # end if

    return render_template("eboa_nav/query_gauges.html")

def query_gauges():
    """
    Query gauges.
    """
    current_app.logger.debug("Query gauges")
    query = Query()
    kwargs = {}
    if request.form["gauge_name_like"] != "":
        op="notlike"
        if not "gauge_name_notlike_check" in request.form:
            op="like"
        # end if
        kwargs["name_like"] = {"str": request.form["gauge_name_like"], "op": op}
    # end if
    if "gauge_names" in request.form and request.form["gauge_names"] != "":
        op="notin"
        if not "gauge_name_notin_check" in request.form:
            op="in"
        # end if
        kwargs["names"] = {"list": [], "op": op}
        i = 0
        for source in request.form.getlist("gauge_names"):
            kwargs["names"]["list"].append(source)
            i+=1
        # end for
    # end if
    if request.form["gauge_system_like"] != "":
        op="notlike"
        if not "gauge_system_notlike_check" in request.form:
            op="like"
        # end if
        kwargs["system_like"] = {"str": request.form["gauge_system_like"], "op": op}
    # end if
    if "gauge_systems" in request.form and request.form["gauge_systems"] != "":
        op="notin"
        if not "gauge_system_notin_check" in request.form:
            op="in"
        # end if
        kwargs["systems"] = {"list": [], "op": op}
        i = 0
        for source in request.form.getlist("gauge_systems"):
            kwargs["systems"]["list"].append(source)
            i+=1
        # end for
    # end if
    if request.form["dim_signature_like"] != "":
        op="notlike"
        if not "dim_signature_notlike_check" in request.form:
            op="like"
        # end if
        kwargs["dim_signature_like"] = {"str": request.form["dim_signature_like"], "op": op}
    # end if
    if "dim_signatures" in request.form and request.form["dim_signatures"] != "":
        op="notin"
        if not "dim_signature_notin_check" in request.form:
            op="in"
        # end if
        kwargs["dim_signatures"] = {"list": [], "op": op}
        i = 0
        for source in request.form.getlist("dim_signatures"):
            kwargs["dim_signatures"]["list"].append(source)
            i+=1
        # end for
    # end if

    gauges = query.get_gauges_join(**kwargs)

    return gauges

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

@bp.route("/query-annotation-cnfs", methods=["GET", "POST"])
def query_annotation_cnfs_and_render():
    """
    Query annotation configurations amd render.
    """
    current_app.logger.debug("Query annotation configurations and render")
    if request.method == "POST":
        annotation_cnfs = query_annotation_cnfs()

        return render_template("eboa_nav/annotation_cnfs_nav.html", annotation_cnfs=annotation_cnfs)
    # end if

    return render_template("eboa_nav/query_annotation_cnfs.html")

def query_annotation_cnfs():
    """
    Query annotation configurations.
    """
    current_app.logger.debug("Query annotation configurations")
    query = Query()
    kwargs = {}
    if request.form["annotation_name_like"] != "":
        op="notlike"
        if not "annotation_name_notlike_check" in request.form:
            op="like"
        # end if
        kwargs["name_like"] = {"str": request.form["annotation_name_like"], "op": op}
    # end if
    if "annotation_names" in request.form and request.form["annotation_names"] != "":
        op="notin"
        if not "annotation_name_notin_check" in request.form:
            op="in"
        # end if
        kwargs["names"] = {"list": [], "op": op}
        i = 0
        for source in request.form.getlist("annotation_names"):
            kwargs["names"]["list"].append(source)
            i+=1
        # end for
    # end if
    if request.form["annotation_system_like"] != "":
        op="notlike"
        if not "annotation_system_notlike_check" in request.form:
            op="like"
        # end if
        kwargs["system_like"] = {"str": request.form["annotation_system_like"], "op": op}
    # end if
    if "annotation_systems" in request.form and request.form["annotation_systems"] != "":
        op="notin"
        if not "annotation_system_notin_check" in request.form:
            op="in"
        # end if
        kwargs["systems"] = {"list": [], "op": op}
        i = 0
        for source in request.form.getlist("annotation_systems"):
            kwargs["systems"]["list"].append(source)
            i+=1
        # end for
    # end if
    if request.form["dim_signature_like"] != "":
        op="notlike"
        if not "dim_signature_notlike_check" in request.form:
            op="like"
        # end if
        kwargs["dim_signature_like"] = {"str": request.form["dim_signature_like"], "op": op}
    # end if
    if "dim_signatures" in request.form and request.form["dim_signatures"] != "":
        op="notin"
        if not "dim_signature_notin_check" in request.form:
            op="in"
        # end if
        kwargs["dim_signatures"] = {"list": [], "op": op}
        i = 0
        for source in request.form.getlist("dim_signatures"):
            kwargs["dim_signatures"]["list"].append(source)
            i+=1
        # end for
    # end if

    annotation_cnfs = query.get_annotation_cnfs_join(**kwargs)

    return annotation_cnfs

@bp.route("/query-jsonify-annotation-cnfs")
def query_jsonify_annotation_cnfs():
    """
    Query all the annotation configurations.
    """
    current_app.logger.debug("Query annotation configurations")
    query = Query()
    annotation_cnfs = query.get_annotation_cnfs()
    jsonified_annotation_cnfs = [annotation_cnf.jsonify() for annotation_cnf in annotation_cnfs]
    return jsonify(jsonified_annotation_cnfs)

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

@bp.route("/query-ers", methods=["GET", "POST"])
def query_ers_and_render():
    """
    Query explicit references and render.
    """
    current_app.logger.debug("Query explicit references and render")
    if request.method == "POST":
        ers = query_ers()

        return render_template("eboa_nav/explicit_references_nav.html", ers=ers)
    # end if
    return render_template("eboa_nav/query_explicit_references.html")

def query_ers():
    """
    Query explicit references.
    """
    current_app.logger.debug("Query explicit references")

    query = Query()
    kwargs = {}
    if request.form["er_like"] != "":
        op="notlike"
        if not "er_notlike_check" in request.form:
            op="like"
        # end if
        kwargs["explicit_ref_like"] = {"str": request.form["er_like"], "op": op}
    # end if
    if "ers" in request.form and request.form["ers"] != "":
        op="notin"
        if not "er_notin_check" in request.form:
            op="in"
        # end if
        kwargs["ers"] = {"list": [], "op": op}
        i = 0
        for source in request.form.getlist("ers"):
            kwargs["ers"]["list"].append(source)
            i+=1
        # end for
    # end if
    if request.form["group_like"] != "":
        op="notlike"
        if not "group_notlike_check" in request.form:
            op="like"
        # end if
        kwargs["group_like"] = {"str": request.form["group_like"], "op": op}
    # end if
    if "groups" in request.form and request.form["groups"] != "":
        op="notin"
        if not "group_notin_check" in request.form:
            op="in"
        # end if
        kwargs["groups"] = {"list": [], "op": op}
        i = 0
        for source in request.form.getlist("groups"):
            kwargs["groups"]["list"].append(source)
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
    ers = query.get_explicit_refs_join(**kwargs)

    return ers

@bp.route("/query-jsonify-ers")
def query_jsonify_ers():
    """
    Query all the ers.
    """
    current_app.logger.debug("Query explicit references")
    query = Query()
    ers = query.get_explicit_refs()
    jsonified_ers = [er.jsonify() for er in ers]
    return jsonify(jsonified_ers)

@bp.route("/query-jsonify-er-groups")
def query_jsonify_er_groups():
    """
    Query all the ers groups.
    """
    current_app.logger.debug("Query explicit reference groups")
    query = Query()
    er_groups = query.get_explicit_refs_groups()
    jsonified_er_groups = [er_group.jsonify() for er_group in er_groups]
    return jsonify(jsonified_er_groups)

@bp.route("/query-dim-signatures", methods=["GET", "POST"])
def query_dim_signatures_and_render():
    """
    Query DIM signatures amd render.
    """
    current_app.logger.debug("Query DIM signatures and render")
    if request.method == "POST":
        dim_signatures = query_dim_signatures()

        return render_template("eboa_nav/dim_signatures_nav.html", dim_signatures=dim_signatures)
    # end if

    return render_template("eboa_nav/query_dim_signatures.html")

def query_dim_signatures():
    """
    Query DIM signatures.
    """
    current_app.logger.debug("Query DIM signatures")
    query = Query()
    kwargs = {}
    if request.form["dim_signature_like"] != "":
        op="notlike"
        if not "dim_signature_notlike_check" in request.form:
            op="like"
        # end if
        kwargs["dim_signature_like"] = {"str": request.form["dim_signature_like"], "op": op}
    # end if
    if "dim_signatures" in request.form and request.form["dim_signatures"] != "":
        op="notin"
        if not "dim_signature_notin_check" in request.form:
            op="in"
        # end if
        kwargs["dim_signatures"] = {"list": [], "op": op}
        i = 0
        for source in request.form.getlist("dim_signatures"):
            kwargs["dim_signatures"]["list"].append(source)
            i+=1
        # end for
    # end if

    dim_signatures = query.get_dim_signatures(**kwargs)

    return dim_signatures

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
    returned_values = engine.treat_data(data)
    exit_information = {
        "returned_values": returned_values
    }
    return jsonify(exit_information)
