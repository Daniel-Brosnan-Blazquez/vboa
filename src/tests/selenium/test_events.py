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
import tests.selenium.functions as functions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
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


class TestEngine(unittest.TestCase):
    def setUp(self):
        # Create the engine to manage the data
        self.engine_eboa = Engine()
        self.query_eboa = Query()

        # Create session to connect to the database
        self.session = Session()

        # Clear all tables before executing the test
        self.query_eboa.clear_db()

        self.options = Options()
        self.options.headless = True
        subprocess.call(["pkill", "firefox"])

    def tearDown(self):
        # Close connections to the DDBB
        self.engine_eboa.close_session()
        self.query_eboa.close_session()
        self.session.close()

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

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[12]/button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))

        driver.quit()

        assert number_of_elements == 2

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

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        # Click on show map
        timelineButton = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[11]/label")
        if not timelineButton.find_element_by_xpath('input').is_selected():
            timelineButton.click()
        # end if

        # Apply filters and click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[12]/button')))
        submitButton.click()

        timeline = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[1]/div[3]/div[2]')

        timeline.screenshot(screenshot_path + "timeline_events_screenshot.png")

        condition = timeline.is_displayed()

        event = self.session.query(Event).all()[0]

        assert driver.execute_script('return events;') == {
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

        driver.quit()

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

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        ## Like ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        # Fill the source_like input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[1]/div[1]/input")
        inputElement.send_keys("source_2.xml")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[12]/button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not Like ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        # Fill the source_like input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[1]/div[1]/input")
        inputElement.send_keys("source_2.xml")

        notLikeButton = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[1]/div[1]/label")
        if not notLikeButton.find_element_by_xpath("input").is_selected():
            notLikeButton.click()
        # end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[12]/button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## In ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        # Fill the source_in input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[1]/div[2]/div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("source_1.xml")
        inputElement.send_keys(Keys.RETURN)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[12]/button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not In ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        # Fill the source_in input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[1]/div[2]/div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("source_2.xml")
        inputElement.send_keys(Keys.RETURN)

        notInButton = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[1]/div[2]/label")
        if not notInButton.find_element_by_xpath("input").is_selected():
            notInButton.click()
        # end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[12]/button')))
        submitButton.click()

        # Check table generate
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        driver.quit()

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

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        ## Like ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        # Fill the explicit_ref_like input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[2]/div[1]/input")
        inputElement.send_keys("EXPLICIT_REFERENCE_EVENT_2")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[12]/button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not Like ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        # Fill the explicit_ref_like input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[2]/div[1]/input")
        inputElement.send_keys("EXPLICIT_REFERENCE_EVENT_2")

        notLikeButton = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[2]/div[1]/label")
        if not notLikeButton.find_element_by_xpath("input").is_selected():
            notLikeButton.click()
        # end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[12]/button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## In ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        # Fill the explicit_ref_in input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[2]/div[2]/div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("EXPLICIT_REFERENCE_EVENT_1")
        inputElement.send_keys(Keys.RETURN)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[12]/button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not In ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        # Fill the explicit_ref_in input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[2]/div[2]/div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("EXPLICIT_REFERENCE_EVENT_2")
        inputElement.send_keys(Keys.RETURN)

        notInButton = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[2]/div[2]/label")
        if not notInButton.find_element_by_xpath("input").is_selected():
            notInButton.click()
        # end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[12]/button')))
        submitButton.click()

        # Check table generate
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        driver.quit()

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

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        ## Like ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        # Fill the key_like input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[3]/div[1]/input")
        inputElement.send_keys("EVENT_KEY")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[12]/button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not Like ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        # Fill the key_like input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[3]/div[1]/input")
        inputElement.send_keys("EVENT_KEY")

        notLikeButton = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[3]/div[1]/label")
        if not notLikeButton.find_element_by_xpath("input").is_selected():
            notLikeButton.click()
        # end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[12]/button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## In ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        # Fill the key_in input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[3]/div[2]/div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("EVENT_KEY_2")
        inputElement.send_keys(Keys.RETURN)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[12]/button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not In ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        # Fill the key_in input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[3]/div[2]/div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("EVENT_KEY")
        inputElement.send_keys(Keys.RETURN)

        notInButton = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[3]/div[2]/label")
        if not notInButton.find_element_by_xpath("input").is_selected():
            notInButton.click()
        # end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[12]/button')))
        submitButton.click()

        # Check table generate
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        driver.quit()

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

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        ## Like ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        # Fill the gauge_name_like input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[4]/div[1]/div[1]/input")
        inputElement.send_keys("GAUGE_NAME_1")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[12]/button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not Like ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        # Fill the gauge_name_like input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[4]/div[1]/div[1]/input")
        inputElement.send_keys("GAUGE_NAME_1")

        notLikeButton = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[4]/div[1]/div[1]/label")
        if not notLikeButton.find_element_by_xpath("input").is_selected():
            notLikeButton.click()
        # end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[12]/button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        ## In ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        # Fill the gauge_name_in input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[4]/div[2]/div[1]/div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("GAUGE_NAME_2")
        inputElement.send_keys(Keys.RETURN)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[12]/button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        ## Not In ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        # Fill the gauge_name_in input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[4]/div[2]/div[1]/div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("GAUGE_NAME_1")
        inputElement.send_keys(Keys.RETURN)

        notInButton = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[4]/div[2]/div[1]/label")
        if not notInButton.find_element_by_xpath("input").is_selected():
            notInButton.click()
        # end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[12]/button')))
        submitButton.click()

        # Check table generate
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        driver.quit()

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

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        ## Like ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        # Fill the gauge_system_like input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[4]/div[1]/div[2]/input")
        inputElement.send_keys("GAUGE_SYSTEM_1")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[12]/button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not Like ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        # Fill the gauge_system_like input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[4]/div[1]/div[2]/input")
        inputElement.send_keys("GAUGE_SYSTEM_1")

        notLikeButton = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[4]/div[1]/div[2]/label")
        if not notLikeButton.find_element_by_xpath("input").is_selected():
            notLikeButton.click()
        # end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[12]/button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        ## In ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        # Fill the gauge_system_in input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[4]/div[2]/div[2]/div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("GAUGE_SYSTEM_2")
        inputElement.send_keys(Keys.RETURN)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[12]/button')))
        submitButton.click()

        # Check table generated
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        ## Not In ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        # Fill the gauge_system_in input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[4]/div[2]/div[2]/div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("GAUGE_SYSTEM_1")
        inputElement.send_keys(Keys.RETURN)

        notInButton = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[4]/div[2]/div[2]/label")
        if not notInButton.find_element_by_xpath("input").is_selected():
            notInButton.click()
        # end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[12]/button')))
        submitButton.click()

        # Check table generate
        events_table = wait.until(EC.visibility_of_element_located((By.ID,"events")))
        number_of_elements = len(events_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(events_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        driver.quit()

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
                                                    "name": "text_name_1",
                                                    "value": "text_value_1"
                                                    }]
                                                }]
                        }]
                    }]
                }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        ## == ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "events", "text", "text_name_1", "text_value_1", True, "==")

        assert number_of_elements == 1 and empty_element is False

        ## Not Like ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "events", "text", "text_name_1", "text_value_2", False, "==")

        driver.quit()

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

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        ## == ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", True, "==")

        assert number_of_elements == 1 and empty_element is False

        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", True, "==")

        assert empty_element is True

        ## > ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", True, ">")

        assert empty_element is True

        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", True, ">")

        assert number_of_elements == 1 and empty_element is False

        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", True, ">")

        assert empty_element == True

        ## >= ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", True, ">=")

        assert number_of_elements == 1 and empty_element is False

        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", True, ">=")

        assert number_of_elements == 1 and empty_element is False

        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", True, ">=")

        assert empty_element == True

        ## < ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", True, "<")

        assert empty_element is True

        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", True, "<")

        assert empty_element is True

        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", True, "<")

        assert number_of_elements == 1 and empty_element is False

        ## <= ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", True, "<=")

        assert number_of_elements == 1 and empty_element is False

        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", True, "<=")

        assert empty_element is True

        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", True, "<=")

        assert number_of_elements == 1 and empty_element is False

        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", True, "!=")

        assert empty_element is True

        ## != ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", True, "!=")

        assert number_of_elements == 1 and empty_element is False

        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", True, "!=")

        driver.quit()

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

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        ## == ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "events", "double", "double_name_1", "3.5", True, "==")

        assert number_of_elements == 1 and empty_element is False
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "events", "double", "double_name_1", "3.5", False, "==")

        assert empty_element is True

        ## > ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "events", "double", "double_name_1", "3.5", True, ">")

        assert empty_element is True

        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "events", "double", "double_name_1", "3.25", True, ">")

        assert number_of_elements == 1 and empty_element is False

        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "events", "double", "double_name_1", "3.75", True, ">")

        assert empty_element == True

        ## >= ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "events", "double", "double_name_1", "3.5", True, ">=")

        assert number_of_elements == 1 and empty_element is False

        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "events", "double", "double_name_1", "3.25", True, ">=")

        assert number_of_elements == 1 and empty_element is False

        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "events", "double", "double_name_1", "3.75", True, ">=")

        assert empty_element == True

        ## < ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "events", "double", "double_name_1", "3.5", True, "<")

        assert empty_element is True

        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "events", "double", "double_name_1", "3.25", True, "<")

        assert empty_element is True

        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "events", "double", "double_name_1", "3.75", True, "<")

        assert number_of_elements == 1 and empty_element is False

        ## <= ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "events", "double", "double_name_1", "3.5", True, "<=")

        assert number_of_elements == 1 and empty_element is False

        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "events", "double", "double_name_1", "3.25", True, "<=")

        assert empty_element is True

        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "events", "double", "double_name_1", "3.75", True, "<=")

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "events", "double", "double_name_1", "3.5", True, "!=")

        assert empty_element is True

        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "events", "double", "double_name_1", "3.25", True, "!=")

        assert number_of_elements == 1 and empty_element is False

        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "events", "double", "double_name_1", "3.75", True, "!=")

        driver.quit()

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

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        ## == ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element =  functions.value_comparer(driver, wait, "events", "ingestion_time", ingestion_time, None, True, "==")

        assert number_of_elements == 1 and empty_element is False

        ## > ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element =  functions.value_comparer(driver, wait, "events", "ingestion_time", ingestion_time, None, True, ">")

        assert empty_element is True

        ## >= ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element =  functions.value_comparer(driver, wait, "events", "ingestion_time", ingestion_time, None, True, ">=")

        assert number_of_elements == 1 and empty_element is False

        ## < ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element =  functions.value_comparer(driver, wait, "events", "ingestion_time", ingestion_time, None, True, "<")

        assert empty_element is True

        ## <= ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element =  functions.value_comparer(driver, wait, "events", "ingestion_time", ingestion_time, None, True, "<=")

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element =  functions.value_comparer(driver, wait, "events", "ingestion_time", ingestion_time, None, True, "!=")

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

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element =  functions.two_values_comparer(driver, wait, "events", "text", "double", "text_name_1", "text_value_1", "double_name_1", "1.4", True, True, "==", "==")

        assert number_of_elements == 1 and empty_element is False

        driver.quit()

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
                                       {"name": "text_name_1",
                                        "type": "text",
                                        "value": "text_value_1"
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
                                       {"name": "text_name_2",
                                        "type": "text",
                                        "value": "text_value_2"
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

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        ## == ## Full period##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element =  functions.period_comparer(driver, wait, "events", start_value = "2018-06-05T03:00:00", start_operator = "==", end_value = "2018-06-05T04:00:00", end_operator = "==")

        assert number_of_elements == 1 and empty_element is False

        ## >= ## Only Start##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element =  functions.period_comparer(driver, wait, "events", start_value = "2018-06-05T03:00:00", start_operator = ">=")

        assert number_of_elements == 2

        ## != ## Only End##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element =  functions.period_comparer(driver, wait, "events", end_value = "2018-06-05T04:00:00", end_operator = "!=")

        assert number_of_elements == 2

        ## > ## Only Start## < ## Only Start##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element =  functions.two_periods_comparer(driver, wait, "events", start_value_1 = "2018-06-05T01:30:00", start_operator_1 = ">", start_value_2 = "2018-06-05T03:00:00", start_operator_2 = "<")

        assert number_of_elements == 1 and empty_element is False

        ## <= ## Start## > ## End## != ## Start## >= ## End##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element =  functions.two_periods_comparer(driver, wait, "events", start_value_1 = "2018-06-05T03:00:00", start_operator_1 = "<=", end_value_1 = "2018-06-05T02:30:00", end_operator_1 = ">",
        start_value_2 = "2018-06-05T04:00:00", start_operator_2 = "!=", end_value_2 = "2018-06-05T03:00:00", end_operator_2 = ">=")

        assert number_of_elements == 2

        driver.quit()

        assert True
