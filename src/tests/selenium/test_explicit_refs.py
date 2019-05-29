"""
Automated tests for the explicit_refs tab

Written by DEIMOS Space S.L. (femd)

module vboa
"""
import os
import sys
import unittest
import time
import subprocess
import datetime
import tests.selenium.functions as functions
import re
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
from eboa.debugging import debug

# Import datamodel
from eboa.datamodel.dim_signatures import DimSignature
from eboa.datamodel.alerts import Alert
from eboa.datamodel.events import Event, EventLink, EventKey, EventText, EventDouble, EventObject, EventGeometry, EventBoolean, EventTimestamp
from eboa.datamodel.gauges import Gauge
from eboa.datamodel.sources import Source, SourceStatus
from eboa.datamodel.explicit_refs import ExplicitRef, ExplicitRefGrp, ExplicitRefLink
from eboa.datamodel.annotations import Annotation, AnnotationCnf, AnnotationText, AnnotationDouble, AnnotationObject, AnnotationGeometry, AnnotationBoolean, AnnotationTimestamp


class TestExplicitReferencesTab(unittest.TestCase):
    @debug
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
        options.add_argument('window-size=1920,1080')
        
        # Create a new instance of the Chrome driver
        self.driver = webdriver.Chrome(options=options)

    @debug
    def tearDown(self):
        # Close connections to the DDBB
        self.engine_eboa.close_session()
        self.query_eboa.close_session()
        self.session.close()
        self.driver.quit()
        
    @debug
    def test_explicit_refs_query_no_filter(self):

        # Insert data
        data = {"operations": [{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source.xml",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "explicit_references": [{
                "name": "EXPLICIT_REFERENCE",
                "links": [{
                    "back_ref": "BACK_REF_LINK",
                    "link": "EXPLICIT_REFERENCE_2",
                    "name": "EXPLICIT_REFERENCE_LINK"
                }],
                "group": "EXPLICIT_REFERENCE_GROUP"
            }],
            "events": [{
                "explicit_reference": "EXPLICIT_REFERENCE",
                "gauge": {"name": "GAUGE_NAME",
                          "system": "GAUGE_SYSTEM",
                          "insertion_type": "SIMPLE_UPDATE"},
                "start": "2018-06-05T04:07:03",
                "stop": "2018-06-05T06:07:36"
                },{
                "explicit_reference": "EXPLICIT_REFERENCE_2",
                "gauge": {"name": "GAUGE_NAME_2",
                          "system": "GAUGE_SYSTEM_2",
                          "insertion_type": "SIMPLE_UPDATE"},
                "start": "2018-06-05T04:07:12",
                "stop": "2018-06-05T06:07:24"
                }]
            }]}

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5);

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        # Check explicit reference
        explicit_reference_1 = explicit_ref_table.find_elements_by_xpath("tbody/tr[1]/td[1]")

        assert explicit_reference_1[0].text == "EXPLICIT_REFERENCE"

        # Check group
        group = explicit_ref_table.find_elements_by_xpath("tbody/tr[1]/td[2]")

        assert group[0].text == "EXPLICIT_REFERENCE_GROUP"

        # Check group
        ingestion_time = explicit_ref_table.find_elements_by_xpath("tbody/tr[1]/td[5]")

        assert re.match("....-..-..T..:..:...*", ingestion_time[0].text)

        # Check uuid
        uuid = explicit_ref_table.find_elements_by_xpath("tbody/tr[1]/td[7]")

        assert re.match("........-....-....-....-............", uuid[0].text)
        
    @debug
    def test_explicit_refs_query_explicit_ref_filter(self):

        # Insert data
        data = {"operations": [{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_1.xml",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "events": [{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT_1",
                "gauge": {"name": "GAUGE_NAME",
                          "system": "GAUGE_SYSTEM",
                          "insertion_type": "SIMPLE_UPDATE"},
                "start": "2018-06-05T04:07:03",
                "stop": "2018-06-05T06:07:36"
                },{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT_2",
                "gauge": {"name": "GAUGE_NAME_2",
                          "system": "GAUGE_SYSTEM_2",
                          "insertion_type": "SIMPLE_UPDATE"},
                "start": "2018-06-05T04:07:12",
                "stop": "2018-06-05T06:07:24"
                }]
            },{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_2.xml",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "events": [{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT_3",
                "gauge": {"name": "GAUGE_NAME_3",
                          "system": "GAUGE_SYSTEM_3",
                          "insertion_type": "SIMPLE_UPDATE"},
                "start": "2018-06-05T04:07:05",
                "stop": "2018-06-05T06:07:31"
                }]
            }
        ]}

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5);

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the explicit_ref_like input
        input_element = self.driver.find_element_by_id("er-like-input-ers")
        input_element.send_keys("EXPLICIT_REFERENCE_EVENT_2")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the explicit_ref_like input
        input_element = self.driver.find_element_by_id("er-like-input-ers")
        input_element.send_keys("EXPLICIT_REFERENCE_EVENT_2")

        not_like_button = self.driver.find_element_by_id("er-like-label-ers")
        not_like_button.click()

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the explicit_ref_in input
        select_element = self.driver.find_element_by_id("er-in-select-ers")
        input_element = select_element.find_element_by_xpath("../div/ul/li/input")
        input_element.click()
        input_element.send_keys("EXPLICIT_REFERENCE_EVENT_1")
        input_element.send_keys(Keys.RETURN)
        input_element.click()
        input_element.send_keys("EXPLICIT_REFERENCE_EVENT_3")
        input_element.send_keys(Keys.RETURN)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the explicit_ref_in input
        select_element = self.driver.find_element_by_id("er-in-select-ers")
        input_element = select_element.find_element_by_xpath("../div/ul/li/input")
        input_element.click()
        input_element.send_keys("EXPLICIT_REFERENCE_EVENT_2")
        input_element.send_keys(Keys.RETURN)

        not_in_button = self.driver.find_element_by_id("er-in-label-ers")
        not_in_button.click()

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generate
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

    def test_explicit_refs_query_group_filter(self):

        # Insert data
        data = {"operations": [{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_1.xml",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "explicit_references": [{
                "group": "EXPL_GROUP_1",
                "name": "EXPLICIT_REFERENCE_1",
                "links": [{"name": "LINK_NAME_1",
                       "link": "EXPLICIT_REFERENCE_LINK_1"}]
                },{
                "group": "EXPL_GROUP_2",
                "name": "EXPLICIT_REFERENCE_2",
                "links": [{"name": "LINK_NAME_2",
                       "link": "EXPLICIT_REFERENCE_LINK_2"}]
                }]
            },{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_2.xml",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "explicit_references": [{
                "group": "EXPL_GROUP_1",
                "name": "EXPLICIT_REFERENCE_3",
                "links": [{"name": "LINK_NAME_3",
                       "link": "EXPLICIT_REFERENCE_LINK_3"}]
                }]
            }
        ]}

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5);

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the group_like input
        input_element = self.driver.find_element_by_id("er-group-like-input-ers")
        input_element.send_keys("EXPL_GROUP_2")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the group_like input
        input_element = self.driver.find_element_by_id("er-group-like-input-ers")
        input_element.send_keys("EXPL_GROUP_2")

        not_like_button = self.driver.find_element_by_id("er-group-like-label-ers")
        not_like_button.click()

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the group_in input
        select_element = self.driver.find_element_by_id("er-group-in-select-ers")
        input_element = select_element.find_element_by_xpath("../div/ul/li/input")
        input_element.click()
        input_element.send_keys("EXPL_GROUP_1")
        input_element.send_keys(Keys.RETURN)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the group_in input
        select_element = self.driver.find_element_by_id("er-group-in-select-ers")
        input_element = select_element.find_element_by_xpath("../div/ul/li/input")
        input_element.click()
        input_element.send_keys("EXPL_GROUP_2")
        input_element.send_keys(Keys.RETURN)

        not_in_button = self.driver.find_element_by_id("er-group-in-label-ers")
        not_in_button.click()

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generate
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

    # Not filtering
    def test_explicit_refs_query_source_filter(self):

        # Insert data
        data = {"operations": [{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_1.xml",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "explicit_references": [{
                "group": "EXPL_GROUP_1",
                "name": "EXPLICIT_REFERENCE_1"
                },{
                "group": "EXPL_GROUP_2",
                "name": "EXPLICIT_REFERENCE_2"
                }],
            "events": [{
                "explicit_reference": "EXPLICIT_REFERENCE_1",
                "gauge": {"name": "GAUGE_NAME_1",
                          "system": "GAUGE_SYSTEM_1",
                          "insertion_type": "SIMPLE_UPDATE"},
                "start": "2018-06-05T04:07:05",
                "stop": "2018-06-05T06:07:31"
                }]
            },{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_2.xml",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "explicit_references": [{
                "group": "EXPL_GROUP_1",
                "name": "EXPLICIT_REFERENCE_3"
                }]
            }
        ]}

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5);

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the source_like input
        input_element = self.driver.find_element_by_id("source-like-input-ers")
        input_element.send_keys("source_1.xml")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the source_like input
        input_element = self.driver.find_element_by_id("source-like-input-ers")
        input_element.send_keys("source_1.xml")

        not_like_button = self.driver.find_element_by_id("source-like-label-ers")
        not_like_button.click()

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-no-data")))
        
        assert no_data

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the source_in input
        select_element = self.driver.find_element_by_id("source-in-select-ers")
        input_element = select_element.find_element_by_xpath("../div/ul/li/input")
        input_element.click()
        input_element.send_keys("source_1.xml")
        input_element.send_keys(Keys.RETURN)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the source_in input
        select_element = self.driver.find_element_by_id("source-in-select-ers")
        input_element = select_element.find_element_by_xpath("../div/ul/li/input")
        input_element.click()
        input_element.send_keys("source_2.xml")
        input_element.send_keys(Keys.RETURN)

        not_in_button = self.driver.find_element_by_id("source-in-label-ers")
        not_in_button.click()

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generate
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

    def test_explicit_refs_query_key_filter(self):

        # Insert data
        data = {"operations": [{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_1.xml",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "events": [{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT_1",
                "gauge": {"name": "GAUGE_NAME_1",
                          "system": "GAUGE_SYSTEM_1",
                          "insertion_type": "EVENT_KEYS"},
                "start": "2018-06-05T04:07:03",
                "stop": "2018-06-05T06:07:36",
                "key": "EVENT_KEY_1"
                },{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT_2",
                "gauge": {"name": "GAUGE_NAME_2",
                          "system": "GAUGE_SYSTEM_2",
                          "insertion_type": "EVENT_KEYS"},
                "start": "2018-06-05T04:07:12",
                "stop": "2018-06-05T06:07:24",
                "key": "EVENT_KEY_2"
                }]
            },{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_2.xml",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "events": [{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT_3",
                "gauge": {"name": "GAUGE_NAME_2",
                          "system": "GAUGE_SYSTEM_2",
                          "insertion_type": "EVENT_KEYS"},
                "start": "2018-06-05T04:07:05",
                "stop": "2018-06-05T06:07:31",
                "key": "EVENT_KEY_3"
                }]
            }
        ]}

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5);

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the gauge_name_like input
        input_element = self.driver.find_element_by_id("key-like-input-ers")
        input_element.send_keys("EVENT_KEY_1")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the gauge_name_like input
        input_element = self.driver.find_element_by_id("key-like-input-ers")
        input_element.send_keys("EVENT_KEY_1")

        not_like_button = self.driver.find_element_by_id("key-like-label-ers")
        not_like_button.click()

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the gauge_name_in input
        select_element = self.driver.find_element_by_id("key-in-select-ers")
        input_element = select_element.find_element_by_xpath("../div/ul/li/input")
        input_element.click()
        input_element.send_keys("EVENT_KEY_2")
        input_element.send_keys(Keys.RETURN)
        input_element.click()
        input_element.send_keys("EVENT_KEY_3")
        input_element.send_keys(Keys.RETURN)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the gauge_name_in input
        select_element = self.driver.find_element_by_id("key-in-select-ers")
        input_element = select_element.find_element_by_xpath("../div/ul/li/input")
        input_element.click()
        input_element.send_keys("EVENT_KEY_1")
        input_element.send_keys(Keys.RETURN)

        not_in_button = self.driver.find_element_by_id("key-in-label-ers")
        not_in_button.click()

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generate
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

    def test_explicit_refs_query_gauge_name_filter(self):

        # Insert data
        data = {"operations": [{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_1.xml",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "events": [{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT_1",
                "gauge": {"name": "GAUGE_NAME_1",
                          "system": "GAUGE_SYSTEM_1",
                          "insertion_type": "EVENT_KEYS"},
                "start": "2018-06-05T04:07:03",
                "stop": "2018-06-05T06:07:36",
                "key": "EVENT_KEY"
                },{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT_2",
                "gauge": {"name": "GAUGE_NAME_2",
                          "system": "GAUGE_SYSTEM_2",
                          "insertion_type": "EVENT_KEYS"},
                "start": "2018-06-05T04:07:12",
                "stop": "2018-06-05T06:07:24",
                "key": "EVENT_KEY_2"
                }]
            },{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_2.xml",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "events": [{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT_3",
                "gauge": {"name": "GAUGE_NAME_2",
                          "system": "GAUGE_SYSTEM_2",
                          "insertion_type": "EVENT_KEYS"},
                "start": "2018-06-05T04:07:05",
                "stop": "2018-06-05T06:07:31",
                "key": "EVENT_KEY_3"
                }]
            }
        ]}

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5);

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the gauge_name_like input
        input_element = self.driver.find_element_by_id("gauge-name-like-input-ers")
        input_element.send_keys("GAUGE_NAME_1")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the gauge_name_like input
        input_element = self.driver.find_element_by_id("gauge-name-like-input-ers")
        input_element.send_keys("GAUGE_NAME_1")

        not_like_button = self.driver.find_element_by_id("gauge-name-like-label-ers")
        not_like_button.click()

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the gauge_name_in input
        select_element = self.driver.find_element_by_id("gauge-name-in-select-ers")
        input_element = select_element.find_element_by_xpath("../div/ul/li/input")
        input_element.click()
        input_element.send_keys("GAUGE_NAME_2")
        input_element.send_keys(Keys.RETURN)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the gauge_name_in input
        select_element = self.driver.find_element_by_id("gauge-name-in-select-ers")
        input_element = select_element.find_element_by_xpath("../div/ul/li/input")
        input_element.click()
        input_element.send_keys("GAUGE_NAME_1")
        input_element.send_keys(Keys.RETURN)

        not_in_button = self.driver.find_element_by_id("gauge-name-in-label-ers")
        not_in_button.click()

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generate
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

    def test_explicit_refs_query_gauge_system_filter(self):

        # Insert data
        data = {"operations": [{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_1.xml",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "events": [{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT",
                "gauge": {"name": "GAUGE_NAME_1",
                          "system": "GAUGE_SYSTEM_1",
                          "insertion_type": "EVENT_KEYS"},
                "start": "2018-06-05T04:07:03",
                "stop": "2018-06-05T06:07:36",
                "key": "EVENT_KEY"
                },{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT_2",
                "gauge": {"name": "GAUGE_NAME_2",
                          "system": "GAUGE_SYSTEM_2",
                          "insertion_type": "EVENT_KEYS"},
                "start": "2018-06-05T04:07:12",
                "stop": "2018-06-05T06:07:24",
                "key": "EVENT_KEY_2"
                }]
            },{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_2.xml",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "events": [{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT",
                "gauge": {"name": "GAUGE_NAME_2",
                          "system": "GAUGE_SYSTEM_2",
                          "insertion_type": "EVENT_KEYS"},
                "start": "2018-06-05T04:07:05",
                "stop": "2018-06-05T06:07:31",
                "key": "EVENT_KEY_3"
                }]
            }
        ]}

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5);

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the gauge_system_like input
        input_element = self.driver.find_element_by_id("gauge-system-like-input-ers")
        input_element.send_keys("GAUGE_SYSTEM_1")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the gauge_system_like input
        input_element = self.driver.find_element_by_id("gauge-system-like-input-ers")
        input_element.send_keys("GAUGE_SYSTEM_1")

        not_like_button = self.driver.find_element_by_id("gauge-system-like-label-ers")
        not_like_button.click()

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the gauge_system_in input
        select_element = self.driver.find_element_by_id("gauge-system-in-select-ers")
        input_element = select_element.find_element_by_xpath("../div/ul/li/input")
        input_element.click()
        input_element.send_keys("GAUGE_SYSTEM_2")
        input_element.send_keys(Keys.RETURN)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the gauge_system_in input
        select_element = self.driver.find_element_by_id("gauge-system-in-select-ers")
        input_element = select_element.find_element_by_xpath("../div/ul/li/input")
        input_element.click()
        input_element.send_keys("GAUGE_SYSTEM_1")
        input_element.send_keys(Keys.RETURN)

        not_in_button = self.driver.find_element_by_id("gauge-system-in-label-ers")
        not_in_button.click()

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generate
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

    def test_explicit_refs_query_events_value_text(self):

        # Insert data
        data = {"operations":[{
                        "mode": "insert",
                        "dim_signature": {"name": "dim_signature",
                                          "exec": "exec",
                                          "version": "1.0"},
                        "source": {"name": "source.xml",
                                   "generation_time": "2018-07-05T02:07:03",
                                   "validity_start": "2018-06-05T02:07:03",
                                   "validity_stop": "2018-06-05T08:07:36"},
                        "events": [{"gauge": {"name": "GAUGE_NAME",
                                              "system": "GAUGE_SYSTEM",
                                              "insertion_type": "SIMPLE_UPDATE"},
                                    "explicit_reference": "EXPLICIT_REFERENCE_1",
                                    "start": "2018-06-05T02:07:03",
                                    "stop": "2018-06-05T08:07:36",
                                    "values": [{"name": "VALUES",
                                               "type": "object",
                                               "values": [
                                                   {"type": "text",
                                                    "name": "textname_1",
                                                    "value": "textvalue_1"
                                                    }]
                                                }]
                                    },
                                    {"gauge": {"name": "GAUGE_NAME",
                                              "system": "GAUGE_SYSTEM",
                                              "insertion_type": "SIMPLE_UPDATE"},
                                    "explicit_reference": "EXPLICIT_REFERENCE_2",
                                    "start": "2018-06-05T02:07:03",
                                    "stop": "2018-06-05T08:07:36"}
                        ]
                    }]
                }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5);

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "events-ers", "text", "textname_1", "textvalue_1", True, "==", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "events-ers", "text", "textname_1", "textvalue_2", False, "==", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-no-data")))

        assert no_data
        
    def test_explicit_refs_query_events_value_timestamp(self):

        # Insert data
        data = {"operations":[{
                        "mode": "insert",
                        "dim_signature": {"name": "dim_signature",
                                          "exec": "exec",
                                          "version": "1.0"},
                        "source": {"name": "source.xml",
                                   "generation_time": "2018-07-05T02:07:03",
                                   "validity_start": "2018-06-05T02:07:03",
                                   "validity_stop": "2018-06-05T08:07:36"},
                        "events": [{"gauge": {"name": "GAUGE_NAME",
                                              "system": "GAUGE_SYSTEM",
                                              "insertion_type": "SIMPLE_UPDATE"},
                                    "explicit_reference": "EXPLICIT_REFERENCE_1",
                                    "start": "2018-06-05T02:07:03",
                                    "stop": "2018-06-05T08:07:36",
                                    "values": [{"name": "VALUES",
                                               "type": "object",
                                               "values": [
                                                   {"type": "timestamp",
                                                    "name": "timestamp_name_1",
                                                    "value": "2019-04-26T14:14:14"
                                                    }]
                                                }]
                        },
                                    {"gauge": {"name": "GAUGE_NAME",
                                              "system": "GAUGE_SYSTEM",
                                              "insertion_type": "SIMPLE_UPDATE"},
                                    "explicit_reference": "EXPLICIT_REFERENCE_2",
                                    "start": "2018-06-05T02:07:03",
                                    "stop": "2018-06-05T08:07:36"}]
                    }]}

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5);

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "events-ers", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", True, "==", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "events-ers", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", True, "==",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        no_data = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-no-data")))

        assert no_data

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "events-ers", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", True, ">", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        no_data = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "events-ers", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", True, ">", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "events-ers", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", True, ">", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        no_data = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-no-data")))

        assert no_data

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "events-ers", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", True, ">=", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "events-ers", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", True, ">=", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "events-ers", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", True, ">=",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        no_data = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-no-data")))

        assert no_data

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "events-ers", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", True, "<",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        no_data = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "events-ers", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", True, "<", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "events-ers", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", True, "<=", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "events-ers", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", True, "<=",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        no_data = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "events-ers", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", True, "<=", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "events-ers", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", True, "!=",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        no_data = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "events-ers", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", True, "!=", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

    def test_explicit_refs_query_events_value_double(self):

        # Insert data
        data = {"operations":[{
                        "mode": "insert",
                        "dim_signature": {"name": "dim_signature",
                                          "exec": "exec",
                                          "version": "1.0"},
                        "source": {"name": "source.xml",
                                   "generation_time": "2018-07-05T02:07:03",
                                   "validity_start": "2018-06-05T02:07:03",
                                   "validity_stop": "2018-06-05T08:07:36"},
                        "events": [{"gauge": {"name": "GAUGE_NAME",
                                              "system": "GAUGE_SYSTEM",
                                              "insertion_type": "SIMPLE_UPDATE"},
                                    "explicit_reference": "EXPLICIT_REFERENCE_1",
                                    "start": "2018-06-05T02:07:03",
                                    "stop": "2018-06-05T08:07:36",
                                    "values": [{"name": "VALUES",
                                               "type": "object",
                                               "values": [
                                                   {"type": "double",
                                                    "name": "double_name_1",
                                                    "value": "3.5"
                                                    }]
                                                }]
                        },
                                    {"gauge": {"name": "GAUGE_NAME",
                                              "system": "GAUGE_SYSTEM",
                                              "insertion_type": "SIMPLE_UPDATE"},
                                    "explicit_reference": "EXPLICIT_REFERENCE_2",
                                    "start": "2018-06-05T02:07:03",
                                    "stop": "2018-06-05T08:07:36"}]
                    }]
                }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5);

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "events-ers", "double", "double_name_1", "3.5", True, "==", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "events-ers", "double", "double_name_1", "3.5", False, "==",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        no_data = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-no-data")))

        assert no_data

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "events-ers", "double", "double_name_1", "3.5", True, ">",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        no_data = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "events-ers", "double", "double_name_1", "3.25", True, ">", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "events-ers", "double", "double_name_1", "3.75", True, ">",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        no_data = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-no-data")))

        assert no_data

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "events-ers", "double", "double_name_1", "3.5", True, ">=", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "events-ers", "double", "double_name_1", "3.25", True, ">=", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "events-ers", "double", "double_name_1", "3.75", True, ">=",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        no_data = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-no-data")))

        assert no_data

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "events-ers", "double", "double_name_1", "3.5", True, "<",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        no_data = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "events-ers", "double", "double_name_1", "3.25", True, "<",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        no_data = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "events-ers", "double", "double_name_1", "3.75", True, "<", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "events-ers", "double", "double_name_1", "3.5", True, "<=", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "events-ers", "double", "double_name_1", "3.25", True, "<=",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        no_data = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "events-ers", "double", "double_name_1", "3.75", True, "<=", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "events-ers", "double", "double_name_1", "3.5", True, "!=",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        no_data = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "events-ers", "double", "double_name_1", "3.25", True, "!=", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

    def test_explicit_refs_query_events_two_values(self):

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
                           "validity_stop": "2018-06-05T08:07:36"},
            "events": [{"gauge": {"name": "GAUGE_NAME",
                                  "system": "GAUGE_SYSTEM",
                                  "insertion_type": "SIMPLE_UPDATE"},
                        "explicit_reference": "EXPLICIT_REFERENCE_1",
                        "start": "2018-06-05T02:07:03",
                        "stop": "2018-06-05T08:07:36",
                        "values": [{"name": "VALUES",
                                   "type": "object",
                                   "values": [
                                       {"name": "text_name_1",
                                        "type": "text",
                                        "value": "text_value_1"
                                       }]
                                   }]
                    }]
            },{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE_2",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_2.xml",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "events": [{"gauge": {"name": "GAUGE_NAME",
                                  "system": "GAUGE_SYSTEM",
                                  "insertion_type": "SIMPLE_UPDATE"},
                        "explicit_reference": "EXPLICIT_REFERENCE_2",
                        "start": "2018-06-05T02:07:03",
                        "stop": "2018-06-05T08:07:36",
                        "values": [{"name": "VALUES",
                                   "type": "object",
                                   "values":  [
                                   {"name": "text_name_1",
                                    "type": "text",
                                    "value": "text_value_1"
                                       },
                                   {"name": "double_name_1",
                                    "type": "double",
                                    "value": "1.4"
                                       }]
                                   }]
                        },{"gauge": {"name": "GAUGE_NAME",
                                              "system": "GAUGE_SYSTEM",
                                              "insertion_type": "SIMPLE_UPDATE"},
                                    "explicit_reference": "EXPLICIT_REFERENCE_3",
                                    "start": "2018-06-05T02:07:03",
                                    "stop": "2018-06-05T08:07:36",
                                    "values": [{"name": "VALUES",
                                               "type": "object",
                                               "values": [
                                                   {"name": "text_name_3",
                                                    "type": "text",
                                                    "value": "text_value_2"
                                                   }]
                                               }]
                                    }]
            }]
        }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5);

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "events-ers", "text", "text_name_1", "text_value_1", True, "==", 1)
        self.driver.find_element_by_id("events-ers-add-value").click()
        functions.fill_value(self.driver, wait, "events-ers", "double", "double_name_1", "1.4", True, "==", 2)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

    def test_explicit_refs_query_annotation_name_filter(self):

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
                           "validity_stop": "2018-06-05T08:07:36"},
            "annotations": [{
                "explicit_reference" : "EXPLICIT_REFERENCE_1",
                "annotation_cnf": {
                    "name": "NAME_1",
                    "system": "SYSTEM"
                    },
                "values": [{
                    "name": "details",
                    "type": "object",
                    "values": []
                    }]
                }]
            },{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE_2",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_2.xml",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "annotations": [{
                "explicit_reference" : "EXPLICIT_REFERENCE_2",
                "annotation_cnf": {
                    "name": "NAME_1",
                    "system": "SYSTEM"
                    },
                "values": [{
                    "name": "details",
                    "type": "object",
                    "values": []
                    }]
                },{
                "explicit_reference" : "EXPLICIT_REFERENCE_2",
                "annotation_cnf": {
                    "name": "NAME_2",
                    "system": "SYSTEM"
                    },
                "values": [{
                    "name": "details",
                    "type": "object",
                    "values": []
                    }]
                }]
            }]
        }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5);

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the annotation_name_like input
        # Fill the gauge_name_like input
        input_element = self.driver.find_element_by_id("annotation-name-like-input-ers")
        input_element.send_keys("NAME_2")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the annotation_name_like input
        input_element = self.driver.find_element_by_id("annotation-name-like-input-ers")
        input_element.send_keys("NAME_2")

        not_like_button = self.driver.find_element_by_id("annotation-name-like-label-ers")
        not_like_button.click()

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the annotation_name_in input
        input_element = self.driver.find_element_by_id("/html/body/div[1]/div/div[2]/div/div/div[4]/div/div/div/div/div/form/div[4]/div[2]/div[2]/div[2]/div[1]/div/ul/li/input")
        input_element.click()
        input_element.send_keys("NAME_1")
        input_element.send_keys(Keys.RETURN)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(explicit_ref_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the annotation_name_in input
        input_element = self.driver.find_element_by_id("/html/body/div[1]/div/div[2]/div/div/div[4]/div/div/div/div/div/form/div[4]/div[2]/div[2]/div[2]/div[1]/div/ul/li/input")
        input_element.click()
        input_element.send_keys("NAME_2")
        input_element.send_keys(Keys.RETURN)

        not_in_button = self.driver.find_element_by_id("/html/body/div[1]/div/div[2]/div/div/div[4]/div/div/div/div/div/form/div[4]/div[2]/div[2]/div[2]/div[1]/label")
        not_in_button.click()

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generate
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(explicit_ref_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

    def test_explicit_refs_query_annotation_system_filter(self):

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
                           "validity_stop": "2018-06-05T08:07:36"},
            "annotations": [{
                "explicit_reference" : "EXPLICIT_REFERENCE_1",
                "annotation_cnf": {
                    "name": "NAME_1",
                    "system": "SYSTEM_1"
                    },
                "values": [{
                    "name": "details",
                    "type": "object",
                    "values": []
                    }]
                }]
            },{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE_2",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_2.xml",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "annotations": [{
                "explicit_reference" : "EXPLICIT_REFERENCE_2",
                "annotation_cnf": {
                    "name": "NAME_1",
                    "system": "SYSTEM_1"
                    },
                "values": [{
                    "name": "details",
                    "type": "object",
                    "values": []
                    }]
                },{
                "explicit_reference" : "EXPLICIT_REFERENCE_2",
                "annotation_cnf": {
                    "name": "NAME_2",
                    "system": "SYSTEM_2"
                    },
                "values": [{
                    "name": "details",
                    "type": "object",
                    "values": []
                    }]
                }]
            }]
        }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5);

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the annotation_system_like input
        input_element = self.driver.find_element_by_id("/html/body/div[1]/div/div[2]/div/div/div[4]/div/div/div/div/div/form/div[4]/div[2]/div[2]/div[1]/div[2]/input")
        input_element.send_keys("SYSTEM_2")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(explicit_ref_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # find the element that's name attribute is gauge_system_like
        input_element = self.driver.find_element_by_id("/html/body/div[1]/div/div[2]/div/div/div[4]/div/div/div/div/div/form/div[4]/div[2]/div[2]/div[1]/div[2]/input")
        input_element.send_keys("SYSTEM_2")

        not_like_button = self.driver.find_element_by_id("/html/body/div[1]/div/div[2]/div/div/div[4]/div/div/div/div/div/form/div[4]/div[2]/div[2]/div[1]/div[2]/label")
        not_like_button.click()

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(explicit_ref_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # find the element that's name attribute is gauge_system_in
        input_element = self.driver.find_element_by_id("/html/body/div[1]/div/div[2]/div/div/div[4]/div/div/div/div/div/form/div[4]/div[2]/div[2]/div[2]/div[2]/div/ul/li/input")
        input_element.click()
        input_element.send_keys("SYSTEM_1")
        input_element.send_keys(Keys.RETURN)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generated
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(explicit_ref_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # find the element that's name attribute is gauge_system_in
        input_element = self.driver.find_element_by_id("/html/body/div[1]/div/div[2]/div/div/div[4]/div/div/div/div/div/form/div[4]/div[2]/div[2]/div[2]/div[2]/div/ul/li/input")
        input_element.click()
        input_element.send_keys("SYSTEM_2")
        input_element.send_keys(Keys.RETURN)

        not_in_button = self.driver.find_element_by_id("/html/body/div[1]/div/div[2]/div/div/div[4]/div/div/div/div/div/form/div[4]/div[2]/div[2]/div[2]/div[2]/label")
        not_in_button.click()

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"submit-button-query-explicit-references")))
        submit_button.click()

        # Check table generate
        explicit_ref_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-reference-nav-details-table")))
        number_of_elements = len(explicit_ref_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(explicit_ref_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

    # Not working
    def test_explicit_refs_query_ingestion_time(self):

        # Insert data
        data = {"operations":[{
                        "mode": "insert",
                        "dim_signature": {"name": "dim_signature",
                                          "exec": "exec",
                                          "version": "1.0"},
                        "source": {"name": "source.xml",
                                   "generation_time": "2018-07-05T02:07:03",
                                   "validity_start": "2018-06-05T02:07:03",
                                   "validity_stop": "2018-06-05T08:07:36"},
                        "explicit_references": [{
                            "group": "EXPL_GROUP_1",
                            "name": "EXPLICIT_REFERENCE_1"
                            }]
                    }]
                }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        ingestion_time = self.session.query(ExplicitRef).all()[0].ingestion_time.isoformat()

        wait = WebDriverWait(self.driver,5);

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        number_of_elements, empty_element =  functions.value_comparer(self.driver, wait, "explicit_refs", "ingestion_time", ingestion_time, None, True, "==")

        assert number_of_elements == 1 and empty_element is False

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        number_of_elements, empty_element =  functions.value_comparer(self.driver, wait, "explicit_refs", "ingestion_time", ingestion_time, None, True, ">")

        assert empty_element is True

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        number_of_elements, empty_element =  functions.value_comparer(self.driver, wait, "explicit_refs", "ingestion_time", ingestion_time, None, True, ">=")

        assert number_of_elements == 1 and empty_element is False

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        number_of_elements, empty_element =  functions.value_comparer(self.driver, wait, "explicit_refs", "ingestion_time", ingestion_time, None, True, "<")

        assert empty_element is True

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        number_of_elements, empty_element =  functions.value_comparer(self.driver, wait, "explicit_refs", "ingestion_time", ingestion_time, None, True, "<=")

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        number_of_elements, empty_element =  functions.value_comparer(self.driver, wait, "explicit_refs", "ingestion_time", ingestion_time, None, True, "!=")

        assert empty_element is True

    def test_explicit_refs_query_annotations_value_text(self):

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
                           "validity_stop": "2018-06-05T08:07:36"},
            "annotations": [{
                "explicit_reference" : "EXPLICIT_REFERENCE",
                "annotation_cnf": {
                    "name": "NAME_1",
                    "system": "SYSTEM"
                    },
                "values": [{
                    "name": "details",
                    "type": "object",
                    "values": [
                        {"name": "text_name_1",
                         "type": "text",
                         "value": "text_value_1"
                        }]
                    }]
                }]
            },{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE_2",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_2.xml",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "annotations": [{
                "explicit_reference" : "EXPLICIT_REFERENCE",
                "annotation_cnf": {
                    "name": "NAME_1",
                    "system": "SYSTEM"
                    },
                "values": [{
                    "name": "details",
                    "type": "object",
                    "values":  [
                    {"name": "text_name_2",
                     "type": "text",
                     "value": "text_value_2"
                        }]
                    }]
                },{
                "explicit_reference" : "EXPLICIT_REFERENCE",
                "annotation_cnf": {
                    "name": "NAME_2",
                    "system": "SYSTEM"
                    },
                "values": [{
                    "name": "details",
                    "type": "object",
                    "values": [
                        {"name": "text_name_3",
                         "type": "text",
                         "value": "text_value_2"
                        }]
                    }]
                }]
            }]
        }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5);

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit References")

        number_of_elements, empty_element = functions.value_comparer(self.driver, wait,"explicit_refs_2", "text", "text_name_1", "text_value_1", True, "==")

        assert number_of_elements == 1 and empty_element is False

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit References")

        number_of_elements, empty_element = functions.value_comparer(self.driver, wait,"explicit_refs_2", "text", "text_name_1", "text_value_2", False, "==")

        assert  number_of_elements == 2

    def test_explicit_refs_query_annotations_value_timestamp(self):

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
                           "validity_stop": "2018-06-05T08:07:36"},
            "annotations": [{
                "explicit_reference" : "EXPLICIT_REFERENCE",
                "annotation_cnf": {
                    "name": "NAME_1",
                    "system": "SYSTEM"
                    },
                "values": [{
                    "name": "details",
                    "type": "object",
                    "values": [
                        {"name": "timestamp_name_1",
                         "type": "timestamp",
                         "value": "2019-04-26T14:14:14"
                        }]
                    }]
                }]
            }]
        }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5);

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit References")

        number_of_elements, empty_element = functions.value_comparer(self.driver, wait,"explicit_refs_2", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", True, "==")

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit References")

        number_of_elements, empty_element = functions.value_comparer(self.driver, wait,"explicit_refs_2", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", True, "==")

        assert empty_element is True

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit References")

        number_of_elements, empty_element = functions.value_comparer(self.driver, wait,"explicit_refs_2", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", True, ">")

        assert empty_element is True

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit References")

        number_of_elements, empty_element = functions.value_comparer(self.driver, wait,"explicit_refs_2", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", True, ">")

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit References")

        number_of_elements, empty_element = functions.value_comparer(self.driver, wait,"explicit_refs_2", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", True, ">")

        assert empty_element == True

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit References")

        number_of_elements, empty_element = functions.value_comparer(self.driver, wait,"explicit_refs_2", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", True, ">=")

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit References")

        number_of_elements, empty_element = functions.value_comparer(self.driver, wait,"explicit_refs_2", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", True, ">=")

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit References")

        number_of_elements, empty_element = functions.value_comparer(self.driver, wait,"explicit_refs_2", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", True, ">=")

        assert empty_element == True

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit References")

        number_of_elements, empty_element = functions.value_comparer(self.driver, wait,"explicit_refs_2", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", True, "<")

        assert empty_element is True

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit References")

        number_of_elements, empty_element = functions.value_comparer(self.driver, wait,"explicit_refs_2", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", True, "<")

        assert empty_element is True

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit References")

        number_of_elements, empty_element = functions.value_comparer(self.driver, wait,"explicit_refs_2", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", True, "<")

        assert number_of_elements == 1 and empty_element is False

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit References")

        number_of_elements, empty_element = functions.value_comparer(self.driver, wait,"explicit_refs_2", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", True, "<=")

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit References")

        number_of_elements, empty_element = functions.value_comparer(self.driver, wait,"explicit_refs_2", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", True, "<=")

        assert empty_element is True

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit References")

        number_of_elements, empty_element = functions.value_comparer(self.driver, wait,"explicit_refs_2", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", True, "<=")

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit References")

        number_of_elements, empty_element = functions.value_comparer(self.driver, wait,"explicit_refs_2", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", True, "!=")

        assert empty_element is True

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit References")

        number_of_elements, empty_element = functions.value_comparer(self.driver, wait,"explicit_refs_2", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", True, "!=")

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit References")

        number_of_elements, empty_element = functions.value_comparer(self.driver, wait,"explicit_refs_2", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", True, "!=")

        assert number_of_elements == 1 and empty_element is False

    def test_explicit_refs_query_annotations_value_double(self):

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
                           "validity_stop": "2018-06-05T08:07:36"},
            "annotations": [{
                "explicit_reference" : "EXPLICIT_REFERENCE",
                "annotation_cnf": {
                    "name": "NAME_1",
                    "system": "SYSTEM"
                    },
                "values": [{
                    "name": "details",
                    "type": "object",
                    "values": [
                        {"name": "double_name_1",
                         "type": "double",
                         "value": "3.5"
                        }]
                    }]
                }]
            }]
        }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5);

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit References")

        number_of_elements, empty_element = functions.value_comparer(self.driver, wait,"explicit_refs_2", "double", "double_name_1", "3.5", True, "==")

        assert number_of_elements == 1 and empty_element is False
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit References")

        number_of_elements, empty_element = functions.value_comparer(self.driver, wait,"explicit_refs_2", "double", "double_name_1", "3.5", False, "==")

        assert empty_element is True

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit References")

        number_of_elements, empty_element = functions.value_comparer(self.driver, wait,"explicit_refs_2", "double", "double_name_1", "3.5", True, ">")

        assert empty_element is True

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit References")

        number_of_elements, empty_element = functions.value_comparer(self.driver, wait,"explicit_refs_2", "double", "double_name_1", "3.25", True, ">")

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit References")

        number_of_elements, empty_element = functions.value_comparer(self.driver, wait,"explicit_refs_2", "double", "double_name_1", "3.75", True, ">")

        assert empty_element == True

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit References")

        number_of_elements, empty_element = functions.value_comparer(self.driver, wait,"explicit_refs_2", "double", "double_name_1", "3.5", True, ">=")

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit References")

        number_of_elements, empty_element = functions.value_comparer(self.driver, wait,"explicit_refs_2", "double", "double_name_1", "3.25", True, ">=")

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit References")

        number_of_elements, empty_element = functions.value_comparer(self.driver, wait,"explicit_refs_2", "double", "double_name_1", "3.75", True, ">=")

        assert empty_element == True

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit References")

        number_of_elements, empty_element = functions.value_comparer(self.driver, wait,"explicit_refs_2", "double", "double_name_1", "3.5", True, "<")

        assert empty_element is True

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit References")

        number_of_elements, empty_element = functions.value_comparer(self.driver, wait,"explicit_refs_2", "double", "double_name_1", "3.25", True, "<")

        assert empty_element is True

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit References")

        number_of_elements, empty_element = functions.value_comparer(self.driver, wait,"explicit_refs_2", "double", "double_name_1", "3.75", True, "<")

        assert number_of_elements == 1 and empty_element is False

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit References")

        number_of_elements, empty_element = functions.value_comparer(self.driver, wait,"explicit_refs_2", "double", "double_name_1", "3.5", True, "<=")

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit References")

        number_of_elements, empty_element = functions.value_comparer(self.driver, wait,"explicit_refs_2", "double", "double_name_1", "3.25", True, "<=")

        assert empty_element is True

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit References")

        number_of_elements, empty_element = functions.value_comparer(self.driver, wait,"explicit_refs_2", "double", "double_name_1", "3.75", True, "<=")

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit References")

        number_of_elements, empty_element = functions.value_comparer(self.driver, wait,"explicit_refs_2", "double", "double_name_1", "3.5", True, "!=")

        assert empty_element is True

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit References")

        number_of_elements, empty_element = functions.value_comparer(self.driver, wait,"explicit_refs_2", "double", "double_name_1", "3.25", True, "!=")

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit References")

        number_of_elements, empty_element = functions.value_comparer(self.driver, wait,"explicit_refs_2", "double", "double_name_1", "3.75", True, "!=")

        assert number_of_elements == 1 and empty_element is False

    def test_explicit_refs_query_annotations_two_values(self):

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
                           "validity_stop": "2018-06-05T08:07:36"},
            "annotations": [{
                "explicit_reference" : "EXPLICIT_REFERENCE_1",
                "annotation_cnf": {
                    "name": "NAME_1",
                    "system": "SYSTEM"
                    },
                "values": [{
                    "name": "details",
                    "type": "object",
                    "values": [
                        {"name": "text_name_1",
                         "type": "text",
                         "value": "text_value_1"
                        }]
                    }]
                }]
            },{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE_2",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_2.xml",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "annotations": [{
                "explicit_reference" : "EXPLICIT_REFERENCE_2",
                "annotation_cnf": {
                    "name": "NAME_1",
                    "system": "SYSTEM"
                    },
                "values": [{
                    "name": "details",
                    "type": "object",
                    "values":  [
                    {"name": "text_name_1",
                     "type": "text",
                     "value": "text_value_1"
                        },
                    {"name": "double_name_1",
                     "type": "double",
                     "value": "1.4"
                        }]
                    }]
                },{
                "explicit_reference" : "EXPLICIT_REFERENCE_3",
                "annotation_cnf": {
                    "name": "NAME_2",
                    "system": "SYSTEM"
                    },
                "values": [{
                    "name": "details",
                    "type": "object",
                    "values": [
                        {"name": "text_name_3",
                         "type": "text",
                         "value": "text_value_2"
                        }]
                    }]
                }]
            }]
        }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5);

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit References")

        number_of_elements, empty_element =  functions.two_values_comparer( driver, wait, "explicit_refs_1", "text", "double", "text_name_1", "text_value_1", "double_name_1", "1.4", True, True, "==", "==")

        assert number_of_elements == 1 and empty_element is False

        assert True

    def test_explicit_refs_query_period(self):

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
                           "validity_start": "2018-06-05T00:00:00",
                           "validity_stop": "2018-06-05T08:00:00"},
            "events": [{"gauge": {"name": "GAUGE_NAME",
                                  "system": "GAUGE_SYSTEM",
                                  "insertion_type": "SIMPLE_UPDATE"},
                        "explicit_reference": "EXPLICIT_REFERENCE_EVENT_1",
                        "start": "2018-06-05T02:00:00",
                        "stop": "2018-06-05T03:00:00",
                        "values": [{"name": "VALUES",
                                   "type": "object",
                                   "values": [
                                       {"name": "text_name_1",
                                        "type": "text",
                                        "value": "text_value_1"
                                       }]
                                   }]
                    },{"gauge": {"name": "GAUGE_NAME_2",
                                  "system": "GAUGE_SYSTEM_2",
                                  "insertion_type": "SIMPLE_UPDATE"},
                        "explicit_reference": "EXPLICIT_REFERENCE_EVENT_2",
                        "start": "2018-06-05T03:00:00",
                        "stop": "2018-06-05T04:00:00",
                        "values": [{"name": "VALUES",
                                   "type": "object",
                                   "values": [
                                       {"name": "text_name_2",
                                        "type": "text",
                                        "value": "text_value_2"
                                       }]
                                   }]
                    },{"gauge": {"name": "GAUGE_NAME_3",
                                  "system": "GAUGE_SYSTEM_3",
                                  "insertion_type": "SIMPLE_UPDATE"},
                        "explicit_reference": "EXPLICIT_REFERENCE_EVENT_3",
                        "start": "2018-06-05T04:00:00",
                        "stop": "2018-06-05T05:00:00",
                        "values": [{"name": "VALUES",
                                   "type": "object",
                                   "values": [
                                       {"name": "text_name_3",
                                        "type": "text",
                                        "value": "text_value_3"
                                       }]
                                   }]
                    }]
            }]
        }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5);

        ## == ## Full period##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        number_of_elements, empty_element =  functions.period_comparer(self.driver, wait, "explicit_refs", "2018-06-05T03:00:00", "==","2018-06-05T04:00:00", "==")

        assert number_of_elements == 1 and empty_element is False

        ## >= ## Only Start##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        number_of_elements, empty_element =  functions.period_comparer(self.driver, wait, "explicit_refs", start_value = "2018-06-05T03:00:00", start_operator = ">=")

        assert number_of_elements == 2

        ## != ## Only End##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        number_of_elements, empty_element =  functions.period_comparer(self.driver, wait, "explicit_refs", end_value = "2018-06-05T04:00:00", end_operator = "!=")

        assert number_of_elements == 2

        ## > ## Only Start## < ## Only Start##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        number_of_elements, empty_element =  functions.two_periods_comparer(self.driver, wait, "explicit_refs", start_value_1 = "2018-06-05T01:30:00", start_operator_1 = ">", start_value_2 = "2018-06-05T03:00:00", start_operator_2 = "<")

        assert number_of_elements == 1 and empty_element is False

        ## <= ## Start## > ## End## != ## Start## >= ## End##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        number_of_elements, empty_element =  functions.two_periods_comparer(self.driver, wait, "explicit_refs", start_value_1 = "2018-06-05T03:00:00", start_operator_1 = "<=", end_value_1 = "2018-06-05T02:30:00", end_operator_1 = ">",
        start_value_2 = "2018-06-05T04:00:00", start_operator_2 = "!=", end_value_2 = "2018-06-05T03:00:00", end_operator_2 = ">=")

        assert number_of_elements == 2

        assert True
