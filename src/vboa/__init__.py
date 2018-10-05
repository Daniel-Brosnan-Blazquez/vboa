"""
Router definition

Written by DEIMOS Space S.L. (dibb)

module vboa
"""
# Import python utilities
import os

# Import flask utilities
from flask import Flask
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

    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

    toolbar = DebugToolbarExtension(app)

    return app
