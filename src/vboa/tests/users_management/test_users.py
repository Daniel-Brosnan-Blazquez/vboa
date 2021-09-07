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

class TestUsersTab(unittest.TestCase):

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
    
    def test_users_no_data(self):

        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/users-management/uboa-nav")

        # Go to tab
        functions.goToTab(self.driver,"Users")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'users-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"users-nav-no-data")))

        assert no_data

    def test_users_query_no_filter(self):

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
        
        # Used port 5002 to test and make login
        self.driver.get("http://localhost:5002/")
        
        functions.login(self.driver, "administrator", "password")

        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5002/users-management/uboa-nav")

        # Go to tab
        functions.goToTab(self.driver,"Users")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'users-submit-button')))
        functions.click(submitButton)

        # Check table generated
        users_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-users-table")))
        number_of_elements = len(users_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        users = self.query_uboa.get_users()

        # Check email
        email = users_table.find_elements_by_xpath("tbody/tr[1]/td[3]")

        assert email[0].text == "administrator@test.com"

        # Check username
        username = users_table.find_elements_by_xpath("tbody/tr[1]/td[4]")

        assert username[0].text == "administrator"

        # Check group
        group = users_table.find_elements_by_xpath("tbody/tr[1]/td[5]")

        assert group[0].text == "Deimos"

        # Check active
        active = users_table.find_elements_by_xpath("tbody/tr[1]/td[6]")

        assert active[0].text == "True"

        # Check previous_login_at
        previous_login_at = users_table.find_elements_by_xpath("tbody/tr[1]/td[7]")

        assert previous_login_at[0].text == users[0].last_login_at.isoformat()

        # Check last_login_at
        last_login_at = users_table.find_elements_by_xpath("tbody/tr[1]/td[8]")

        assert last_login_at[0].text == users[0].current_login_at.isoformat()

        # Check previous_login_ip
        previous_login_ip = users_table.find_elements_by_xpath("tbody/tr[1]/td[9]")

        assert previous_login_ip[0].text == "Never login"
        
        # Check last_login_ip
        last_login_ip = users_table.find_elements_by_xpath("tbody/tr[1]/td[10]")

        assert last_login_ip[0].text == users[0].current_login_ip

        # Check login_count
        login_count = users_table.find_elements_by_xpath("tbody/tr[1]/td[11]")

        assert login_count[0].text == str(users[0].login_count)

        # Check user_uuid
        user_uuid = users_table.find_elements_by_xpath("tbody/tr[1]/td[12]")

        assert user_uuid[0].text == str(users[0].user_uuid)

    def test_users_query_email_filter(self):

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
        functions.goToTab(self.driver,"Users")

        # Fill the email_like input
        input_element = self.driver.find_element_by_id("users-email-text")
        input_element.send_keys("administrator@test.com")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'users-submit-button')))
        functions.click(submitButton)

        # Check table generated
        users_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-users-table")))
        number_of_elements = len(users_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(users_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not Like ##
        self.driver.get("http://localhost:5000/users-management/uboa-nav")

        # Go to tab
        functions.goToTab(self.driver,"Users")

        # Fill the email_like input
        input_element = self.driver.find_element_by_id("users-email-text")
        input_element.send_keys("administrator@test.com")

        menu = Select(self.driver.find_element_by_id("users-email-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'users-submit-button')))
        functions.click(submitButton)

        # Check table generated
        users_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-users-table")))
        number_of_elements = len(users_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(users_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

        ## In ##
        self.driver.get("http://localhost:5000/users-management/uboa-nav")

        # Go to tab
        functions.goToTab(self.driver,"Users")

        # Fill the email_like input
        input_element = self.driver.find_element_by_id("users-emails-in-text")
        functions.click(input_element)

        input_element.send_keys("operator@test.com")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("users-emails-in-select"))
        options.select_by_visible_text("operator@test.com")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'users-submit-button')))
        functions.click(submitButton)

        # Check table generated
        users_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-users-table")))
        number_of_elements = len(users_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(users_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

        ## Not In ##
        self.driver.get("http://localhost:5000/users-management/uboa-nav")

        # Go to tab
        functions.goToTab(self.driver,"Users")

        # Fill the email_like input
        input_element = self.driver.find_element_by_id("users-emails-in-text")
        functions.click(input_element)

        input_element.send_keys("administrator@test.com")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("users-emails-in-select"))
        options.select_by_visible_text("administrator@test.com")

        notInButton = self.driver.find_element_by_id("users-emails-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        # end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'users-submit-button')))
        functions.click(submitButton)

        # Check table generated
        users_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-users-table")))
        number_of_elements = len(users_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(users_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

    def test_users_query_username_filter(self):

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
        functions.goToTab(self.driver,"Users")

        # Fill the username_like input
        input_element = self.driver.find_element_by_id("users-username-text")
        input_element.send_keys("administrator")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'users-submit-button')))
        functions.click(submitButton)

        # Check table generated
        users_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-users-table")))
        number_of_elements = len(users_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(users_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not Like ##
        self.driver.get("http://localhost:5000/users-management/uboa-nav")

        # Go to tab
        functions.goToTab(self.driver,"Users")

        # Fill the username_like input
        input_element = self.driver.find_element_by_id("users-username-text")
        input_element.send_keys("administrator")

        menu = Select(self.driver.find_element_by_id("users-username-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'users-submit-button')))
        functions.click(submitButton)

        # Check table generated
        users_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-users-table")))
        number_of_elements = len(users_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(users_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

        ## In ##
        self.driver.get("http://localhost:5000/users-management/uboa-nav")

        # Go to tab
        functions.goToTab(self.driver,"Users")

        # Fill the username_like input
        input_element = self.driver.find_element_by_id("users-usernames-in-text")
        functions.click(input_element)

        input_element.send_keys("operator")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("users-usernames-in-select"))
        options.select_by_visible_text("operator")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'users-submit-button')))
        functions.click(submitButton)

        # Check table generated
        users_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-users-table")))
        number_of_elements = len(users_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(users_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

        ## Not In ##
        self.driver.get("http://localhost:5000/users-management/uboa-nav")

        # Go to tab
        functions.goToTab(self.driver,"Users")

        # Fill the username_like input
        input_element = self.driver.find_element_by_id("users-usernames-in-text")
        functions.click(input_element)

        input_element.send_keys("administrator")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("users-usernames-in-select"))
        options.select_by_visible_text("administrator")

        notInButton = self.driver.find_element_by_id("users-usernames-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        # end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'users-submit-button')))
        functions.click(submitButton)

        # Check table generated
        users_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-users-table")))
        number_of_elements = len(users_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(users_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1
    
    def test_users_query_group_filter(self):

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
        functions.goToTab(self.driver,"Users")

        # Fill the group_like input
        input_element = self.driver.find_element_by_id("users-group-text")
        input_element.send_keys("Deimos")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'users-submit-button')))
        functions.click(submitButton)

        # Check table generated
        users_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-users-table")))
        number_of_elements = len(users_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(users_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not Like ##
        self.driver.get("http://localhost:5000/users-management/uboa-nav")

        # Go to tab
        functions.goToTab(self.driver,"Users")

        # Fill the group_like input
        input_element = self.driver.find_element_by_id("users-group-text")
        input_element.send_keys("Deimos")

        menu = Select(self.driver.find_element_by_id("users-group-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'users-submit-button')))
        functions.click(submitButton)

        # Check table generated
        users_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-users-table")))
        number_of_elements = len(users_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(users_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

        ## In ##
        self.driver.get("http://localhost:5000/users-management/uboa-nav")

        # Go to tab
        functions.goToTab(self.driver,"Users")

        # Fill the group_like input
        input_element = self.driver.find_element_by_id("users-groups-in-text")
        functions.click(input_element)

        input_element.send_keys("ESA")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("users-groups-in-select"))
        options.select_by_visible_text("ESA")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'users-submit-button')))
        functions.click(submitButton)

        # Check table generated
        users_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-users-table")))
        number_of_elements = len(users_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(users_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

        ## Not In ##
        self.driver.get("http://localhost:5000/users-management/uboa-nav")

        # Go to tab
        functions.goToTab(self.driver,"Users")

        # Fill the group_like input
        input_element = self.driver.find_element_by_id("users-groups-in-text")
        functions.click(input_element)

        input_element.send_keys("Deimos")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("users-groups-in-select"))
        options.select_by_visible_text("Deimos")

        notInButton = self.driver.find_element_by_id("users-groups-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        # end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'users-submit-button')))
        functions.click(submitButton)

        # Check table generated
        users_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-users-table")))
        number_of_elements = len(users_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(users_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1
    
    def test_users_query_role_filter(self):

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
        functions.goToTab(self.driver,"Users")

        # Fill the role_like input
        input_element = self.driver.find_element_by_id("users-role-text")
        input_element.send_keys("administrator")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'users-submit-button')))
        functions.click(submitButton)

        # Check table generated
        users_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-users-table")))
        number_of_elements = len(users_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(users_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not Like ##
        self.driver.get("http://localhost:5000/users-management/uboa-nav")

        # Go to tab
        functions.goToTab(self.driver,"Users")

        # Fill the role_like input
        input_element = self.driver.find_element_by_id("users-role-text")
        input_element.send_keys("administrator")

        menu = Select(self.driver.find_element_by_id("users-role-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'users-submit-button')))
        functions.click(submitButton)

        # Check table generated
        users_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-users-table")))
        number_of_elements = len(users_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(users_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

        ## In ##
        self.driver.get("http://localhost:5000/users-management/uboa-nav")

        # Go to tab
        functions.goToTab(self.driver,"Users")

        # Fill the role_like input
        input_element = self.driver.find_element_by_id("users-roles-in-text")
        functions.click(input_element)

        input_element.send_keys("operator")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("users-roles-in-select"))
        options.select_by_visible_text("operator")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'users-submit-button')))
        functions.click(submitButton)

        # Check table generated
        users_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-users-table")))
        number_of_elements = len(users_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(users_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

        ## Not In ##
        self.driver.get("http://localhost:5000/users-management/uboa-nav")

        # Go to tab
        functions.goToTab(self.driver,"Users")

        # Fill the role_like input
        input_element = self.driver.find_element_by_id("users-roles-in-text")
        functions.click(input_element)

        input_element.send_keys("administrator")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("users-roles-in-select"))
        options.select_by_visible_text("administrator")

        notInButton = self.driver.find_element_by_id("users-roles-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        # end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'users-submit-button')))
        functions.click(submitButton)

        # Check table generated
        users_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-users-table")))
        number_of_elements = len(users_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(users_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

    def test_users_query_active(self):

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
        functions.goToTab(self.driver,"Users")

        options = Select(self.driver.find_element_by_id("users-active"))
        options.select_by_visible_text("")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'users-submit-button')))
        functions.click(submitButton)

        # Check table generated
        users_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-users-table")))
        number_of_elements = len(users_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(users_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        # true option
        self.driver.get("http://localhost:5000/users-management/uboa-nav")

        # Go to tab
        functions.goToTab(self.driver,"Users")

        options = Select(self.driver.find_element_by_id("users-active"))
        options.select_by_visible_text("true")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'users-submit-button')))
        functions.click(submitButton)

        # Check table generated
        users_table = wait.until(EC.visibility_of_element_located((By.ID,"uboa-nav-users-table")))
        number_of_elements = len(users_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(users_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False
        
        # false option
        self.driver.get("http://localhost:5000/users-management/uboa-nav")

        # Go to tab
        functions.goToTab(self.driver,"Users")

        options = Select(self.driver.find_element_by_id("users-active"))
        options.select_by_visible_text("false")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'users-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"users-nav-no-data")))

        assert no_data