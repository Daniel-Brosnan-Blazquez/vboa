"""
Script for generating the expected authentication and authorization security layer applied to routes

Written by DEIMOS Space S.L.

module vboa
"""
# Import python utilities
import subprocess
from subprocess import PIPE
import json
import os

# Import vboa
import vboa

# Import aux functions
import vboa.tests.security.functions as security_functions

# Obtain the paths of the files containing decorators like "@.*route"
module_path = os.path.dirname(vboa.__file__)
command = 'PYFILES=`find {} -path {}/tests -prune -o -name "*py"`; grep -sl "^[ \t]*@.*route" $PYFILES'.format(module_path, module_path)
path_files = subprocess.run(command, shell=True, stdout=PIPE).stdout.decode()

# Generate dictionary with relevant security information
dict_app_security = security_functions.set_dict_app_security(path_files)

path_json_file = "inputs/app_security_to_review.json"

with open(path_json_file, "w") as outfile:
    json.dump(dict_app_security, outfile, indent=4)

print("Security analysis generated and exported to {}".format(path_json_file))
