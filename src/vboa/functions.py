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
import pytz
from dateutil import parser

# Import orbit
import eboa.ingestion.orbit as eboa_orbit

# Import flask utilities
from flask import request, url_for

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

    # Initialize reporting period (now  - window_delay days - window_size days, now - window_delay days)
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
    :param tle_string: TLE text
    :type tle_string: str
    :param include_track: flag indicating if the track of the satellite needs to be included
    :type include_track: bool
    :param width: number indicating the width of the line for the track of the events
    :type width: float
    :param colors_by_gauge: dictionary for the colors of tracks depending on the events' gauges
    :type colors_by_gauge: dict

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
        czml_data = tle_to_czml_data(tle_string, events[0].start, events[-1].stop, 300)

        czml_data[1]["path"]["material"]["solidColor"]["color"]["rgba"] = ["213", "255", "0", 150]
    else:
        czml_data = []
    # end if
    
    for event in events:
        czml_data_event = tle_to_czml_data(tle_string, event.start, event.stop, 300)

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

def _calculate_lead_trail_intervals(orbit_duration, start_period, stop_period):
    """
    Function to calculate lean and trail intervals to be included in the czml data structure

    :param orbit_duration: duration of the orbit of the satellite calculated from the TLE
    :type orbit_duration: float
    :param start_period: start date of the period to cover by the positions
    :type start_period: datetime
    :param stop_period: stop date of the period to cover by the positions
    :type stop_period: datetime

    :return: czml data structure associated to the TLE received
    :rtype: dict
    """

    start_period_iso = start_period.replace(tzinfo=pytz.UTC).isoformat()
    stop_period_iso = stop_period.replace(tzinfo=pytz.UTC).isoformat()
    
    minutes_in_sim = (stop_period - start_period).total_seconds()/60

    left_over_minutes = minutes_in_sim % orbit_duration

    orbit_duration_seconds = orbit_duration * 60

    # Obtain the lead and trail intervals
    interval_start = start_period_iso
    interval_stop = (start_period + datetime.timedelta(minutes=left_over_minutes)).replace(tzinfo=pytz.UTC).isoformat()
    j = 0
    lead_intervals = []
    trail_intervals = []
    while interval_start < stop_period_iso:

        lead_intervals.append({
            "interval": interval_start + "/" + interval_stop,
            "epoch": interval_start,
            "number": [0, orbit_duration_seconds, orbit_duration_seconds, 0]
        })
        trail_intervals.append({
            "interval": interval_start + "/" + interval_stop,
            "epoch": interval_start,
            "number": [0, 0, orbit_duration_seconds, orbit_duration_seconds]
        })

        j += 1

        interval_start = interval_stop
        interval_stop = (start_period + datetime.timedelta(minutes=left_over_minutes) + datetime.timedelta(minutes=j*orbit_duration)).replace(tzinfo=pytz.UTC).isoformat()
        
    # end while

    return lead_intervals, trail_intervals

