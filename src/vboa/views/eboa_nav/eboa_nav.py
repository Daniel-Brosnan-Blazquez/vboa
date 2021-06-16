"""
EBOA navigation section definition

Written by DEIMOS Space S.L. (dibb)

module vboa
"""
# Import python utilities
import sys
import json
from distutils import util
import shlex
from subprocess import Popen, PIPE

# Import flask utilities
from flask import Blueprint, flash, g, current_app, redirect, render_template, request, url_for, send_from_directory
from flask_debugtoolbar import DebugToolbarExtension
from flask import jsonify

# Import eboa utilities
from eboa.engine.query import Query
import eboa.engine.engine as eboa_engine
from eboa.engine.engine import Engine

# Import triggering
from eboa.triggering.eboa_triggering import get_triggering_conf

bp = Blueprint("eboa_nav", __name__, url_prefix="/eboa_nav")
query = Query()
engine = Engine()

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
        filters = request.form.to_dict(flat=False).copy()
        filters["offset"] = [""]

        if "query_events" in filters:
            events = query_events(filters)
            show = define_what_to_show_events(filters)
            events_geometries = []
            if show["map"]:
                events_geometries = [{"event": event, "geometries": engine.geometries_to_wkt(event.eventGeometries)} for event in events if len(event.eventGeometries) > 0]
            # end if        

            return render_template("eboa_nav/events_nav.html", events=events, events_geometries=events_geometries, show=show, filters=filters)
        else:
            event_alerts = query_event_alerts(filters)
            show = define_what_to_show_alerts(filters)
            return render_template("eboa_nav/alerts_nav.html", event_alerts=event_alerts, show=show, filters=filters)
        # end if
    
    # end if
    return render_template("eboa_nav/query_events.html")

@bp.route("/query-events-pages", methods=["GET", "POST"])
def query_events_pages():
    """
    Query events using pages and render.
    """
    current_app.logger.debug("Query events using pages and render")
    filters = request.json
    events = query_events(filters)
    show = define_what_to_show_events(filters)
    events_geometries = []
    if show["map"]:
        events_geometries = [{"event": event, "geometries": engine.geometries_to_wkt(event.eventGeometries)} for event in events if len(event.eventGeometries) > 0]
    # end if        

    return render_template("eboa_nav/events_nav.html", events=events, events_geometries=events_geometries, show=show, filters=filters)

def define_what_to_show_events(filters):
    """
    Function to define what to show for events
    """
    show = {}
    show["timeline"]=True
    if not "show_timeline" in filters:
        show["timeline"] = False
    # end if
    show["map"]=True
    if not "show_map" in filters:
        show["map"] = False
    # end if        

    return show

@bp.route("/query-events-by-er/<string:er>")
def query_events_by_er(er):
    """
    Query events associated to the explicit reference received.
    """
    current_app.logger.debug("Query events by explicit reference")
    show = {}
    show["timeline"]=True
    show["map"]=True
    filters = {}
    filters["offset"] = [""]
    filters["limit"] = ["100"]

    events = query.get_events(explicit_refs={"filter": [er], "op": "in"})

    events_geometries = []
    events_geometries = [{"event": event, "geometries": engine.geometries_to_wkt(event.eventGeometries)} for event in events if len(event.eventGeometries) > 0]

    return render_template("eboa_nav/events_nav.html", events=events, events_geometries=events_geometries, show=show, filters=filters)

@bp.route("/query-events-by-source-uuid/<string:source_uuid>")
def query_events_by_source_uuid(source_uuid):
    """
    Query events associated to the source corresponding to the UUID received.
    """
    current_app.logger.debug("Query events by source uuid")
    show = {}
    show["timeline"]=True
    show["map"]=True
    filters = {}
    filters["offset"] = [""]
    filters["limit"] = ["100"]

    events = query.get_events(source_uuids={"filter": [source_uuid], "op": "in"})

    events_geometries = []
    events_geometries = [{"event": event, "geometries": engine.geometries_to_wkt(event.eventGeometries)} for event in events if len(event.eventGeometries) > 0]

    return render_template("eboa_nav/events_nav.html", events=events, events_geometries=events_geometries, show=show, filters=filters)

def query_events(filters):
    """
    Query events.
    """
    current_app.logger.debug("Query events")

    kwargs = set_filters_for_query_events_or_event_alerts(filters)

    events = query.get_events(**kwargs)

    return events

def query_event_alerts(filters):
    """
    Query event alerts.
    """
    current_app.logger.debug("Query event alerts")

    kwargs = set_filters_for_query_events_or_event_alerts(filters)

    event_alerts = query.get_event_alerts(kwargs)

    return event_alerts

def set_filters_for_query_events_or_event_alerts(filters):
    """
    Set filter for query events or query event alerts.
    """
    kwargs = {}

    if filters["key"][0] != "":
        kwargs["keys"] = {"filter": filters["key"][0], "op": filters["key_operator"][0]}
    # end if
    elif "keys" in filters and filters["keys"][0] != "":
        op="notin"
        if not "key_notin_check" in filters:
            op="in"
        # end if
        kwargs["keys"] = {"filter": [], "op": op}
        i = 0
        for key in filters["keys"]:
            kwargs["keys"]["filter"].append(key)
            i+=1
        # end for
    # end if

    if filters["event_value_name"][0] != "":
        value_operators = filters["event_value_operator"]
        value_types = filters["event_value_type"]
        values = filters["event_value"]
        value_name_ops = filters["event_value_name_op"]
        kwargs["value_filters"] = []
        i = 0
        for value_name in filters["event_value_name"]:
            if value_name[0] != "":
                if (values[i] == "" and value_types[i] == "text") or (values[i][0] != "" and value_types[i] != "object"):
                    kwargs["value_filters"].append({"name": {"op": value_name_ops[i], "filter": value_name},
                                                          "type": value_types[i],
                                                          "value": {"op": value_operators[i], "filter": values[i]}})
                else:
                    kwargs["value_filters"].append({"name": {"op": value_name_ops[i], "filter": value_name},
                                                          "type": value_types[i]})
            # end if
            i+=1
        # end for
    # end if

    if filters["source"][0] != "":
        op="notlike"
        if not "source_notlike_check" in filters:
            op="like"
        # end if
        kwargs["sources"] = {"filter": filters["source"][0], "op": filters["source_operator"][0]}
    # end if
    elif "sources" in filters and filters["sources"][0] != "":
        op="notin"
        if not "source_notin_check" in filters:
            op="in"
        # end if
        kwargs["sources"] = {"filter": [], "op": op}
        i = 0
        for source in filters["sources"]:
            kwargs["sources"]["filter"].append(source)
            i+=1
        # end for
    # end if
    if filters["er"][0] != "":
        op="notlike"
        if not "er_notlike_check" in filters:
            op="like"
        # end if
        kwargs["explicit_refs"] = {"filter": filters["er"][0], "op": filters["er_operator"][0]}
    # end if
    elif "ers" in filters and filters["ers"][0] != "":
        op="notin"
        if not "er_notin_check" in filters:
            op="in"
        # end if
        kwargs["explicit_refs"] = {"filter": [], "op": op}
        i = 0
        for er in filters["ers"]:
            kwargs["explicit_refs"]["filter"].append(er)
            i+=1
        # end for
    # end if
    if filters["gauge_name"][0] != "":
        op="notlike"
        if not "gauge_name_notlike_check" in filters:
            op="like"
        # end if
        kwargs["gauge_names"] = {"filter": filters["gauge_name"][0], "op": filters["gauge_name_operator"][0]}
    # end if
    elif "gauge_names" in filters and filters["gauge_names"][0] != "":
        op="notin"
        if not "gauge_name_notin_check" in filters:
            op="in"
        # end if
        kwargs["gauge_names"] = {"filter": [], "op": op}
        i = 0
        for gauge_name in filters["gauge_names"]:
            kwargs["gauge_names"]["filter"].append(gauge_name)
            i+=1
        # end for
    # end if
    if filters["gauge_system"][0] != "":
        op="notlike"
        if not "gauge_system_notlike_check" in filters:
            op="like"
        # end if
        kwargs["gauge_systems"] = {"filter": filters["gauge_system"][0], "op": filters["gauge_system_operator"][0]}
    # end if
    elif "gauge_systems" in filters and filters["gauge_systems"][0] != "":
        op="notin"
        if not "gauge_system_notin_check" in filters:
            op="in"
        # end if
        kwargs["gauge_systems"] = {"filter": [], "op": op}
        i = 0
        for gauge_system in filters["gauge_systems"]:
            kwargs["gauge_systems"]["filter"].append(gauge_system)
            i+=1
        # end for
    # end if
    if filters["start"][0] != "":
        kwargs["start_filters"] = []
        i = 0
        operators = filters["start_operator"]
        for start in filters["start"]:
            kwargs["start_filters"].append({"date": start, "op": operators[i]})
            i+=1
        # end for
    # end if
    if filters["stop"][0] != "":
        kwargs["stop_filters"] = []
        i = 0
        operators = filters["stop_operator"]
        for stop in filters["stop"]:
            kwargs["stop_filters"].append({"date": stop, "op": operators[i]})
            i+=1
        # end for
    # end if
    if filters["ingestion_time"][0] != "":
        if "query_events" in filters:
            kwargs["ingestion_time_filters"] = []
        else:
            kwargs["event_ingestion_time_filters"] = []
        # end if
        i = 0
        operators = filters["ingestion_time_operator"]
        for ingestion_time in filters["ingestion_time"]:
            if "query_events" in filters:
                kwargs["ingestion_time_filters"].append({"date": ingestion_time, "op": operators[i]})
            else:
                kwargs["event_ingestion_time_filters"].append({"date": ingestion_time, "op": operators[i]})
            # end if
            i+=1
        # end for
    # end if
    if filters["event_duration"][0] != "":
        kwargs["duration_filters"] = []
        i = 0
        operators = filters["event_duration_operator"]
        for event_duration in filters["event_duration"]:
            kwargs["duration_filters"].append({"float": float(event_duration), "op": operators[i]})
            i+=1
        # end for
    # end if

    # Query restrictions
    if filters["order_by"][0] != "":
        descending = True
        if not "order_descending" in filters:
            descending = False
        # end if
        kwargs["order_by"] = {"field": filters["order_by"][0], "descending": descending}
    # end if

    if filters["limit"][0] != "":
        kwargs["limit"] = filters["limit"][0]
    # end if

    if filters["offset"][0] != "":
        kwargs["offset"] = filters["offset"][0]
    # end if

    return kwargs

