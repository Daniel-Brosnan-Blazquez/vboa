"""
Filters for annotations in json format

Written by DEIMOS Space S.L. (dibb)

module vboa
"""
# Import python utilities
import datetime
from dateutil import parser
import re

# Import operators
from vboa.filters.operators import arithmetic_operators, text_operators, regex_operators

def check_system(annotation, annotation_filter):
    """
    Method to get the annotation inside the dict of annotations with system annotation["system"]

    :param annotation: annotation structure for explicit references
    :type annotation: dict
    :param annotation_filter: annotation filter
    :type annotation_filter: dict

    :return: flag indicating if the annotation system matches the filter
    :rtype: bool

    """
    matches = False
    # Check if there is a filter for the system
    if "system" in annotation_filter:
        system_filter = annotation_filter["system"]
        # Check if the system matches
        if system_filter["op"] in arithmetic_operators.keys():
            op = arithmetic_operators[system_filter["op"]]
            if op(annotation["system"], system_filter["filter"]):
                matches = True
            # end if
        # end if
        if system_filter["op"] in regex_operators.keys():
            if re.match(system_filter["filter"], annotation["system"]):
                matches = True
            # end if
        # end if
    else:
        matches = True
    # end if

    return matches

def check_systems(annotations, annotation_filter, stop_first):

    annotations_matching = []
    for annotation in annotations:
        annotation_matches = check_system(annotation, annotation_filter)
        if annotation_matches:
            annotations_matching.append(annotation)
        # end if

        if stop_first:
            break
        # end if
    # end for

    return annotations_matching

def insert_annotation(annotation, found_annotations, annotation_filter):
    """
    """
    group = "annotations"
    if "group" in annotation_filter:
        group = annotation_filter["group"]
    # end if

    if group not in found_annotations:
        found_annotations[group] = []
    # end if

    found_annotations[group].append(annotation)

    return

def search_annotations(indexed_annotations, annotation_filters, stop_first = True):
    """
    Recursive method to get the annotations inside the dictionary of annotations

    :param indexed_annotations: dict of annotations
    :type indexed_annotations: dict
    :param annotation_filters: list of annotation filters
    :type annotation_filters: list of annotation filters
    :param stop_first: bool indicating if the search must stop for every filter when found the first match
    :type stop_first: bool

    :return: found_annotations
    :rtype: dict

    """
    found_annotations = {}

    for annotation_filter in annotation_filters:
        name_filter = annotation_filter["name"]
        if indexed_annotations != None and (name_filter["op"] == "==" or name_filter["op"] == "in"):
            if name_filter["op"] == "==":
                names = [name_filter["filter"]]
            else:
                names = name_filter["filter"]
            # end if
            for name in names:
                if name in indexed_annotations:
                    for annotation in indexed_annotations[name]:
                        annotation_matches = check_system(annotation, annotation_filter)
                        if annotation_matches:
                            insert_annotation(annotation, found_annotations, annotation_filter)

                            if stop_first:
                                break
                            # end if

                        # end if
                # end if
            # end if
        else:
            for annotation_name in indexed_annotations:

                annotations_matching = []
                # Discriminate by type of operator
                if name_filter["op"] in arithmetic_operators.keys():
                    op = arithmetic_operators[name_filter["op"]]
                    # Check if the annotation name matches
                    if op(annotation_name, name_filter["filter"]):
                        annotations_matching = check_systems(indexed_annotations[annotation_name], annotation_filter, stop_first)
                    # end if
                elif name_filter["op"] in regex_operators.keys():
                    # Check if the annotation name matches
                    if re.match(name_filter["filter"], annotation_name):
                        annotations_matching = check_systems(indexed_annotations[annotation_name], annotation_filter, stop_first)
                    # end if
                # end if

                for annotation in annotations_matching:
                    insert_annotation(annotation, found_annotations, annotation_filter)

                    if stop_first:
                        break
                    # end if
                    
                # end if
                    
            # end for
        # end if
    # end for
        
    # end for
    return found_annotations

def get_annotations_definition(explicit_reference, annotation_filters, stop_first = True):
    """
    Method to get the annotations inside the explicit reference structure

    :param entity: dictionary with the entity
    :type entity: dict
    :param annotation_filters: list of annotation filters
    :type annotation_filters: list of annotation filters
    :param stop_first: bool indicating if the search must stop for every filter when found the first match
    :type stop_first: bool

    :return: found_annotations
    :rtype: dict

    """
    found_annotations = []
    if "annotations" in explicit_reference:
        found_annotations = search_annotations(explicit_reference["annotations"], annotation_filters, stop_first = stop_first)
    # end if
    
    return found_annotations

def get_annotations_from_data_definition(annotations, data):
    """
    Method to get the annotations inside the data structure from a list of dicts containing annotation UUIDs

    :return: annotations
    :rtype: dict

    """
    
    return [data["annotations"][annotation["annotation_uuid"]] for annotation in annotations]

def add_filters(app):
    """
    Method to add the filters associated to the annotations in json format
    to the app
    """
    
    @app.template_filter()
    def get_annotations(explicit_reference, annotation_filters, stop_first = True):
        return get_annotations_definition(explicit_reference, annotation_filters, stop_first)

    @app.template_filter()
    def get_annotations_from_data(annotations, data):
        return get_annotations_from_data_definition(annotations, data)
