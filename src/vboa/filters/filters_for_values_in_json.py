"""
Filters for values in json format

Written by DEIMOS Space S.L. (dibb)

module vboa
"""
# Import python utilities
import datetime
from dateutil import parser
import re

# Import operators
from eboa.engine.operators import arithmetic_operators, text_operators, regex_operators

def check_value(value, value_filter):
    """
    Method to get the values inside the list of values with name value_name

    :param value: value structure
    :type list_values: list
    :param value_filters: list of value filters
    :type value_filters: list of value filters

    :return: found_values
    :rtype: list

    """
    matches = False
    # Check if there is a filter for the value
    if "value" in value_filter:
        value_value_filter = value_filter["value"]
        # Check if the value value matches
        if value_value_filter["op"] in arithmetic_operators.keys():
            op = arithmetic_operators[value_value_filter["op"]]
            if op(value["value"], value_value_filter["filter"]):
                matches = True
            # end if
        # end if
        if value_value_filter["op"] in regex_operators.keys():
            if re.match(value_value_filter["filter"], value["value"]):
                matches = True
            # end if
        # end if
    else:
        matches = True
    # end if

    return matches

def insert_value(value, found_values, value_filter):
    """
    """
    group = "values"
    if "group" in value_filter:
        group = value_filter["group"]
    # end if

    if group not in found_values:
        found_values[group] = []
    # end if

    found_values[group].append(value)

    return

def search_values(list_values, value_filters, stop_first = True, indexed_values = None):
    """
    Recursive method to get the values inside the list of values with name value_name

    :param list_values: list of values
    :type list_values: list
    :param value_filters: list of value filters
    :type value_filters: list of value filters
    :param stop_first: bool indicating if the search must stop for every filter when found the first match
    :type stop_first: bool

    :return: found_values
    :rtype: dict

    """
    found_values = {}

    for value_filter in value_filters:
        name_filter = value_filter["name"]
        if indexed_values != None and name_filter["op"] == "==":
            if name_filter["filter"] in indexed_values:
                for value in indexed_values[name_filter["filter"]]:
                    value_matches = check_value(value, value_filter)
                    if value_matches:
                        insert_value(value, found_values, value_filter)

                        if stop_first:
                            break
                        # end if
                        
                    # end if
            # end if
        else:
            for value in list_values:

                if type(value) == list:
                    found_values += _search_values(value, [value_filter], stop_first)
                # end if

                value_matches = False
                # Discriminate by type of operator
                if name_filter["op"] in arithmetic_operators.keys():
                    op = arithmetic_operators[name_filter["op"]]
                    # Check if the value name matches
                    if op(value["name"], name_filter["filter"]):
                        value_matches = check_value(value, value_filter)
                    # end if
                elif name_filter["op"] in regex_operators.keys():
                    # Check if the value name matches
                    if re.match(name_filter["filter"], value["name"]):
                        value_matches = check_value(value, value_filter)
                    # end if
                # end if

                if value_matches:
                    insert_value(value, found_values, value_filter)

                    if stop_first:
                        break
                    # end if
                    
                # end if
                    
            # end for
        # end if
    # end for
        
    # end for
    return found_values

def get_values_definition(entity, value_filters, stop_first = True):
    """
    Method to get the values inside the entity structure with name value_name

    :param entity: dictionary with the entity
    :type entity: dict
    :param value_filters: list of value filters
    :type value_filters: list of value filters
    :param stop_first: bool indicating if the search must stop for every filter when found the first match
    :type stop_first: bool

    :return: found_values
    :rtype: dict

    """
    indexed_values = None
    if "indexed_values" in entity:
        indexed_values = entity["indexed_values"]
    # end if
    
    found_values = search_values(entity["values"], value_filters, stop_first = stop_first, indexed_values = indexed_values)
    return found_values

def add_filters(app):
    """
    Method to add the filters associated to the values in json format
    to the app
    """
    
    @app.template_filter()
    def get_values(entity, value_filters, stop_first = True):
        return get_values_definition(entity, value_filters, stop_first)
