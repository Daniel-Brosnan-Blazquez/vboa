"""
Automated tests for the gauges tab

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
from selenium.webdriver.support.ui import WebDriverWait, Select
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


class TestGaugesTab(unittest.TestCase):

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('window-size=1920,1080')
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)

    def setUp(self):
        # Create the engine to manage the data
        self.engine_eboa = Engine()
        self.query_eboa = Query()

        # Create session to connect to the database
        self.session = Session()

        # Clear all tables before executing the test
        self.query_eboa.clear_db()

    def tearDown(self):
        # Close connections to the DDBB
        self.engine_eboa.close_session()
        self.query_eboa.close_session()
        self.session.close()

    @classmethod
    def tearDownClass(self):
        self.driver.quit()

    def test_gauges_no_filter_no_network(self):

        # Insert data
        data = {"operations": [{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source.xml",
                        "reception_time": "2018-07-05T02:07:03",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "events": [{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT",
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
            }]}

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5);

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Gauges")
        functions.click_no_graphs_gauges(self.driver)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'gauges-submit-button')))
        functions.click(submitButton)

        # Check table generated
        gauges_table = wait.until(EC.visibility_of_element_located((By.ID,"gauges-table")))
        number_of_elements = len(gauges_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        # Check gauge_name
        gauge_name = gauges_table.find_elements_by_xpath("tbody/tr[1]/td[1]")

        assert gauge_name[0].text == "GAUGE_NAME"

        # Check gauge_system
        gauge_system = gauges_table.find_elements_by_xpath("tbody/tr[1]/td[2]")

        assert gauge_system[0].text == "GAUGE_SYSTEM"

        #Check dim_signature
        dim_signature = gauges_table.find_elements_by_xpath("tbody/tr[1]/td[3]")

        assert dim_signature[0].text == "DIM_SIGNATURE"

        # Check uuid
        uuid = gauges_table.find_elements_by_xpath("tbody/tr[1]/td[4]")

        assert re.match("........-....-....-....-............", uuid[0].text)

    def test_gauges_no_filter_with_network(self):

        screenshot_path = os.path.dirname(os.path.abspath(__file__)) + "/screenshots/gauges/"

        if not os.path.exists(screenshot_path):
            os.makedirs(screenshot_path)
        #end if

        # Insert data
        data = {"operations": [{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source.xml",
                        "reception_time": "2018-07-05T02:07:03",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "events": [{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT",
                "gauge": {"name": "GAUGE_NAME",
                          "system": "GAUGE_SYSTEM",
                          "insertion_type": "SIMPLE_UPDATE"},
                "start": "2018-06-05T04:07:03",
                "stop": "2018-06-05T06:07:36"
                }]
            }]}

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5);

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Gauges")
        functions.click_no_graphs_gauges(self.driver)

        # Click on show network
        networkButton = self.driver.find_element_by_id("gauges-show-network")
        if not networkButton.find_element_by_xpath('input').is_selected():
            functions.select_checkbox(networkButton)
        #end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'gauges-submit-button')))
        functions.click(submitButton)

        gauge = self.session.query(Gauge).all()[0]

        dim_signature = self.session.query(DimSignature).all()[0]

        assert self.driver.execute_script('return gauges;') == [{
            "description": '',
            "id": str(gauge.gauge_uuid),
            "name": "GAUGE_NAME",
            "system": "GAUGE_SYSTEM",
            "dim_signature_uuid": str(dim_signature.dim_signature_uuid),
            "dim_signature_name": "DIM_SIGNATURE",
            "gauges_linking": [],
            "gauges_linked": []
        }]

        network = self.driver.find_element_by_id("gauges-nav-network")

        network.screenshot(screenshot_path + "network_of_gauges_screenshot.png")

        condition = network.is_displayed()

        assert condition

    def test_gauges_query_gauge_name_filter(self):

        # Insert data
        data = {"operations": [{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_1.xml",
                        "reception_time": "2018-07-05T02:07:03",
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
                        "reception_time": "2018-07-05T02:07:03",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "events": [{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT",
                "gauge": {"name": "GAUGE_NAME_3",
                          "system": "GAUGE_SYSTEM_3",
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
        functions.goToTab(self.driver,"Gauges")
        functions.click_no_graphs_gauges(self.driver)

        # Fill the gauge_name_like input
        input_element = self.driver.find_element_by_id("gauges-gauge-name-text")
        input_element.send_keys("GAUGE_NAME_1")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'gauges-submit-button')))
        functions.click(submitButton)

        # Check table generated
        gauges_table = wait.until(EC.visibility_of_element_located((By.ID,"gauges-table")))
        number_of_elements = len(gauges_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(gauges_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Gauges")
        functions.click_no_graphs_gauges(self.driver)

        # Fill the gauge_name_like input
        input_element = self.driver.find_element_by_id("gauges-gauge-name-text")
        input_element.send_keys("GAUGE_NAME_1")

        Select(self.driver.find_element_by_id("gauges-gauge-name-operator")).select_by_visible_text("notlike")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'gauges-submit-button')))
        functions.click(submitButton)

        # Check table generated
        gauges_table = wait.until(EC.visibility_of_element_located((By.ID,"gauges-table")))
        number_of_elements = len(gauges_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(gauges_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Gauges")
        functions.click_no_graphs_gauges(self.driver)

        # Fill the gauge_name_in input
        input_element = self.driver.find_element_by_id("gauges-gauge-names-in-text")
        input_element.send_keys("G")
        Select(self.driver.find_element_by_id("gauges-gauge-names-in-select")).select_by_visible_text("GAUGE_NAME_1")
        Select(self.driver.find_element_by_id("gauges-gauge-names-in-select")).select_by_visible_text("GAUGE_NAME_3")
        
        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'gauges-submit-button')))
        functions.click(submitButton)

        # Check table generated
        gauges_table = wait.until(EC.visibility_of_element_located((By.ID,"gauges-table")))
        number_of_elements = len(gauges_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(gauges_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Gauges")
        functions.click_no_graphs_gauges(self.driver)

        # Fill the gauge_name_in input
        input_element = self.driver.find_element_by_id("gauges-gauge-names-in-text")
        input_element.send_keys("G")
        Select(self.driver.find_element_by_id("gauges-gauge-names-in-select")).select_by_visible_text("GAUGE_NAME_1")

        notInButton = self.driver.find_element_by_id("gauges-gauge-names-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        #end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'gauges-submit-button')))
        functions.click(submitButton)

        # Check table generate
        gauges_table = wait.until(EC.visibility_of_element_located((By.ID,"gauges-table")))
        number_of_elements = len(gauges_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(gauges_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

    def test_gauges_query_gauge_system_filter(self):

        # Insert data
        data = {"operations": [{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_1.xml",
                        "reception_time": "2018-07-05T02:07:03",
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
                        "reception_time": "2018-07-05T02:07:03",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "events": [{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT",
                "gauge": {"name": "GAUGE_NAME_3",
                          "system": "GAUGE_SYSTEM_3",
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
        functions.goToTab(self.driver,"Gauges")
        functions.click_no_graphs_gauges(self.driver)

        # Fill the gauge_system_like input
        input_element = self.driver.find_element_by_id("gauges-gauge-system-text")
        input_element.send_keys("GAUGE_SYSTEM_1")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'gauges-submit-button')))
        functions.click(submitButton)

        # Check table generated
        gauges_table = wait.until(EC.visibility_of_element_located((By.ID,"gauges-table")))
        number_of_elements = len(gauges_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(gauges_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Gauges")
        functions.click_no_graphs_gauges(self.driver)

        # Fill the gauge_system_like input
        input_element = self.driver.find_element_by_id("gauges-gauge-system-text")
        input_element.send_keys("GAUGE_SYSTEM_1")

        Select(self.driver.find_element_by_id("gauges-gauge-system-operator")).select_by_visible_text("notlike")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'gauges-submit-button')))
        functions.click(submitButton)

        # Check table generated
        gauges_table = wait.until(EC.visibility_of_element_located((By.ID,"gauges-table")))
        number_of_elements = len(gauges_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(gauges_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Gauges")
        functions.click_no_graphs_gauges(self.driver)

        # Fill the gauge_system_in input
        input_element = self.driver.find_element_by_id("gauges-gauge-systems-in-text")
        input_element.send_keys("G")
        Select(self.driver.find_element_by_id("gauges-gauge-systems-in-select")).select_by_visible_text("GAUGE_SYSTEM_1")
        Select(self.driver.find_element_by_id("gauges-gauge-systems-in-select")).select_by_visible_text("GAUGE_SYSTEM_3")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'gauges-submit-button')))
        functions.click(submitButton)

        # Check table generated
        gauges_table = wait.until(EC.visibility_of_element_located((By.ID,"gauges-table")))
        number_of_elements = len(gauges_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(gauges_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Gauges")
        functions.click_no_graphs_gauges(self.driver)

        # Fill the gauge_system_in input
        input_element = self.driver.find_element_by_id("gauges-gauge-systems-in-text")
        input_element.send_keys("G")
        Select(self.driver.find_element_by_id("gauges-gauge-systems-in-select")).select_by_visible_text("GAUGE_SYSTEM_1")
        notInButton = self.driver.find_element_by_id("gauges-gauge-system-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        #end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'gauges-submit-button')))
        functions.click(submitButton)

        # Check table generate
        gauges_table = wait.until(EC.visibility_of_element_located((By.ID,"gauges-table")))
        number_of_elements = len(gauges_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(gauges_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

    def test_gauges_query_dim_signature_filter(self):

        # Insert data
        data = {"operations": [{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE_1",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_1.xml",
                        "reception_time": "2018-07-05T02:07:03",
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
                  "name": "DIM_SIGNATURE_2",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_2.xml",
                        "reception_time": "2018-07-05T02:07:03",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "events": [{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT",
                "gauge": {"name": "GAUGE_NAME_3",
                          "system": "GAUGE_SYSTEM_3",
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
        functions.goToTab(self.driver,"Gauges")
        functions.click_no_graphs_gauges(self.driver)

        # Fill the dim_signature_like input
        input_element = self.driver.find_element_by_id("gauges-dim-signature-text")
        input_element.send_keys("DIM_SIGNATURE_2")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'gauges-submit-button')))
        functions.click(submitButton)

        # Check table generated
        gauges_table = wait.until(EC.visibility_of_element_located((By.ID,"gauges-table")))
        number_of_elements = len(gauges_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(gauges_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Gauges")
        functions.click_no_graphs_gauges(self.driver)

        # Fill the dim_signature_like input
        input_element = self.driver.find_element_by_id("gauges-dim-signature-text")
        input_element.send_keys("DIM_SIGNATURE_2")

        Select(self.driver.find_element_by_id("gauges-dim-signature-operator")).select_by_visible_text("notlike")
        
        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'gauges-submit-button')))
        functions.click(submitButton)

        # Check table generated
        gauges_table = wait.until(EC.visibility_of_element_located((By.ID,"gauges-table")))
        number_of_elements = len(gauges_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Gauges")
        functions.click_no_graphs_gauges(self.driver)

        # Fill the dim_signature_in input
        input_element = self.driver.find_element_by_id("gauges-dim-signatures-in-text")
        input_element.send_keys("D")
        Select(self.driver.find_element_by_id("gauges-dim-signatures-in-select")).select_by_visible_text("DIM_SIGNATURE_1")
        
        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'gauges-submit-button')))
        functions.click(submitButton)

        # Check table generated
        gauges_table = wait.until(EC.visibility_of_element_located((By.ID,"gauges-table")))
        number_of_elements = len(gauges_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Gauges")
        functions.click_no_graphs_gauges(self.driver)

        # Fill the dim_signature_in input
        input_element = self.driver.find_element_by_id("gauges-dim-signatures-in-text")
        input_element.send_keys("D")
        Select(self.driver.find_element_by_id("gauges-dim-signatures-in-select")).select_by_visible_text("DIM_SIGNATURE_2")

        notInButton = self.driver.find_element_by_id("gauges-dim-signatures-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        #end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'gauges-submit-button')))
        functions.click(submitButton)

        # Check table generate
        gauges_table = wait.until(EC.visibility_of_element_located((By.ID,"gauges-table")))
        number_of_elements = len(gauges_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(gauges_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2
