"""
Automated tests for the dim_signatures tab

Written by DEIMOS Space S.L. (femd)

module vboa
"""
import os
import sys
import unittest
import time
import subprocess
import datetime
import re
import tests.selenium.functions as functions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains,TouchActions
from selenium.webdriver.common.keys import Keys

# Import engine of the DDBB
import eboa.engine.engine as eboa_engine
from eboa.engine.engine import Engine
from eboa.engine.query import Query
from eboa.datamodel.base import Session, engine, Base
from eboa.engine.errors import UndefinedEventLink, DuplicatedEventLinkRef, WrongPeriod, SourceAlreadyIngested, WrongValue, OddNumberOfCoordinates, EboaResourcesPathNotAvailable, WrongGeometry

# Import datamodel
from eboa.datamodel.dim_signatures import DimSignature
from eboa.datamodel.alerts import Alert
from eboa.datamodel.events import Event, EventLink, EventKey, EventText, EventDouble, EventObject, EventGeometry, EventBoolean, EventTimestamp
from eboa.datamodel.gauges import Gauge
from eboa.datamodel.sources import Source, SourceStatus
from eboa.datamodel.explicit_refs import ExplicitRef, ExplicitRefGrp, ExplicitRefLink
from eboa.datamodel.annotations import Annotation, AnnotationCnf, AnnotationText, AnnotationDouble, AnnotationObject, AnnotationGeometry, AnnotationBoolean, AnnotationTimestamp


class TestDimSignaturesTab(unittest.TestCase):
    def setUp(self):
        # Create the engine to manage the data
        self.engine_eboa = Engine()
        self.query_eboa = Query()

        # Create session to connect to the database
        self.session = Session()

        # Clear all tables before executing the test
        self.query_eboa.clear_db()

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')

        # Kill webserver
        subprocess.call(["pkill", "chrome"])

        # Create a new instance of the Chrome driver
        self.driver = webdriver.Chrome(options=options)

    def tearDown(self):
        # Close connections to the DDBB
        self.engine_eboa.close_session()
        self.query_eboa.close_session()
        self.session.close()
        self.driver.quit()

    def test_dim_signatures_query_no_filter(self):

        # Insert data
        data = {"operations": [{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE_1",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_1.xml",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"}
            },{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE_2",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_2.xml",
                           "generation_time": "2018-07-05T14:14:14",
                           "validity_start": "2018-06-05T14:14:14",
                           "validity_stop": "2018-06-06T11:57:17"}
            }]
        }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,30);

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"DIM Signatures")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'dim-signatures-submit-button')))
        submitButton.click()

        # Check table generated
        dim_signatures_table = wait.until(EC.visibility_of_element_located((By.ID,"dim-signatures-table")))
        number_of_elements = len(dim_signatures_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        # Check dim_signature
        name = dim_signatures_table.find_elements_by_xpath("tbody/tr[1]/td[1]")

        # Check uuid
        uuid = dim_signatures_table.find_elements_by_xpath("tbody/tr[1]/td[5]")

        assert re.match("........-....-....-....-............", uuid[0].text)

    def test_dim_signatures_query_dim_signature_filter(self):

        # Insert data
        data = {"operations": [{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE_1",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_1.xml",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"}
            },{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE_2",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_2.xml",
                           "generation_time": "2018-07-05T14:14:14",
                           "validity_start": "2018-06-05T14:14:14",
                           "validity_stop": "2018-06-06T11:57:17"}
            },{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE_3",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_3.xml",
                           "generation_time": "2018-07-05T02:07:13",
                           "validity_start": "2018-06-05T03:09:33",
                           "validity_stop": "2018-06-05T08:17:46"}
            }]
        }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,30);

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"DIM Signatures")

        # Fill the dim_signature_like input
        inputElement = self.driver.find_element_by_id("dim-signatures-dim-signature-like-text")
        inputElement.send_keys("DIM_SIGNATURE_2")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'dim-signatures-submit-button')))
        submitButton.click()

        # Check table generated
        dim_signatures_table = wait.until(EC.visibility_of_element_located((By.ID,"dim-signatures-table")))
        number_of_elements = len(dim_signatures_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(dim_signatures_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"DIM Signatures")

        # Fill the dim_signature_like input
        inputElement = self.driver.find_element_by_id("dim-signatures-dim-signature-like-text")
        inputElement.send_keys("DIM_SIGNATURE_2")

        notLikeButton = self.driver.find_element_by_id("dim-signatures-dim-signature-like-checkbox")
        if not notLikeButton.find_element_by_xpath("input").is_selected():
            notLikeButton.click()
        #end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'dim-signatures-submit-button')))
        submitButton.click()

        # Check table generated
        dim_signatures_table = wait.until(EC.visibility_of_element_located((By.ID,"dim-signatures-table")))
        number_of_elements = len(dim_signatures_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"DIM Signatures")

        # Fill the dim_signature_in input
        inputElement = self.driver.find_element_by_id("dim-signatures-dim-signature-in-text").find_element_by_xpath("../div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("DIM_SIGNATURE_1")
        inputElement.send_keys(Keys.RETURN)
        inputElement.click()
        inputElement.send_keys("DIM_SIGNATURE_3")
        inputElement.send_keys(Keys.RETURN)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'dim-signatures-submit-button')))
        submitButton.click()

        # Check table generated
        dim_signatures_table = wait.until(EC.visibility_of_element_located((By.ID,"dim-signatures-table")))
        number_of_elements = len(dim_signatures_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"DIM Signatures")

        # Fill the dim_signature_in input
        inputElement = self.driver.find_element_by_id("dim-signatures-dim-signature-in-text").find_element_by_xpath("../div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("DIM_SIGNATURE_2")
        inputElement.send_keys(Keys.RETURN)

        notInButton = self.driver.find_element_by_id("dim-signatures-dim-signature-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            notInButton.click()
        #end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'dim-signatures-submit-button')))
        submitButton.click()

        # Check table generate
        dim_signatures_table = wait.until(EC.visibility_of_element_located((By.ID,"dim-signatures-table")))
        number_of_elements = len(dim_signatures_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(dim_signatures_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2