@bp.route("/query-event-links/<uuid:event_uuid>")
def query_event_links_and_render(event_uuid):
    """
    Query events linked to the event corresponding to the UUID received and render.
    """
    current_app.logger.debug("Query event links and render")
    links = query_event_links(event_uuid)
    events = links["prime_events"] + [link["event"] for link in links["events_linking"]] + [link["event"] for link in links["linked_events"]]
    events_geometries = [{"event": event, "geometries": engine.geometries_to_wkt(event.eventGeometries)} for event in events if len(event.eventGeometries) > 0]
    return render_template("eboa_nav/linked_events_nav.html", links=links, events=events, events_geometries=events_geometries)

def query_event_links(event_uuid):
    """
    Query events linked to the event corresponding to the UUID received.
    """
    current_app.logger.debug("Query event links")
    links = query.get_linked_events_details(event_uuid=event_uuid, back_ref = True)

    return links

@bp.route("/query-jsonify-event-values/<uuid:event_uuid>")
def query_jsonify_event_values(event_uuid):
    """
    Query values related to the event with the corresponding received UUID.
    """
    current_app.logger.debug("Query values corresponding to the event with specified UUID " + str(event_uuid))
    values = query.get_event_values([event_uuid])
    jsonified_values = [value.jsonify() for value in values]
    return jsonify(jsonified_values)

@bp.route("/query-annotations", methods=["GET", "POST"])
def query_annotations_and_render():
    """
    Query annotations and render.
    """
    current_app.logger.debug("Query annotations and render")
    if request.method == "POST":
        filters = request.form.to_dict(flat=False).copy()
        filters["offset"] = [""]

        annotations = query_annotations(filters)
        show = define_what_to_show_annotations(filters)
        annotations_geometries = []
        if show["map"]:
            annotations_geometries = [{"annotation": annotation, "geometries": engine.geometries_to_wkt(annotation.annotationGeometries)} for annotation in annotations if len(annotation.annotationGeometries) > 0]
        # end if

        return render_template("eboa_nav/annotations_nav.html", annotations=annotations, annotations_geometries=annotations_geometries, show=show, filters=filters)
    # end if
    return render_template("eboa_nav/query_annotations.html")

@bp.route("/query-annotations-pages", methods=["POST"])
def query_annotations_pages():
    """
    Query annotations using pages and render.
    """
    current_app.logger.debug("Query annotations using pages and render")
    filters = request.json
    annotations = query_annotations(filters)
    
    show = define_what_to_show_annotations(filters)
    annotations_geometries = []
    if show["map"]:
        annotations_geometries = [{"annotation": annotation, "geometries": engine.geometries_to_wkt(annotation.annotationGeometries)} for annotation in annotations if len(annotation.annotationGeometries) > 0]
    # end if

    return render_template("eboa_nav/annotations_nav.html", annotations=annotations, annotations_geometries=annotations_geometries, show=show, filters=filters)

def define_what_to_show_annotations(filters):
    """
    Function to define what to show for annotations
    """
    show = {}
    show["map"]=True
    if not "show_map" in filters:
        show["map"] = False
    # end if

    return show

@bp.route("/query-annotations-by-er/<string:er>")
def query_annotations_by_er(er):
    """
    Query annotations associated to the explicit reference received.
    """
    current_app.logger.debug("Query annotations by explicit reference")
    show = {}
    show["map"]=True
    filters = {}
    filters["offset"] = [""]
    filters["limit"] = ["100"]
    
    annotations = query.get_annotations(explicit_refs={"filter": [er], "op": "in"})

    annotations_geometries = [{"annotation": annotation, "geometries": engine.geometries_to_wkt(annotation.annotationGeometries)} for annotation in annotations if len(annotation.annotationGeometries) > 0]

    return render_template("eboa_nav/annotations_nav.html", annotations=annotations, annotations_geometries=annotations_geometries, show=show, filters=filters)

@bp.route("/query-annotation/<uuid:annotation_uuid>")
def query_annotation(annotation_uuid):
    """
    Query annotation corresponding to the UUID received.
    """
    current_app.logger.debug("Query annotation")
    
    show = {}
    show["map"]=True
    filters = {}
    filters["offset"] = [""]
    filters["limit"] = ["100"]

    annotation = query.get_annotations(annotation_uuids={"filter": [annotation_uuid], "op": "in"})

    annotation_geometries = []
    if len(annotation[0].annotationGeometries) > 0: 
        annotation_geometries = [{"annotation": annotation, "geometries": engine.geometries_to_wkt(annotation.annotationGeometries)}]

    return render_template("eboa_nav/annotations_nav.html", annotations=annotation, annotations_geometries=annotation_geometries, show=show, filters=filters)

@bp.route("/query-annotations-by-source-uuid/<string:source_uuid>")
def query_annotations_by_source_uuid(source_uuid):
    """
    Query annotations associated to the source corresponding to the UUID received.
    """
    current_app.logger.debug("Query annotations by source uuid")
    show = {}
    show["map"]=True
    filters = {}
    filters["offset"] = [""]
    filters["limit"] = ["100"]

    annotations = query.get_annotations(source_uuids={"filter": [source_uuid], "op": "in"})

    annotations_geometries = []
    annotations_geometries = [{"annotation": annotation, "geometries": engine.geometries_to_wkt(annotation.annotationGeometries)} for annotation in annotations if len(annotation.annotationGeometries) > 0]

    return render_template("eboa_nav/annotations_nav.html", annotations=annotations, annotations_geometries=annotations_geometries, show=show, filters=filters)

