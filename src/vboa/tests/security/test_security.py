"""
Automated tests for the the authentication and authorization security layer

Written by DEIMOS Space S.L.

module vboa
"""
# Import python utilities
import unittest
import subprocess
from subprocess import PIPE
import json
import os

# Import vboa
import vboa

# Import aux functions
import vboa.tests.security.functions as security_functions

class TestSecurity(unittest.TestCase):
   
    def test_authentication_and_authorization_security(self):

        # Obtain the paths of the files containing decorators like "@.*route"
        module_path = os.path.dirname(vboa.__file__)
        command = 'PYFILES=`find {} -name "*py"`; grep -sl "^[ \t]*@.*route" $PYFILES'.format(module_path)
        path_files = subprocess.run(command, shell=True, stdout=PIPE).stdout.decode()
        
        # Expected dict and the actual dict of my app
        dict_app_security_actual = security_functions.set_dict_app_security(path_files)
        
        path_json_file = "inputs/app_security.json"
        dict_app_security_expected = json.load(open(path_json_file))
        
        assert dict_app_security_actual == dict_app_security_expected
