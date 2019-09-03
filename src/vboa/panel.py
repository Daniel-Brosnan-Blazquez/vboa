"""
VBOA inital panel section definition

Written by DEIMOS Space S.L. (dibb)

module vboa
"""
# Import python utilities
import os
from subprocess import Popen, PIPE
import shlex

# Import flask utilities
from flask import Blueprint, flash, g, redirect, render_template, request, url_for, jsonify

bp = Blueprint('panel', __name__)

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
