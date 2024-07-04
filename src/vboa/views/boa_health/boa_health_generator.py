"""
Generator module for the boa health monitoring view

Written by DEIMOS Space S.L. (dibb)

module vboa
"""
# Import python utilities
import os

# Import helpers
from vboa.functions import export_html

# Import vboa app creator
from vboa import create_app

# Import flask utilities
from flask import url_for

version = "1.0"

def generate_report(begin, end, metadata, parameters = None):

    app = create_app()
    client = app.test_client()
    response = client.post(url_for("health.show_health"), data={
        "start": begin,
        "stop": end,
    })

    html_file_path = export_html(response)

    metadata["operations"][0]["report"]["generator_version"] = version
    metadata["operations"][0]["report"]["group"] = "BOA_HEALTH"
    metadata["operations"][0]["report"]["group_description"] = "Group of reports dedicated for the monitoring of the health of the docker container hosting the BOA"

    return html_file_path
