"""
Specific instantiation for the #VIEWS_DIR# visualization tool

Written by DEIMOS Space S.L. (dibb)

module #VIEWS_DIR#
"""
# Import python utilities
import os

# Import flask utilities
from flask import Flask, send_from_directory
from flask_debugtoolbar import DebugToolbarExtension
import jinja2

# Import vboa
import vboa

def create_app():
    """
    Create and configure an instance of vboa application.
    """
    app = vboa.create_app()
    
    # Register the specific templates folder
    templates_folder = os.path.dirname(__file__) + "/templates"
    templates_loader = jinja2.ChoiceLoader([
        jinja2.FileSystemLoader(templates_folder),
        app.jinja_loader
    ])
    app.jinja_loader = templates_loader

    # Register the specific static folder
    static_folder = os.path.dirname(__file__) + "/static"
    @app.route('/static_images/<path:filename>')
    def resolve_static(filename):
        return send_from_directory(static_folder + "/images", filename)
    # end def
    
    return app