def query_annotations(filters):
    """
    Query annotations.
    """
    current_app.logger.debug("Query annotations")

    kwargs = {}

    if filters["annotation_value_name"][0] != "":
        value_operators = filters["annotation_value_operator"]
        value_types = filters["annotation_value_type"]
        values = filters["annotation_value"]
        value_name_ops = filters["annotation_value_name_op"]
        kwargs["value_filters"] = []
        i = 0
        for value_name in filters["annotation_value_name"]:
            if value_name[0] != "":
                if (values[i] == "" and value_types[i] == "text") or (values[i][0] != "" and value_types[i] != "object"):
                    kwargs["value_filters"].append({"name": {"op": value_name_ops[i], "filter": value_name},
                                                          "type": value_types[i],
                                                          "value": {"op": value_operators[i], "filter": values[i]}})
                else:
                    kwargs["value_filters"].append({"name": {"op": value_name_ops[i], "filter": value_name},
                                                          "type": value_types[i]})
            # end if
            i+=1
        # end for
    # end if

    if filters["source"][0] != "":
        op="notlike"
        if not "source_notlike_check" in filters:
            op="like"
        # end if
        kwargs["sources"] = {"filter": filters["source"][0], "op": filters["source_operator"][0]}
    # end if
    elif "sources" in filters and filters["sources"][0] != "":
        op="notin"
        if not "source_notin_check" in filters:
            op="in"
        # end if
        kwargs["sources"] = {"filter": [], "op": op}
        i = 0
        for source in filters["sources"]:
            kwargs["sources"]["filter"].append(source)
            i+=1
        # end for
    # end if
    if filters["er"][0] != "":
        op="notlike"
        if not "er_notlike_check" in filters:
            op="like"
        # end if
        kwargs["explicit_refs"] = {"filter": filters["er"][0], "op": filters["er_operator"][0]}
    # end if
    elif "ers" in filters and filters["ers"][0] != "":
        op="notin"
        if not "er_notin_check" in filters:
            op="in"
        # end if
        kwargs["explicit_refs"] = {"filter": [], "op": op}
        i = 0
        for er in filters["ers"]:
            kwargs["explicit_refs"]["filter"].append(er)
            i+=1
        # end for
    # end if
    if filters["annotation_name"][0] != "":
        op="notlike"
        if not "annotation_name_notlike_check" in filters:
            op="like"
        # end if
        kwargs["annotation_cnf_names"] = {"filter": filters["annotation_name"][0], "op": filters["annotation_name_operator"][0]}
    # end if
    elif "annotation_names" in filters and filters["annotation_names"][0] != "":
        op="notin"
        if not "annotation_name_notin_check" in filters:
            op="in"
        # end if
        kwargs["annotation_cnf_names"] = {"filter": [], "op": op}
        i = 0
        for annotation_name in filters["annotation_names"]:
            kwargs["annotation_cnf_names"]["filter"].append(annotation_name)
            i+=1
        # end for
    # end if
    if filters["annotation_system"][0] != "":
        op="notlike"
        if not "annotation_system_notlike_check" in filters:
            op="like"
        # end if
        kwargs["annotation_cnf_systems"] = {"filter": filters["annotation_system"][0], "op": filters["annotation_system_operator"][0]}
    # end if
    elif "annotation_systems" in filters and filters["annotation_systems"][0] != "":
        op="notin"
        if not "annotation_system_notin_check" in filters:
            op="in"
        # end if
        kwargs["annotation_cnf_systems"] = {"filter": [], "op": op}
        i = 0
        for annotation_system in filters["annotation_systems"]:
            kwargs["annotation_cnf_systems"]["filter"].append(annotation_system)
            i+=1
        # end for
    # end if
    if filters["ingestion_time"][0] != "":
        kwargs["ingestion_time_filters"] = []
        i = 0
        operators = filters["ingestion_time_operator"]
        for ingestion_time in filters["ingestion_time"]:
            kwargs["ingestion_time_filters"].append({"date": ingestion_time, "op": operators[i]})
            i+=1
        # end for
    # end if

    # Query restrictions
    if filters["order_by"][0] != "":
        descending = True
        if not "order_descending" in filters:
            descending = False
        # end if
        kwargs["order_by"] = {"field": filters["order_by"][0], "descending": descending}
    # end if

    if filters["limit"][0] != "":
        kwargs["limit"] = filters["limit"][0]
    # end if

    if filters["offset"][0] != "":
        kwargs["offset"] = filters["offset"][0]
    # end if

    annotations = query.get_annotations(**kwargs)

    return annotations

@bp.route("/query-jsonify-annotation-values/<uuid:annotation_uuid>")
def query_jsonify_annotation_values(annotation_uuid):
    """
    Query values related to the annotation with the corresponding received UUID.
    """
    current_app.logger.debug("Query values corresponding to the annotation with specified UUID " + str(annotation_uuid))
    values = query.get_annotation_values([annotation_uuid])
    jsonified_values = [value.jsonify() for value in values]
    return jsonify(jsonified_values)

@bp.route("/query-sources", methods=["GET", "POST"])
def query_sources_and_render():
    """
    Query sources amd render.
    """
    current_app.logger.debug("Query sources and render")
    if request.method == "POST":
        filters = request.form.to_dict(flat=False).copy()
        filters["offset"] = [""]

        sources = query_sources(filters)
        show = define_what_to_show_sources(filters)
        return render_template("eboa_nav/sources_nav.html", sources=sources, show=show, filters=filters)
    # end if

    return render_template("eboa_nav/query_sources.html")

@bp.route("/query-sources-pages", methods=["POST"])
def query_sources_pages():
    """
    Query sources using pages and render.
    """
    current_app.logger.debug("Query sources using pages and render")
    filters = request.json

    sources = query_sources(filters)
    show = define_what_to_show_sources(filters)
    return render_template("eboa_nav/sources_nav.html", sources=sources, show=show, filters=filters)

def define_what_to_show_sources(filters):
    """
    Function to define what to show for sources
    """

    show = {}
    show["validity_timeline"]=True
    if not "show_validity_timeline" in filters:
        show["validity_timeline"] = False
    # end if
    show["generation_to_ingestion_timeline"]=True
    if not "show_generation_to_ingestion_timeline" in filters:
        show["generation_to_ingestion_timeline"] = False
    # end if
    show["number_events_xy"]=True
    if not "show_number_events_xy" in filters:
        show["number_events_xy"] = False
    # end if
    show["ingestion_duration_xy"]=True
    if not "show_ingestion_duration_xy" in filters:
        show["ingestion_duration_xy"] = False
    # end if
    show["generation_time_to_ingestion_time_xy"]=True
    if not "show_generation_time_to_ingestion_time_xy" in filters:
        show["generation_time_to_ingestion_time_xy"] = False
    # end if
    
    return show

def query_sources(filters):
    """
    Query sources.
    """
    current_app.logger.debug("Query sources")
    kwargs = {}
    if filters["source"][0] != "":
        op="notlike"
        if not "source_notlike_check" in filters:
            op="like"
        # end if
        kwargs["names"] = {"filter": filters["source"][0], "op": filters["source_operator"][0]}
    # end if
    elif "sources" in filters and filters["sources"][0] != "":
        op="notin"
        if not "source_notin_check" in filters:
            op="in"
        # end if
        kwargs["names"] = {"filter": [], "op": op}
        i = 0
        for source in filters["sources"]:
            kwargs["names"]["filter"].append(source)
            i+=1
        # end for
    # end if
    if filters["dim_signature"][0] != "":
        op="notlike"
        if not "dim_signature_notlike_check" in filters:
            op="like"
        # end if
        kwargs["dim_signatures"] = {"filter": filters["dim_signature"][0], "op": filters["dim_signature_operator"][0]}
    # end if
    elif "dim_signatures" in filters and filters["dim_signatures"][0] != "":
        op="notin"
        if not "dim_signature_notin_check" in filters:
            op="in"
        # end if
        kwargs["dim_signatures"] = {"filter": [], "op": op}
        i = 0
        for dim_signature in filters["dim_signatures"]:
            kwargs["dim_signatures"]["filter"].append(dim_signature)
            i+=1
        # end for
    # end if
    if filters["validity_start"][0] != "":
        kwargs["validity_start_filters"] = []
        i = 0
        operators = filters["validity_start_operator"]
        for start in filters["validity_start"]:
            kwargs["validity_start_filters"].append({"date": start, "op": operators[i]})
            i+=1
        # end for
    # end if
    if filters["validity_stop"][0] != "":
        kwargs["validity_stop_filters"] = []
        i = 0
        operators = filters["validity_stop_operator"]
        for stop in filters["validity_stop"]:
            kwargs["validity_stop_filters"].append({"date": stop, "op": operators[i]})
            i+=1
        # end for
    # end if
    if filters["reported_validity_start"][0] != "":
        kwargs["reported_validity_start_filters"] = []
        i = 0
        operators = filters["reported_validity_start_operator"]
        for start in filters["reported_validity_start"]:
            kwargs["reported_validity_start_filters"].append({"date": start, "op": operators[i]})
            i+=1
        # end for
    # end if
    if filters["reported_validity_stop"][0] != "":
        kwargs["reported_validity_stop_filters"] = []
        i = 0
        operators = filters["reported_validity_stop_operator"]
        for stop in filters["reported_validity_stop"]:
            kwargs["reported_validity_stop_filters"].append({"date": stop, "op": operators[i]})
            i+=1
        # end for
    # end if
    if filters["reception_time"][0] != "":
        kwargs["reception_time_filters"] = []
        i = 0
        operators = filters["reception_time_operator"]
        for reception_time in filters["reception_time"]:
            kwargs["reception_time_filters"].append({"date": reception_time, "op": operators[i]})
            i+=1
        # end for
    # end if
    if filters["ingestion_time"][0] != "":
        kwargs["ingestion_time_filters"] = []
        i = 0
        operators = filters["ingestion_time_operator"]
        for ingestion_time in filters["ingestion_time"]:
            kwargs["ingestion_time_filters"].append({"date": ingestion_time, "op": operators[i]})
            i+=1
        # end for
    # end if
    if filters["processing_duration"][0] != "":
        kwargs["processing_duration_filters"] = []
        i = 0
        operators = filters["processing_duration_operator"]
        for processing_duration in filters["processing_duration"]:
            kwargs["processing_duration_filters"].append({"float": float(processing_duration), "op": operators[i]})
            i+=1
        # end for
    # end if
    if filters["ingestion_duration"][0] != "":
        kwargs["ingestion_duration_filters"] = []
        i = 0
        operators = filters["ingestion_duration_operator"]
        for ingestion_duration in filters["ingestion_duration"]:
            kwargs["ingestion_duration_filters"].append({"float": float(ingestion_duration), "op": operators[i]})
            i+=1
        # end for
    # end if
    if filters["generation_time"][0] != "":
        kwargs["generation_time_filters"] = []
        i = 0
        operators = filters["generation_time_operator"]
        for generation_time in filters["generation_time"]:
            kwargs["generation_time_filters"].append({"date": generation_time, "op": operators[i]})
            i+=1
        # end for
    # end if
    if filters["reported_generation_time"][0] != "":
        kwargs["reported_generation_time_filters"] = []
        i = 0
        operators = filters["reported_generation_time_operator"]
        for reported_generation_time in filters["reported_generation_time"]:
            kwargs["reported_generation_time_filters"].append({"date": reported_generation_time, "op": operators[i]})
            i+=1
        # end for
    # end if
    if filters["ingestion_completeness"][0] != "":
        kwargs["ingestion_completeness"] = bool(util.strtobool(filters["ingestion_completeness"][0]))
    # end if
    if filters["processor"][0] != "":
        op="notlike"
        if not "processor_notlike_check" in filters:
            op="like"
        # end if
        kwargs["processors"] = {"filter": filters["processor"][0], "op": filters["processor_operator"][0]}
    # end if
    elif "processors" in filters and filters["processors"][0] != "":
        op="notin"
        if not "processor_notin_check" in filters:
            op="in"
        # end if
        kwargs["processors"] = {"filter": [], "op": op}
        i = 0
        for processor in filters["processors"]:
            kwargs["processors"]["filter"].append(processor)
            i+=1
        # end for
    # end if

    if filters["source_validity_duration"][0] != "":
        kwargs["validity_duration_filters"] = []
        i = 0
        operators = filters["source_validity_duration_operator"]
        for source_validity_duration in filters["source_validity_duration"]:
            kwargs["validity_duration_filters"].append({"float": float(source_validity_duration), "op": operators[i]})
            i+=1
        # end for
    # end if

    if "source_statuses" in filters and filters["source_statuses"][0] != "":
        op="notin"
        if not "status_notin_check" in filters:
            op="in"
        # end if
        kwargs["statuses"] = {"filter": [], "op": op}
        i = 0
        for status in filters["source_statuses"]:
            kwargs["statuses"]["filter"].append(str(eboa_engine.exit_codes[status]["status"]))
            i+=1
        # end for
    # end if
    
    # Query restrictions
    if filters["order_by"][0] != "":
        descending = True
        if not "order_descending" in filters:
            descending = False
        # end if
        kwargs["order_by"] = {"field": filters["order_by"][0], "descending": descending}
    # end if

    if filters["limit"][0] != "":
        kwargs["limit"] = filters["limit"][0]
    # end if

    if filters["offset"][0] != "":
        kwargs["offset"] = filters["offset"][0]
    # end if

    sources = query.get_sources(**kwargs)

    return sources

