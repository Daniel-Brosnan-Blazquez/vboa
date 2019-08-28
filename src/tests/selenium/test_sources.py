"""
Automated tests for the sources tab

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

class TestSourcesTab(unittest.TestCase):

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

    def test_sources_query_no_filter_no_graphs(self):

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
                           "validity_stop": "2018-06-05T08:07:36"}
            }]
        }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]
        wait = WebDriverWait(self.driver,5);

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        # Click on query button
        functions.click(submit_button)

        # Check table generatedd
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        # Check name
        name = sources_table.find_elements_by_xpath("tbody/tr[1]/td[1]")

        assert name[0].text == "source_1.xml"

        # Check validity_start
        validity_start = sources_table.find_elements_by_xpath("tbody/tr[1]/td[2]")

        assert validity_start[0].text == "2018-06-05 02:07:03"

        # Check validity_stop
        validity_stop = sources_table.find_elements_by_xpath("tbody/tr[1]/td[3]")

        assert validity_stop[0].text == "2018-06-05 08:07:36"
        # Check duration
        duration = sources_table.find_elements_by_xpath("tbody/tr[1]/td[4]")

        assert duration[0].text == str((parser.parse(validity_stop[0].text) - parser.parse(validity_start[0].text)).total_seconds())

        # Check generation_time
        generation_time = sources_table.find_elements_by_xpath("tbody/tr[1]/td[5]")

        assert generation_time[0].text == "2018-07-05 02:07:03"

        #Check ingestion_time
        ingestion_time = sources_table.find_elements_by_xpath("tbody/tr[1]/td[6]")

        assert ingestion_time[0].text == self.session.query(Source).all()[0].ingestion_time.isoformat().replace("T"," ")

        # Check ingestion_duration
        ingestion_duration = sources_table.find_elements_by_xpath("tbody/tr[1]/td[7]")

        assert re.match(".:..:.........", ingestion_duration[0].text)

        #Check dim_signature
        dim_signature = sources_table.find_elements_by_xpath("tbody/tr[1]/td[8]")

        assert dim_signature[0].text == "DIM_SIGNATURE_1"

        #Check processor
        processor = sources_table.find_elements_by_xpath("tbody/tr[1]/td[9]")

        assert processor[0].text == "exec"

        #Check version
        version = sources_table.find_elements_by_xpath("tbody/tr[1]/td[10]")

        assert version[0].text == "1.0"

        # Check uuid
        uuid = sources_table.find_elements_by_xpath("tbody/tr[1]/td[11]")

        assert re.match("........-....-....-....-............", uuid[0].text)

    def test_sources_query_no_filter_with_graphs(self):

        screenshot_path = os.path.dirname(os.path.abspath(__file__)) + "/screenshots/sources/"

        if not os.path.exists(screenshot_path):
            os.makedirs(screenshot_path)
        #end if

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
                           "validity_stop": "2018-06-05T08:07:36"}
            }]
        }


        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5);

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        # Click on show validity_timeline
        validity_timeline_button = self.driver.find_element_by_id("sources-show-validity-timeline")
        if not validity_timeline_button.find_element_by_xpath('input').is_selected():
            functions.select_checkbox(validity_timeline_button)
        #end if

        # Click on show gen2ing_timeline
        gen2ing_timeline_button = self.driver.find_element_by_id("sources-show-generation-to-ingestion-timeline")
        if not gen2ing_timeline_button.find_element_by_xpath('input').is_selected():
            functions.select_checkbox(gen2ing_timeline_button)
        #end if

        # Click on show number_events_per_source
        number_events_per_source_button = self.driver.find_element_by_id("sources-show-number-events-xy")
        if not number_events_per_source_button.find_element_by_xpath('input').is_selected():
            functions.select_checkbox(number_events_per_source_button)
        #end if

        # Click on show ingestion_duration
        ingestion_duration_button = self.driver.find_element_by_id("sources-show-ingestion-duration-xy")
        if not ingestion_duration_button.find_element_by_xpath('input').is_selected():
            functions.select_checkbox(ingestion_duration_button)
        #end if

        # Click on show gen2ing_times
        gen2ing_times_button = self.driver.find_element_by_id("sources-show-generation-time-to-ingestion-time-xy")
        if not gen2ing_times_button.find_element_by_xpath('input').is_selected():
            functions.select_checkbox(gen2ing_times_button)
        #end if

        # Click on query button
        functions.click(submit_button)

        source = self.session.query(Source).all()[0]

        assert self.driver.execute_script('return sources;') == [{
                "id": str(source.source_uuid),
                "name": "source_1.xml",
                "dim_signature": "DIM_SIGNATURE_1",
                "processor": "exec",
                "version": "1.0",
                "validity_start": "2018-06-05 02:07:03",
                "validity_stop": "2018-06-05 08:07:36",
                "ingestion_time": source.ingestion_time.isoformat().replace("T"," "),
                "ingestion_duration": str(source.ingestion_duration),
                "generation_time": "2018-07-05 02:07:03",
                "number_of_events": "0"
                }]

        validity_timeline = self.driver.find_element_by_id("sources-nav-validity-timeline")

        validity_timeline.screenshot(screenshot_path + "validity_timeline_sources_screenshot.png")

        gen2ing_timeline = self.driver.find_element_by_id("sources-nav-generation-to-ingestion-timeline")

        gen2ing_timeline.screenshot(screenshot_path + "gen2ing_timeline_sources_screenshot.png")

        number_events_per_source = self.driver.find_element_by_id("sources-nav-number-events-xy")

        number_events_per_source.screenshot(screenshot_path + "number_events_per_source_sources_screenshot.png")

        ingestion_duration = self.driver.find_element_by_id("sources-nav-ingestion-duration-xy")

        ingestion_duration.screenshot(screenshot_path + "ingestion_duration_sources_screenshot.png")

        gen2ing_time = self.driver.find_element_by_id("sources-nav-generation-time-to-ingestion-time-xy")

        gen2ing_time.screenshot(screenshot_path + "gen2ing_time_sources_screenshot.png")

        condition = validity_timeline.is_displayed() and gen2ing_timeline.is_displayed() and number_events_per_source.is_displayed() and ingestion_duration.is_displayed() and gen2ing_time.is_displayed()

        assert condition

    def test_sources_query_name_filter(self):

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
                               "validity_stop": "2018-06-05T02:08:12"}
            },{
                "mode": "insert",
                "dim_signature": {
                      "name": "DIM_SIGNATURE_2",
                      "exec": "exec_2",
                      "version": "1.0"
                },
                "source":  {"name": "source_2.xml",
                        "reception_time": "2018-07-05T02:07:03",
                               "generation_time": "2018-07-06T12:35:24",
                               "validity_start": "2018-06-06T12:35:28",
                               "validity_stop": "2018-06-06T12:38:14"}
            },{
                "mode": "insert",
                "dim_signature": {
                      "name": "DIM_SIGNATURE_2",
                      "exec": "exec",
                      "version": "1.0"
                },
                "source":  {"name": "source_3.xml",
                        "reception_time": "2018-07-05T02:07:03",
                               "generation_time": "2018-07-06T14:10:04",
                               "validity_start": "2018-06-06T22:02:04",
                               "validity_stop": "2018-06-06T23:08:45"}
                }
        ]}

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5);

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        # Fill the source_like input
        inputElement = self.driver.find_element_by_id("sources-source-names-like-text")
        inputElement.send_keys("source_2.xml")

        # Click on query button
        functions.click(submit_button)

        # Check table generatedd
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        # Fill the source_like input
        inputElement = self.driver.find_element_by_id("sources-source-names-like-text")
        inputElement.send_keys("source_2.xml")

        notLikeButton = self.driver.find_element_by_id("sources-source-names-like-checkbox")
        if not notLikeButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notLikeButton)
        #end if

        # Click on query button
        functions.click(submit_button)

        # Check table generatedd
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        # Fill the source_in input
        inputElement = self.driver.find_element_by_id("sources-source-names-in-text").find_element_by_xpath("../div/ul/li/input")
        functions.click(inputElement)

        assert len(self.driver.find_element_by_id("sources-source-names-in-text").find_elements_by_xpath("option")) == 3

        inputElement.send_keys("source_2.xml")
        inputElement.send_keys(Keys.RETURN)
        functions.click(inputElement)
        inputElement.send_keys("source_3.xml")
        inputElement.send_keys(Keys.RETURN)

        # Click on query button
        functions.click(submit_button)

        # Check table generatedd
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        # Fill the source_in input
        inputElement = self.driver.find_element_by_id("sources-source-names-in-text").find_element_by_xpath("../div/ul/li/input")
        functions.click(inputElement)

        assert len(self.driver.find_element_by_id("sources-source-names-in-text").find_elements_by_xpath("option")) == 3

        inputElement.send_keys("source_3.xml")
        inputElement.send_keys(Keys.RETURN)

        notInButton = self.driver.find_element_by_id("sources-source-names-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        #end if

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

    def test_sources_query_processor_filter(self):

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
                               "validity_stop": "2018-06-05T02:08:12"}
            },{
                "mode": "insert",
                "dim_signature": {
                      "name": "DIM_SIGNATURE_2",
                      "exec": "exec_2",
                      "version": "1.0"
                },
                "source":  {"name": "source_2.xml",
                        "reception_time": "2018-07-05T02:07:03",
                               "generation_time": "2018-07-06T12:35:24",
                               "validity_start": "2018-06-06T12:35:28",
                               "validity_stop": "2018-06-06T12:38:14"}
            },{
                "mode": "insert",
                "dim_signature": {
                      "name": "DIM_SIGNATURE_2",
                      "exec": "exec",
                      "version": "1.0"
                },
                "source":  {"name": "source_3.xml",
                        "reception_time": "2018-07-05T02:07:03",
                               "generation_time": "2018-07-06T14:10:04",
                               "validity_start": "2018-06-06T22:02:04",
                               "validity_stop": "2018-06-06T23:08:45"}
                }
        ]}

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5);

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        # Fill the processor_like input
        inputElement = self.driver.find_element_by_id("sources-processors-like-text")
        inputElement.send_keys("exec_2")

        # Click on query button
        functions.click(submit_button)

        # Check table generatedd
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        # Fill the processor_like input
        inputElement = self.driver.find_element_by_id("sources-processors-like-text")
        inputElement.send_keys("exec_2")

        notLikeButton = self.driver.find_element_by_id("sources-processors-like-checkbox")
        if not notLikeButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notLikeButton)
        #end if

        # Click on query button
        functions.click(submit_button)

        # Check table generatedd
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        # Fill the processor_in input
        inputElement = self.driver.find_element_by_id("sources-processors-in-text").find_element_by_xpath("../div/ul/li/input")
        functions.click(inputElement)

        assert len(self.driver.find_element_by_id("sources-processors-in-text").find_elements_by_xpath("option")) == 2

        inputElement.send_keys("exec")
        inputElement.send_keys(Keys.RETURN)

        # Click on query button
        functions.click(submit_button)

        # Check table generatedd
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        # Fill the processor_in input
        inputElement = self.driver.find_element_by_id("sources-processors-in-text").find_element_by_xpath("../div/ul/li/input")
        functions.click(inputElement)

        assert len(self.driver.find_element_by_id("sources-processors-in-text").find_elements_by_xpath("option")) == 2

        inputElement.send_keys("exec_2")
        inputElement.send_keys(Keys.RETURN)

        notInButton = self.driver.find_element_by_id("sources-processors-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        #end if

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

    def test_sources_query_dim_signature_filter(self):

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
                               "validity_stop": "2018-06-05T02:08:12"}
            },{
                "mode": "insert",
                "dim_signature": {
                      "name": "DIM_SIGNATURE_2",
                      "exec": "exec_2",
                      "version": "1.0"
                },
                "source":  {"name": "source_2.xml",
                        "reception_time": "2018-07-05T02:07:03",
                               "generation_time": "2018-07-06T12:35:24",
                               "validity_start": "2018-06-06T12:35:28",
                               "validity_stop": "2018-06-06T12:38:14"}
            },{
                "mode": "insert",
                "dim_signature": {
                      "name": "DIM_SIGNATURE_3",
                      "exec": "exec",
                      "version": "1.0"
                },
                "source":  {"name": "source_3.xml",
                        "reception_time": "2018-07-05T02:07:03",
                               "generation_time": "2018-07-06T14:10:04",
                               "validity_start": "2018-06-06T22:02:04",
                               "validity_stop": "2018-06-06T23:08:45"}
                }
        ]}

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5);

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        # Fill the dim_signature_like input
        inputElement = self.driver.find_element_by_id("sources-dim-signatures-like-text")
        inputElement.send_keys("DIM_SIGNATURE_2")

        # Click on query button
        functions.click(submit_button)

        # Check table generatedd
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        # Fill the dim_signature_like input
        inputElement = self.driver.find_element_by_id("sources-dim-signatures-like-text")
        inputElement.send_keys("DIM_SIGNATURE_2")

        notLikeButton = self.driver.find_element_by_id("sources-dim-signatures-like-checkbox")
        if not notLikeButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notLikeButton)
        #end if

        # Click on query button
        functions.click(submit_button)

        # Check table generatedd
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        # Fill the dim_signature_in input
        inputElement = self.driver.find_element_by_id("sources-dim-signatures-in-text").find_element_by_xpath("../div/ul/li/input")
        functions.click(inputElement)

        assert len(self.driver.find_element_by_id("sources-dim-signatures-in-text").find_elements_by_xpath("option")) == 3

        inputElement.send_keys("DIM_SIGNATURE_1")
        inputElement.send_keys(Keys.RETURN)
        functions.click(inputElement)
        inputElement.send_keys("DIM_SIGNATURE_2")
        inputElement.send_keys(Keys.RETURN)

        # Click on query button
        functions.click(submit_button)

        # Check table generatedd
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        # Fill the dim_signature_in input
        inputElement = self.driver.find_element_by_id("sources-dim-signatures-in-text").find_element_by_xpath("../div/ul/li/input")
        functions.click(inputElement)

        assert len(self.driver.find_element_by_id("sources-dim-signatures-in-text").find_elements_by_xpath("option")) == 3

        inputElement.send_keys("DIM_SIGNATURE_3")
        inputElement.send_keys(Keys.RETURN)

        notInButton = self.driver.find_element_by_id("sources-dim-signatures-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        #end if

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

    def test_sources_query_period(self):

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
                               "validity_start": "2018-06-05T02:00:00",
                               "validity_stop": "2018-06-05T03:00:00"}
            },{
                "mode": "insert",
                "dim_signature": {
                      "name": "DIM_SIGNATURE_2",
                      "exec": "exec_2",
                      "version": "1.0"
                },
                "source":  {"name": "source_2.xml",
                        "reception_time": "2018-07-05T02:07:03",
                               "generation_time": "2018-07-05T02:07:03",
                               "validity_start": "2018-06-05T03:00:00",
                               "validity_stop": "2018-06-05T04:00:00"}
            },{
                "mode": "insert",
                "dim_signature": {
                      "name": "DIM_SIGNATURE_3",
                      "exec": "exec",
                      "version": "1.0"
                },
                "source":  {"name": "source_3.xml",
                        "reception_time": "2018-07-05T02:07:03",
                               "generation_time": "2018-07-05T02:07:03",
                               "validity_start": "2018-06-05T04:00:00",
                               "validity_stop": "2018-06-05T05:00:00"}
                }
        ]}

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5);

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_validity_period(self.driver, wait, "sources", 1, "2018-06-05T03:00:00", "==","2018-06-05T04:00:00", "==")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_validity_period(self.driver, wait, "sources", 1, start_value = "2018-06-05T03:00:00", start_operator = ">=")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_validity_period(self.driver, wait, "sources", 1, end_value = "2018-06-05T04:00:00", end_operator = "!=")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        ## > ## Only Start ## < ## Only Start ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_validity_period(self.driver, wait, "sources", 1, start_value = "2018-06-05T01:30:00", start_operator = ">")
        functions.click(self.driver.find_element_by_id("sources-add-validity-start-validity-stop"))

        functions.fill_validity_period(self.driver, wait, "sources", 2, start_value = "2018-06-05T03:00:00", start_operator = "<")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## <= ## Start ## > ## End ## != ## Start ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_validity_period(self.driver, wait, "sources", 1, start_value = "2018-06-05T03:00:00", start_operator = "<=", end_value = "2018-06-05T02:30:00", end_operator = ">")
        functions.click(self.driver.find_element_by_id("sources-add-validity-start-validity-stop"))
        functions.fill_validity_period(self.driver, wait, "sources", 2, start_value = "2018-06-05T04:00:00", start_operator = "!=", end_value = "2018-06-05T03:00:00", end_operator = ">=")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

    def test_sources_query_ingestion_time(self):

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
                    }]
                }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        ingestion_time = self.session.query(Source).all()[0].ingestion_time.isoformat()

        wait = WebDriverWait(self.driver,5);

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_ingestion_time(self.driver, wait,"sources", ingestion_time, "==", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## == and < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_ingestion_time(self.driver, wait,"sources", ingestion_time, "==", 1)
        functions.click(self.driver.find_element_by_id("sources-add-ingestion-time"))
        functions.fill_ingestion_time(self.driver, wait,"sources", "9999-01-01T00:00:00", "<", 2)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_ingestion_time(self.driver, wait,"sources",ingestion_time, ">", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element is True

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_ingestion_time(self.driver, wait,"sources", ingestion_time, ">=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_ingestion_time(self.driver, wait,"sources", ingestion_time, "<", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element is True

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_ingestion_time(self.driver, wait,"sources", ingestion_time, "<=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_ingestion_time(self.driver, wait,"sources", ingestion_time, "!=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element is True

    def test_sources_query_generation_time(self):

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
                    }]
                }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5);

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_generation_time(self.driver, wait,"sources", "2018-07-05T02:07:03", "==", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_generation_time(self.driver, wait,"sources", "2018-07-05T02:07:03", ">", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element is True

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_generation_time(self.driver, wait,"sources", "2018-07-05T02:07:03", ">=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_generation_time(self.driver, wait,"sources", "2018-07-05T02:07:03", "<", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element is True

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_generation_time(self.driver, wait,"sources", "2018-07-05T02:07:03", "<=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_generation_time(self.driver, wait,"sources", "2018-07-05T02:07:03", "!=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element is True

    def test_sources_query_value_ingestion_duration(self):

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
                    }]
                }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        ingestion_duration = str(self.session.query(Source).all()[0].ingestion_duration.total_seconds())

        wait = WebDriverWait(self.driver,5);

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_ingestion_duration(self.driver, wait, "sources", ingestion_duration, "==", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_ingestion_duration(self.driver, wait, "sources", ingestion_duration, ">", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is True

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_ingestion_duration(self.driver, wait, "sources", ingestion_duration, ">=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_ingestion_duration(self.driver, wait, "sources", ingestion_duration, "<", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is True

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_ingestion_duration(self.driver, wait, "sources", ingestion_duration, "<=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_ingestion_duration(self.driver, wait, "sources", ingestion_duration, "!=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is True

    def test_sources_query_value_statuses(self):
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
                               "validity_stop": "2018-06-05T02:08:12"}
            }
        ]}

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        assert eboa_engine.exit_codes["SOURCE_ALREADY_INGESTED"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5);

        ## OK Status ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        # Fill the status_in input
        inputElement = self.driver.find_element_by_id("sources-statuses-initial-in-text").find_element_by_xpath("../div/ul/li/input")
        functions.click(inputElement)

        assert len(self.driver.find_element_by_id("sources-statuses-initial-in-text").find_elements_by_xpath("option")) == 20

        inputElement.send_keys("OK")
        inputElement.send_keys(Keys.RETURN)

        # Click on query button
        functions.click(submit_button)

        # Check table generatedd
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not OK Status ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        # Fill the status_in input
        inputElement = self.driver.find_element_by_id("sources-statuses-initial-in-text").find_element_by_xpath("../div/ul/li/input")
        functions.click(inputElement)

        assert len(self.driver.find_element_by_id("sources-statuses-initial-in-text").find_elements_by_xpath("option")) == 20

        inputElement.send_keys("OK")
        inputElement.send_keys(Keys.RETURN)

        notInButton = self.driver.find_element_by_id("sources-statuses-initial-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        #end if

        # Click on query button
        functions.click(submit_button)

        # Check table generatedd
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False
