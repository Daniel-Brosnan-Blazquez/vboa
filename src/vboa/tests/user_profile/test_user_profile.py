"""
Automated tests for the user profile view

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

class TestUserProfile(unittest.TestCase):

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
    
    def test_user_profile_info(self):

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
        
        self.driver.get("http://localhost:5000/login")
        
        functions.login(self.driver, "administrator", "password")

        self.driver.get("http://localhost:5000/user-profile/?user=administrator")

        email_expected = "administrator@test.com"
        username_expected= "administrator"
        group_expected= "Deimos"
        roles_expected= "administrator"
        
        assert email_expected == self.driver.find_element_by_id("email").text
        assert username_expected == self.driver.find_element_by_id("username").text
        assert group_expected == self.driver.find_element_by_id("group").text
        assert roles_expected == self.driver.find_element_by_id("roles").text

    def test_change_password(self):

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
        
        self.driver.get("http://localhost:5000/login")
        
        functions.login(self.driver, "administrator", "password")

        self.driver.get("http://localhost:5000/user-profile/?user=administrator")

        self.driver.find_element_by_id("user-profile-change-password-submit-button").click()

        wait.until(EC.text_to_be_present_in_element((By.TAG_NAME,"h2"),"Please, add new password"))

        # Fill password
        input_element = self.driver.find_element_by_xpath("//*[@id='boa-body']/section/div/div[2]/div/div/form/div[2]/input")
        input_element.send_keys("password")

        # Fill the new password
        input_element = self.driver.find_element_by_xpath("//*[@id='boa-body']/section/div/div[2]/div/div/form/div[3]/input")
        input_element.send_keys("newpassword")

        # Fill the confirm new password
        input_element = self.driver.find_element_by_xpath("//*[@id='boa-body']/section/div/div[2]/div/div/form/div[4]/input")
        input_element.send_keys("newpassword")
        
        confirm_button = self.driver.find_elements_by_xpath("//*[contains(text(), 'Confirm')]")
        functions.click(confirm_button[0])
        
        # Logout
        self.driver.get("http://localhost:5000/logout")
        
        # Login with the new password
        self.driver.get("http://localhost:5000/login") 
        functions.login(self.driver, "administrator", "newpassword")