@bp.route("/query-source/<uuid:source_uuid>")
def query_source(source_uuid):
    """
    Query source corresponding to the UUID received.
    """
    current_app.logger.debug("Query source")
    source = query.get_sources(source_uuids={"filter": [source_uuid], "op": "in"})
    show = {}
    show["validity_timeline"]=True
    show["generation_to_ingestion_timeline"]=True
    show["number_events_xy"]=True
    show["ingestion_duration_xy"]=True
    show["generation_time_to_ingestion_time_xy"]=True

    filters = {}
    filters["offset"] = [""]
    filters["limit"] = ["100"]
    
    return render_template("eboa_nav/sources_nav.html", sources=source, show=show, filters=filters)

@bp.route("/query-sources-by-name/<string:name>")
def query_sources_by_name(name):
    """
    Query sources corresponding to the name received.
    """
    current_app.logger.debug("Query sources by name")
    sources = query.get_sources(names={"filter": name, "op": "=="})
    show = {}
    show["validity_timeline"]=True
    show["generation_to_ingestion_timeline"]=True
    show["number_events_xy"]=True
    show["ingestion_duration_xy"]=True
    show["generation_time_to_ingestion_time_xy"]=True

    filters = {}
    filters["offset"] = [""]
    filters["limit"] = ["100"]
    
    return render_template("eboa_nav/sources_nav.html", sources=sources, show=show, filters=filters)

@bp.route("/query-sources-by-dim/<uuid:dim_signature_uuid>")
def query_sources_by_dim(dim_signature_uuid):
    """
    Query sources associated to the DIM signature corresponding to the UUID received.
    """
    current_app.logger.debug("Query sources by DIM signature")
    sources = query.get_sources(dim_signature_uuids={"filter": [dim_signature_uuid], "op": "in"})
    show = {}
    show["validity_timeline"]=True
    show["generation_to_ingestion_timeline"]=True
    show["number_events_xy"]=True
    show["ingestion_duration_xy"]=True
    show["generation_time_to_ingestion_time_xy"]=True

    filters = {}    
    filters["offset"] = [""]
    filters["limit"] = ["100"]
    
    return render_template("eboa_nav/sources_nav.html", sources=sources, show=show, filters=filters)

@bp.route("/query-jsonify-sources")
def query_jsonify_sources():
    """
    Query all the sources.
    """

    current_app.logger.debug("Query source")

    # Get limit and offset values
    limit = request.args.get("limit")
    offset = request.args.get("offset")
    search = request.args.get("search")

    # Set the filters for the query
    kwargs = {}
    kwargs["limit"] = limit
    kwargs["offset"] = offset
    kwargs["order_by"] = {"field": "reception_time", "descending": True}
    kwargs["names"] = {"filter": search, "op": "=="}

    sources = query.get_sources(**kwargs)
    jsonified_sources = [source.jsonify() for source in sources]
    return jsonify(jsonified_sources)

@bp.route("/query-jsonify-sources-by-processor")
def query_jsonify_sources_by_processor():
    """
    Query all the sources.
    """

    current_app.logger.debug("Query source")

    # Get limit and offset values
    limit = request.args.get("limit")
    offset = request.args.get("offset")
    search = request.args.get("search")

    # Set the filters for the query
    kwargs = {}
    kwargs["limit"] = limit
    kwargs["offset"] = offset
    kwargs["order_by"] = {"field": "reception_time", "descending": True}
    kwargs["processors"] = {"filter": "%" + search + "%", "op": "like"}

    sources = query.get_sources(**kwargs)
    jsonified_sources = [source.jsonify() for source in sources]
    return jsonify(jsonified_sources)

@bp.route("/query-jsonify-source-statuses/<uuid:source_uuid>")
def query_jsonify_source_statuses(source_uuid):
    """
    Query statuses related to the source with the corresponding received UUID.
    """
    current_app.logger.debug("Query statuses corresponding to the source with the specified UUID " + str(source_uuid))
    sources = query.get_sources(source_uuids = {"filter": [source_uuid], "op": "in"})
    jsonified_statuses = [source_status.jsonify() for source in sources for source_status in source.statuses]
    return jsonify(jsonified_statuses)

@bp.route("/get-source-status")
def get_source_status():
    """
    Get the source statuses defined in the EBOA component.
    """
    current_app.logger.debug("Get source statuses")
    return jsonify(eboa_engine.exit_codes)

def prepare_reingestion_of_sources_and_dependencies(sources, source_uuids_matching_triggering_rule, source_uuids_not_matching_triggering_rule):

    sources_to_follow_reingestion = []
    
    if len(sources) > 0:
        # Get triggering configuration
        triggering_xpath = get_triggering_conf()
        for source in sources:
            matching_rules = triggering_xpath("/triggering_rules/rule[match(source_mask, $file_name)]", file_name = source.name)
            if len(matching_rules) > 0:
                rule = matching_rules[0]
                skip = rule.get("skip")
                if skip != "true":
                    source_uuids_matching_triggering_rule.append(source.source_uuid)
                    source_type = triggering_xpath("/triggering_rules/rule[match(source_mask, $file_name)]/source_type", file_name = source.name)[0].text
                    source_masks_depending_on_this = triggering_xpath("/triggering_rules/rule[dependencies/source_type = $source_type]/source_mask", source_type = source_type)
                    if len(source_masks_depending_on_this) > 0:
                        source_masks_sql = [source_mask.text.replace('.*', '%').replace('.', '_').replace('*', '%') for source_mask in source_masks_depending_on_this]
                        # Obtain events linking to the events of the source
                        event_uuid_links = [link.event_uuid_link for event in source.events for link in event.eventLinks]

                        for source_mask_sql in source_masks_sql:
                            events = query.get_events(event_uuids = {"filter": event_uuid_links, "op": "in"}, sources = {"filter": source_mask_sql, "op": "like"})
                            sources_linked = [event.source for event in events]
                            sources_to_follow_reingestion = sources_to_follow_reingestion + [source for source in sources_linked if source.source_uuid not in source_uuids_matching_triggering_rule]
                        # end for
                    # end if
                else:
                    source_uuids_not_matching_triggering_rule.append(source.source_uuid)
                # end if
            else:
                source_uuids_not_matching_triggering_rule.append(source.source_uuid)
            # end if
        # end for
    # end if

    if len(sources_to_follow_reingestion) > 0:
        prepare_reingestion_of_sources_and_dependencies(list(set(sources_to_follow_reingestion)), source_uuids_matching_triggering_rule, source_uuids_not_matching_triggering_rule)
    # end if

    return

