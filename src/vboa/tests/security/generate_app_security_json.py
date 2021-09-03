#!/usr/bin/env python3
"""
Script for generating the expected authentication and authorization security layer applied to routes

Written by DEIMOS Space S.L.

module vboa
"""
# Import python utilities
import json
import os

# Import vboa
import vboa

# Import aux functions
import vboa.tests.security.functions as security_functions

# Obtain the paths of the files containing decorators like "@.*route"
module_path = os.path.dirname(vboa.__file__)
path_files = security_functions.obtain_python_files_with_route_decorator(module_path)

# Generate dictionary with relevant security information
dict_app_security = security_functions.set_dict_app_security(path_files)

path_json_file = os.path.dirname(os.path.abspath(__file__)) + "/inputs/app_security.json"

with open(path_json_file, "w") as outfile:
    json.dump(dict_app_security, outfile, indent=4)

print("Security analysis generated and exported to {}".format(path_json_file))
