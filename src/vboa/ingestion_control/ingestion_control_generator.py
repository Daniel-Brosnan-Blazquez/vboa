"""
Generator module for the ingestion control view

Written by DEIMOS Space S.L. (dibb)

module vboa
"""
# Import python utilities
import os

# Import helpers
from vboa.functions import export_html

# Import vboa app creator
from vboa import create_app

version = "1.0"

def generate_report(begin, end, metadata):

    app = create_app()
    client = app.test_client()
    response = client.post("/ingestion_control/ingestion_control", data={
        "start": begin,
        "stop": end,
    })

    html_file_path = export_html(response)

    metadata["operations"][0]["report"]["generator"] = os.path.basename(__file__)
    metadata["operations"][0]["report"]["generator_version"] = version
    metadata["operations"][0]["report"]["group"] = "INGESTION_CONTROL"
    metadata["operations"][0]["report"]["group_description"] = "Group of reports dedicated for the monitoring of the ingestion chain"

    return html_file_path
