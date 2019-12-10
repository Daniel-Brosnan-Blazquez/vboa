"""
BOA scheduler navigation section definition

Written by DEIMOS Space S.L. (dibb)

module vboa
"""
# Import python utilities
import datetime
from dateutil import parser

# Import flask utilities
from flask import Blueprint, current_app, render_template, request
from flask import jsonify

# Import sboa utilities
from sboa.engine.query import Query
import sboa.engine.engine as sboa_engine
from sboa.engine.engine import Engine

# Import auxiliary functions
from rboa.engine.functions import get_rboa_archive_path
from rboa.triggering.rboa_triggering import get_reporting_conf

archive_path = get_rboa_archive_path()

bp = Blueprint("sboa", __name__, url_prefix="/sboa")
query = Query()
engine = Engine()

# Simulation size in days
simulation_size = 90

##############
# NAVIGATION #
##############

@bp.route("/navigate", methods=["GET"])
def navigate():
    """
    Panel for the BOA scheduler navigation functionality.
    """        
    return render_template("boa_scheduler/query_rules.html")


@bp.route("/simulate", methods=["GET"])
def simulate():
    """
    Panel for the BOA scheduler simulation functionality.
    """

    t0 = datetime.datetime.now().date()

    list_tasks, simulated_tasks = generate_task_lists(t0)
    
    return render_template("boa_scheduler/simulate_agenda.html", tasks = list_tasks, t0 = t0, simulated_tasks = simulated_tasks, simulation_size = simulation_size)

@bp.route("/simulate/<string:t0>", methods=["GET"])
def simulate_with_t0(t0):
    """
    Panel for the BOA scheduler simulation functionality.
    """

    try:
        parser.parse(t0)
    except:
        return render_template("panel/error.html")
    # end try
    
    list_tasks, simulated_tasks = generate_task_lists(parser.parse(t0).date())
    
    return render_template("boa_scheduler/simulate_agenda.html", tasks = list_tasks, t0 = parser.parse(t0).date(), simulated_tasks = simulated_tasks, simulation_size = simulation_size)

def generate_task_lists(t0):
    """
    Method to obtain the agenda and simulate the execution following the simulation size
    """
    
    list_rules = []
    list_tasks = []
    engine.generate_rules_and_tasks(list_rules, list_tasks, t0 = t0)

    for task in list_tasks:
        rules = [rule for rule in list_rules if rule["rule_uuid"] == task["rule_uuid"]]
        task["rule_name"] = rules[0]["name"]
        task["periodicity"] = rules[0]["periodicity"]
        task["window_delay"] = rules[0]["window_delay"]
        task["window_size"] = rules[0]["window_size"]
        task["triggering_time"] = parser.parse(task["triggering_time"])
    # end for

    simulated_tasks = []
    for task in list_tasks:
        number_of_executions = int(simulation_size / float(task["periodicity"]))
        if number_of_executions > 100:
            number_of_executions = 100
        # end if
        
        for execution in range(number_of_executions):
            triggering_time = task["triggering_time"] + (datetime.timedelta(days=float(task["periodicity"])) * execution)
            stop_coverage = triggering_time - datetime.timedelta(days=float(task["window_delay"]))
            start_coverage = stop_coverage - datetime.timedelta(days=float(task["window_size"]))            

            simulated_tasks.append({
                "task_uuid": task["task_uuid"],
                "name": task["name"],
                "command": task["command"],
                "rule_name": task["rule_name"],
                "periodicity": task["periodicity"],
                "window_delay": task["window_delay"],
                "window_size": task["window_size"],
                "triggering_time": triggering_time,
                "start_coverage": start_coverage,
                "stop_coverage": stop_coverage,
            })
    # end for

    return list_tasks, simulated_tasks

@bp.route("/load-agenda/<string:t0>", methods=["GET"])
def load_agenda(t0):
    """
    Route for loading the agenda.
    """

    try:
        parser.parse(t0)
    except:
        return jsonify({"status": -1, "message": "The T0 value {} is not a valid date".format(t0)})
    # end try
    
    returned_status = engine.insert_configuration(parser.parse(t0).date())
    
    return jsonify(returned_status)
