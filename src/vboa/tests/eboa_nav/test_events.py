"""
Automated tests for the events tab

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
import dateutil.parser as parser
import vboa.tests.functions as functions
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

class TestEventsTab(unittest.TestCase):

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
    
    def test_events_no_data(self):

        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"events-nav-no-data")))

        assert no_data

    def test_events_query_no_filter_no_timeline(self):

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

        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        # Check gauge_name
        gauge_name = events_table.find_elements_by_xpath("tbody/tr[td[text() = 'GAUGE_NAME']]/td[2]")

        assert gauge_name[0].text == "GAUGE_NAME"

        # Check gauge_system
        gauge_system = events_table.find_elements_by_xpath("tbody/tr[td[text() = 'GAUGE_NAME']]/td[3]")

        assert gauge_system[0].text == "GAUGE_SYSTEM"

        # Check start
        start_date = events_table.find_elements_by_xpath("tbody/tr[td[text() = 'GAUGE_NAME']]/td[4]")

        assert start_date[0].text == "2018-06-05T04:07:03"

        # Check stop
        stop_date = events_table.find_elements_by_xpath("tbody/tr[td[text() = 'GAUGE_NAME']]/td[5]")

        assert stop_date[0].text == "2018-06-05T06:07:36"

        # Check duration
        duration = events_table.find_elements_by_xpath("tbody/tr[td[text() = 'GAUGE_NAME']]/td[6]")

        assert duration[0].text == str((parser.parse(stop_date[0].text) - parser.parse(start_date[0].text)).total_seconds())

        # Check ingestion_time
        ingestion_time = events_table.find_elements_by_xpath("tbody/tr[td[text() = 'GAUGE_NAME']]/td[7]")

        assert re.match("....-..-..T..:..:...*", ingestion_time[0].text)

        #Check source
        source = events_table.find_elements_by_xpath("tbody/tr[td[text() = 'GAUGE_NAME']]/td[8]")

        assert source[0].text == "source.xml"

        #Check source
        explicit_ref = events_table.find_elements_by_xpath("tbody/tr[td[text() = 'GAUGE_NAME']]/td[9]")

        assert explicit_ref[0].text == "EXPLICIT_REFERENCE_EVENT"

        # Check uuid
        uuid = events_table.find_elements_by_xpath("tbody/tr[td[text() = 'GAUGE_NAME']]/td[11]")

        assert re.match("........-....-....-....-............", uuid[0].text)

    def test_events_query_no_filter_with_timeline(self):

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

        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        # Click on show map
        timelineButton = self.driver.find_element_by_id("events-show-timeline")
        if not timelineButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(timelineButton)
        # end if

        # Apply filters and click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        timeline = self.driver.find_element_by_id('events-nav-timeline')

        condition = timeline.is_displayed()

        assert condition

        event = self.session.query(Event).all()[0]

        assert self.driver.execute_script('return events;') == [{
            "id": str(event.event_uuid),
            "gauge":{
                "name": "GAUGE_NAME",
                "system": "GAUGE_SYSTEM"
            },
            "explicit_reference": 'EXPLICIT_REFERENCE_EVENT',
            "explicit_ref_uuid": str(event.explicit_ref_uuid),
            "ingestion_time": event.ingestion_time.isoformat(),
            "source": "source.xml",
            "source_uuid": str(event.source_uuid),
            "start": "2018-06-05T04:07:03",
            "stop": "2018-06-05T06:07:36",
            }]

        # Linked events table
        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/eboa_nav/query-event-links/" + str(event.event_uuid))

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"linked-events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        # Check description
        gauge_name = events_table.find_elements_by_xpath("tbody/tr[td[text() = 'GAUGE_NAME']]/td[2]")

        assert gauge_name[0].text == "PRIME"
        
        # Check gauge_name
        gauge_name = events_table.find_elements_by_xpath("tbody/tr[td[text() = 'GAUGE_NAME']]/td[3]")

        assert gauge_name[0].text == "GAUGE_NAME"

        # Check gauge_system
        gauge_system = events_table.find_elements_by_xpath("tbody/tr[td[text() = 'GAUGE_NAME']]/td[4]")

        assert gauge_system[0].text == "GAUGE_SYSTEM"

        # Check start
        start_date = events_table.find_elements_by_xpath("tbody/tr[td[text() = 'GAUGE_NAME']]/td[5]")

        assert start_date[0].text == "2018-06-05T04:07:03"

        # Check stop
        stop_date = events_table.find_elements_by_xpath("tbody/tr[td[text() = 'GAUGE_NAME']]/td[6]")

        assert stop_date[0].text == "2018-06-05T06:07:36"

        # Check duration
        duration = events_table.find_elements_by_xpath("tbody/tr[td[text() = 'GAUGE_NAME']]/td[7]")

        assert duration[0].text == str((parser.parse(stop_date[0].text) - parser.parse(start_date[0].text)).total_seconds())

        # Check ingestion_time
        ingestion_time = events_table.find_elements_by_xpath("tbody/tr[td[text() = 'GAUGE_NAME']]/td[8]")

        assert re.match("....-..-..T..:..:...*", ingestion_time[0].text)

        #Check source
        source = events_table.find_elements_by_xpath("tbody/tr[td[text() = 'GAUGE_NAME']]/td[9]")

        assert source[0].text == "source.xml"

        #Check source
        explicit_ref = events_table.find_elements_by_xpath("tbody/tr[td[text() = 'GAUGE_NAME']]/td[10]")

        assert explicit_ref[0].text == "EXPLICIT_REFERENCE_EVENT"

        # Check uuid
        uuid = events_table.find_elements_by_xpath("tbody/tr[td[text() = 'GAUGE_NAME']]/td[12]")

        assert re.match("........-....-....-....-............", uuid[0].text)

    def test_events_query_source_filter(self):

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
                        "reception_time": "2018-07-05T02:07:03",
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

        wait = WebDriverWait(self.driver,5)

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        # Fill the source_like input
        input_element = self.driver.find_element_by_id("events-source-text")
        input_element.send_keys("source_2.xml")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click_no_graphs_events(self.driver)

        # Fill the source input
        input_element = self.driver.find_element_by_id("events-source-text")
        input_element.send_keys("source_2.xml")

        menu = Select(self.driver.find_element_by_id("events-source-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click_no_graphs_events(self.driver)

        # Fill the source_in input
        input_element = self.driver.find_element_by_id("events-sources-in-text")
        functions.click(input_element)

        input_element.send_keys("source_1.xml")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("events-sources-in-select"))
        options.select_by_visible_text("source_1.xml")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click_no_graphs_events(self.driver)

        # Fill the source_in input
        input_element = self.driver.find_element_by_id("events-sources-in-text")
        functions.click(input_element)

        input_element.send_keys("source_2.xml")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("events-sources-in-select"))
        options.select_by_visible_text("source_2.xml")

        notInButton = self.driver.find_element_by_id("events-sources-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        # end if

        # Click on query button
        functions.click(submit_button)

        # Check table generate
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

    def test_events_query_explicit_ref_filter(self):

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
                        "reception_time": "2018-07-05T02:07:03",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "events": [{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT_1",
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

        wait = WebDriverWait(self.driver,5)

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        # Fill the explicit_ref_like input
        input_element = self.driver.find_element_by_id("events-er-text")
        input_element.send_keys("EXPLICIT_REFERENCE_EVENT_2")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click_no_graphs_events(self.driver)

        # Fill the explicit reference input
        input_element = self.driver.find_element_by_id("events-er-text")
        input_element.send_keys("EXPLICIT_REFERENCE_EVENT_2")

        menu = Select(self.driver.find_element_by_id("events-er-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click_no_graphs_events(self.driver)

        # Fill the explicit_reference_in input
        input_element = self.driver.find_element_by_id("events-ers-in-text")
        functions.click(input_element)

        input_element.send_keys("EXPLICIT_REFERENCE_EVENT_1")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("events-ers-in-select"))
        options.select_by_visible_text("EXPLICIT_REFERENCE_EVENT_1")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click_no_graphs_events(self.driver)

        # Fill the explicit_ref_in input
        input_element = self.driver.find_element_by_id("events-ers-in-text")
        functions.click(input_element)

        input_element.send_keys("EXPLICIT_REFERENCE_EVENT_2")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("events-ers-in-select"))
        options.select_by_visible_text("EXPLICIT_REFERENCE_EVENT_2")

        notInButton = self.driver.find_element_by_id("events-ers-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        # end if

        # Click on query button
        functions.click(submit_button)

        # Check table generate
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

    def test_events_query_key_filter(self):

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
                "gauge": {"name": "GAUGE_NAME",
                          "system": "GAUGE_SYSTEM",
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
                "key": "EVENT_KEY_2"
                }]
            }
        ]}

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5)

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        # Fill the key_like input
        input_element = self.driver.find_element_by_id("events-key-text")
        input_element.send_keys("EVENT_KEY")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click_no_graphs_events(self.driver)

        # Fill the key input
        input_element = self.driver.find_element_by_id("events-key-text")
        input_element.send_keys("EVENT_KEY")

        menu = Select(self.driver.find_element_by_id("events-key-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click_no_graphs_events(self.driver)

        # Fill the key_in input
        input_element = self.driver.find_element_by_id("events-keys-in-text")
        functions.click(input_element)

        input_element.send_keys("EVENT_KEY_2")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("events-keys-in-select"))
        options.select_by_visible_text("EVENT_KEY_2")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

       ## Not In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click_no_graphs_events(self.driver)

        # Fill the key_in input
        input_element = self.driver.find_element_by_id("events-keys-in-text")
        functions.click(input_element)

        input_element.send_keys("EVENT_KEY")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("events-keys-in-select"))
        options.select_by_visible_text("EVENT_KEY")

        notInButton = self.driver.find_element_by_id("events-keys-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        # end if

        # Click on query button
        functions.click(submit_button)

        # Check table generate
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

    def test_events_query_gauge_name_filter(self):
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

        wait = WebDriverWait(self.driver,5)

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        # Fill the gauge_name_like input
        input_element = self.driver.find_element_by_id("events-gauge-name-text")
        input_element.send_keys("GAUGE_NAME_1")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click_no_graphs_events(self.driver)

        # Fill the gauge name input
        input_element = self.driver.find_element_by_id("events-gauge-name-text")
        input_element.send_keys("GAUGE_NAME_1")

        menu = Select(self.driver.find_element_by_id("events-gauge-name-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click_no_graphs_events(self.driver)

        # Fill the gauge_name_in input
        input_element = self.driver.find_element_by_id("events-gauge-names-in-text")
        functions.click(input_element)

        input_element.send_keys("GAUGE_NAME_2")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("events-gauge-names-in-select"))
        options.select_by_visible_text("GAUGE_NAME_2")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        ## Not In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click_no_graphs_events(self.driver)

        # Fill the gauge_name_in input
        input_element = self.driver.find_element_by_id("events-gauge-names-in-text")
        functions.click(input_element)

        input_element.send_keys("GAUGE_NAME_1")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("events-gauge-names-in-select"))
        options.select_by_visible_text("GAUGE_NAME_1")

        notInButton = self.driver.find_element_by_id("events-gauge-names-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        # end if

        # Click on query button
        functions.click(submit_button)

        # Check table generate
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

    def test_events_query_gauge_system_filter(self):

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

        wait = WebDriverWait(self.driver,5)

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        # Fill the gauge_system_like input
        input_element = self.driver.find_element_by_id("events-gauge-system-text")
        input_element.send_keys("GAUGE_SYSTEM_1")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click_no_graphs_events(self.driver)

        # Fill the gauge system input
        input_element = self.driver.find_element_by_id("events-gauge-system-text")
        input_element.send_keys("GAUGE_SYSTEM_1")

        menu = Select(self.driver.find_element_by_id("events-gauge-system-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click_no_graphs_events(self.driver)

        # Fill the gauge_system_in input
        input_element = self.driver.find_element_by_id("events-gauge-systems-in-text")
        functions.click(input_element)

        input_element.send_keys("GAUGE_SYSTEM_2")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("events-gauge-systems-in-select"))
        options.select_by_visible_text("GAUGE_SYSTEM_2")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        ## Not In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click_no_graphs_events(self.driver)

        # Fill the gauge_system_in input
        input_element = self.driver.find_element_by_id("events-gauge-systems-in-text")
        functions.click(input_element)

        input_element.send_keys("GAUGE_SYSTEM_1")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("events-gauge-systems-in-select"))
        options.select_by_visible_text("GAUGE_SYSTEM_1")

        notInButton = self.driver.find_element_by_id("events-gauge-systems-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        # end if

        # Click on query button
        functions.click(submit_button)

        # Check table generate
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0
        
        assert number_of_elements == 2

    def test_events_query_value_text(self):

        # Insert data
        data = {"operations":[{
                        "mode": "insert",
                        "dim_signature": {"name": "dim_signature",
                                          "exec": "exec",
                                          "version": "1.0"},
                        "source": {"name": "source.xml",
                        "reception_time": "2018-07-05T02:07:03",
                                   "generation_time": "2018-07-05T02:07:03",
                                   "validity_start": "2018-06-05T02:07:03",
                                   "validity_stop": "2018-06-05T08:07:36"},
                        "events": [{"gauge": {"name": "GAUGE_NAME",
                                              "system": "GAUGE_SYSTEM",
                                              "insertion_type": "SIMPLE_UPDATE"},
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
                        }]
                    }]
                }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5)

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "text", "textname_1", "textvalue_1", "==", "==", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "text", "textname_1", "textvalue_2", "!=", "==", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"events-nav-no-data")))

        assert no_data

    def test_events_query_value_timestamp(self):

        # Insert data
        data = {"operations":[{
                        "mode": "insert",
                        "dim_signature": {"name": "dim_signature",
                                          "exec": "exec",
                                          "version": "1.0"},
                        "source": {"name": "source.xml",
                        "reception_time": "2018-07-05T02:07:03",
                                   "generation_time": "2018-07-05T02:07:03",
                                   "validity_start": "2018-06-05T02:07:03",
                                   "validity_stop": "2018-06-05T08:07:36"},
                        "events": [{"gauge": {"name": "GAUGE_NAME",
                                              "system": "GAUGE_SYSTEM",
                                              "insertion_type": "SIMPLE_UPDATE"},
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
                        }]
                    }]}

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5)

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", "==", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", "==", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"events-nav-no-data")))

        assert no_data

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"events-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", "==", ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"events-nav-no-data")))

        assert no_data

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", "==", ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"events-nav-no-data")))

        assert no_data

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"events-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", "==", "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"events-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", "==", "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"events-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"events-nav-no-data")))

        assert no_data

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", "==", "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

    def test_events_query_value_double(self):

        # Insert data
        data = {"operations":[{
                        "mode": "insert",
                        "dim_signature": {"name": "dim_signature",
                                          "exec": "exec",
                                          "version": "1.0"},
                        "source": {"name": "source.xml",
                        "reception_time": "2018-07-05T02:07:03",
                                   "generation_time": "2018-07-05T02:07:03",
                                   "validity_start": "2018-06-05T02:07:03",
                                   "validity_stop": "2018-06-05T08:07:36"},
                        "events": [{"gauge": {"name": "GAUGE_NAME",
                                              "system": "GAUGE_SYSTEM",
                                              "insertion_type": "SIMPLE_UPDATE"},
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
                        }]
                    }]
                }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5)

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.5", "==", "==", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.5", "!=", "==", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"events-nav-no-data")))

        assert no_data

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.5", "==", ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"events-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.25", "==", ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.75", "==", ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"events-nav-no-data")))

        assert no_data

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.5", "==", ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.25", "==", ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.75", "==", ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"events-nav-no-data")))

        assert no_data

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.5", "==", "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"events-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.25", "==", "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"events-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.75", "==", "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.5", "==", "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.25", "==", "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"events-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.75", "==", "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.5", "==", "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"events-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.25", "==", "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.75", "==", "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

    def test_events_query_value_event_duration(self):

        # Insert data
        data = {"operations":[{
                        "mode": "insert",
                        "dim_signature": {"name": "dim_signature",
                                          "exec": "exec",
                                          "version": "1.0"},
                        "source": {"name": "source.xml",
                        "reception_time": "2018-07-05T02:07:03",
                                   "generation_time": "2018-07-05T02:07:03",
                                   "validity_start": "2018-06-05T02:07:03",
                                   "validity_stop": "2018-06-05T08:07:36"},
                        "events": [{"gauge": {"name": "GAUGE_NAME",
                                              "system": "GAUGE_SYSTEM",
                                              "insertion_type": "SIMPLE_UPDATE"},
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
                        }]
                    }]
                }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        events = self.session.query(Event).all()
        event_duration = str((events[0].stop - events[0].start).total_seconds())

        wait = WebDriverWait(self.driver,5)

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click_no_graphs_events(self.driver)

        functions.fill_any_duration(self.driver, wait, "events", "event", event_duration, "==", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click_no_graphs_events(self.driver)

        functions.fill_any_duration(self.driver, wait, "events", "event", event_duration, ">", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"events-nav-no-data")))

        assert no_data

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click_no_graphs_events(self.driver)

        functions.fill_any_duration(self.driver, wait, "events", "event", event_duration, ">=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click_no_graphs_events(self.driver)

        functions.fill_any_duration(self.driver, wait, "events", "event", event_duration, "<", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"events-nav-no-data")))

        assert no_data

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click_no_graphs_events(self.driver)

        functions.fill_any_duration(self.driver, wait, "events", "event", event_duration, "<=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click_no_graphs_events(self.driver)

        functions.fill_any_duration(self.driver, wait, "events", "event", event_duration, "!=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"events-nav-no-data")))

        assert no_data
    
    def test_events_query_ingestion_time(self):

        # Insert data
        data = {"operations":[{
                        "mode": "insert",
                        "dim_signature": {"name": "dim_signature",
                                          "exec": "exec",
                                          "version": "1.0"},
                        "source": {"name": "source.xml",
                        "reception_time": "2018-07-05T02:07:03",
                                   "generation_time": "2018-07-05T02:07:03",
                                   "validity_start": "2018-06-05T02:07:03",
                                   "validity_stop": "2018-06-05T08:07:36"},
                        "events": [{"gauge": {"name": "GAUGE_NAME",
                                              "system": "GAUGE_SYSTEM",
                                              "insertion_type": "SIMPLE_UPDATE"},
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
                        }]
                    }]
                }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        ingestion_time = self.session.query(Event).all()[0].ingestion_time.isoformat()

        wait = WebDriverWait(self.driver,5)

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_ingestion_time(self.driver, wait, "events", ingestion_time, "==", 1)
        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_ingestion_time(self.driver, wait, "events", ingestion_time, ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"events-nav-no-data")))

        assert no_data

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_ingestion_time(self.driver, wait, "events", ingestion_time, ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_ingestion_time(self.driver, wait, "events", ingestion_time, "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"events-nav-no-data")))

        assert no_data

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_ingestion_time(self.driver, wait, "events", ingestion_time, "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_ingestion_time(self.driver, wait, "events", ingestion_time, "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"events-nav-no-data")))

        assert no_data

    def test_events_query_two_values(self):

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
            "events": [{"gauge": {"name": "GAUGE_NAME",
                                  "system": "GAUGE_SYSTEM",
                                  "insertion_type": "SIMPLE_UPDATE"},
                        "start": "2018-06-05T02:07:03",
                        "stop": "2018-06-05T08:07:36",
                        "values": [{"name": "VALUES",
                                   "type": "object",
                                   "values": [
                                       {"name": "textname_1",
                                        "type": "text",
                                        "value": "textvalue_1"
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
                        "reception_time": "2018-07-05T02:07:03",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "events": [{"gauge": {"name": "GAUGE_NAME",
                                  "system": "GAUGE_SYSTEM",
                                  "insertion_type": "SIMPLE_UPDATE"},
                        "start": "2018-06-05T02:07:03",
                        "stop": "2018-06-05T08:07:36",
                        "values": [{"name": "VALUES",
                                   "type": "object",
                                   "values":  [
                                   {"name": "textname_1",
                                    "type": "text",
                                    "value": "textvalue_1"
                                       },
                                   {"name": "double_name_1",
                                    "type": "double",
                                    "value": "1.4"
                                       }]
                                   }]
                        },{"gauge": {"name": "GAUGE_NAME",
                                              "system": "GAUGE_SYSTEM",
                                              "insertion_type": "SIMPLE_UPDATE"},
                                    "start": "2018-06-05T02:07:03",
                                    "stop": "2018-06-05T08:07:36",
                                    "values": [{"name": "VALUES",
                                               "type": "object",
                                               "values": [
                                                   {"name": "textname_3",
                                                    "type": "text",
                                                    "value": "textvalue_2"
                                                   }]
                                               }]
                                    }]
            }]
        }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "text", "textname_1", "textvalue_1", "==", "==", 1)
        functions.click(self.driver.find_element_by_id("events-add-value"))
        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "1.4", "==", "==", 2)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

    def test_events_query_period(self):

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
                           "validity_start": "2018-06-05T00:00:00",
                           "validity_stop": "2018-06-05T08:00:00"},
            "events": [{"gauge": {"name": "GAUGE_NAME",
                                  "system": "GAUGE_SYSTEM",
                                  "insertion_type": "SIMPLE_UPDATE"},
                        "start": "2018-06-05T02:00:00",
                        "stop": "2018-06-05T03:00:00",
                        "values": [{"name": "VALUES",
                                   "type": "object",
                                   "values": [
                                       {"name": "textname_1",
                                        "type": "text",
                                        "value": "textvalue_1"
                                       }]
                                   }]
                    },{"gauge": {"name": "GAUGE_NAME_2",
                                  "system": "GAUGE_SYSTEM_2",
                                  "insertion_type": "SIMPLE_UPDATE"},
                        "start": "2018-06-05T03:00:00",
                        "stop": "2018-06-05T04:00:00",
                        "values": [{"name": "VALUES",
                                   "type": "object",
                                   "values": [
                                       {"name": "textname_2",
                                        "type": "text",
                                        "value": "textvalue_2"
                                       }]
                                   }]
                    },{"gauge": {"name": "GAUGE_NAME_3",
                                  "system": "GAUGE_SYSTEM_3",
                                  "insertion_type": "SIMPLE_UPDATE"},
                        "start": "2018-06-05T04:00:00",
                        "stop": "2018-06-05T05:00:00",
                        "values": [{"name": "VALUES",
                                   "type": "object",
                                   "values": [
                                       {"name": "textname_3",
                                        "type": "text",
                                        "value": "textvalue_3"
                                       }]
                                   }]
                    }]
            }]
        }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5)

        ## == ## Full period##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_period(self.driver, wait, "events", 1,  start_value = "2018-06-05T03:00:00", start_operator = "==", end_value = "2018-06-05T04:00:00", end_operator = "==")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## >= ## Only Start##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_period(self.driver, wait, "events", 1,  start_value = "2018-06-05T03:00:00", start_operator = ">=")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        ## != ## Only End##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_period(self.driver, wait, "events", 1,  end_value = "2018-06-05T04:00:00", end_operator = "!=")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        ## > ## Only Start## < ## Only Start##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_period(self.driver, wait, "events", 1, start_value = "2018-06-05T01:30:00", start_operator = ">")
        functions.click(self.driver.find_element_by_id("events-add-start-stop"))
        functions.fill_period(self.driver, wait, "events", 2, start_value = "2018-06-05T03:00:00", start_operator = "<")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## <= ## Start## > ## End## != ## Start## >= ## End##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_period(self.driver, wait, "events", 1, start_value = "2018-06-05T03:00:00", start_operator = "<=", end_value = "2018-06-05T02:30:00", end_operator = ">")
        functions.click(self.driver.find_element_by_id("events-add-start-stop"))
        functions.fill_period(self.driver, wait, "events", 2, start_value = "2018-06-05T04:00:00", start_operator = "!=", end_value = "2018-06-05T03:00:00", end_operator = ">=")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        functions.click(submitButton)

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2
