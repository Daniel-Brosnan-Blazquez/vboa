"""
Generator module for the reporting control view

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

    template_name = None
    if "type" in parameters:
        if parameters["type"] == "ALERTS_ERRORS":
            template_name = "alerts_and_errors"
        # end if
    # end if

    response = client.post(url_for("reporting_control.show_reporting_control"), data={
        "start": begin,
        "stop": end,
        "template": template_name
    })

    html_file_path = export_html(response)

    metadata["operations"][0]["report"]["generator_version"] = version
    metadata["operations"][0]["report"]["group"] = "REPORTING_CONTROL"
    metadata["operations"][0]["report"]["group_description"] = "Group of reports dedicated for the monitoring of the reporting chain"

    return html_file_path
