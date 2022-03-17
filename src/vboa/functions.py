"""
Helper module for the vboa

Written by DEIMOS Space S.L. (dibb)

module vboa
"""
# Import python utilities
from tempfile import mkstemp
from distutils import util
import datetime
import json
import tle2czml
import pytz

# Import flask utilities
from flask import request

# Import EBOA errors
from eboa.engine.errors import ErrorParsingParameters

########
# Date functions
########
def get_start_stop_filters(filters, window_size, window_delay):
    """
    Get start and stop filters from the specified values in the corresponding form

    :param filters: dictionary with the content of the submit form
    :type filters: dict
    :param window_size: size of the window in days (used in case there are no time filters)
    :type window_size: float
    :param window_delay: time in days between the current time and the stop of the window (used in case there are no time filters)
    :type window_delay: float
    """

    # Initialize reporting period (now - window_size days, now)
    start_filter = {
        "date": (datetime.datetime.now() - datetime.timedelta(days=window_delay)).isoformat(),
        "operator": "<="
    }
    stop_filter = {
        "date": (datetime.datetime.now() - datetime.timedelta(days=(window_delay+window_size))).isoformat(),
        "operator": ">="
    }
    
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

########
# Export functions
########
def export_html(response):
    html_file_path = None
    if response.status_code == 200:
        html = response.get_data().decode('utf8')
        (_, html_file_path) = mkstemp()
        f= open(html_file_path,"w+")
        f.write(html)
        f.close()
    # end if

    return html_file_path

########
# Alert functions
########
def set_specific_alert_filters(filters):
    """
    Set filter for query alerts.
    """
    kwargs = {}

    if filters["alert_name"][0] != "":
        kwargs["names"] = {"filter": filters["alert_name"][0], "op": filters["alert_name_operator"][0]}
    # end if
    elif "alert_names" in filters and filters["alert_names"][0] != "":
        op="notin"
        if not "alert_name_notin_check" in filters:
            op="in"
        # end if
        kwargs["names"] = {"filter": [], "op": op}
        i = 0
        for alert_name in filters["alert_names"]:
            kwargs["names"]["filter"].append(alert_name)
            i+=1
        # end for
    # end if

    if filters["alert_group"][0] != "":
        kwargs["groups"] = {"filter": filters["alert_group"][0], "op": filters["alert_group_operator"][0]}
    # end if
    elif "alert_groups" in filters and filters["alert_groups"][0] != "":
        op="notin"
        if not "alert_group_notin_check" in filters:
            op="in"
        # end if
        kwargs["groups"] = {"filter": [], "op": op}
        i = 0
        for alert_group in filters["alert_groups"]:
            kwargs["groups"]["filter"].append(alert_group)
            i+=1
        # end for
    # end if

    if filters["alert_generator"][0] != "":
        kwargs["generators"] = {"filter": filters["alert_generator"][0], "op": filters["alert_generator_operator"][0]}
    # end if
    elif "alert_generators" in filters and filters["alert_generators"][0] != "":
        op="notin"
        if not "alert_generator_notin_check" in filters:
            op="in"
        # end if
        kwargs["generators"] = {"filter": [], "op": op}
        i = 0
        for alert_generator in filters["alert_generators"]:
            kwargs["generators"]["filter"].append(alert_generator)
            i+=1
        # end for
    # end if

    if filters["alert_ingestion_time"][0] != "":
        kwargs["alert_ingestion_time_filters"] = []
        i = 0
        operators = filters["alert_ingestion_time_operator"]
        for alert_ingestion_time in filters["alert_ingestion_time"]:
            kwargs["alert_ingestion_time_filters"].append({"date": alert_ingestion_time, "op": operators[i]})
            i+=1
        # end for
    # end if

    if filters["alert_solved_time"][0] != "":
        kwargs["solved_time_filters"] = []
        i = 0
        operators = filters["alert_solved_time_operator"]
        for alert_solved_time in filters["alert_solved_time"]:
            kwargs["solved_time_filters"].append({"date": alert_solved_time, "op": operators[i]})
            i+=1
        # end for
    # end if

    if filters["alert_notification_time"][0] != "":
        kwargs["notification_time_filters"] = []
        i = 0
        operators = filters["alert_notification_time_operator"]
        for alert_notification_time in filters["alert_notification_time"]:
            kwargs["notification_time_filters"].append({"date": alert_notification_time, "op": operators[i]})
            i+=1
        # end for
    # end if

    if filters["alert_validated"][0] != "":
        kwargs["validated"] = bool(util.strtobool(filters["alert_validated"][0]))
    # end if

    if filters["alert_notified"][0] != "":
        kwargs["notified"] = bool(util.strtobool(filters["alert_notified"][0]))
    # end if

    if filters["alert_solved"][0] != "":
        kwargs["solved"] = bool(util.strtobool(filters["alert_solved"][0]))
    # end if

    if "alert_severities" in filters and filters["alert_severities"][0] != "":
        op="notin"
        if not "alert_severity_notin_check" in filters:
            op="in"
        # end if
        kwargs["severities"] = {"filter": [], "op": op}
        i = 0
        for alert_severities in filters["alert_severities"]:
            kwargs["severities"]["filter"].append(alert_severities)
            i+=1
        # end for
    # end if

    return kwargs

