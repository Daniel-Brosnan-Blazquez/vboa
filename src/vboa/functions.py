"""
Helper module for the vboa

Written by DEIMOS Space S.L. (dibb)

module vboa
"""
# Import python utilities
from tempfile import mkstemp
from distutils import util
import datetime

# Import flask utilities
from flask import request

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
