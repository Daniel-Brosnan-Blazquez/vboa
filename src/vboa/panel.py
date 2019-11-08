"""
VBOA inital panel section definition

Written by DEIMOS Space S.L. (dibb)

module vboa
"""
# Import python utilities
import os
from subprocess import Popen, PIPE
import shlex
import json
from tempfile import mkstemp
import datetime

# Import flask utilities
from flask import Blueprint, flash, g, redirect, render_template, request, url_for, jsonify

# Import rboa engine
import rboa.engine.engine as rboa_engine
from rboa.engine.engine import Engine

bp = Blueprint('panel', __name__)

version="1.0"

@bp.route('/')
def index():
    """
    Show initial panel.
    """

    return render_template('panel/index.html')

def execute_command(command):
    '''
    Method to execute a command
    '''
    
    command_split = shlex.split(command)
    try:
        program = Popen(command_split, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, error = program.communicate()
        return_code = program.returncode
        command_status = {"command": command,
                          "output": output.decode("utf-8"),
                          "error": error.decode("utf-8"),
                          "return_code": return_code}
    except FileNotFoundError:
        output = ""
        error = "Command {} not found".format(command)
        return_code = -1
        command_status = {"command": command,
                          "output": output,
                          "error": error,
                          "return_code": return_code}
    # end if

    return command_status

@bp.route('/check-orc-status')
def check_orc_status():
    """
    Check ORC status.
    """

    orc_status = {}

    orc_scheduler_check = os.system("pgrep orcScheduler")
    if orc_scheduler_check == 0:
        orc_status["scheduler"] = {"status": "on"}
    else:
        orc_status["scheduler"] = {"status": "off"}
    # end if

    orc_ingester_check = os.system("pgrep orcIngester")
    if orc_ingester_check == 0:
        orc_status["ingester"] = {"status": "on"}
    else:
        orc_status["ingester"] = {"status": "off"}
    # end if
    
    return jsonify(orc_status)

@bp.route('/switch-on-orc')
def switch_on_orc():
    """
    Switch on ORC.
    """
    
    command = "orcBolg --command start"

    command_status = execute_command(command)
    
    return jsonify(command_status)

@bp.route('/switch-off-orc')
def switch_off_orc():
    """
    Switch off ORC.
    """
    
    command = "orcBolg --command stop"

    command_status = execute_command(command)
    
    return jsonify(command_status)

@bp.route('/check-cron-status')
def check_cron_status():
    """
    Check CRON status.
    """

    cron_status = {}

    cron_check = os.system("pgrep crond")
    if cron_check == 0:
        cron_status["crond"] = {"status": "on"}
    else:
        cron_status["crond"] = {"status": "off"}
    # end if
    
    return jsonify(cron_status)

@bp.route('/switch-on-cron')
def switch_on_cron():
    """
    Switch on CRON.
    """

    command = "crond"

    command_status = execute_command(command)
    
    return jsonify(command_status)

@bp.route('/switch-off-cron')
def switch_off_cron():
    """
    Switch off CRON.
    """
    
    command = "pkill crond"

    command_status = execute_command(command)
    
    return jsonify(command_status)

@bp.route('/save-screenshot', methods=["POST"])
def save_screenshot():
    """
    Save screenshot.
    """

    html = request.json["html"]
    name = request.json["name"]
    group = request.json["group"]
    group_description = request.json["group_description"]

    (_, html_file_path) = mkstemp()
    f= open(html_file_path,"w+")
    f.write(html)
    f.close()
    
    creation_date = datetime.datetime.now().isoformat()
    metadata = {"operations": [{
        "mode": "insert",
        "report": {"name": name,
                   "group": group,
                   "group_description": group_description,
                   "path": html_file_path,
                   "compress": "true",
                   "generation_mode": "MANUAL",
                   "validity_start": creation_date,
                   "validity_stop": creation_date,
                   "triggering_time": creation_date,
                   "generation_start": creation_date,
                   "generation_stop": creation_date,
                   "generator": os.path.basename(__file__),
                   "generator_version": version
        }
    }]
    }

    failures = []
    successes = []
    
    try:
        engine_rboa = Engine()
        returned_statuses = engine_rboa.treat_data(metadata, name)
        engine_rboa.close_session()

        failures = [returned_status for returned_status in returned_statuses if not returned_status["status"] in [rboa_engine.exit_codes["OK"]["status"]]]
        successes = [returned_status for returned_status in returned_statuses if returned_status["status"] in [rboa_engine.exit_codes["OK"]["status"]]]

    except Exception as e:
        failures = [-1]
    # end try

    if len(failures) > 0:
        result = {
            "status": -1,
            "message": "The screenshot could not be saved. The operation returned the exit code: {}".format(failures[0])
        }
    else:
        result = {
            "status": 0,
            "message": "The screenshot has been saved successfully"
        }
    # end if
        
        
    return jsonify(result)