@bp.route("/prepare-reingestion-of-sources", methods=["POST"])
def prepare_reingestion_of_sources():
    """
    Prepare reingestion of selected sources.
    """
    current_app.logger.debug("Prepare reingestion of selected sources")
    filters = request.json
    sources_from_uuids = query.get_sources(source_uuids = {"filter": filters["sources"], "op": "in"})

    sources = query.get_sources(names = {"filter": [source.name for source in sources_from_uuids], "op": "in"})

    source_uuids_matching_triggering_rule = []
    source_uuids_not_matching_triggering_rule = []
    prepare_reingestion_of_sources_and_dependencies(sources, source_uuids_matching_triggering_rule, source_uuids_not_matching_triggering_rule)

    sources_matching_triggering_rule = query.get_sources(source_uuids = {"filter": source_uuids_matching_triggering_rule, "op": "in"})

    sources_not_matching_triggering_rule = query.get_sources(source_uuids = {"filter": source_uuids_not_matching_triggering_rule, "op": "in"})

    return render_template("eboa_nav/reingestion_of_sources.html", sources_matching_triggering_rule=sources_matching_triggering_rule, sources_not_matching_triggering_rule=sources_not_matching_triggering_rule)

@bp.route("/prepare-deletion-of-sources", methods=["POST"])
def prepare_deletion_of_sources():
    """
    Prepare deletion of selected sources.
    """
    current_app.logger.debug("Prepare deletion of selected sources")
    filters = request.json
    sources_from_uuids = query.get_sources(source_uuids = {"filter": filters["sources"], "op": "in"})

    sources = query.get_sources(names = {"filter": [source.name for source in sources_from_uuids], "op": "in"})

    return render_template("eboa_nav/deletion_of_sources.html", sources=sources)

