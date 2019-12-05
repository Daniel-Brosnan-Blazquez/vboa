"""
RBOA navigation section definition

Written by DEIMOS Space S.L. (dibb)

module vboa
"""
# Import python utilities
import sys
import json
import tarfile
import json
import shlex
from subprocess import Popen, PIPE
from multiprocessing import Pool

# Import flask utilities
from flask import Blueprint, flash, g, current_app, redirect, render_template, request, url_for
from flask_debugtoolbar import DebugToolbarExtension
from flask import jsonify

# Import eboa utilities
from eboa.engine.query import Query
import rboa.engine.engine as rboa_engine
from eboa.engine.engine import Engine

# Import auxiliary functions
from rboa.engine.functions import get_rboa_archive_path
from rboa.triggering.rboa_triggering import get_reporting_conf

archive_path = get_rboa_archive_path()

bp = Blueprint("rboa_nav", __name__, url_prefix="/rboa_nav")
query = Query()
engine = Engine()

##############
# NAVIGATION #
##############

@bp.route("/", methods=["GET", "POST"])
def navigate():
    """
    Initial panel for the RBOA navigation functionality.
    """
    filters = []
    if request.method == "POST":
        filters = request.json
    # end if
        
    return render_template("rboa_nav/query_reports.html", filters = filters)

@bp.route("/query-reports", methods=["GET", "POST"])
def query_reports_and_render():
    """
    Query reports amd render.
    """
    current_app.logger.debug("Query reports and render")
    if request.method == "POST":
        filters = request.form.to_dict(flat=False).copy()
        filters["offset"] = [""]

        reports = query_reports(filters)
        show = define_what_to_show_reports(filters)
        return render_template("rboa_nav/reports_nav.html", reports=reports, show=show, filters=filters)
    # end if

    return render_template("rboa_nav/query_reports.html")

@bp.route("/query-reports-pages", methods=["POST"])
def query_reports_pages():
    """
    Query reports using pages and render.
    """
    current_app.logger.debug("Query reports using pages and render")
    filters = request.json

    reports = query_reports(filters)
    show = define_what_to_show_reports(filters)
    return render_template("rboa_nav/reports_nav.html", reports=reports, show=show, filters=filters)

def define_what_to_show_reports(filters):
    """
    Function to define what to show for reports
    """

    show = {}
    show["validity_timeline"]=True
    if not "show_validity_timeline" in filters:
        show["validity_timeline"] = False
    # end if
    show["generation_duration_xy"]=True
    if not "show_generation_duration_xy" in filters:
        show["generation_duration_xy"] = False
    # end if
    
    return show

