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
import vboa.tests.selenium.functions as functions
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
    
    def test_sources_no_data(self):

        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"sources-nav-no-data")))

        assert no_data

    def test_sources_query_no_filter_no_graphs(self):

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
                            "validity_stop": "2018-06-05T08:07:36",
                            "priority": 10,
                            "ingestion_completeness": {
                                    "check": "false",
                                    "message": "MISSING DEPENDENCIES"}
                }
        }]}

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]
        
        wait = WebDriverWait(self.driver,5)

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

        assert name[0].text == "source.xml"

        # Check validity_start
        validity_start = sources_table.find_elements_by_xpath("tbody/tr[1]/td[4]")

        assert validity_start[0].text == "2018-06-05T02:07:03"

        # Check validity_stop
        validity_stop = sources_table.find_elements_by_xpath("tbody/tr[1]/td[5]")

        assert validity_stop[0].text == "2018-06-05T08:07:36"
        
        # Check duration
        duration = sources_table.find_elements_by_xpath("tbody/tr[1]/td[6]")

        assert duration[0].text == str((parser.parse(validity_stop[0].text) - parser.parse(validity_start[0].text)).total_seconds())

        # Check generation_time
        generation_time = sources_table.find_elements_by_xpath("tbody/tr[1]/td[7]")

        assert generation_time[0].text == "2018-07-05T02:07:03"

        #Check priority
        priority = sources_table.find_elements_by_xpath("tbody/tr[1]/td[8]")

        assert priority[0].text == "10"
        
        #Check reception_time
        reception_time = sources_table.find_elements_by_xpath("tbody/tr[1]/td[9]")

        assert reception_time[0].text == self.session.query(Source).all()[0].reception_time.isoformat()
        
        #Check ingestion_time
        ingestion_time = sources_table.find_elements_by_xpath("tbody/tr[1]/td[10]")

        assert ingestion_time[0].text == self.session.query(Source).all()[0].ingestion_time.isoformat()

        # Check ingestion_duration
        ingestion_duration = sources_table.find_elements_by_xpath("tbody/tr[1]/td[11]")

        assert re.match(".:..:.........", ingestion_duration[0].text)

        # Check processing_duration
        processing_duration = sources_table.find_elements_by_xpath("tbody/tr[1]/td[12]")

        assert processing_duration[0].text == "None"

        # Check reported_validity_start
        reported_validity_start = sources_table.find_elements_by_xpath("tbody/tr[1]/td[13]")

        assert reported_validity_start[0].text == "2018-06-05T02:07:03"

        # Check reported_validity_stop
        reported_validity_stop = sources_table.find_elements_by_xpath("tbody/tr[1]/td[14]")

        assert reported_validity_stop[0].text == "2018-06-05T08:07:36"
        
        # Check duration
        duration = sources_table.find_elements_by_xpath("tbody/tr[1]/td[15]")

        assert duration[0].text == str((parser.parse(reported_validity_stop[0].text) - parser.parse(reported_validity_start[0].text)).total_seconds())

        #Check reported_generation_time
        reported_generation_time = sources_table.find_elements_by_xpath("tbody/tr[1]/td[16]")

        assert reported_generation_time[0].text == self.session.query(Source).all()[0].reported_generation_time.isoformat()
        
        #Check ingestion_completeness
        ingestion_completeness = sources_table.find_elements_by_xpath("tbody/tr[1]/td[17]")

        assert ingestion_completeness[0].text == "False"

        #Check ingestion_completeness_message
        ingestion_completeness_message = sources_table.find_elements_by_xpath("tbody/tr[1]/td[18]")

        assert ingestion_completeness_message[0].text == "MISSING DEPENDENCIES"
        
        #Check dim_signature
        dim_signature = sources_table.find_elements_by_xpath("tbody/tr[1]/td[19]")

        assert dim_signature[0].text == "dim_signature"

        #Check processor
        processor = sources_table.find_elements_by_xpath("tbody/tr[1]/td[20]")

        assert processor[0].text == "exec"

        #Check version
        version = sources_table.find_elements_by_xpath("tbody/tr[1]/td[21]")

        assert version[0].text == "1.0"

        # Check uuid
        uuid = sources_table.find_elements_by_xpath("tbody/tr[1]/td[22]")

        assert re.match("........-....-....-....-............", uuid[0].text)

    def test_sources_query_no_filter_with_graphs(self):

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
                            "validity_stop": "2018-06-05T08:07:36",
                            "priority": 10,
                            "ingestion_completeness": {
                                    "check": "false",
                                    "message": "MISSING DEPENDENCIES"}
                }
        }]}


        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5)

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
                "name": "source.xml",
                "dim_signature": "dim_signature",
                "processor": "exec",
                "version": "1.0",
                "validity_start": "2018-06-05T02:07:03",
                "validity_stop": "2018-06-05T08:07:36",
                "reported_validity_start": "2018-06-05T02:07:03",
                "reported_validity_stop": "2018-06-05T08:07:36",
                "reception_time": source.reception_time.isoformat(),
                "ingestion_time": source.ingestion_time.isoformat(),
                "processing_duration": "0:00:00",
                "ingestion_duration": str(source.ingestion_duration),
                "generation_time": "2018-07-05T02:07:03",
                "reported_generation_time": "2018-07-05T02:07:03",
                "number_of_events": "0",
                "priority": str(source.priority),
                "ingestion_completeness": "False",
                "ingestion_completeness_message": "MISSING DEPENDENCIES",
                "ingestion_error": "False" 
                }]

        validity_timeline = self.driver.find_element_by_id("sources-nav-validity-timeline")

        gen2ing_timeline = self.driver.find_element_by_id("sources-nav-generation-to-ingestion-timeline")

        number_events_per_source = self.driver.find_element_by_id("sources-nav-number-events-xy")

        ingestion_duration = self.driver.find_element_by_id("sources-nav-ingestion-duration-xy")

        gen2ing_time = self.driver.find_element_by_id("sources-nav-generation-time-to-ingestion-time-xy")

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

        wait = WebDriverWait(self.driver,5)

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        # Fill the source input
        input_element = self.driver.find_element_by_id("sources-source-name-text")
        input_element.send_keys("source_2.xml")

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

        # Fill the source input
        input_element = self.driver.find_element_by_id("sources-source-name-text")
        input_element.send_keys("source_2.xml")

        menu = Select(self.driver.find_element_by_id("sources-source-operator"))
        menu.select_by_visible_text("notlike")

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
        input_element = self.driver.find_element_by_id("sources-source-names-in-text")
        functions.click(input_element)

        input_element.send_keys("source_2.xml")
        input_element.send_keys(Keys.LEFT_SHIFT)
        input_element.clear()
        input_element.send_keys("source_3.xml")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("sources-source-names-in-select"))
        options.select_by_visible_text("source_2.xml")
        options.select_by_visible_text("source_3.xml")

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
        input_element = self.driver.find_element_by_id("sources-source-names-in-text")
        functions.click(input_element)

        input_element.send_keys("source_3.xml")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("sources-source-names-in-select"))
        options.select_by_visible_text("source_3.xml")

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

        wait = WebDriverWait(self.driver,5)

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        # Fill the processor input
        input_element = self.driver.find_element_by_id("sources-processor-text")
        input_element.send_keys("exec_2")

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

        # Fill the processor input
        input_element = self.driver.find_element_by_id("sources-processor-text")
        input_element.send_keys("exec_2")

        menu = Select(self.driver.find_element_by_id("sources-processor-operator"))
        menu.select_by_visible_text("notlike")

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
        input_element = self.driver.find_element_by_id("sources-processors-in-text")
        functions.click(input_element)

        input_element.send_keys("exec")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("sources-processors-in-select"))
        options.select_by_visible_text("exec")

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
        input_element = self.driver.find_element_by_id("sources-processors-in-text")
        functions.click(input_element)

        input_element.send_keys("exec_2")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("sources-processors-in-select"))
        options.select_by_visible_text("exec_2")

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

        wait = WebDriverWait(self.driver,5)

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        # Fill the dim_signature input
        input_element = self.driver.find_element_by_id("sources-dim-signature-text")
        input_element.send_keys("DIM_SIGNATURE_2")

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

        # Fill the dim_signature input
        input_element = self.driver.find_element_by_id("sources-dim-signature-text")
        input_element.send_keys("DIM_SIGNATURE_2")

        menu = Select(self.driver.find_element_by_id("sources-dim-signature-operator"))
        menu.select_by_visible_text("notlike")

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
        input_element = self.driver.find_element_by_id("sources-dim-signatures-in-text")
        functions.click(input_element)

        input_element.send_keys("DIM_SIGNATURE_1")
        input_element.send_keys(Keys.LEFT_SHIFT)
        input_element.clear()
        input_element.send_keys("DIM_SIGNATURE_2")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("sources-dim-signatures-in-select"))
        options.select_by_visible_text("DIM_SIGNATURE_1")
        options.select_by_visible_text("DIM_SIGNATURE_2")

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
        input_element = self.driver.find_element_by_id("sources-dim-signatures-in-text")
        functions.click(input_element)

        input_element.send_keys("DIM_SIGNATURE_3")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("sources-dim-signatures-in-select"))
        options.select_by_visible_text("DIM_SIGNATURE_3")

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

        wait = WebDriverWait(self.driver,5)

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

        wait = WebDriverWait(self.driver,5)

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
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"sources-nav-no-data")))

        assert no_data

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
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"sources-nav-no-data")))

        assert no_data

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
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"sources-nav-no-data")))

        assert no_data

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

        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "generation-time", "2018-07-05T02:07:03", "==", 1)

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

        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "generation-time", "2018-07-05T02:07:03", ">", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"sources-nav-no-data")))

        assert no_data

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "generation-time", "2018-07-05T02:07:03", ">=", 1)

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

        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "generation-time", "2018-07-05T02:07:03", "<", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"sources-nav-no-data")))

        assert no_data

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "generation-time", "2018-07-05T02:07:03", "<=", 1)

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

        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "generation-time", "2018-07-05T02:07:03", "!=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"sources-nav-no-data")))

        assert no_data

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

        wait = WebDriverWait(self.driver,5)

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
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"sources-nav-no-data")))

        assert no_data

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
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"sources-nav-no-data")))

        assert no_data

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
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"sources-nav-no-data")))

        assert no_data

    def test_sources_query_reported_validity(self):

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
                         "validity_stop": "2018-06-05T03:00:00",
                         "priority": 10,
                         "ingestion_completeness": {
                              "check": "false",
                              "message": "MISSING DEPENDENCIES"}
                }
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
                         "validity_stop": "2018-06-05T04:00:00",
                         "priority": 10,
                         "ingestion_completeness": {
                              "check": "false",
                              "message": "MISSING DEPENDENCIES"}
                }
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
                         "validity_stop": "2018-06-05T05:00:00",
                         "priority": 10,
                         "ingestion_completeness": {
                              "check": "false",
                              "message": "MISSING DEPENDENCIES"}
                }
            }
        ]}

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5)

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_any_period(self.driver, wait, "sources", "reported-validity-start-reported-validity-stop", 1, "2018-06-05T03:00:00", "==","2018-06-05T04:00:00", "==")

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

        functions.fill_any_period(self.driver, wait, "sources", "reported-validity-start-reported-validity-stop", 1, start_value = "2018-06-05T03:00:00", start_operator = ">=")

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

        functions.fill_any_period(self.driver, wait, "sources", "reported-validity-start-reported-validity-stop", 1, end_value = "2018-06-05T04:00:00", end_operator = "!=")

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

        functions.fill_any_period(self.driver, wait, "sources", "reported-validity-start-reported-validity-stop", 1, start_value = "2018-06-05T01:30:00", start_operator = ">")
        functions.click(self.driver.find_element_by_id("sources-add-reported-validity-start-reported-validity-stop"))

        functions.fill_any_period(self.driver, wait, "sources", "reported-validity-start-reported-validity-stop", 2, start_value = "2018-06-05T03:00:00", start_operator = "<")

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

        functions.fill_any_period(self.driver, wait, "sources", "reported-validity-start-reported-validity-stop", 1, start_value = "2018-06-05T03:00:00", start_operator = "<=", end_value = "2018-06-05T02:30:00", end_operator = ">")
        functions.click(self.driver.find_element_by_id("sources-add-reported-validity-start-reported-validity-stop"))
        functions.fill_any_period(self.driver, wait, "sources", "reported-validity-start-reported-validity-stop", 2, start_value = "2018-06-05T04:00:00", start_operator = "!=", end_value = "2018-06-05T03:00:00", end_operator = ">=")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

    def test_sources_query_reception_time(self):

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
                            "validity_stop": "2018-06-05T08:07:36",
                            "priority": 10,
                            "ingestion_completeness": {
                                    "check": "false",
                                    "message": "MISSING DEPENDENCIES"}
                }
        }]}

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        reception_time = self.session.query(Source).all()[0].reception_time.isoformat()

        wait = WebDriverWait(self.driver,5)

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "reception-time", reception_time, "==", 1)

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

        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "reception-time", reception_time, "==", 1)
        functions.click(self.driver.find_element_by_id("sources-add-reception-time"))
        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "reception-time", "9999-01-01T00:00:00", "<", 2)

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

        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "reception-time", reception_time, ">", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"sources-nav-no-data")))

        assert no_data

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "reception-time", reception_time, ">=", 1)

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

        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "reception-time", reception_time, "<", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"sources-nav-no-data")))

        assert no_data

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "reception-time", reception_time, "<=", 1)

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

        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "reception-time", reception_time, "!=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"sources-nav-no-data")))

        assert no_data

    def test_sources_query_processing_duration(self):

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
                            "validity_stop": "2018-06-05T08:07:36",
                            "priority": 10,
                            "ingestion_completeness": {
                                    "check": "false",
                                    "message": "MISSING DEPENDENCIES"}
                }
        }]}

        # Example value for processing duration field
        processing_duration = "21633.0"

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data(processing_duration = datetime.timedelta(seconds=float(processing_duration)))[0]["status"]

        wait = WebDriverWait(self.driver,5)

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_text_operator_with_more_option(self.driver, wait, "sources", "processing-duration", processing_duration, "==", 1)

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

        functions.fill_text_operator_with_more_option(self.driver, wait, "sources", "processing-duration", processing_duration, ">", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"sources-nav-no-data")))

        assert no_data

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_text_operator_with_more_option(self.driver, wait, "sources", "processing-duration", processing_duration, ">=", 1)

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

        functions.fill_text_operator_with_more_option(self.driver, wait, "sources", "processing-duration", processing_duration, "<", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"sources-nav-no-data")))

        assert no_data

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_text_operator_with_more_option(self.driver, wait, "sources", "processing-duration", processing_duration, "<=", 1)

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

        functions.fill_text_operator_with_more_option(self.driver, wait, "sources", "processing-duration", processing_duration, "!=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"sources-nav-no-data")))

        assert no_data

    def test_sources_query_reported_generation_time(self):

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
                            "validity_stop": "2018-06-05T08:07:36",
                            "priority": 10,
                            "ingestion_completeness": {
                                    "check": "false",
                                    "message": "MISSING DEPENDENCIES"}
                }
        }]}


        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_text_operator_with_more_option(self.driver, wait, "sources", "reported-generation-time", "2018-07-05T02:07:03", "==", 1)

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

        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "reported-generation-time", "2018-07-05T02:07:03", ">", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"sources-nav-no-data")))

        assert no_data

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "reported-generation-time", "2018-07-05T02:07:03", ">=", 1)

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

        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "reported-generation-time", "2018-07-05T02:07:03", "<", 1)

        # Click on query button
        functions.click(submit_button)

       # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"sources-nav-no-data")))

        assert no_data

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "reported-generation-time", "2018-07-05T02:07:03", "<=", 1)

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

        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "reported-generation-time", "2018-07-05T02:07:03", "!=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"sources-nav-no-data")))

        assert no_data

    def test_sources_query_ingestion_completeness(self):

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
                            "validity_stop": "2018-06-05T08:07:36",
                            "priority": 10,
                            "ingestion_completeness": {
                                    "check": "false",
                                    "message": "MISSING DEPENDENCIES"}
                }
        }]}


        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        option = Select(self.driver.find_element_by_id("sources-ingestion-completeness"))
        option.select_by_visible_text("")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        # true option
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        option = Select(self.driver.find_element_by_id("sources-ingestion-completeness"))
        option.select_by_visible_text("true")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"sources-nav-no-data")))

        assert no_data

         # false option
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        option = Select(self.driver.find_element_by_id("sources-ingestion-completeness"))
        option.select_by_visible_text("false")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

    # def test_sources_query_value_statuses(self):
    #     # Insert data
    #     data = {"operations": [{
    #             "mode": "insert",
    #             "dim_signature": {
    #                   "name": "DIM_SIGNATURE_1",
    #                   "exec": "exec",
    #                   "version": "1.0"
    #             },
    #             "source":  {"name": "source_1.xml",
    #                     "reception_time": "2018-07-05T02:07:03",
    #                            "generation_time": "2018-07-05T02:07:03",
    #                            "validity_start": "2018-06-05T02:07:03",
    #                            "validity_stop": "2018-06-05T02:08:12"}
    #         }
    #     ]}

    #     # Check data is correctly inserted
    #     self.engine_eboa.data = data
    #     assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

    #     assert eboa_engine.exit_codes["SOURCE_ALREADY_INGESTED"]["status"] == self.engine_eboa.treat_data()[0]["status"]

    #     wait = WebDriverWait(self.driver,5);

    #     ## OK Status ##
    #     self.driver.get("http://localhost:5000/eboa_nav/")

    #     # Go to tab
    #     functions.goToTab(self.driver,"Sources")
    #     submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
    #     functions.click_no_graphs_sources(self.driver)

    #     # Fill the status_in input
    #     input_element = self.driver.find_element_by_id("sources-statuses-initial-in-text")
    #     functions.click(input_element)
    #     input_element.send_keys("OK")
    #     input_element.send_keys(Keys.RETURN)

    #     # Click on query button
    #     functions.click(submit_button)

    #     # Check table generatedd
    #     sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
    #     number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
    #     empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

    #     assert number_of_elements == 1 and empty_element is False

    #     ## Not OK Status ##
    #     self.driver.get("http://localhost:5000/eboa_nav/")

    #     # Go to tab
    #     functions.goToTab(self.driver,"Sources")
    #     submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
    #     functions.click_no_graphs_sources(self.driver)

    #     # Fill the status_in input
    #     input_element = self.driver.find_element_by_id("sources-statuses-initial-in-text")
    #     functions.click(input_element)

    #     input_element.send_keys("OK")
    #     input_element.send_keys(Keys.LEFT_SHIFT)

    #     options = Select(self.driver.find_element_by_id("sources-statuses-initial-in-select"))
    #     options.select_by_visible_text("OK")

    #     notInButton = self.driver.find_element_by_id("sources-statuses-initial-checkbox")
    #     if not notInButton.find_element_by_xpath("input").is_selected():
    #         functions.select_checkbox(notInButton)
    #     #end if

    #     # Click on query button
    #     functions.click(submit_button)

    #     # Check table generatedd
    #     sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources-table")))
    #     number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
    #     empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

    #     assert number_of_elements == 1 and empty_element is False
