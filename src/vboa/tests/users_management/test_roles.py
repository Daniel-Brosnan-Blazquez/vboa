"""
Automated tests for the events tab

Written by DEIMOS Space S.L.

module vboa
"""

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

class TestRolesTab(unittest.TestCase):

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
    
    def test_roles_no_data(self):

        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/users-management/uboa-nav")

        # Go to tab
        functions.goToTab(self.driver,"Roles")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'roles-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"roles-nav-no-data")))

        assert no_data

    def test_roles_query_no_filter(self):

        data = {"operations": [{
            "mode": "insert",
            "users": [
                {
                    "email": "administrator@test.com",
                    "username": "administrator",
                    "password": password,
                    "roles": ["administrator"]
                }
            ],
            "roles": [
                {
                    "name": "administrator",
                    "description": "Administrator of the system"
                }
            ]
        }]}

        # Check data is correctly inserted
        self.engine_uboa.data = data
        assert uboa_engine.exit_codes["OK"]["status"] == self.engine_uboa.treat_data()[0]["status"]
        
        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/users-management/uboa-nav")

        # Go to tab
        functions.goToTab(self.driver,"Roles")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'roles-submit-button')))
        functions.click(submitButton)

        # Check table generated
        roles_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-roles-table")))
        number_of_elements = len(roles_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        roles = self.query_uboa.get_roles()
        
        # Check role
        role = roles_table.find_elements_by_xpath("tbody/tr[1]/td[1]")

        assert role[0].text == "administrator"

        # Check description
        description = roles_table.find_elements_by_xpath("tbody/tr[1]/td[2]")

        assert description[0].text == "Administrator of the system"

        # Check role_uuid
        role_uuid = roles_table.find_elements_by_xpath("tbody/tr[1]/td[3]")

        assert role_uuid[0].text == str(roles[0].role_uuid)


    def test_roles_query_email_filter(self):

        data = {"operations": [{
            "mode": "insert",
            "users": [
                {
                    "email": "administrator@test.com",
                    "username": "administrator",
                    "password": password,
                    "roles": ["administrator"],
                    "group": "Deimos"
                },{
                    "email": "operator@test.com",
                    "username": "operator",
                    "password": password,
                    "roles": ["operator"],
                    "group": "Deimos"
                },
            ]
        }]}

        # Check data is correctly inserted
        self.engine_uboa.data = data
        assert uboa_engine.exit_codes["OK"]["status"] == self.engine_uboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5)

        ## Like ##
        self.driver.get("http://localhost:5000/users-management/uboa-nav")

        # Go to tab
        functions.goToTab(self.driver,"Roles")

        # Fill the email_like input
        input_element = self.driver.find_element_by_id("roles-email-text")
        input_element.send_keys("administrator@test.com")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'roles-submit-button')))
        functions.click(submitButton)

        # Check table generated
        roles_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-roles-table")))
        number_of_elements = len(roles_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(roles_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not Like ##
        self.driver.get("http://localhost:5000/users-management/uboa-nav")

        # Go to tab
        functions.goToTab(self.driver,"Roles")

        # Fill the email_like input
        input_element = self.driver.find_element_by_id("roles-email-text")
        input_element.send_keys("administrator@test.com")

        menu = Select(self.driver.find_element_by_id("roles-email-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'roles-submit-button')))
        functions.click(submitButton)

        # Check table generated
        roles_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-roles-table")))
        number_of_elements = len(roles_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(roles_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

        ## In ##
        self.driver.get("http://localhost:5000/users-management/uboa-nav")

        # Go to tab
        functions.goToTab(self.driver,"Roles")

        # Fill the email_like input
        input_element = self.driver.find_element_by_id("roles-emails-in-text")
        functions.click(input_element)

        input_element.send_keys("operator@test.com")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("roles-emails-in-select"))
        options.select_by_visible_text("operator@test.com")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'roles-submit-button')))
        functions.click(submitButton)

        # Check table generated
        roles_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-roles-table")))
        number_of_elements = len(roles_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(roles_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

        ## Not In ##
        self.driver.get("http://localhost:5000/users-management/uboa-nav")

        # Go to tab
        functions.goToTab(self.driver,"Roles")

        # Fill the email_like input
        input_element = self.driver.find_element_by_id("roles-emails-in-text")
        functions.click(input_element)

        input_element.send_keys("administrator@test.com")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("roles-emails-in-select"))
        options.select_by_visible_text("administrator@test.com")

        notInButton = self.driver.find_element_by_id("roles-emails-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        # end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'roles-submit-button')))
        functions.click(submitButton)

        # Check table generated
        roles_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-roles-table")))
        number_of_elements = len(roles_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(roles_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

    def test_roles_query_username_filter(self):

        data = {"operations": [{
            "mode": "insert",
            "users": [
                {
                    "email": "administrator@test.com",
                    "username": "administrator",
                    "password": password,
                    "roles": ["administrator"],
                    "group": "Deimos"
                },{
                    "email": "operator@test.com",
                    "username": "operator",
                    "password": password,
                    "roles": ["operator"],
                    "group": "Deimos"
                },
            ]
        }]}

        # Check data is correctly inserted
        self.engine_uboa.data = data
        assert uboa_engine.exit_codes["OK"]["status"] == self.engine_uboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5)

        ## Like ##
        self.driver.get("http://localhost:5000/users-management/uboa-nav")

        # Go to tab
        functions.goToTab(self.driver,"Roles")

        # Fill the username_like input
        input_element = self.driver.find_element_by_id("roles-username-text")
        input_element.send_keys("administrator")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'roles-submit-button')))
        functions.click(submitButton)

        # Check table generated
        roles_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-roles-table")))
        number_of_elements = len(roles_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(roles_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not Like ##
        self.driver.get("http://localhost:5000/users-management/uboa-nav")

        # Go to tab
        functions.goToTab(self.driver,"Roles")

        # Fill the username_like input
        input_element = self.driver.find_element_by_id("roles-username-text")
        input_element.send_keys("administrator")

        menu = Select(self.driver.find_element_by_id("roles-username-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'roles-submit-button')))
        functions.click(submitButton)

        # Check table generated
        roles_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-roles-table")))
        number_of_elements = len(roles_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(roles_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

        ## In ##
        self.driver.get("http://localhost:5000/users-management/uboa-nav")

        # Go to tab
        functions.goToTab(self.driver,"Roles")

        # Fill the username_like input
        input_element = self.driver.find_element_by_id("roles-usernames-in-text")
        functions.click(input_element)

        input_element.send_keys("operator")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("roles-usernames-in-select"))
        options.select_by_visible_text("operator")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'roles-submit-button')))
        functions.click(submitButton)

        # Check table generated
        roles_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-roles-table")))
        number_of_elements = len(roles_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(roles_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

        ## Not In ##
        self.driver.get("http://localhost:5000/users-management/uboa-nav")

        # Go to tab
        functions.goToTab(self.driver,"Roles")

        # Fill the username_like input
        input_element = self.driver.find_element_by_id("roles-usernames-in-text")
        functions.click(input_element)

        input_element.send_keys("administrator")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("roles-usernames-in-select"))
        options.select_by_visible_text("administrator")

        notInButton = self.driver.find_element_by_id("roles-usernames-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        # end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'roles-submit-button')))
        functions.click(submitButton)

        # Check table generated
        roles_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-roles-table")))
        number_of_elements = len(roles_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(roles_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1
    
    def test_roles_query_group_filter(self):

        data = {"operations": [{
            "mode": "insert",
            "users": [
                {
                    "email": "administrator@test.com",
                    "username": "administrator",
                    "password": password,
                    "roles": ["administrator"],
                    "group": "Deimos"
                },{
                    "email": "operator@test.com",
                    "username": "operator",
                    "password": password,
                    "roles": ["operator"],
                    "group": "ESA"
                },
            ]
        }]}

        # Check data is correctly inserted
        self.engine_uboa.data = data
        assert uboa_engine.exit_codes["OK"]["status"] == self.engine_uboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5)

        ## Like ##
        self.driver.get("http://localhost:5000/users-management/uboa-nav")

        # Go to tab
        functions.goToTab(self.driver,"Roles")

        # Fill the group_like input
        input_element = self.driver.find_element_by_id("roles-group-text")
        input_element.send_keys("Deimos")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'roles-submit-button')))
        functions.click(submitButton)

        # Check table generated
        roles_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-roles-table")))
        number_of_elements = len(roles_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(roles_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not Like ##
        self.driver.get("http://localhost:5000/users-management/uboa-nav")

        # Go to tab
        functions.goToTab(self.driver,"Roles")

        # Fill the group_like input
        input_element = self.driver.find_element_by_id("roles-group-text")
        input_element.send_keys("Deimos")

        menu = Select(self.driver.find_element_by_id("roles-group-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'roles-submit-button')))
        functions.click(submitButton)

        # Check table generated
        roles_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-roles-table")))
        number_of_elements = len(roles_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(roles_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

        ## In ##
        self.driver.get("http://localhost:5000/users-management/uboa-nav")

        # Go to tab
        functions.goToTab(self.driver,"Roles")

        # Fill the group_like input
        input_element = self.driver.find_element_by_id("roles-groups-in-text")
        functions.click(input_element)

        input_element.send_keys("ESA")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("roles-groups-in-select"))
        options.select_by_visible_text("ESA")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'roles-submit-button')))
        functions.click(submitButton)

        # Check table generated
        roles_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-roles-table")))
        number_of_elements = len(roles_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(roles_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

        ## Not In ##
        self.driver.get("http://localhost:5000/users-management/uboa-nav")

        # Go to tab
        functions.goToTab(self.driver,"Roles")

        # Fill the group_like input
        input_element = self.driver.find_element_by_id("roles-groups-in-text")
        functions.click(input_element)

        input_element.send_keys("Deimos")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("roles-groups-in-select"))
        options.select_by_visible_text("Deimos")

        notInButton = self.driver.find_element_by_id("roles-groups-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        # end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'roles-submit-button')))
        functions.click(submitButton)

        # Check table generated
        roles_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-roles-table")))
        number_of_elements = len(roles_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(roles_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1
    
    def test_roles_query_role_filter(self):

        data = {"operations": [{
            "mode": "insert",
            "users": [
                {
                    "email": "administrator@test.com",
                    "username": "administrator",
                    "password": password,
                    "roles": ["administrator"],
                    "group": "Deimos"
                },{
                    "email": "operator@test.com",
                    "username": "operator",
                    "password": password,
                    "roles": ["operator"],
                    "group": "Deimos"
                },
            ]
        }]}

        # Check data is correctly inserted
        self.engine_uboa.data = data
        assert uboa_engine.exit_codes["OK"]["status"] == self.engine_uboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5)

        ## Like ##
        self.driver.get("http://localhost:5000/users-management/uboa-nav")

        # Go to tab
        functions.goToTab(self.driver,"Roles")

        # Fill the role_like input
        input_element = self.driver.find_element_by_id("roles-role-text")
        input_element.send_keys("administrator")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'roles-submit-button')))
        functions.click(submitButton)

        # Check table generated
        roles_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-roles-table")))
        number_of_elements = len(roles_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(roles_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not Like ##
        self.driver.get("http://localhost:5000/users-management/uboa-nav")

        # Go to tab
        functions.goToTab(self.driver,"Roles")

        # Fill the role_like input
        input_element = self.driver.find_element_by_id("roles-role-text")
        input_element.send_keys("administrator")

        menu = Select(self.driver.find_element_by_id("roles-role-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'roles-submit-button')))
        functions.click(submitButton)

        # Check table generated
        roles_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-roles-table")))
        number_of_elements = len(roles_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(roles_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

        ## In ##
        self.driver.get("http://localhost:5000/users-management/uboa-nav")

        # Go to tab
        functions.goToTab(self.driver,"Roles")

        # Fill the role_like input
        input_element = self.driver.find_element_by_id("roles-roles-in-text")
        functions.click(input_element)

        input_element.send_keys("operator")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("roles-roles-in-select"))
        options.select_by_visible_text("operator")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'roles-submit-button')))
        functions.click(submitButton)

        # Check table generated
        roles_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-roles-table")))
        number_of_elements = len(roles_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(roles_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

        ## Not In ##
        self.driver.get("http://localhost:5000/users-management/uboa-nav")

        # Go to tab
        functions.goToTab(self.driver,"Roles")

        # Fill the role_like input
        input_element = self.driver.find_element_by_id("roles-roles-in-text")
        functions.click(input_element)

        input_element.send_keys("administrator")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("roles-roles-in-select"))
        options.select_by_visible_text("administrator")

        notInButton = self.driver.find_element_by_id("roles-roles-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        # end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'roles-submit-button')))
        functions.click(submitButton)

        # Check table generated
        roles_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-roles-table")))
        number_of_elements = len(roles_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(roles_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

    def test_roles_query_active(self):

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


        # Check data is correctly inserted
        self.engine_uboa.data = data
        assert uboa_engine.exit_codes["OK"]["status"] == self.engine_uboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/users-management/uboa-nav")

        # Go to tab
        functions.goToTab(self.driver,"Roles")

        options = Select(self.driver.find_element_by_id("roles-active"))
        options.select_by_visible_text("")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'roles-submit-button')))
        functions.click(submitButton)

        # Check table generated
        roles_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-roles-table")))
        number_of_elements = len(roles_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(roles_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        # true option
        self.driver.get("http://localhost:5000/users-management/uboa-nav")

        # Go to tab
        functions.goToTab(self.driver,"Roles")

        options = Select(self.driver.find_element_by_id("roles-active"))
        options.select_by_visible_text("true")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'roles-submit-button')))
        functions.click(submitButton)

        # Check table generated
        roles_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-roles-table")))
        number_of_elements = len(roles_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(roles_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False
        
        # false option
        self.driver.get("http://localhost:5000/users-management/uboa-nav")

        # Go to tab
        functions.goToTab(self.driver,"Roles")

        options = Select(self.driver.find_element_by_id("roles-active"))
        options.select_by_visible_text("false")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'roles-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"roles-nav-no-data")))

        assert no_data