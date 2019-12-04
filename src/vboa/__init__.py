"""
Router definition

Written by DEIMOS Space S.L. (dibb)

module vboa
"""
# Import python utilities
import os
import numpy
import re

# Import flask utilities
from flask import Flask, current_app, render_template
from flask_debugtoolbar import DebugToolbarExtension

# Import contents
from vboa import panel
from vboa.eboa_nav import eboa_nav
from vboa.rboa_nav import rboa_nav
from vboa.boa_health import boa_health
from vboa.ingestion_control import ingestion_control
from vboa.reporting_control import reporting_control

# Import ingestion functions
import eboa.ingestion.functions as ingestion_functions

# Import alert severity codes
from eboa.engine.alerts import alert_severity_codes

def create_app():
    """
    Create and configure an instance of the Flask application.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.jinja_env.add_extension('jinja2.ext.do')
    app.config.from_mapping(
        SECRET_KEY=b'\xca+-\x9b\xcek.\x9fkM \xea\x8d\x1c\x99&'
    )

    app.register_blueprint(panel.bp)
    app.register_blueprint(eboa_nav.bp)
    app.register_blueprint(rboa_nav.bp)
    app.register_blueprint(boa_health.bp)
    app.register_blueprint(ingestion_control.bp)
    app.register_blueprint(reporting_control.bp)

    # the toolbar is only enabled in debug mode:
    app.debug = False
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

    toolbar = DebugToolbarExtension(app)

    # Error handeling
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("panel/error.html"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("panel/error.html"), 500

    @app.errorhandler(403)
    def page_forbidden(e):
        return render_template("panel/error.html"), 403
    
    @app.template_test()
    def has_value(values, name, value):
        filtered_values = [available_value for available_value in values if available_value.name == name and available_value.value == value]
        if len(filtered_values) > 0:
            return True
        else:
            return False

    @app.template_test()
    def match(item, matching_text):

        return re.match(matching_text, item)

    @app.template_filter()
    def reject_events_with_link_name(list_of_events, link_name):
        """Convert a string to all caps."""
        result = [event for event in list_of_events if len([link for link in event.eventLinks if link.name == link_name]) == 0]
        
        return result

    @app.template_filter()
    def filter_events_by_text_value(list_of_events, name, filter):
        """Convert a string to all caps."""
        result = [event for event in list_of_events if len([value.value for value in event.eventTexts if value.name == name and value.value == filter]) > 0]
        
        return result

    @app.template_filter()
    def events_group_by_text_value(list_of_events, name):
        """Convert a string to all caps."""
        result = {}
        for event in list_of_events:
            values = [value.value for value in event.eventTexts if value.name == name]
            if len(values) > 0:
                value = values[0]
            else:
                value = "N/A"
            # end if
            if not value in result:
                result[value] = []
            # end if
            result[value].append(event)
        # end for
        return result

    @app.template_filter()
    def events_group_by_ref_group(list_of_events):
        """Convert a string to all caps."""
        result = {}
        groups = [event.explicitRef.group.name for event in list_of_events]
        unique_groups = sorted(set(groups))
        for group in unique_groups:
            result[group] = [event for event in list_of_events if event.explicitRef.group.name == group]
        # end for
        return result


    @app.template_filter()
    def events_group_by_ref_annotation(list_of_events, value_name, value_type, name = None, system = None):
        """Group events by a value of an annotation associated to its explicit reference."""
        result = {}
        if value_type == "boolean":
            value_type_qualifier = "annotationBooleans"
        elif value_type == "double":
            value_type_qualifier = "annotationDoubles"
        elif value_type == "timestamp":
            value_type_qualifier = "annotationTimestamps"
        elif value_type == "geometry":
            value_type_qualifier = "annotationGeometries"
        else:
            value_type_qualifier = "annotationTexts"
        # end if
        if name and system:
            annotations = [annotation for event in list_of_events for annotation in event.explicitRef.annotations if annotation.annotationCnf.name == name and annotation.annotationCnf.system == system]
        elif name:
            annotations = [annotation for event in list_of_events for annotation in event.explicitRef.annotations if annotation.annotationCnf.name == name]
        elif system:
            annotations = [annotation for event in list_of_events for annotation in event.explicitRef.annotations for event in list_of_events if annotation.annotationCnf.system == system]
        else:
            groups = []
        # end if
        groups = [value.value for annotation in annotations for value in eval("annotation." + value_type_qualifier) if value.name == value_name]
        unique_groups = sorted(set(groups))
        for group in unique_groups:
            if name and system:
                result[group] = set([event for event in list_of_events for annotation in event.explicitRef.annotations for value in eval("annotation." + value_type_qualifier) if value.value == group and annotation.annotationCnf.name == name and annotation.annotationCnf.system == system])
            elif name:
                result[group] = set([event for event in list_of_events for annotation in event.explicitRef.annotations for value in eval("annotation." + value_type_qualifier) if value.value == group and annotation.annotationCnf.name == name])
            elif system:
                result[group] = set([event for event in list_of_events for annotation in event.explicitRef.annotations for value in eval("annotation." + value_type_qualifier) if value.value == group and annotation.annotationCnf.system == system])
            # end if
        # end for
        return result

    @app.template_filter()    
    def refs_get_first_annotation(list_of_refs, name = None, system = None):
        """Convert a string to all caps."""
        result = []
        for ref in list_of_refs:
            if name and system:
                annotations = [annotation for annotation in ref.annotations if annotation.annotationCnf.name == name and annotation.annotationCnf.system == system]
            elif name:
                annotations = [annotation for annotation in ref.annotations if annotation.annotationCnf.name == name]
            elif system:
                annotations = [annotation for annotation in ref.annotations if annotation.annotationCnf.system == system]
            else:
                annotations = ref.annotations
            # end if
            if len(annotations) > 0:
                result.append(annotations[0])
            # end if
        # end for
        
        return result

    @app.template_filter()
    def filter_events_by_text_values(list_of_events, name, values):
        """Convert a string to all caps."""
        result = []
        for event in list_of_events:
            list_values = [value.value for value in event.eventTexts if value.name == name and value.value in values]
            if len(list_values) > 0:
                result.append(event)
            # end if
        # end for
        return result

    @app.template_filter()
    def get_timeline_duration(list_of_events):
        result = 0
        for event in list_of_events:
            result += event.get_duration()
        # end for
        return result

    @app.template_filter()
    def get_timeline_minimum_duration(list_of_events):
        durations = [event.get_duration() for event in list_of_events]
        return min(durations)

    @app.template_filter()
    def get_timeline_maximum_duration(list_of_events):
        durations = [event.get_duration() for event in list_of_events]
        return max(durations)

    @app.template_filter()
    def flatten(list_of_lists):
        return [item for list in list_of_lists for item in list]

    @app.template_filter()
    def get_severity_label(severity):
        severity_labels = [severity_label for severity_label in alert_severity_codes if alert_severity_codes[severity_label] == severity]
        return severity_labels[0]

    @app.template_filter()
    def get_value_key(dict, key):

        return dict[key]

    @app.template_filter()
    def mean(list_of_items):

        return numpy.mean(list_of_items)

    @app.template_filter()
    def sort_lists_by_length(list_of_lists):
        """Convert a string to all caps."""
        sorted_list = list_of_lists.copy()
        sorted_list.sort(key=len)
        
        return sorted_list

    ###
    # Date operations
    ###
    @app.template_filter()
    def convert_eboa_events_to_date_segments(list_of_events):
        """Convert list of events to date segments."""
        
        return ingestion_functions.convert_eboa_events_to_date_segments(list_of_events)

    @app.template_filter()
    def merge_timeline(timeline):
        
        return ingestion_functions.merge_timeline(timeline)

    @app.template_filter()
    def get_timeline_duration_segments(timeline):
        
        return ingestion_functions.get_timeline_duration(timeline)

    
    return app
