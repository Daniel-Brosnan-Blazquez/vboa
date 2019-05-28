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


class TestEventsTab(unittest.TestCase):
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

        wait = WebDriverWait(self.driver,30);

        self.   driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        # Check gauge_name
        gauge_name = events_table.find_elements_by_xpath("tbody/tr[1]/td[2]")

        assert gauge_name[0].text == "GAUGE_NAME"

        # Check gauge_system
        gauge_system = events_table.find_elements_by_xpath("tbody/tr[1]/td[3]")

        assert gauge_system[0].text == "GAUGE_SYSTEM"

        # Check start
        start_date = events_table.find_elements_by_xpath("tbody/tr[1]/td[4]")

        assert start_date[0].text == "2018-06-05 04:07:03"

        # Check stop
        stop_date = events_table.find_elements_by_xpath("tbody/tr[1]/td[5]")

        assert stop_date[0].text == "2018-06-05 06:07:36"

        # Check duration
        duration = events_table.find_elements_by_xpath("tbody/tr[1]/td[6]")

        assert duration[0].text == str((parser.parse(stop_date[0].text) - parser.parse(start_date[0].text)).total_seconds())

        # Check ingestion_time
        ingestion_time = events_table.find_elements_by_xpath("tbody/tr[1]/td[7]")

        assert re.match("....-..-.. ..:..:...*", ingestion_time[0].text)

        #Check source
        source = events_table.find_elements_by_xpath("tbody/tr[1]/td[8]")

        assert source[0].text == "source.xml"

        #Check source
        explicit_ref = events_table.find_elements_by_xpath("tbody/tr[1]/td[9]")

        assert explicit_ref[0].text == "EXPLICIT_REFERENCE_EVENT"

        # Check uuid
        uuid = events_table.find_elements_by_xpath("tbody/tr[1]/td[11]")

        assert re.match("........-....-....-....-............", uuid[0].text)

    def test_events_query_no_filter_with_timeline(self):

        screenshot_path = os.path.dirname(os.path.abspath(__file__)) + "/screenshots/events/"

        if not os.path.exists(screenshot_path):
            os.makedirs(screenshot_path)

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

        wait = WebDriverWait(self.driver,30)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        # Click on show map
        timelineButton = self.driver.find_element_by_id("events-show-timeline")
        if not timelineButton.find_element_by_xpath("input").is_selected():
            timelineButton.click()
        # end if


        # Apply filters and click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        timeline = self.driver.find_element_by_id('events-nav-timeline')

        timeline.screenshot(screenshot_path + "timeline_events_screenshot.png")

        condition = timeline.is_displayed()

        event = self.session.query(Event).all()[0]

        assert self.driver.execute_script('return events;') == {
            "events":[{
                "id": str(event.event_uuid),
                "gauge":{
                    "name": "GAUGE_NAME",
                    "system": "GAUGE_SYSTEM"
                },
                "start": "2018-06-05 04:07:03",
                "stop": "2018-06-05 06:07:36",
                "source": "source.xml"
                }]
            }

        return condition

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

        wait = WebDriverWait(self.driver,30);

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        # Fill the source_like input
        inputElement = self.driver.find_element_by_id("events-sources-like-text")
        inputElement.send_keys("source_2.xml")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        # Fill the source_like input
        inputElement = self.driver.find_element_by_id("events-sources-like-text")
        inputElement.send_keys("source_2.xml")

        notLikeButton = self.driver.find_element_by_id("events-sources-like-checkbox")
        if not notLikeButton.find_element_by_xpath("input").is_selected():
            notLikeButton.click()
        # end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        # Fill the source_in input
        inputElement = self.driver.find_element_by_id("events-sources-in-text").find_element_by_xpath("../div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("source_1.xml")
        inputElement.send_keys(Keys.RETURN)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        # Fill the source_in input
        inputElement = self.driver.find_element_by_id("events-sources-in-text").find_element_by_xpath("../div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("source_2.xml")
        inputElement.send_keys(Keys.RETURN)

        notInButton = self.driver.find_element_by_id("events-sources-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            notInButton.click()
        # end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

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

        wait = WebDriverWait(self.driver,30);

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        # Fill the explicit_ref_like input
        inputElement = self.driver.find_element_by_id("events-explicit-refs-like-text")
        inputElement.send_keys("EXPLICIT_REFERENCE_EVENT_2")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        # Fill the explicit_ref_like input
        inputElement = self.driver.find_element_by_id("events-explicit-refs-like-text")
        inputElement.send_keys("EXPLICIT_REFERENCE_EVENT_2")

        notLikeButton = self.driver.find_element_by_id("events-explicit-refs-like-checkbox")
        if not notLikeButton.find_element_by_xpath("input").is_selected():
            notLikeButton.click()
        # end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        # Fill the explicit_ref_in input
        inputElement = self.driver.find_element_by_id("events-explicit-refs-in-text").find_element_by_xpath("../div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("EXPLICIT_REFERENCE_EVENT_1")
        inputElement.send_keys(Keys.RETURN)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        # Fill the explicit_ref_in input
        inputElement = self.driver.find_element_by_id("events-explicit-refs-in-text").find_element_by_xpath("../div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("EXPLICIT_REFERENCE_EVENT_2")
        inputElement.send_keys(Keys.RETURN)

        notInButton = self.driver.find_element_by_id("events-explicit-refs-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            notInButton.click()
        # end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

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

        wait = WebDriverWait(self.driver,30);

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        # Fill the key_like input
        inputElement = self.driver.find_element_by_id("events-event-keys-like-text")
        inputElement.send_keys("EVENT_KEY")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        # Fill the key_like input
        inputElement = self.driver.find_element_by_id("events-event-keys-like-text")
        inputElement.send_keys("EVENT_KEY")

        notLikeButton = self.driver.find_element_by_id("events-event-keys-like-checkbox")
        if not notLikeButton.find_element_by_xpath("input").is_selected():
            notLikeButton.click()
        # end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        # Fill the key_in input
        inputElement = self.driver.find_element_by_id("events-event-keys-in-text").find_element_by_xpath("../div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("EVENT_KEY_2")
        inputElement.send_keys(Keys.RETURN)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        # Fill the key_in input
        inputElement = self.driver.find_element_by_id("events-event-keys-in-text").find_element_by_xpath("../div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("EVENT_KEY")
        inputElement.send_keys(Keys.RETURN)

        notInButton = self.driver.find_element_by_id("events-event-keys-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            notInButton.click()
        # end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

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

        wait = WebDriverWait(self.driver,30);

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        # Fill the gauge_name_like input
        inputElement = self.driver.find_element_by_id("events-gauge-names-like-text")
        inputElement.send_keys("GAUGE_NAME_1")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        # Fill the gauge_name_like input
        inputElement = self.driver.find_element_by_id("events-gauge-names-like-text")
        inputElement.send_keys("GAUGE_NAME_1")

        notLikeButton = self.driver.find_element_by_id("events-gauge-names-like-checkbox")
        if not notLikeButton.find_element_by_xpath("input").is_selected():
            notLikeButton.click()
        # end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        # Fill the gauge_name_in input
        inputElement = self.driver.find_element_by_id("events-gauge-names-in-text").find_element_by_xpath("../div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("GAUGE_NAME_2")
        inputElement.send_keys(Keys.RETURN)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        ## Not In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        # Fill the gauge_name_in input
        inputElement = self.driver.find_element_by_id("events-gauge-names-in-text").find_element_by_xpath("../div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("GAUGE_NAME_1")
        inputElement.send_keys(Keys.RETURN)

        notInButton = self.driver.find_element_by_id("events-gauge-names-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            notInButton.click()
        # end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

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

        wait = WebDriverWait(self.driver,30);

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        # Fill the gauge_system_like input
        inputElement = self.driver.find_element_by_id("events-gauge-system-like-text")
        inputElement.send_keys("GAUGE_SYSTEM_1")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        # Fill the gauge_system_like input
        inputElement = self.driver.find_element_by_id("events-gauge-system-like-text")
        inputElement.send_keys("GAUGE_SYSTEM_1")

        notLikeButton = self.driver.find_element_by_id("events-gauge-system-like-checkbox")
        if not notLikeButton.find_element_by_xpath("input").is_selected():
            notLikeButton.click()
        # end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        # Fill the gauge_system_in input
        inputElement = self.driver.find_element_by_id("events-gauge-system-in-text").find_element_by_xpath("../div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("GAUGE_SYSTEM_2")
        inputElement.send_keys(Keys.RETURN)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        ## Not In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        # Fill the gauge_system_in input
        inputElement = self.driver.find_element_by_id("events-gauge-system-in-text").find_element_by_xpath("../div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("GAUGE_SYSTEM_1")
        inputElement.send_keys(Keys.RETURN)

        notInButton = self.driver.find_element_by_id("events-gauge-system-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            notInButton.click()
        # end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

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

        wait = WebDriverWait(self.driver,30);

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_value(self.driver, wait, "events", "text", "textname_1", "textvalue_1", True, "==", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_value(self.driver, wait, "events", "text", "textname_1", "textvalue_2", False, "==", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert  number_of_elements == 1 and empty_element is True

    def test_events_query_value_timestamp(self):

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

        wait = WebDriverWait(self.driver,30);

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", True, "==", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", True, "==", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element is True

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", True, ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element is True

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", True, ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", True, ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element == True

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", True, ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", True, ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", True, ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element == True

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", True, "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element is True

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", True, "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element is True

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", True, "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", True, "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", True, "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element is True

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", True, "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", True, "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element is True

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", True, "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", True, "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

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

        wait = WebDriverWait(self.driver,30);

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.5", True, "==", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.5", False, "==", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element is True

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.5", True, ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element is True

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.25", True, ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.75", True, ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element == True

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.5", True, ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.25", True, ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.75", True, ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element == True

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.5", True, "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element is True

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.25", True, "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element is True

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.75", True, "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.5", True, "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.25", True, "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element is True

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.75", True, "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.5", True, "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element is True

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.25", True, "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.75", True, "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

    def test_events_query_ingestion_time(self):

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

        wait = WebDriverWait(self.driver,30);

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_ingestion_time(self.driver, wait, "events", ingestion_time, "==", 1)
        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_ingestion_time(self.driver, wait, "events", ingestion_time, ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element is True

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_ingestion_time(self.driver, wait, "events", ingestion_time, ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_ingestion_time(self.driver, wait, "events", ingestion_time, "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element is True

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_ingestion_time(self.driver, wait, "events", ingestion_time, "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_ingestion_time(self.driver, wait, "events", ingestion_time, "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element is True

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

        wait = WebDriverWait(self.driver,30);

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_value(self.driver, wait, "events", "text", "textname_1", "textvalue_1", True, "==", 1)
        self.driver.find_element_by_id("events-add-value").click()
        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "1.4", True, "==", 2)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        assert True

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

        wait = WebDriverWait(self.driver,30);

        ## == ## Full period##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_period(self.driver, wait, "events", 1,  start_value = "2018-06-05T03:00:00", start_operator = "==", end_value = "2018-06-05T04:00:00", end_operator = "==")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## >= ## Only Start##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_period(self.driver, wait, "events", 1,  start_value = "2018-06-05T03:00:00", start_operator = ">=")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        ## != ## Only End##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_period(self.driver, wait, "events", 1,  end_value = "2018-06-05T04:00:00", end_operator = "!=")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        ## > ## Only Start## < ## Only Start##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_period(self.driver, wait, "events", 1, start_value = "2018-06-05T01:30:00", start_operator = ">")
        self.driver.find_element_by_id("events-add-start-stop").click()
        functions.fill_period(self.driver, wait, "events", 2, start_value = "2018-06-05T03:00:00", start_operator = "<")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## <= ## Start## > ## End## != ## Start## >= ## End##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        functions.fill_period(self.driver, wait, "events", 1, start_value = "2018-06-05T03:00:00", start_operator = "<=", end_value = "2018-06-05T02:30:00", end_operator = ">")
        self.driver.find_element_by_id("events-add-start-stop").click()
        functions.fill_period(self.driver, wait, "events", 2, start_value = "2018-06-05T04:00:00", start_operator = "!=", end_value = "2018-06-05T03:00:00", end_operator = ">=")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'events-submit-button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events-table")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        assert True
