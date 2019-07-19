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
from flask import Flask, current_app
from flask_debugtoolbar import DebugToolbarExtension

# Import contents
from vboa import panel
from vboa.eboa_nav import eboa_nav
from vboa.boa_health import boa_health
from vboa.ingestion_control import ingestion_control

# Import engine
import eboa.engine.engine as eboa_engine

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
    app.register_blueprint(boa_health.bp)
    app.register_blueprint(ingestion_control.bp)

    # the toolbar is only enabled in debug mode:
    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

    toolbar = DebugToolbarExtension(app)

    @app.template_test()
    def has_value(values, name, value):
        filtered_values = [available_value for available_value in values if available_value.name == name and available_value.value == value]
        if len(filtered_values) > 0:
            return True
        else:
            return False

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
        severity_labels = [severity_label for severity_label in eboa_engine.alert_severity_codes if eboa_engine.alert_severity_codes[severity_label] == severity]
        return severity_labels[0]

    @app.template_filter()
    def get_value_key(dict, key):

        return dict[key]

    @app.template_filter()
    def mean(list_of_items):

        return numpy.mean(list_of_items)

    @app.template_test()
    def match(item, matching_text):

        return re.match(matching_text, item)

    return app