@bp.route("/download-source/<string:source_name>")
def download_source(source_name):
    """
    Download of selected source.
    """
    current_app.logger.debug("Download of selected source")

    command = "minArcStatus --file " + source_name
    command_split = shlex.split(command)
    program = Popen(command_split, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, error = program.communicate()        
    return_code = program.returncode

    # Get filename and filepath from minArcStatus output
    filename = output.decode().split(",")[1].split('=>')[1].replace('"', "")
    filepath = output.decode().split(",")[2].split('=>')[1].replace('"', "")

    return send_from_directory(filepath, filename, as_attachment=True)

@bp.route("/delete-sources", methods=["POST"])
def delete_sources():
    """
    Delete selected sources.
    """
    current_app.logger.debug("Delete selected sources")
    filters = request.json
    query.get_sources(names = {"filter": filters["sources"], "op": "in"}, delete=True)

    return {"status": "OK"}

@bp.route("/query-gauges", methods=["GET", "POST"])
def query_gauges_and_render():
    """
    Query gauges amd render.
    """
    current_app.logger.debug("Query gauges and render")
    if request.method == "POST":
        filters = request.form.to_dict(flat=False).copy()
        filters["offset"] = [""]
        gauges = query_gauges(filters)

        show = define_what_to_show_gauges(filters)

        links = []
        if show["network"]:
            links = query_linked_gauges(gauges)
        # end if
        
        return render_template("eboa_nav/gauges_nav.html", gauges=gauges, links=links, show=show, filters=filters)
    # end if

    return render_template("eboa_nav/query_gauges.html")

@bp.route("/query-gauges-pages", methods=["POST"])
def query_gauges_pages():
    """
    Query gauges using pages and render.
    """
    current_app.logger.debug("Query gauges using pages and render")

    filters = request.json
    gauges = query_gauges(filters)

    show = define_what_to_show_gauges(filters)

    links = []
    if show["network"]:
        links = query_linked_gauges(gauges)
    # end if

    return render_template("eboa_nav/gauges_nav.html", gauges=gauges, links=links, show=show, filters=filters)

def define_what_to_show_gauges(filters):

    show = {}
    if not "show_network" in filters:
        show["network"] = False
    else:
        show["network"]=True
    # end if

    return show
    
@bp.route("/query-gauges-by-dim/<uuid:dim_signature_uuid>")
def query_gauges_by_dim(dim_signature_uuid):
    """
    Query gauges associated to the DIM signature corresponding to the UUID received.
    """
    current_app.logger.debug("Query gauges by DIM signature")
    gauges = query.get_gauges(dim_signature_uuids={"filter": [dim_signature_uuid], "op": "in"})
    show = {}
    show["network"]=True

    filters = {}
    filters["offset"] = [""]
    filters["limit"] = ["100"]
    
    links = query_linked_gauges(gauges)

    return render_template("eboa_nav/gauges_nav.html", gauges=gauges, links=links, show=show, filters=filters)

def register_gauge_node (links, gauge, registered_gauges):
    """
    Register gauge node for the linked gauges.
    """
    if gauge.gauge_uuid not in registered_gauges:
        registered_gauges[gauge.gauge_uuid] = {
            "gauge_uuid": str(gauge.gauge_uuid),
            "name": gauge.name,
            "system": gauge.system,
            "dim_signature_uuid": gauge.dim_signature_uuid,
            "dim_signature_name": gauge.dim_signature.dim_signature,
            "gauges_linking": [],
            "gauges_linked": []
        }
        links.append(registered_gauges[gauge.gauge_uuid])
    # end if
    return registered_gauges[gauge.gauge_uuid]

def query_linked_gauges(gauges):
    """
    Query linked gauges.
    """
    current_app.logger.debug("Query linked gauges")
    links = []
    linked_gauges = {}
    registered_gauges = {}
    for gauge in gauges:
        gauge_node = register_gauge_node(links, gauge, registered_gauges)
        # Get the associated events
        events = query.get_events(gauge_uuids = {"filter": [gauge.gauge_uuid], "op": "in"},
                                  limit = 1)
        if len(events) > 0:
            # Get the events that link to the related events
            linking_event_uuids = [event_link.event_uuid_link for event_link in events[0].eventLinks]
            linking_events = query.get_events(event_uuids = {"filter": linking_event_uuids, "op": "in"})

            # Get the events that linked by the related events
            linked_event_links = query.get_event_links(event_uuid_links = {"filter": [events[0].event_uuid], "op": "in"})
            linked_event_uuids = [event_link.event_uuid for event_link in linked_event_links]
            linked_events = query.get_events(event_uuids = {"filter": linked_event_uuids, "op": "in"})

            # Get the gauges associated to the events linking to the related events
            gauges_linking = set([(str(event.gauge.gauge_uuid), [event_link.name for event_link in events[0].eventLinks if event_link.event_uuid_link == event.event_uuid][0]) for event in linking_events])

            # Get the gauges associated to the events linked by the related events
            gauges_linked = set([(str(event.gauge.gauge_uuid), [event_link.name for event_link in linked_event_links if event_link.event_uuid == event.event_uuid][0]) for event in linked_events])

            linking_linked_events = set (linked_events + linking_events)
            unique_linking_linked_gauges = set([event.gauge for event in linking_linked_events])
            for linking_linked_gauge in unique_linking_linked_gauges:
                register_gauge_node(links, linking_linked_gauge, registered_gauges)
            # end for
            
            # Associate gauges
            for gauge_linking in gauges_linking:
                gauge_linking_uuid = gauge_linking[0]
                link_name = gauge_linking[1]
                if (gauge_linking_uuid, str(gauge.gauge_uuid)) not in linked_gauges:
                    linked_gauges[(gauge_linking_uuid, str(gauge.gauge_uuid))] = True
                    gauge_node["gauges_linking"].append({"gauge_uuid": gauge_linking_uuid, "link_name": link_name})
                # end if
            # end for
            for gauge_linked in gauges_linked:
                gauge_linked_uuid = gauge_linked[0]
                link_name = gauge_linked[1]
                if (str(gauge.gauge_uuid), gauge_linked_uuid) not in linked_gauges:
                    linked_gauges[(str(gauge.gauge_uuid), gauge_linked_uuid)] = True
                    gauge_node["gauges_linked"].append({"gauge_uuid": gauge_linked_uuid, "link_name": link_name})
                # end if
            # end for
        # end if
    # end for

    return links

def query_gauges(filters):
    """
    Query gauges.
    """
    current_app.logger.debug("Query gauges")
    kwargs = {}
    if filters["gauge_name"][0] != "":
        op="notlike"
        if not "gauge_name_notlike_check" in filters:
            op="like"
        # end if
        kwargs["names"] = {"filter": filters["gauge_name"][0], "op": filters["gauge_name_operator"][0]}
    # end if
    elif "gauge_names" in filters and filters["gauge_names"][0] != "":
        op="notin"
        if not "gauge_name_notin_check" in filters:
            op="in"
        # end if
        kwargs["names"] = {"filter": [], "op": op}
        i = 0
        for gauge_name in filters["gauge_names"]:
            kwargs["names"]["filter"].append(gauge_name)
            i+=1
        # end for
    # end if
    if filters["gauge_system"][0] != "":
        op="notlike"
        if not "gauge_system_notlike_check" in filters:
            op="like"
        # end if
        kwargs["systems"] = {"filter": filters["gauge_system"][0], "op": filters["gauge_system_operator"][0]}
    # end if
    elif "gauge_systems" in filters and filters["gauge_systems"][0] != "":
        op="notin"
        if not "gauge_system_notin_check" in filters:
            op="in"
        # end if
        kwargs["systems"] = {"filter": [], "op": op}
        i = 0
        for gauge_system in filters["gauge_systems"]:
            kwargs["systems"]["filter"].append(gauge_system)
            i+=1
        # end for
    # end if
    if filters["dim_signature"][0] != "":
        op="notlike"
        if not "dim_signature_notlike_check" in filters:
            op="like"
        # end if
        kwargs["dim_signatures"] = {"filter": filters["dim_signature"][0], "op": filters["dim_signature_operator"][0]}
    # end if
    elif "dim_signatures" in filters and filters["dim_signatures"][0] != "":
        op="notin"
        if not "dim_signature_notin_check" in filters:
            op="in"
        # end if
        kwargs["dim_signatures"] = {"filter": [], "op": op}
        i = 0
        for dim_signature in filters["dim_signatures"]:
            kwargs["dim_signatures"]["filter"].append(dim_signature)
            i+=1
        # end for
    # end if

    # Query restrictions
    if filters["order_by"][0] != "":
        descending = True
        if not "order_descending" in filters:
            descending = False
        # end if
        kwargs["order_by"] = {"field": filters["order_by"][0], "descending": descending}
    # end if

    if filters["limit"][0] != "":
        kwargs["limit"] = filters["limit"][0]
    # end if

    if filters["offset"][0] != "":
        kwargs["offset"] = filters["offset"][0]
    # end if

    gauges = query.get_gauges(**kwargs)

    return gauges

@bp.route("/query-jsonify-gauges-by-name")
def query_jsonify_gauges_by_name():
    """
    Query all the gauges.
    """
    current_app.logger.debug("Query gauge by name")
    # Get limit and offset values
    limit = request.args.get("limit")
    offset = request.args.get("offset")
    search = request.args.get("search")

    # Set the filters for the query
    kwargs = {}
    kwargs["limit"] = limit
    kwargs["offset"] = offset
    kwargs["names"] = {"filter": "%" + search + "%", "op": "like"}

    gauges = query.get_gauges(**kwargs)
    jsonified_gauges = [gauge.jsonify() for gauge in gauges]
    return jsonify(jsonified_gauges)

@bp.route("/query-jsonify-gauges-by-system")
def query_jsonify_gauges_by_system():
    """
    Query all the gauges.
    """
    current_app.logger.debug("Query gauge by system")
    # Get limit and offset values
    limit = request.args.get("limit")
    offset = request.args.get("offset")
    search = request.args.get("search")

    # Set the filters for the query
    kwargs = {}
    kwargs["limit"] = limit
    kwargs["offset"] = offset
    kwargs["systems"] = {"filter": "%" + search + "%", "op": "like"}

    gauges = query.get_gauges(**kwargs)
    jsonified_gauges = [gauge.jsonify() for gauge in gauges]
    return jsonify(jsonified_gauges)

@bp.route("/query-annotation-cnfs", methods=["GET", "POST"])
def query_annotation_cnfs_and_render():
    """
    Query annotation configurations amd render.
    """
    current_app.logger.debug("Query annotation configurations and render")
    if request.method == "POST":
        filters = request.form.to_dict(flat=False).copy()
        filters["offset"] = [""]
        annotation_cnfs = query_annotation_cnfs(filters)

        return render_template("eboa_nav/annotation_cnfs_nav.html", annotation_cnfs=annotation_cnfs, filters=filters)
    # end if

    return render_template("eboa_nav/query_annotation_cnfs.html")

@bp.route("/query-annotation-cnfs-pages", methods=["POST"])
def query_annotation_cnfs_pages():
    """
    Query annotation configurations using pages and render.
    """
    current_app.logger.debug("Query annotation configurations using pages and render")
    filters = request.json
    annotation_cnfs = query_annotation_cnfs(filters)

    return render_template("eboa_nav/annotation_cnfs_nav.html", annotation_cnfs=annotation_cnfs, filters=filters)

@bp.route("/query-annotation-cnfs-by-dim/<uuid:dim_signature_uuid>")
def query_annotation_cnfs_by_dim(dim_signature_uuid):
    """
    Query annotation configurations associated to the DIM signature corresponding to the UUID received.
    """
    current_app.logger.debug("Query annotation configurations by DIM signature")
    annotation_cnfs = query.get_annotation_cnfs(dim_signature_uuids={"filter": [dim_signature_uuid], "op": "in"})

    filters = {}
    filters["offset"] = [""]
    filters["limit"] = ["100"]
    
    return render_template("eboa_nav/annotation_cnfs_nav.html", annotation_cnfs=annotation_cnfs, filters=filters)

def query_annotation_cnfs(filters):
    """
    Query annotation configurations.
    """
    current_app.logger.debug("Query annotation configurations")
    kwargs = {}
    if filters["annotation_name"][0] != "":
        op="notlike"
        if not "annotation_name_notlike_check" in filters:
            op="like"
        # end if
        kwargs["names"] = {"filter": filters["annotation_name"][0], "op": filters["annotation_name_operator"][0]}
    # end if
    elif "annotation_names" in filters and filters["annotation_names"][0] != "":
        op="notin"
        if not "annotation_name_notin_check" in filters:
            op="in"
        # end if
        kwargs["names"] = {"filter": [], "op": op}
        i = 0
        for annotation_name in filters["annotation_names"]:
            kwargs["names"]["filter"].append(annotation_name)
            i+=1
        # end for
    # end if
    if filters["annotation_system"][0] != "":
        op="notlike"
        if not "annotation_system_notlike_check" in filters:
            op="like"
        # end if
        kwargs["systems"] = {"filter": filters["annotation_system"][0], "op": filters["annotation_system_operator"][0]}
    # end if
    elif "annotation_systems" in filters and filters["annotation_systems"][0] != "":
        op="notin"
        if not "annotation_system_notin_check" in filters:
            op="in"
        # end if
        kwargs["systems"] = {"filter": [], "op": op}
        i = 0
        for annotation_system in filters["annotation_systems"]:
            kwargs["systems"]["filter"].append(annotation_system)
            i+=1
        # end for
    # end if
    if filters["dim_signature"][0] != "":
        op="notlike"
        if not "dim_signature_notlike_check" in filters:
            op="like"
        # end if
        kwargs["dim_signatures"] = {"filter": filters["dim_signature"][0], "op": filters["dim_signature_operator"][0]}
    # end if
    elif "dim_signatures" in filters and filters["dim_signatures"][0] != "":
        op="notin"
        if not "dim_signature_notin_check" in filters:
            op="in"
        # end if
        kwargs["dim_signatures"] = {"filter": [], "op": op}
        i = 0
        for dim_signature in filters["dim_signatures"]:
            kwargs["dim_signatures"]["filter"].append(dim_signature)
            i+=1
        # end for
    # end if

    # Query restrictions
    if filters["order_by"][0] != "":
        descending = True
        if not "order_descending" in filters:
            descending = False
        # end if
        kwargs["order_by"] = {"field": filters["order_by"][0], "descending": descending}
    # end if

    if filters["limit"][0] != "":
        kwargs["limit"] = filters["limit"][0]
    # end if

    if filters["offset"][0] != "":
        kwargs["offset"] = filters["offset"][0]
    # end if

    annotation_cnfs = query.get_annotation_cnfs(**kwargs)

    return annotation_cnfs

@bp.route("/query-jsonify-annotation-cnfs-by-name")
def query_jsonify_annotation_cnfs_by_name():
    """
    Query all the annotation configurations.
    """
    current_app.logger.debug("Query annotation configurations")
    # Get limit and offset values
    limit = request.args.get("limit")
    offset = request.args.get("offset")
    search = request.args.get("search")

    # Set the filters for the query
    kwargs = {}
    kwargs["limit"] = limit
    kwargs["offset"] = offset
    kwargs["names"] = {"filter": "%" + search + "%", "op": "like"}
    
    annotation_cnfs = query.get_annotation_cnfs(**kwargs)
    jsonified_annotation_cnfs = [annotation_cnf.jsonify() for annotation_cnf in annotation_cnfs]
    return jsonify(jsonified_annotation_cnfs)

@bp.route("/query-jsonify-annotation-cnfs-by-system")
def query_jsonify_annotation_cnfs_by_system():
    """
    Query all the annotation configurations.
    """
    current_app.logger.debug("Query annotation configurations")
    # Get limit and offset values
    limit = request.args.get("limit")
    offset = request.args.get("offset")
    search = request.args.get("search")

    # Set the filters for the query
    kwargs = {}
    kwargs["limit"] = limit
    kwargs["offset"] = offset
    kwargs["systems"] = {"filter": "%" + search + "%", "op": "like"}
    
    annotation_cnfs = query.get_annotation_cnfs(**kwargs)
    jsonified_annotation_cnfs = [annotation_cnf.jsonify() for annotation_cnf in annotation_cnfs]
    return jsonify(jsonified_annotation_cnfs)

@bp.route("/query-jsonify-keys")
def query_jsonify_keys():
    """
    Query all the keys.
    """
    current_app.logger.debug("Query event keys")
    # Get limit and offset values
    limit = request.args.get("limit")
    offset = request.args.get("offset")
    search = request.args.get("search")

    # Set the filters for the query
    kwargs = {}
    kwargs["limit"] = limit
    kwargs["offset"] = offset
    kwargs["keys"] = {"filter": search, "op": "=="}

    keys = query.get_event_keys(**kwargs)
    jsonified_keys = [key.jsonify() for key in keys]
    return jsonify(jsonified_keys)

@bp.route("/query-ers", methods=["GET", "POST"])
def query_ers_and_render():
    """
    Query explicit references and render.
    """
    current_app.logger.debug("Query explicit references and render")
    if request.method == "POST":
        filters = request.form.to_dict(flat=False).copy()
        filters["offset"] = [""]
        ers = query_ers(filters)

        return render_template("eboa_nav/explicit_references_nav.html", ers=ers, filters=filters)
    # end if
    return render_template("eboa_nav/query_explicit_references.html")

@bp.route("/query-ers-pages", methods=["POST"])
def query_ers_pages():
    """
    Query explicit references using pages and render.
    """
    current_app.logger.debug("Query explicit references using pages and render")
    filters = request.json
    ers = query_ers(filters)

    return render_template("eboa_nav/explicit_references_nav.html", ers=ers, filters=filters)

def query_ers(filters):
    """
    Query explicit references.
    """
    current_app.logger.debug("Query explicit references")

    kwargs = {}
    if filters["er"][0] != "":
        op="notlike"
        if not "er_notlike_check" in filters:
            op="like"
        # end if
        kwargs["explicit_refs"] = {"filter": filters["er"][0], "op": filters["er_operator"][0]}
    # end if
    elif "ers" in filters and filters["ers"][0] != "":
        op="notin"
        if not "er_notin_check" in filters:
            op="in"
        # end if
        kwargs["explicit_refs"] = {"filter": [], "op": op}
        i = 0
        for er in filters["ers"]:
            kwargs["explicit_refs"]["filter"].append(er)
            i+=1
        # end for
    # end if
    if filters["group"][0] != "":
        op="notlike"
        if not "group_notlike_check" in filters:
            op="like"
        # end if
        kwargs["groups"] = {"filter": filters["group"][0], "op": filters["group_operator"][0]}
    # end if
    elif "groups" in filters and filters["groups"][0] != "":
        op="notin"
        if not "group_notin_check" in filters:
            op="in"
        # end if
        kwargs["groups"] = {"filter": [], "op": op}
        i = 0
        for group in filters["groups"]:
            kwargs["groups"]["filter"].append(group)
            i+=1
        # end for
    # end if
    if filters["source"][0] != "":
        op="notlike"
        if not "source_notlike_check" in filters:
            op="like"
        # end if
        kwargs["sources"] = {"filter": filters["source"][0], "op": filters["source_operator"][0]}
    # end if
    elif "sources" in filters and filters["sources"][0] != "":
        op="notin"
        if not "source_notin_check" in filters:
            op="in"
        # end if
        kwargs["sources"] = {"filter": [], "op": op}
        i = 0
        for source in filters["sources"]:
            kwargs["sources"]["filter"].append(source)
            i+=1
        # end for
    # end if
    if filters["ingestion_time"][0] != "":
        kwargs["explicit_ref_ingestion_time_filters"] = []
        i = 0
        operators = filters["ingestion_time_operator"]
        for ingestion_time in filters["ingestion_time"]:
            kwargs["explicit_ref_ingestion_time_filters"].append({"date": ingestion_time, "op": operators[i]})
            i+=1
        # end for
    # end if

    ####
    # Event filters
    ####
    if filters["key"][0] != "":
        op="notlike"
        if not "key_notlike_check" in filters:
            op="like"
        # end if
        kwargs["keys"] = {"filter": filters["key"][0], "op": filters["key_operator"][0]}
    # end if
    elif "keys" in filters and filters["keys"][0] != "":
        op="notin"
        if not "key_notin_check" in filters:
            op="in"
        # end if
        kwargs["keys"] = {"filter": [], "op": op}
        i = 0
        for key in filters["keys"]:
            kwargs["keys"]["filter"].append(key)
            i+=1
        # end for
    # end if
    if filters["event_value_name"][0] != "":
        value_operators = filters["event_value_operator"]
        value_types = filters["event_value_type"]
        values = filters["event_value"]
        value_name_ops = filters["event_value_name_op"]
        kwargs["event_value_filters"] = []
        i = 0
        for value_name in filters["event_value_name"]:
            if value_name[0] != "":
                if (values[i] == "" and value_types[i] == "text") or (values[i][0] != "" and value_types[i] != "object"):
                    kwargs["event_value_filters"].append({"name": {"op": value_name_ops[i], "filter": value_name},
                                                          "type": value_types[i],
                                                          "value": {"op": value_operators[i], "filter": values[i]}})
                else:
                    kwargs["event_value_filters"].append({"name": {"op": value_name_ops[i], "filter": value_name},
                                                          "type": value_types[i]})
            # end if
            i+=1
        # end for
    # end if
    if filters["gauge_name"][0] != "":
        op="notlike"
        if not "gauge_name_notlike_check" in filters:
            op="like"
        # end if
        kwargs["gauge_names"] = {"filter": filters["gauge_name"][0], "op": filters["gauge_name_operator"][0]}
    # end if
    elif "gauge_names" in filters and filters["gauge_names"][0] != "":
        op="notin"
        if not "gauge_name_notin_check" in filters:
            op="in"
        # end if
        kwargs["gauge_names"] = {"filter": [], "op": op}
        i = 0
        for gauge_name in filters["gauge_names"]:
            kwargs["gauge_names"]["filter"].append(gauge_name)
            i+=1
        # end for
    # end if
    if filters["gauge_system"][0] != "":
        op="notlike"
        if not "gauge_system_notlike_check" in filters:
            op="like"
        # end if
        kwargs["gauge_systems"] = {"filter": filters["gauge_system"][0], "op": filters["gauge_system_operator"][0]}
    # end if
    elif "gauge_systems" in filters and filters["gauge_systems"][0] != "":
        op="notin"
        if not "gauge_system_notin_check" in filters:
            op="in"
        # end if
        kwargs["gauge_systems"] = {"filter": [], "op": op}
        i = 0
        for gauge_system in filters["gauge_systems"]:
            kwargs["gauge_systems"]["filter"].append(gauge_system)
            i+=1
        # end for
    # end if
    if filters["start"][0] != "":
        kwargs["start_filters"] = []
        i = 0
        operators = filters["start_operator"]
        for start in filters["start"]:
            kwargs["start_filters"].append({"date": start, "op": operators[i]})
            i+=1
        # end for
    # end if
    if filters["stop"][0] != "":
        kwargs["stop_filters"] = []
        i = 0
        operators = filters["stop_operator"]
        for stop in filters["stop"]:
            kwargs["stop_filters"].append({"date": stop, "op": operators[i]})
            i+=1
        # end for
    # end if
    if filters["event_duration"][0] != "":
        kwargs["duration_filters"] = []
        i = 0
        operators = filters["event_duration_operator"]
        for event_duration in filters["event_duration"]:
            kwargs["duration_filters"].append({"float": float(event_duration), "op": operators[i]})
            i+=1
        # end for
    # end if

    ####
    # Annotation filters
    ####
    if filters["annotation_value_name"][0] != "":
        value_operators = filters["annotation_value_operator"]
        value_types = filters["annotation_value_type"]
        values = filters["annotation_value"]
        value_name_ops = filters["annotation_value_name_op"]
        kwargs["annotation_value_filters"] = []
        i = 0
        for value_name in filters["annotation_value_name"]:
            if value_name[0] != "":
                if (values[i] == "" and value_types[i] == "text") or (values[i][0] != "" and value_types[i] != "object"):
                    kwargs["annotation_value_filters"].append({"name": {"op": value_name_ops[i], "filter": value_name},
                                                          "type": value_types[i],
                                                          "value": {"op": value_operators[i], "filter": values[i]}})
                else:
                    kwargs["annotation_value_filters"].append({"name": {"op": value_name_ops[i], "filter": value_name},
                                                          "type": value_types[i]})
            # end if
            i+=1
        # end for
    # end if
    if filters["annotation_name"][0] != "":
        op="notlike"
        if not "annotation_name_notlike_check" in filters:
            op="like"
        # end if
        kwargs["annotation_cnf_names"] = {"filter": filters["annotation_name"][0], "op": filters["annotation_name_operator"][0]}
    # end if
    elif "annotation_names" in filters and filters["annotation_names"][0] != "":
        op="notin"
        if not "annotation_name_notin_check" in filters:
            op="in"
        # end if
        kwargs["annotation_cnf_names"] = {"filter": [], "op": op}
        i = 0
        for annotation_name in filters["annotation_names"]:
            kwargs["annotation_cnf_names"]["filter"].append(annotation_name)
            i+=1
        # end for
    # end if
    if filters["annotation_system"][0] != "":
        op="notlike"
        if not "annotation_system_notlike_check" in filters:
            op="like"
        # end if
        kwargs["annotation_cnf_systems"] = {"filter": filters["annotation_system"][0], "op": filters["annotation_system_operator"][0]}
    # end if
    elif "annotation_systems" in filters and filters["annotation_systems"][0] != "":
        op="notin"
        if not "annotation_system_notin_check" in filters:
            op="in"
        # end if
        kwargs["annotation_cnf_systems"] = {"filter": [], "op": op}
        i = 0
        for annotation_system in filters["annotation_systems"]:
            kwargs["annotation_cnf_systems"]["filter"].append(annotation_system)
            i+=1
        # end for
    # end if

    # Query restrictions
    if filters["order_by"][0] != "":
        descending = True
        if not "order_descending" in filters:
            descending = False
        # end if
        kwargs["order_by"] = {"field": filters["order_by"][0], "descending": descending}
    # end if

    if filters["limit"][0] != "":
        kwargs["limit"] = filters["limit"][0]
    # end if

    if filters["offset"][0] != "":
        kwargs["offset"] = filters["offset"][0]
    # end if

    ers = query.get_explicit_refs(**kwargs)

    return ers

@bp.route("/query-er/<uuid:explicit_ref_uuid>")
def query_er(explicit_ref_uuid):
    """
    Query explicit reference corresponding to the UUID received.
    """
    current_app.logger.debug("Query explicit reference")
    er = query.get_explicit_refs(explicit_ref_uuids={"filter": [explicit_ref_uuid], "op": "in"})

    filters = {}
    filters["offset"] = [""]
    filters["limit"] = ["100"]
    
    return render_template("eboa_nav/explicit_references_nav.html", ers=er, filters=filters)

@bp.route("/query-er-by-name/<string:name>")
def query_er_by_name(name):
    """
    Query explicit reference corresponding to the name received.
    """
    current_app.logger.debug("Query explicit reference by name")
    er = query.get_explicit_refs(explicit_refs={"filter": name, "op": "=="})

    filters = {}
    filters["offset"] = [""]
    filters["limit"] = ["100"]
    
    return render_template("eboa_nav/explicit_references_nav.html", ers=er, filters=filters)

@bp.route("/query-er-links/<uuid:explicit_ref_uuid>")
def query_er_links_and_render(explicit_ref_uuid):
    """
    Query explicit references linked to the explicit reference corresponding to the UUID received and render.
    """
    current_app.logger.debug("Query explicit reference links and render")
    links = query_er_links(explicit_ref_uuid)
    ers = links["prime_explicit_refs"] + [link["explicit_ref"] for link in links["explicit_refs_linking"]] + [link["explicit_ref"] for link in links["linked_explicit_refs"]]
    return render_template("eboa_nav/linked_explicit_references_nav.html", links=links, ers=ers)

def query_er_links(explicit_ref_uuid):
    """
    Query explicit references linked to the explicit reference corresponding to the UUID received.
    """
    current_app.logger.debug("Query explicit reference links")
    links = query.get_linked_explicit_refs_details(explicit_ref_uuid=explicit_ref_uuid, back_ref = True)

    return links

@bp.route("/query-jsonify-ers")
def query_jsonify_ers():
    """
    Query all the ers.
    """
    current_app.logger.debug("Query explicit references")
    # Get limit and offset values
    limit = request.args.get("limit")
    offset = request.args.get("offset")
    search = request.args.get("search")

    # Set the filters for the query
    kwargs = {}
    kwargs["limit"] = limit
    kwargs["offset"] = offset
    kwargs["explicit_refs"] = {"filter": search, "op": "=="}

    ers = query.get_explicit_refs(**kwargs)
    jsonified_ers = [er.jsonify() for er in ers]
    return jsonify(jsonified_ers)

@bp.route("/query-jsonify-er-groups")
def query_jsonify_er_groups():
    """
    Query all the ers groups.
    """
    current_app.logger.debug("Query explicit reference groups")
    # Get limit and offset values
    limit = request.args.get("limit")
    offset = request.args.get("offset")
    search = request.args.get("search")

    # Set the filters for the query
    kwargs = {}
    kwargs["limit"] = limit
    kwargs["offset"] = offset
    kwargs["names"] = {"filter": "%" + search + "%", "op": "like"}

    er_groups = query.get_explicit_refs_groups(**kwargs)
    jsonified_er_groups = [er_group.jsonify() for er_group in er_groups]
    return jsonify(jsonified_er_groups)

@bp.route("/query-dim-signatures", methods=["GET", "POST"])
def query_dim_signatures_and_render():
    """
    Query DIM signatures amd render.
    """
    current_app.logger.debug("Query DIM signatures and render")
    if request.method == "POST":
        filters = request.form.to_dict(flat=False).copy()
        filters["offset"] = [""]
        dim_signatures = query_dim_signatures(filters)

        return render_template("eboa_nav/dim_signatures_nav.html", dim_signatures=dim_signatures, filters=filters)
    # end if

    return render_template("eboa_nav/query_dim_signatures.html")

@bp.route("/query-dim-signatures-pages", methods=["POST"])
def query_dim_signatures_pages():
    """
    Query DIM signatures using pages and render.
    """
    current_app.logger.debug("Query DIM signatures using pages and render")

    filters = request.json
    dim_signatures = query_dim_signatures(filters)

    return render_template("eboa_nav/dim_signatures_nav.html", dim_signatures=dim_signatures, filters=filters)

def query_dim_signatures(filters):
    """
    Query DIM signatures.
    """
    current_app.logger.debug("Query DIM signatures")
    kwargs = {}
    if filters["dim_signature"][0] != "":
        op="notlike"
        if not "dim_signature_notlike_check" in filters:
            op="like"
        # end if
        kwargs["dim_signatures"] = {"filter": filters["dim_signature"][0], "op": filters["dim_signature_operator"][0]}
    # end if
    elif "dim_signatures" in filters and filters["dim_signatures"][0] != "":
        op="notin"
        if not "dim_signature_notin_check" in filters:
            op="in"
        # end if
        kwargs["dim_signatures"] = {"filter": [], "op": op}
        i = 0
        for dim_signature in filters["dim_signatures"]:
            kwargs["dim_signatures"]["filter"].append(dim_signature)
            i+=1
        # end for
    # end if

    # Query restrictions
    if filters["order_by"][0] != "":
        descending = True
        if not "order_descending" in filters:
            descending = False
        # end if
        kwargs["order_by"] = {"field": filters["order_by"][0], "descending": descending}
    # end if

    if filters["limit"][0] != "":
        kwargs["limit"] = filters["limit"][0]
    # end if

    if filters["offset"][0] != "":
        kwargs["offset"] = filters["offset"][0]
    # end if

    dim_signatures = query.get_dim_signatures(**kwargs)

    return dim_signatures

@bp.route("/query-jsonify-dim-signatures")
def query_jsonify_dim_signatures():
    """
    Query all the DIM signatures.
    """
    current_app.logger.debug("Query DIM signatures")
    # Get limit and offset values
    limit = request.args.get("limit")
    offset = request.args.get("offset")
    search = request.args.get("search")

    # Set the filters for the query
    kwargs = {}
    kwargs["limit"] = limit
    kwargs["offset"] = offset
    kwargs["dim_signatures"] = {"filter": "%" + search + "%", "op": "like"}

    dim_signatures = query.get_dim_signatures(**kwargs)
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
    returned_values = engine.treat_data(data)
    exit_information = {
        "returned_values": returned_values
    }
    return jsonify(exit_information)

@bp.route("/query-alerts-pages", methods=["POST"])
def query_alerts_pages():
    """
    Query alerts using pages and render.
    """
    current_app.logger.debug("Query alerts using pages and render")
    filters = request.json

    if "query_event_alerts" in filters:
        alerts = query_event_alerts(filters)
    # end if
    show = define_what_to_show_alerts(filters) 
    return render_template("eboa_nav/alerts_nav.html", alerts=alerts, show=show, filters=filters)

def define_what_to_show_alerts(filters):
    """
    Function to define what to show for alerts
    """
    show = {}
    show["timeline"]=True
    if not "show_timeline" in filters:
        show["timeline"] = False
    # end if

    return show