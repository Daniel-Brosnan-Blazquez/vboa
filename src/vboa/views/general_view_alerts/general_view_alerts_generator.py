"""
Generator module for the general view of alerts view

Written by DEIMOS Space S.L. (jubv)

module vboa
"""
# Import python utilities
import os

# Import helpers
from vboa.functions import export_html

# Import vboa app creator
from vboa import create_app

version = "1.0"

def generate_report(begin, end, metadata, parameters = None):

    app = create_app()
    client = app.test_client()

    response = client.post("/general_view_alerts", data={
        "start": begin,
        "stop": end
    })

    html_file_path = export_html(response)

    metadata["operations"][0]["report"]["generator_version"] = version
    metadata["operations"][0]["report"]["group"] = "GENREAL_VIEW_OF_ALERTS"
    metadata["operations"][0]["report"]["group_description"] = "Group of reports dedicated to the monitoring of the types of alerts"

    return html_file_path