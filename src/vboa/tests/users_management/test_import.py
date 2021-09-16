"""
Automated tests for the import users

Written by DEIMOS Space S.L.

module vboa
"""
import json
import unittest
import vboa.tests.functions as functions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains,TouchActions
from selenium.webdriver.common.keys import Keys

# Import flask security utils
from flask_security import hash_password

# Import engine of the DDBB
import uboa.engine.engine as uboa_engine
from uboa.engine.engine import Engine
from uboa.engine.query import Query
from uboa.datamodel.base import Session

# Import datamodel
from uboa.datamodel.users import User, Role

# Create an app context to hash passwords (this is because the hash_password depends on configurations related to the app)
import vboa

app = vboa.create_app()
with app.app_context():
    password = hash_password("password")

class TestImportUsers(unittest.TestCase):

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('window-size=1920,1080')
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    

    def setUp(self):
        # Create the engine to manage the data
        self.engine_uboa = Engine()
        self.query_uboa = Query()

        # Create session to connect to the database
        self.session = Session()

        # Clear all tables before executing the test
        self.query_uboa.clear_db()

    def tearDown(self):
        # Close connections to the DDBB
        self.engine_uboa.close_session()
        self.query_uboa.close_session()
        self.session.close()

    @classmethod
    def tearDownClass(self):
        self.driver.quit()
    
    def test_import_from_file(self):
        
        data = {"operations": [{
            "mode": "insert",
            "users": [
                {
                    "email": "administrator@test.com",
                    "username": "administrator",
                    "password": password,
                    "roles": ["administrator"],
                    "group": "Deimos"
                }
            ]
        }]}

       
        self.engine_uboa.data = data
        assert uboa_engine.exit_codes["OK"]["status"] == self.engine_uboa.treat_data()[0]["status"]
        
        wait = WebDriverWait(self.driver,5)

        # Correct file
        self.driver.get("http://localhost:5000/users-management/import-users")

        self.driver.find_element_by_id("import-users-from-file-browse-file").send_keys("/vboa/src/vboa/tests/users_management/input/users_example.json")
        self.driver.find_element_by_id("import-users-from-file-submit-button").click()

        toast_text_expected = "The file 'users_example.json' was imported successfully"

        assert toast_text_expected == wait.until(EC.presence_of_element_located((By.CLASS_NAME,"toast-success"))).text

        # No file or wrong extension file
        self.driver.get("http://localhost:5000/users-management/import-users")

        self.driver.find_element_by_id("import-users-from-file-browse-file").send_keys("/vboa/src/vboa/tests/users_management/input/users_example.xml")
        self.driver.find_element_by_id("import-users-from-file-submit-button").click()

        toast_text_expected = "No file was selected or the extension of the file is incorrect"

        assert toast_text_expected == wait.until(EC.presence_of_element_located((By.CLASS_NAME,"toast-error"))).text

        # Wrong json schema (usernam instead of username)
        self.driver.get("http://localhost:5000/users-management/import-users")

        self.driver.find_element_by_id("import-users-from-file-browse-file").send_keys("/vboa/src/vboa/tests/users_management/input/users_wrong_example.json")
        self.driver.find_element_by_id("import-users-from-file-submit-button").click()

        toast_text_expected = "The source file with name users_wrong_example.json could not be loaded"

        assert toast_text_expected == wait.until(EC.presence_of_element_located((By.CLASS_NAME,"toast-error"))).text

        # With username same as one already in DDBB
        self.driver.get("http://localhost:5000/users-management/import-users")

        self.driver.find_element_by_id("import-users-from-file-browse-file").send_keys("/vboa/src/vboa/tests/users_management/input/users_wrong_example_1.json")
        self.driver.find_element_by_id("import-users-from-file-submit-button").click()

        toast_text_expected = "The metadata of the users information contains the definition of users already inserted in the DDBB"

        assert toast_text_expected == wait.until(EC.presence_of_element_located((By.CLASS_NAME,"toast-error"))).text

    def test_import_manually(self):
        
        data = {"operations": [{
            "mode": "insert",
            "users": [
                {
                    "email": "administrator@test.com",
                    "username": "administrator",
                    "password": password,
                    "roles": ["administrator"],
                    "group": "Deimos"
                }
            ]
        }]}

       
        self.engine_uboa.data = data
        assert uboa_engine.exit_codes["OK"]["status"] == self.engine_uboa.treat_data()[0]["status"]
        
        wait = WebDriverWait(self.driver,5)

        # Correct entry
        self.driver.get("http://localhost:5000/users-management/import-users")

        self.driver.find_element_by_id("import-users-from-editor-submit-button").click()

        toast_text_expected = "The data was imported successfully"

        assert toast_text_expected == wait.until(EC.presence_of_element_located((By.CLASS_NAME,"toast-success"))).text

        # No entry
        self.driver.get("http://localhost:5000/users-management/import-users")

        self.driver.find_element_by_id("import-users-textarea").clear()
        self.driver.find_element_by_id("import-users-from-editor-submit-button").click()

        toast_text_expected = "The data has an error:Expecting value: line 1 column 1 (char 0)"

        assert toast_text_expected == wait.until(EC.presence_of_element_located((By.CLASS_NAME,"toast-error"))).text

        # Wrong json schema (usernam instead of username)
        data_textarea = {
                        "operations":[
                            {
                                "mode":"insert",
                                "users":[
                                    {
                                    "email":"example@example.com",
                                    "usernam":"example",
                                    "password":"example_hash_password",
                                    "roles":[
                                        "example_role"
                                    ]
                                    }
                                ],
                                "roles":[
                                    {
                                    "name":"example_role",
                                    "description":"This text is an example."
                                    }
                                ]
                            }
                        ]
                    }
        
        self.driver.get("http://localhost:5000/users-management/import-users")

        self.driver.find_element_by_id("import-users-textarea").clear()
        self.driver.find_element_by_id("import-users-textarea").send_keys(json.dumps(data_textarea))
        self.driver.find_element_by_id("import-users-from-editor-submit-button").click()

        toast_text_expected = "The metadata of the users information does not pass the schema verification"

        assert toast_text_expected == wait.until(EC.presence_of_element_located((By.CLASS_NAME,"toast-error"))).text

        # With username same as one already in DDBB
        data_textarea = {
                        "operations":[
                            {
                                "mode":"insert",
                                "users":[
                                    {
                                    "email":"example@example.com",
                                    "username":"administrator",
                                    "password":"example_hash_password",
                                    "roles":[
                                        "example_role_2"
                                    ]
                                    }
                                ],
                                "roles":[
                                    {
                                    "name":"example_role_2",
                                    "description":"This text is an other example."
                                    }
                                ]
                            }
                        ]
                    }
        
        self.driver.get("http://localhost:5000/users-management/import-users")

        self.driver.find_element_by_id("import-users-textarea").clear()
        self.driver.find_element_by_id("import-users-textarea").send_keys(json.dumps(data_textarea))
        self.driver.find_element_by_id("import-users-from-editor-submit-button").click()

        toast_text_expected = "The metadata of the users information contains the definition of users already inserted in the DDBB"

        assert toast_text_expected == wait.until(EC.presence_of_element_located((By.CLASS_NAME,"toast-error"))).text
        
