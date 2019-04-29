"""
Router definition

Written by DEIMOS Space S.L. (dibb)

module vboa
"""
# Import python utilities
import os

# Import flask utilities
from flask import Flask, current_app
from flask_debugtoolbar import DebugToolbarExtension

# Import contents
from vboa import panel
from vboa.eboa_nav import eboa_nav

def create_app():
    """
    Create and configure an instance of the Flask application.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY='dev'
    )

    app.register_blueprint(panel.bp)
    app.register_blueprint(eboa_nav.bp)

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
    def selectattr_map(list_of_items, attr, attr_filter, value):
        """Convert a string to all caps."""
        list_result = []
        for items in list_of_items:
            for item in items:
                expression = eval("item." + attr)
                if eval("expression " + attr_filter + " value"):
                    list_result.append(item)
                # end if
            # end for
        # end for
        return list_result

    @app.template_filter()
    def events_group_by_value(list_of_events, name):
        """Convert a string to all caps."""
        result = {}
        for event in list_of_events:
            value = [value.value for value in event.eventTexts if value.name == name][0]
            if not value in result:
                result[value] = []
            # end if
            result[value].append(event)
        # end for
        return result

    @app.template_filter()
    def get_timeline_duration(list_of_events):
        result = 0
        for event in list_of_events:
            result += event.get_duration()
        # end for
        return result

    return app