def tle_to_czml_data(tle_string, start_period, stop_period, step):
    """
    Function to generate a czml data structure from the received TLE including positions in FIXED reference frame

    :param tle_string: TLE of the satellite with the following format:
    SATELLITE-INDICATOR
    1 NNNNNC NNNNNAAA NNNNN.NNNNNNNN +.NNNNNNNN +NNNNN-N +NNNNN-N N NNNNN
    2 NNNNN NNN.NNNN NNN.NNNN NNNNNNN NNN.NNNN NNN.NNNN NN.NNNNNNNNNNNNNN
    :type tle_string: str
    :param start_period: start date of the period to cover by the positions
    :type start_period: datetime
    :param stop_period: stop date of the period to cover by the positions
    :type stop_period: datetime
    :param step: duration in time between calculated positions
    :type step: int

    :return: czml data structure associated to the TLE received
    :rtype: dict
    """

    start_period_iso = start_period.replace(tzinfo=pytz.UTC).isoformat()
    stop_period_iso = stop_period.replace(tzinfo=pytz.UTC).isoformat()

    start_period_iso_no_tzinfo = start_period.replace(tzinfo=None).isoformat()
    stop_period_iso_no_tzinfo = stop_period.replace(tzinfo=None).isoformat()

    # Set period
    period = start_period_iso + "/" + stop_period_iso

    # Get orbit
    satellite_orbit = eboa_orbit.get_orbit(tle_string)

    # Get satellite
    satellite = eboa_orbit.get_satellite(tle_string)

    # Obtain the satellite position during the period in FIXED reference frame from the TLE
    time = start_period_iso_no_tzinfo
    j = 0
    positions = []
    while time < stop_period_iso_no_tzinfo:
        time = (start_period + datetime.timedelta(seconds=j*step)).replace(tzinfo=None).isoformat(timespec="microseconds")
        if time > stop_period_iso_no_tzinfo:
            time = stop_period_iso_no_tzinfo
        # end if
        # Get position of the satellite associated to time in the Earth inertial frame
        error, position, velocity = eboa_orbit.get_ephemeris(satellite_orbit, time)

        # Transform to Earth fixed reference frame
        fixed_satellite_position = eboa_orbit.satellite_positions_to_fixed([position[0], position[1], position[2]], [time])

        # Register position
        positions.append(j*step)
        positions.append(fixed_satellite_position[0] * 1000)
        positions.append(fixed_satellite_position[1] * 1000)
        positions.append(fixed_satellite_position[2] * 1000)
        
        j += 1
    # end while

    # Get orbit duration
    orbit_duration = eboa_orbit.get_orbit_duration(tle_string)

    # Calculate lead and trail intervals
    lead_intervals, trail_intervals = _calculate_lead_trail_intervals(orbit_duration, start_period, stop_period)
    
    czml_data = [
        {
            "id": "document",
            "version": "1.0",
            "clock": {
                "currentTime": start_period_iso,
                "multiplier": 60,
                "interval": period,
                "range": "LOOP_STOP",
                "step": "SYSTEM_CLOCK_MULTIPLIER"
            }
        },
        {
            "id": f"Satellite/{satellite}_{start_period_iso}",
            "description": f"Orbit of Satellite: {satellite}",
            "availability": period,
            "billboard": {
                "show": True,
                "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAADJSURBVDhPnZHRDcMgEEMZjVEYpaNklIzSEfLfD4qNnXAJSFWfhO7w2Zc0Tf9QG2rXrEzSUeZLOGm47WoH95x3Hl3jEgilvDgsOQUTqsNl68ezEwn1vae6lceSEEYvvWNT/Rxc4CXQNGadho1NXoJ+9iaqc2xi2xbt23PJCDIB6TQjOC6Bho/sDy3fBQT8PrVhibU7yBFcEPaRxOoeTwbwByCOYf9VGp1BYI1BA+EeHhmfzKbBoJEQwn1yzUZtyspIQUha85MpkNIXB7GizqDEECsAAAAASUVORK5CYII=",
                "scale": 1.5
            },
            "position": {
                "epoch": start_period_iso,
                "cartesian": positions,
                "interpolationAlgorithm": "LAGRANGE",
                "interpolationDegree": 5,
                "referenceFrame": "FIXED"
            },
            "label": {
                "show": True,
                "text": f"{satellite}",
                "horizontalOrigin": "LEFT",
                "pixelOffset": {
                    "cartesian2": [12, 0]
                },
                "fillColor": {
                    "rgba": ["213", "255", "0", 255]
                },
                "font": "11pt Lucida Console",
                "outlineColor": {
                    "rgba": [0, 0, 0, 255]
                },
                "outlineWidth": 2
            },
            "path": {
                "show": [{
                    "interval": period,
                    "boolean": True
                }],
                "width": 1,
                "leadTime": lead_intervals,
                "trailTime": trail_intervals,
                "resolution": 120,
                "material": {
                    "solidColor": {
                        "color": {
                            "rgba": ["213", "255", "0", 255]
                        }
                    }
                }
            }
        }
    ]
    
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
        explicit_ref_row = "<tr><td>Explicit reference</td><td><a href='" + url_for("eboa_nav.query_er", explicit_ref_uuid=str(event.explicitRef.explicit_ref_uuid)) + "'>" + event.explicitRef.explicit_reference + "</a></td></tr>"
    # end if
    
    return "<table border='1'>" + \
        "<tr><td>UUID</td><td>" + str(event.event_uuid) + "</td></tr>" + \
        explicit_ref_row + \
        "<tr><td>Gauge name</td><td>" + event.gauge.name + "</td></tr>" + \
        "<tr><td>Gauge system</td><td>" + event.gauge.system + "</td></tr>" + \
        "<tr><td>Start</td><td>" + event.start.isoformat() + "</td></tr>" + \
        "<tr><td>Stop</td><td>" + event.stop.isoformat() + "</td></tr>" + \
        "<tr><td>Duration (m)</td><td>" + str(event.get_duration()) + "</td></tr>" + \
        "<tr><td>Source</td><td><a href='" + url_for("eboa_nav.query_source", source_uuid=str(event.source_uuid)) + "'>" + event.source.name + "</a></td></tr>" + \
        "<tr><td>Ingestion time</td><td>" + event.ingestion_time.isoformat() + "</td></tr>" + \
        "<tr><td>Links</td><td><a href='" + url_for("eboa_nav.query_event_links_and_render", event_uuid=str(event.event_uuid)) + "'><i class='fa fa-link'></i></a></td></tr>" + \
        "<tr id='expand-tooltip-values-event-" + str(event.event_uuid) + "'><td>Values</td><td><i class='fa fa-plus-square green' onclick='" + 'vboa.expand_event_values_in_tooltip(String(/expand-tooltip-values-event-' + str(event.event_uuid) + '/).substring(1).slice(0,-1), String(/' + str(event.event_uuid) + '/).substring(1).slice(0,-1))' + "' data-toggle='tooltip' title='Click to show the related values'></i></td></tr>" + \
        "</table>"

