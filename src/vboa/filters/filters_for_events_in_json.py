"""
Filters for events in json format

Written by DEIMOS Space S.L. (dibb)

module vboa
"""
# Import python utilities
import datetime
from dateutil import parser

# Import filters for values
from vboa.filters import filters_for_values_in_json

def get_timeline_duration_from_data_json_definition(data, list_uuids):
    """
    Method to get the timeline duration of the events associated to
    the list of UUIDs registered inside the data structure

    :param data: dictionary where to locate the events in data["events"]
    :type data: dict
    :param list_uuids: list of UUIDs related to events
    :type list_uuids: list

    :return: timeline duration
    :rtype: integer

    """
    result = 0
    for uuid in list_uuids:
        result += (parser.parse(data["events"][uuid]["stop"]) - parser.parse(data["events"][uuid]["start"])).total_seconds()
    # end for
    return result

def get_timeline_duration_from_events_json_definition(events):
    """
    Method to get the timeline duration of the events

    :param events: list of events in json format
    :type events: list

    :return: timeline duration
    :rtype: integer

    """
    return sum([(parser.parse(event["stop"]) - parser.parse(event["start"])).total_seconds() for event in events])

def get_events_json_definition(data, list_uuids):
    """
    Method to get the events structure inside the data structure

    :param data: dictionary where to locate the events in data["events"]
    :type data: dict
    :param list_uuids: list of UUIDs related to events
    :type list_uuids: list

    :return: timeline duration
    :rtype: integer

    """
    return {"events": [data["events"][key] for key in list_uuids]}

def get_events_filtered_by_values_definition(events, value_filters):
    """
    Method to get the events inside the data structure filtered by the received value filters

    :param events: list of events in json format
    :type events: list
    :param value_filters: list of value filters
    :type value_filters: list of value filters

    :return: list of filtered events
    :rtype: list

    """
    list_filtered_events = []
    for event in events:
        list_found_values = filters_for_values_in_json.get_values_definition(event, value_filters)
        if len(list_found_values.keys()) > 0:
            list_filtered_events.append(event)
        # end if
    # end for

    return list_filtered_events

def get_linking_event_definition(event, link_name, data):
    """
    Method to get the events inside the data structure filtered by the received value parameter

    :param event: dictionary with the event
    :type event: dict
    :param link_name: name of the link
    :type event: str
    :param data: dictionary where to locate the events in data["events"]
    :type data: dict

    :return: found event or None
    :rtype: dict

    """
    link = [link for link in event["links_to_me"] if link["name"] == link_name]
    event = None
    if len(link) > 0:
        event = data["events"][link[0]["event_uuid_link"]]
    # end if

    return event

def add_filters(app):
    """
    Method to add the filters associated to the events in json format
    to the app
    """

    @app.template_filter()
    def get_timeline_duration_from_data_json(data, list_uuids):
        return get_timeline_duration_from_data_json_definition(data, list_uuids)
    
    @app.template_filter()
    def get_timeline_duration_from_events_json(events):
        return get_timeline_duration_from_events_json_definition(events)
    
    @app.template_filter()
    def get_events_json(data, list_uuids):
        return get_events_json_definition(data, list_uuids)
    
    @app.template_filter()
    def get_events_filtered_by_values(events, value_filters):
        return get_events_filtered_by_values_definition(events, value_filters)
    
    @app.template_filter()
    def get_linking_event(event, link_name, data):
        return get_linking_event_definition(event, link_name, data)