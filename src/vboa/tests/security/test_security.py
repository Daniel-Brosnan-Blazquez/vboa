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
import io
from contextlib import redirect_stdout

# Import vboa
import vboa

# Import aux functions
import vboa.tests.security.functions as security_functions

class TestSecurity(unittest.TestCase):
   
    def setUp(self):
        # Create a temporary directory
        self.test_dir = "/vboa/src/vboa/tests/security/inputs/"
    
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

    def test_set_dict_app_security_node_not_function(self):

        dict_app_security_expected = {
                                    "authentication_required": [],
                                    "authentication_not_required": [],
                                    "roles": {}
                                    }
        
        dict_app_security = security_functions.set_dict_app_security(os.path.join(self.test_dir, "input_test_1.py"))

        assert dict_app_security == dict_app_security_expected
    
    def test_set_dict_app_security_no_decorators(self):

        dict_app_security_expected = {
                                    "authentication_required": [],
                                    "authentication_not_required": [],
                                    "roles": {}
                                    }
        
        dict_app_security = security_functions.set_dict_app_security(os.path.join(self.test_dir, "input_test_2.py"))

        assert dict_app_security == dict_app_security_expected

    def test_set_dict_app_security_no_ast_call_decorators_type(self):

        dict_app_security_expected = {
                                    "authentication_required": [],
                                    "authentication_not_required": [],
                                    "roles": {}
                                    }
        
        dict_app_security = security_functions.set_dict_app_security(os.path.join(self.test_dir, "input_test_3.py"))

        assert dict_app_security == dict_app_security_expected

    def test_set_dict_app_security_no_relevant_decorators(self):

        dict_app_security_expected = {
                                    "authentication_required": [],
                                    "authentication_not_required": [],
                                    "roles": {}
                                    }
        
        dict_app_security = security_functions.set_dict_app_security(os.path.join(self.test_dir, "input_test_4.py"))

        assert dict_app_security == dict_app_security_expected

    def test_set_dict_app_security_no_route_decorator(self):

        dict_app_security_expected = {
                                    "authentication_required": [],
                                    "authentication_not_required": [],
                                    "roles": {}
                                    }
        
        # Added a \n because print prints all its arguments, seperated by sep (by default a space), and ending with end, by default a newline. https://stackoverflow.com/questions/57094107/python-io-stringio-adding-extra-newline-at-the-end
        stdout_expected = "The method 'view' in module '" + os.path.join(self.test_dir, "input_test_5.py") + "' has decorators for security but does not define a route decorator\n"
        
        dict_app_security = security_functions.set_dict_app_security(os.path.join(self.test_dir, "input_test_5.py"))

        buf = io.StringIO()
        with redirect_stdout(buf):
            security_functions.set_dict_app_security(os.path.join(self.test_dir, "input_test_5.py"))
        assert stdout_expected == buf.getvalue()
        
        assert dict_app_security == dict_app_security_expected

    def test_set_dict_app_security_no_route_decorator_in_first_place(self):
        
        dict_app_security_expected = {
                                    "authentication_required": [],
                                    "authentication_not_required": [],
                                    "roles": {}
                                    }
        
        # Added a \n because print prints all its arguments, seperated by sep (by default a space), and ending with end, by default a newline. https://stackoverflow.com/questions/57094107/python-io-stringio-adding-extra-newline-at-the-end
        stdout_expected = "The method 'view' in module '" + os.path.join(self.test_dir, "input_test_6.py") + "' defines the route decorator '/test/<string:text>' but it is not defined as the first one\n"
        
        dict_app_security = security_functions.set_dict_app_security(os.path.join(self.test_dir, "input_test_6.py"))

        buf = io.StringIO()
        with redirect_stdout(buf):
            security_functions.set_dict_app_security(os.path.join(self.test_dir, "input_test_6.py"))
        assert stdout_expected == buf.getvalue()
        
        assert dict_app_security == dict_app_security_expected

    def test_set_dict_app_security_no_auth_required_decorator_but_route(self):
        
        dict_app_security_expected = {
                                    "authentication_required": [],
                                    "authentication_not_required": [],
                                    "roles": {}
                                    }
        
        # Added a \n because print prints all its arguments, seperated by sep (by default a space), and ending with end, by default a newline. https://stackoverflow.com/questions/57094107/python-io-stringio-adding-extra-newline-at-the-end
        stdout_expected = "The method 'view' in module '" + os.path.join(self.test_dir, "input_test_7.py") + "' associated to the route '/test/<string:text>' does not define the auth_required decorator but defines the roles_accepted decorator\n"
        
        dict_app_security = security_functions.set_dict_app_security(os.path.join(self.test_dir, "input_test_7.py"))

        buf = io.StringIO()
        with redirect_stdout(buf):
            security_functions.set_dict_app_security(os.path.join(self.test_dir, "input_test_7.py"))
        assert stdout_expected == buf.getvalue()
        
        assert dict_app_security == dict_app_security_expected

    def test_set_dict_app_security_with_route(self):

        dict_app_security_expected = {
                                    "authentication_required": [],
                                    "authentication_not_required": [{'method_name': 'view',
                                                                    'module_name': os.path.join(self.test_dir, "input_test_8.py"),
                                                                    'route': '/test/<string:text>'}],
                                    "roles": {}
                                    }
        
        dict_app_security = security_functions.set_dict_app_security(os.path.join(self.test_dir, "input_test_8.py"))
        
        assert dict_app_security == dict_app_security_expected

    def test_set_dict_app_security_no_auth_required_decorator_after_route(self):

        dict_app_security_expected = {
                                    "authentication_required": [],
                                    "authentication_not_required": [],
                                    "roles": {}
                                    }
        
        # Added a \n because print prints all its arguments, seperated by sep (by default a space), and ending with end, by default a newline. https://stackoverflow.com/questions/57094107/python-io-stringio-adding-extra-newline-at-the-end
        stdout_expected = "The method 'view' in module '" + os.path.join(self.test_dir, "input_test_9.py") + "' associated to the route '/test/<string:text>' does not define the auth_required decorator after the route decorator\n"
        
        dict_app_security = security_functions.set_dict_app_security(os.path.join(self.test_dir, "input_test_9.py"))

        buf = io.StringIO()
        with redirect_stdout(buf):
            security_functions.set_dict_app_security(os.path.join(self.test_dir, "input_test_9.py"))
        assert stdout_expected == buf.getvalue()
        
        assert dict_app_security == dict_app_security_expected

    def test_set_dict_app_security_with_route_auth_required_decorator(self):
        
        dict_app_security_expected = {
                                    "authentication_required": [{'method_name': 'view',
                                                                'module_name': os.path.join(self.test_dir, "input_test_10.py"),
                                                                'route': '/test/<string:text>'}],
                                    "authentication_not_required": [],
                                    "roles": {}
                                    }
        
        dict_app_security = security_functions.set_dict_app_security(os.path.join(self.test_dir, "input_test_10.py"))
        
        assert dict_app_security == dict_app_security_expected
    
    def test_set_dict_app_security_with_route_auth_required_roles_accepted_decorator(self):

        dict_app_security_expected = {
                                    "authentication_required": [{'method_name': 'view',
                                                                'module_name': os.path.join(self.test_dir, "input_test_11.py"),
                                                                'route': '/test/<string:text>'}],
                                    "authentication_not_required": [],
                                    "roles": {'admin':[{'method_name': 'view',
                                                        'module_name': os.path.join(self.test_dir, "input_test_11.py"),
                                                        'route': '/test/<string:text>'}],
                                            'operator':[{'method_name': 'view',
                                                        'module_name': os.path.join(self.test_dir, "input_test_11.py"),
                                                        'route': '/test/<string:text>'}]}
                                    }
        
        dict_app_security = security_functions.set_dict_app_security(os.path.join(self.test_dir, "input_test_11.py"))
        
        assert dict_app_security == dict_app_security_expected

    def test_set_dict_app_security_with_role_already_in_dict(self):
        
        dict_app_security_expected = {
                                    "authentication_required": [{'method_name': 'view',
                                                                'module_name': os.path.join(self.test_dir, "input_test_12.py"),
                                                                'route': '/test/<string:text>'},
                                                                {'method_name': 'home',
                                                                'module_name': os.path.join(self.test_dir, "input_test_12.py"),
                                                                'route': '/test/<string:text>'}],
                                    "authentication_not_required": [],
                                    "roles": {'admin':[{'method_name': 'view',
                                                        'module_name': os.path.join(self.test_dir, "input_test_12.py"),
                                                        'route': '/test/<string:text>'},
                                                        {'method_name': 'home',
                                                        'module_name': os.path.join(self.test_dir, "input_test_12.py"),
                                                        'route': '/test/<string:text>'}],
                                            'operator':[{'method_name': 'view',
                                                        'module_name': os.path.join(self.test_dir, "input_test_12.py"),
                                                        'route': '/test/<string:text>'}]}
                                    }
        
        dict_app_security = security_functions.set_dict_app_security(os.path.join(self.test_dir, "input_test_12.py"))
        
        assert dict_app_security == dict_app_security_expected