def find_tle_event(tle_events, date):
    '''
    Function to obtain the nearest TLE event to a date.
    PRE: List of tle_events is not empty

    :param tle_events: list of TLE events
    :type tle_events: list
    :param date: reference date to find the corresponding TLE event
    :type date: datetime.datetime

    :return: TLE event
    :rtype: event
    '''
    # Obtain the list of tle events ordered by distance to date
    tle_events_sorted_by_deltatime = sorted(tle_events, key=lambda event: abs((event.start - date).total_seconds()))

    return tle_events_sorted_by_deltatime[0]

def events_to_czml_data_using_tle_events(events, tle_events, include_track = True, width = 5, colors_by_gauge = {}, step = 300):
    """
    Function to generate a czml data structure from the received events using the received TLE events

    PRE:
    - The list of events is ordered by start in ascending

    :param events: list of events from DDBB
    :type events: list
    :param tle_events: list of TLE events from DDBB
    :type tle_events: list
    :param include_track: flag indicating if the track of the satellite needs to be included
    :type include_track: bool
    :param width: number indicating the width of the line for the track of the events
    :type width: float
    :param colors_by_gauge: dictionary for the colors of tracks depending on the events' gauges
    :type colors_by_gauge: dict
    :param step: duration in time between calculated positions
    :type step: int

    :return: czml data structure associated to the events using the TLE received
    :rtype: dict
    """

    if type(events) != list:
        raise ErrorParsingParameters("The structure of events parameter has to be a list. Received structure is: {}".format(events))
    # end if

    if type(tle_events) != list:
        raise ErrorParsingParameters("The structure of tle_events parameter has to be a list. Received structure is: {}".format(tle_events))
    # end if

    if len(events) > 0:
        # Get start of the period
        start_period_time = events[0].start
        start_period = start_period_time.isoformat()
        start_period_iso = start_period_time.replace(tzinfo=pytz.UTC).isoformat()

        # Get stop of the period
        stop_period_time = events[-1].stop
        stop_period = stop_period_time.isoformat()
        stop_period_iso = stop_period_time.replace(tzinfo=pytz.UTC).isoformat()

        # Set period
        period = start_period_iso + "/" + stop_period_iso
    # end if

    czml_data = []
    if include_track and len(events) > 0:
        corresponding_tle_events = [tle_event for tle_event in tle_events if tle_event.start.isoformat() < stop_period and tle_event.stop.isoformat() > start_period]
        j = 0
        tle_event_index = 0
        positions = []
        for corresponding_tle_event in corresponding_tle_events:
            satellite = corresponding_tle_event.get_value("eventTexts", "satellite")
            first_line = corresponding_tle_event.get_value("eventTexts", "first_line")
            second_line = corresponding_tle_event.get_value("eventTexts", "second_line")
        
            tle_string = satellite + "\n" + first_line + "\n" + second_line

            # Get orbit
            satellite_orbit = eboa_orbit.get_orbit(tle_string)

            # Define period for the TLE
            start_period_tle = corresponding_tle_event.start
            if start_period_tle < start_period_time:
                start_period_tle = start_period_time
            # end if

            stop_period_tle = corresponding_tle_event.stop
            if stop_period_tle > stop_period_time:
                stop_period_tle = stop_period_time
            # end if

            # Obtain the satellite position during the period in FIXED reference frame from the TLE
            time = start_period_tle.replace(tzinfo=None).isoformat()
            stop_period_iso_no_tzinfo = stop_period_tle.replace(tzinfo=None).isoformat()
            while time < stop_period_iso_no_tzinfo:
                time = (start_period_time + datetime.timedelta(seconds=j*step)).replace(tzinfo=None).isoformat(timespec="microseconds")
                if time > stop_period_iso_no_tzinfo and len(corresponding_tle_events) == tle_event_index + 1:
                    time = stop_period_iso_no_tzinfo
                elif time > stop_period_iso_no_tzinfo:
                    break
                # end if

                # Get position of the satellite associated to time in the Earth inertial frame
                error, position, velocity = eboa_orbit.get_ephemeris(satellite_orbit, time)

                # Transform to Earth fixed reference frame
                fixed_satellite_position = eboa_orbit.satellite_positions_to_fixed([position[0], position[1], position[2]], [time])

                # Register position
                positions.append(j*step)
                positions.append(fixed_satellite_position[0] * 1000)
                positions.append(fixed_satellite_position[1] * 1000)
                positions.append(fixed_satellite_position[2] * 1000)

                j += 1
            # end while
            tle_event_index += 1            
        # end for

        if len(corresponding_tle_events) > 0:
            # Get orbit duration
            orbit_duration = eboa_orbit.get_orbit_duration(tle_string)

            # Calculate lead and trail intervals
            lead_intervals, trail_intervals = _calculate_lead_trail_intervals(orbit_duration, start_period_time, stop_period_time)

            czml_data = [
                {
                    "id": "document",
                    "version": "1.0",
                    "clock": {
                        "currentTime": start_period_iso,
                        "multiplier": 60,
                        "interval": period,
                        "range": "LOOP_STOP",
                        "step": "SYSTEM_CLOCK_MULTIPLIER"
                    }
                },
                {
                    "id": f"Satellite/{satellite}_{start_period}",
                    "description": f"Orbit of Satellite: {satellite}",
                    "availability": period,
                    "billboard": {
                        "show": True,
                        "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAADJSURBVDhPnZHRDcMgEEMZjVEYpaNklIzSEfLfD4qNnXAJSFWfhO7w2Zc0Tf9QG2rXrEzSUeZLOGm47WoH95x3Hl3jEgilvDgsOQUTqsNl68ezEwn1vae6lceSEEYvvWNT/Rxc4CXQNGadho1NXoJ+9iaqc2xi2xbt23PJCDIB6TQjOC6Bho/sDy3fBQT8PrVhibU7yBFcEPaRxOoeTwbwByCOYf9VGp1BYI1BA+EeHhmfzKbBoJEQwn1yzUZtyspIQUha85MpkNIXB7GizqDEECsAAAAASUVORK5CYII=",
                        "scale": 1.5
                    },
                    "position": {
                        "epoch": start_period_iso,
                        "cartesian": positions,
                        "interpolationAlgorithm": "LAGRANGE",
                        "interpolationDegree": 5,
                        "referenceFrame": "FIXED"
                    },
                    "label": {
                        "show": True,
                        "text": f"{satellite}",
                        "horizontalOrigin": "LEFT",
                        "pixelOffset": {
                            "cartesian2": [12, 0]
                        },
                        "fillColor": {
                            "rgba": ["213", "255", "0", 255]
                        },
                        "font": "11pt Lucida Console",
                        "outlineColor": {
                            "rgba": [0, 0, 0, 255]
                        },
                        "outlineWidth": 2
                    },
                    "path": {
                        "show": [{
                            "interval": period,
                            "boolean": True
                        }],
                        "width": 1,
                        "leadTime": lead_intervals,
                        "trailTime": trail_intervals,
                        "resolution": 120,
                        "material": {
                            "solidColor": {
                                "color": {
                                    "rgba": ["213", "255", "0", 255]
                                }
                            }
                        }
                    }
                }
            ]
        # end if
    # end if

    for event in events:
        
        # Find relevant TLE
        tle_event = find_tle_event(tle_events, event.start)

        satellite = tle_event.get_value("eventTexts", "satellite")
        first_line = tle_event.get_value("eventTexts", "first_line")
        second_line = tle_event.get_value("eventTexts", "second_line")
        
        tle_string = satellite + "\n" + first_line + "\n" + second_line

        czml_data_event = tle_to_czml_data(tle_string, event.start, event.stop, 300)

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