########
# Czml functions
########
def events_to_czml_data(events, tle_string, include_track = True, width = 5, colors_by_gauge = {}):
    """
    Function to generate a czml data structure from the received events using the received TLE

    PRE:
    - The list of events is ordered by start in ascending

    :param events: list of events from DDBB
    :type events: list

    :return: czml data structure associated to the events using the TLE received
    :rtype: dict
    """

    if type(events) != list:
        raise ErrorParsingParameters("The structure of events parameter has to be a list. Received structure is: {}".format(events))
    # end if

    if len(events) > 0:
        # Get start of the period
        start_period = events[0].start.isoformat()

        # Get stop of the period
        stop_period = events[-1].stop.isoformat()

        # Set period
        period = start_period + "Z/" + stop_period + "Z"
    # end if

    if include_track and len(events) > 0:
        czml_data = json.loads(tle2czml.tle2czml.tles_to_czml(tle_string, start_time=events[0].start.replace(tzinfo=pytz.UTC), end_time=events[-1].stop.replace(tzinfo=pytz.UTC), silent=True))

        czml_data[1]["path"]["material"]["solidColor"]["color"]["rgba"] = ["213", "255", "0", 150]
    else:
        czml_data = []
    # end if
    
    for event in events:
        czml_data_event = json.loads(tle2czml.tle2czml.tles_to_czml(tle_string, start_time=event.start.replace(tzinfo=pytz.UTC), end_time=event.stop.replace(tzinfo=pytz.UTC), silent=True))

        new_object = czml_data_event[1]

        # Set path interval
        new_object["path"]["show"][0]["interval"] = period

        # Change id
        new_object["id"] = str(event.event_uuid)

        # Change description
        new_object["description"] = create_event_tooltip_text(event)

        # Set width
        new_object["path"]["width"] = width

        # Set color
        color = ["46", "204", "113", 255]
        gauge_name = event.gauge.name
        gauge_system = event.gauge.system
        if gauge_name in colors_by_gauge:
            if gauge_system in colors_by_gauge[gauge_name]:
                color = colors_by_gauge[gauge_name][gauge_system]
            # end if
        # end if
        new_object["path"]["material"]["solidColor"]["color"]["rgba"] = color

        # Delete leadTime
        del new_object["path"]["leadTime"]
        
        # Delete trailTime
        del new_object["path"]["trailTime"]

        # Add new object associated to the current event to the czml data structure
        czml_data.append(new_object)

    # end for

    if len(events) > 0:
        
        # Set interval
        czml_data[0]["clock"]["interval"] = period
        
    # end if
    
    return czml_data

def create_event_tooltip_text(event):
    """
    Function to create the text for the tooltip of the event information

    :param event: event from DDBB
    :type event: event from DDBB

    :return: string with the tooltip
    :rtype: str
    """

    # Check if the event has a defined explicit reference
    explicit_ref_row = ""
    if event.explicitRef:
        explicit_ref_row = "<tr><td>Explicit reference</td><td><a href='/eboa_nav/query-er/" + str(event.explicitRef.explicit_ref_uuid) + "'>" + event.explicitRef.explicit_reference + "</a></td></tr>"
    # end if
    
    return "<table border='1'>" + \
        "<tr><td>UUID</td><td>" + str(event.event_uuid) + "</td></tr>" + \
        explicit_ref_row + \
        "<tr><td>Gauge name</td><td>" + event.gauge.name + "</td></tr>" + \
        "<tr><td>Gauge system</td><td>" + event.gauge.system + "</td></tr>" + \
        "<tr><td>Start</td><td>" + event.start.isoformat() + "</td></tr>" + \
        "<tr><td>Stop</td><td>" + event.stop.isoformat() + "</td></tr>" + \
        "<tr><td>Duration (m)</td><td>" + str(event.get_duration()) + "</td></tr>" + \
        "<tr><td>Source</td><td><a href='/eboa_nav/query-source/" + str(event.source_uuid) + "'>" + event.source.name + "</a></td></tr>" + \
        "<tr><td>Ingestion time</td><td>" + event.ingestion_time.isoformat() + "</td></tr>" + \
        "<tr><td>Links</td><td><a href='/eboa_nav/query-event-links/" + str(event.event_uuid) + "'><i class='fa fa-link'></i></a></td></tr>" + \
        "<tr id='expand-tooltip-values-event-" + str(event.event_uuid) + "'><td>Values</td><td><i class='fa fa-plus-square green' onclick='" + 'vboa.expand_event_values_in_tooltip(String(/expand-tooltip-values-event-' + str(event.event_uuid) + '/).substring(1).slice(0,-1), String(/' + str(event.event_uuid) + '/).substring(1).slice(0,-1))' + "' data-toggle='tooltip' title='Click to show the related values'></i></td></tr>" + \
        "</table>"