def query_reports(filters):
    """
    Query reports.
    """
    current_app.logger.debug("Query reports")
    kwargs = {}

    # Get only generated reports
    kwargs["generated"] = True
    
    if filters["report"][0] != "":
        op="notlike"
        if not "report_notlike_check" in filters:
            op="like"
        # end if
        kwargs["names"] = {"filter": filters["report"][0], "op": filters["report_operator"][0]}
    # end if
    elif "reports" in filters and filters["reports"][0] != "":
        op="notin"
        if not "report_notin_check" in filters:
            op="in"
        # end if
        kwargs["names"] = {"filter": [], "op": op}
        i = 0
        for report in filters["reports"]:
            kwargs["names"]["filter"].append(report)
            i+=1
        # end for
    # end if

    if filters["report_group"][0] != "":
        op="notlike"
        if not "report_group_notlike_check" in filters:
            op="like"
        # end if
        kwargs["report_groups"] = {"filter": filters["report_group"][0], "op": filters["report_group_operator"][0]}
    # end if
    elif "report_groups" in filters and filters["report_groups"][0] != "":
        op="notin"
        if not "report_group_notin_check" in filters:
            op="in"
        # end if
        kwargs["report_groups"] = {"filter": [], "op": op}
        i = 0
        for report_group in filters["report_groups"]:
            kwargs["report_groups"]["filter"].append(report_group)
            i+=1
        # end for
    # end if

    if filters["generator"][0] != "":
        op="notlike"
        if not "generator_notlike_check" in filters:
            op="like"
        # end if
        kwargs["generators"] = {"filter": filters["generator"][0], "op": filters["generator_operator"][0]}
    # end if
    elif "generators" in filters and filters["generators"][0] != "":
        op="notin"
        if not "generator_notin_check" in filters:
            op="in"
        # end if
        kwargs["generators"] = {"filter": [], "op": op}
        i = 0
        for generator in filters["generators"]:
            kwargs["generators"]["filter"].append(generator)
            i+=1
        # end for
    # end if

    if filters["validity_start"][0] != "":
        kwargs["validity_start_filters"] = []
        i = 0
        operators = filters["validity_start_operator"]
        for start in filters["validity_start"]:
            kwargs["validity_start_filters"].append({"date": start, "op": operators[i]})
            i+=1
        # end for
    # end if
    if filters["validity_stop"][0] != "":
        kwargs["validity_stop_filters"] = []
        i = 0
        operators = filters["validity_stop_operator"]
        for stop in filters["validity_stop"]:
            kwargs["validity_stop_filters"].append({"date": stop, "op": operators[i]})
            i+=1
        # end for
    # end if

    if filters["report_validity_duration"][0] != "":
        kwargs["validity_duration_filters"] = []
        i = 0
        operators = filters["report_validity_duration_operator"]
        for report_validity_duration in filters["report_validity_duration"]:
            kwargs["validity_duration_filters"].append({"float": float(report_validity_duration)*24*60*60, "op": operators[i]})
            i+=1
        # end for
    # end if

    if filters["triggering_time"][0] != "":
        kwargs["triggering_time_filters"] = []
        i = 0
        operators = filters["triggering_time_operator"]
        for triggering_time in filters["triggering_time"]:
            kwargs["triggering_time_filters"].append({"date": triggering_time, "op": operators[i]})
            i+=1
        # end for
    # end if

    if "statuses" in filters and filters["statuses"][0] != "":
        op="notin"
        if not "status_notin_check" in filters:
            op="in"
        # end if
        kwargs["statuses"] = {"filter": [], "op": op}
        i = 0
        for status in filters["statuses"]:
            kwargs["statuses"]["filter"].append(status)
            i+=1
        # end for
    # end if

    # Query restrictions
    if filters["order_by"][0] != "":
        descending = True
        if not "order_descending" in filters:
            descending = False
        # end if
        kwargs["order_by"] = {"field": filters["order_by"][0], "descending": descending}
    # end if

    if filters["limit"][0] != "":
        kwargs["limit"] = filters["limit"][0]
    # end if

    if filters["offset"][0] != "":
        kwargs["offset"] = filters["offset"][0]
    # end if

    reports = query.get_reports(**kwargs)

    return reports

@bp.route("/query-report/<uuid:report_uuid>")
def query_report(report_uuid):
    """
    Query report corresponding to the UUID received.
    """
    current_app.logger.debug("Query report by identifier")
    reports = query.get_reports(report_uuids={"filter": [report_uuid], "op": "in"})
    if len(reports) > 0:
        report = [0]
    else:
        return render_template("panel/error.html"), 403
    # end if

    html = retrieve_report_content(report)
    
    return html

@bp.route("/query-report-by-name/<string:report_name>", methods=["GET"])
def query_report_by_name(report_name):
    """
    Query report by name
    """
    kwargs = {}
    # Get only generated reports
    kwargs["generated"] = True

    kwargs["names"] = {"filter": [report_name], "op": "in"}
    kwargs["order_by"] = {"field": "generation_stop", "descending": True}

    current_app.logger.debug("Query report by name")
    report = query.get_reports(**kwargs)[0]

    html = retrieve_report_content(report)
    
    return html

def retrieve_report_content(report):
    """
    Retrieve report from archive
    """
    current_app.logger.debug("Retrieve report from archive")

    # Check that the relative_path exists
    if report.relative_path != None:

        file_path = archive_path + "/" + report.relative_path

        if report.compressed:
            # Get the report inside
            tar = tarfile.open(file_path, "r")
            f = tar.extractfile(tar.getnames()[0])
        else:
            f = open(file_path, "r")
        # end if

        html = f.read()

        # Close file
        f.close()

        if report.compressed:
            # Close tar if the report was compressed
            tar.close()
        # end if
    
        return html

    return render_template("panel/error.html")

