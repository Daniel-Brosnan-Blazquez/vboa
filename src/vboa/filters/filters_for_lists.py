"""
Filters for lists

Written by DEIMOS Space S.L. (dibb)

module vboa
"""
# Import python utilities
import datetime
from dateutil import parser
import statistics

# Import filters for values
from vboa.filters import filters_for_values_in_json

def get_statistics_definition(list):
    """
    Method to get the statistics with respect to the values of the received list:
    total, minimum, maximum, mean and standard deviation

    :param list: list of values in number format
    :type list: list

    :return: list statistics
    :rtype: dict

    """
    stats = {}
    stats["min"] = 0
    stats["max"] = 0
    stats["mean"] = 0
    stats["std"] = 0

    if len(list) > 0:
        stats["min"] = min(list)
        stats["max"] = max(list)
        stats["mean"] = statistics.mean(list)
        if len(list) > 1:
            stats["std"] = statistics.stdev(list)
        # end if
        stats["total"] = sum(list)
    # end if

    return stats

def add_filters(app):
    """
    Method to add the filters associated to the events in json format
    to the app
    """

    @app.template_filter()
    def get_statistics(list):
        return get_statistics_definition(list)