@bp.route("/query-jsonify-reports")
def query_jsonify_reports():
    """
    Query all the reports.
    """
    current_app.logger.debug("Query report")
    # Get limit and offset values
    limit = request.args.get("limit")
    offset = request.args.get("offset")
    search = request.args.get("search")

    # Set the filters for the query
    kwargs = {}
    kwargs["limit"] = limit
    kwargs["offset"] = offset
    kwargs["names"] = {"filter": search, "op": "=="}

    reports = query.get_reports(**kwargs)
    jsonified_reports = [report.jsonify() for report in reports]
    return jsonify(jsonified_reports)

@bp.route("/query-jsonify-reports-by-report-group")
def query_jsonify_reports_by_report_group():
    """
    Query all the reports.
    """
    current_app.logger.debug("Query report")
    # Get limit and offset values
    limit = request.args.get("limit")
    offset = request.args.get("offset")
    search = request.args.get("search")

    # Set the filters for the query
    kwargs = {}
    kwargs["limit"] = limit
    kwargs["offset"] = offset
    kwargs["report_groups"] = {"filter": search, "op": "=="}

    reports = query.get_reports(**kwargs)
    jsonified_reports = [report.jsonify() for report in reports]
    return jsonify(jsonified_reports)

@bp.route("/query-jsonify-report-groups")
def query_jsonify_report_groups():
    """
    Query report groups.
    """
    current_app.logger.debug("Query report groups")
    # Get limit and offset values
    limit = request.args.get("limit")
    offset = request.args.get("offset")
    search = request.args.get("search")

    # Set the filters for the query
    kwargs = {}
    kwargs["limit"] = limit
    kwargs["offset"] = offset
    kwargs["names"] = {"filter": "%" + search + "%", "op": "like"}

    report_groups = query.get_report_groups(**kwargs)
    jsonified_report_groups = [report_group.jsonify() for report_group in report_groups]
    return jsonify(jsonified_report_groups)

@bp.route("/query-jsonify-report-statuses/<uuid:report_uuid>")
def query_jsonify_report_statuses(report_uuid):
    """
    Query statuses related to the report with the corresponding received UUID.
    """
    current_app.logger.debug("Query statuses corresponding to the report with the specified UUID " + str(report_uuid))
    reports = query.get_reports(report_uuids = {"filter": [report_uuid], "op": "in"})
    jsonified_statuses = [report_status.jsonify() for report in reports for report_status in report.statuses]
    return jsonify(jsonified_statuses)

@bp.route("/get-report-status")
def get_report_status():
    """
    Get the report statuses defined in the RBOA component.
    """
    current_app.logger.debug("Get report statuses")
    return jsonify(rboa_engine.exit_codes)

#############
# EXECUTION #
#############

@bp.route("/reporting_triggering", methods=["GET"])
def show_execute_reports():
    """
    Show the generators of reporting.
    """
    current_app.logger.debug("Prepare execution view")

    reporting_xpath = get_reporting_conf()
    generators = []
    for generator in reporting_xpath("/reporting_generators/generator"):
        generators.append({"name": generator.xpath("@name")[0],
                          "description": generator.xpath("@description")[0],
                          "name_format": generator.xpath("name_format")[0].text
        })
    # end for
    
    return render_template("rboa_nav/execute_reports.html", generators=generators)

@bp.route("/execute-reports", methods=["POST"])
def execute_reports():
    """
    Execute selected reports.
    """
    current_app.logger.debug("Execute selected reports")
    filters = request.json

    start = filters["start"][0]
    stop = filters["stop"][0]

    parameters = []
    for generator in filters["generators"]:
        parameters.append({
            "generator": generator,
            "start": start,
            "stop": stop
        })
    # end for

    # Trigger parallel generation of reports
    pool = Pool(len(filters["generators"]))
    try:
        pool.map(trigger_generator, parameters)
    finally:
        pool.close()
        pool.join()
    # end try
    
    return render_template("rboa_nav/query_reports.html")

# Function to execute the command
def trigger_generator(parameters):
    generator = parameters["generator"]
    start = parameters["start"]
    stop = parameters["stop"]
    command = "rboa_triggering.py -g '" + generator + "' -m MANUAL -b '" + start + "' -e '" + stop + "'"
    command_split = shlex.split(command)
    program = Popen(command_split, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, error = program.communicate()        
    return_code = program.returncode
# end for
