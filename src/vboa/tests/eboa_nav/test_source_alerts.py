"""
Automated tests for the source alerts tab

Written by DEIMOS Space S.L. (jubv)

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

class TestSourceAlertsTab(unittest.TestCase):

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
    
    def test_source_alerts_no_data(self):

        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

    def test_source_alerts_query_no_filter_with_timeline(self):

        # Insert data
        data = {
                "operations":[
                    {
                        "mode":"insert",
                        "dim_signature":{
                            "name":"dim_signature",
                            "exec":"exec",
                            "version":"1.0"
                        },
                        "source":{
                            "name":"source.json",
                            "reception_time":"2018-06-06T13:33:29",
                            "generation_time":"2018-07-05T02:07:03",
                            "validity_start":"2018-06-05T02:07:03",
                            "validity_stop":"2018-06-05T08:07:36"
                        },
                        "alerts":[
                            {
                            "message":"Alert message",
                            "generator":"test",
                            "notification_time":"2018-06-05T08:07:36",
                            "alert_cnf":{
                                "name":"alert_name1",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_group"
                            },
                            "entity":{
                                "reference_mode":"by_ref",
                                "reference":"source.json",
                                "type":"source"
                            }
                            }
                        ]
                    }
                ]
                }


        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        functions.click_no_graphs_sources(self.driver)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click(submit_button)

        timeline = self.driver.find_element_by_id('timeline-general-view-alerts')
        condition = timeline.is_displayed()

        assert condition

        kwargs ={}
        kwargs["order_by"] = {"field": "notification_time", "descending": False}
        sources_alerts = self.query_eboa.get_source_alerts(kwargs)

        assert len(sources_alerts) == 1

        alerts = [
            {
                "alert_uuid": "<a href='/eboa_nav/query-alert/" + str(sources_alerts[0].source_alert_uuid) + "'>" + str(sources_alerts[0].source_alert_uuid) + "</a>",
                "description": "Alert description",
                "entity": "Source",
                "entity_uuid": "<a href='/eboa_nav/query-source/" + str(sources_alerts[0].source_uuid) + "'>" + str(sources_alerts[0].source_uuid) + "</a>",
                "generator": "test",
                "group": "SOURCES;alert_group",
                "group_alert": "alert_group",
                "id": str(sources_alerts[0].source_alert_uuid),
                "ingestion_time": sources_alerts[0].ingestion_time.isoformat(),
                "justification": "None",
                "message": "Alert message",
                "name": "alert_name1",
                "notification_time": "2018-06-05T08:07:36",
                "notified": "<span class='bold-orange'>None</span>",
                "severity": "critical",
                "solved": "<span class='bold-orange'>None</span>",
                "solved_time": "None",
                "start": "2018-06-05T08:07:36",
                "stop": "2018-06-05T08:07:36",
                "timeline": "alert_name1",
                "validated": "<span class='bold-orange'>None</span>"
            },
        ]

        returned_alerts = self.driver.execute_script('return alerts;')
        functions.assert_equal_list_dictionaries(returned_alerts, alerts)

        # Check source alerts table
        source_alerts_table = self.driver.find_element_by_id("alerts-table")

        # Row 1
        justification = source_alerts_table.find_element_by_xpath("tbody/tr[1]/td[1]")

        assert justification.text == "None"

        severity = source_alerts_table.find_element_by_xpath("tbody/tr[1]/td[2]")

        assert severity.text == "critical"

        group = source_alerts_table.find_element_by_xpath("tbody/tr[1]/td[3]")

        assert group.text == "alert_group"

        name = source_alerts_table.find_element_by_xpath("tbody/tr[1]/td[4]")

        assert name.text == "alert_name1"

        message = source_alerts_table.find_element_by_xpath("tbody/tr[1]/td[5]")

        assert message.text == "Alert message"

        notification_time = source_alerts_table.find_element_by_xpath("tbody/tr[1]/td[6]")

        assert notification_time.text == "2018-06-05T08:07:36"

        solved = source_alerts_table.find_element_by_xpath("tbody/tr[1]/td[7]")

        assert solved.text == "None"

        solved_time = source_alerts_table.find_element_by_xpath("tbody/tr[1]/td[8]")

        assert solved_time.text == "None"

        description = source_alerts_table.find_element_by_xpath("tbody/tr[1]/td[9]")

        assert description.text == "Alert description"

        validated = source_alerts_table.find_element_by_xpath("tbody/tr[1]/td[10]")

        assert validated.text == "None"

        generator = source_alerts_table.find_element_by_xpath("tbody/tr[1]/td[11]")

        assert generator.text == "test"

        notified = source_alerts_table.find_element_by_xpath("tbody/tr[1]/td[12]")

        assert notified.text == "None"

        ingestion_time = source_alerts_table.find_element_by_xpath("tbody/tr[1]/td[13]")

        assert ingestion_time.text == sources_alerts[0].ingestion_time.isoformat()

        alert_uuid = source_alerts_table.find_element_by_xpath("tbody/tr[1]/td[14]")

        assert alert_uuid.text == str(sources_alerts[0].source_alert_uuid)

        source_uuid = source_alerts_table.find_element_by_xpath("tbody/tr[1]/td[15]")

        assert source_uuid.text == str(sources_alerts[0].source_uuid)

    def test_source_alerts_query_name_filter(self):

        # Insert data
        data = {
                "operations":[
                    {
                        "mode":"insert",
                        "dim_signature":{
                            "name":"dim_signature",
                            "exec":"exec",
                            "version":"1.0"
                        },
                        "source":{
                            "name":"source.json",
                            "reception_time":"2018-06-06T13:33:29",
                            "generation_time":"2018-07-05T02:07:03",
                            "validity_start":"2018-06-05T02:07:03",
                            "validity_stop":"2018-06-05T08:07:36"
                        },
                        "alerts":[
                            {
                            "message":"Alert message",
                            "generator":"test",
                            "notification_time":"2018-06-05T08:07:36",
                            "alert_cnf":{
                                "name":"alert_name1",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_group"
                            },
                            "entity":{
                                "reference_mode":"by_ref",
                                "reference":"source.json",
                                "type":"source"
                            }
                            }
                        ]
                    },
                    {
                        "mode":"insert",
                        "dim_signature":{
                            "name":"dim_signature",
                            "exec":"exec",
                            "version":"1.0"
                        },
                        "source":{
                            "name":"source_2.json",
                            "reception_time":"2018-06-06T13:33:29",
                            "generation_time":"2018-07-05T02:07:03",
                            "validity_start":"2018-06-05T02:07:03",
                            "validity_stop":"2018-06-05T08:07:36"
                        },
                        "alerts":[
                            {
                            "message":"Alert message",
                            "generator":"test1",
                            "notification_time":"2019-06-06T08:07:36",
                            "alert_cnf":{
                                "name":"alert_name2",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_group"
                            },
                            "entity":{
                                "reference_mode":"by_ref",
                                "reference":"source_2.json",
                                "type":"source"
                            }
                            }
                        ]
                    },
                    {
                        "mode":"insert",
                        "dim_signature":{
                            "name":"dim_signature",
                            "exec":"exec",
                            "version":"1.0"
                        },
                        "source":{
                            "name":"source_3.json",
                            "reception_time":"2018-06-06T13:33:29",
                            "generation_time":"2018-07-05T02:07:03",
                            "validity_start":"2018-06-05T02:07:03",
                            "validity_stop":"2018-06-05T08:07:36"
                        },
                        "alerts":[
                            {
                            "message":"Alert message",
                            "generator":"test1",
                            "notification_time":"2019-06-06T08:07:36",
                            "alert_cnf":{
                                "name":"alert_name3",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_grou2"
                            },
                            "entity":{
                                "reference_mode":"by_ref",
                                "reference":"source_3.json",
                                "type":"source"
                            }
                            }
                        ]
                    }
                ]
                }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5)

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        # Fill the source input
        input_element = self.driver.find_element_by_id("sources-source-name-text")
        input_element.send_keys("source_2.json")

        # Click on query button
        functions.click(submit_button)

        # Check table generatedd
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        # Fill the source input
        input_element = self.driver.find_element_by_id("sources-source-name-text")
        input_element.send_keys("source_2.json")

        menu = Select(self.driver.find_element_by_id("sources-source-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        functions.click(submit_button)

        # Check table generatedd
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        
        assert number_of_elements == 2

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        # Fill the source_in input
        input_element = self.driver.find_element_by_id("sources-source-names-in-text")
        functions.click(input_element)

        input_element.send_keys("source_2.json")
        input_element.send_keys(Keys.LEFT_SHIFT)
        input_element.clear()
        input_element.send_keys("source_3.json")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("sources-source-names-in-select"))
        options.select_by_visible_text("source_2.json")
        options.select_by_visible_text("source_3.json")

        # Click on query button
        functions.click(submit_button)

        # Check table generatedd
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        # Fill the source_in input
        input_element = self.driver.find_element_by_id("sources-source-names-in-text")
        functions.click(input_element)

        input_element.send_keys("source_3.json")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("sources-source-names-in-select"))
        options.select_by_visible_text("source_3.json")

        notInButton = self.driver.find_element_by_id("sources-source-names-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        #end if

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

    def test_source_alerts_query_processor_filter(self):

        # Insert data
        data = {
                "operations":[
                    {
                        "mode":"insert",
                        "dim_signature":{
                            "name":"dim_signature",
                            "exec":"exec",
                            "version":"1.0"
                        },
                        "source":{
                            "name":"source.json",
                            "reception_time":"2018-06-06T13:33:29",
                            "generation_time":"2018-07-05T02:07:03",
                            "validity_start":"2018-06-05T02:07:03",
                            "validity_stop":"2018-06-05T08:07:36"
                        },
                        "alerts":[
                            {
                            "message":"Alert message",
                            "generator":"test",
                            "notification_time":"2018-06-05T08:07:36",
                            "alert_cnf":{
                                "name":"alert_name1",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_group"
                            },
                            "entity":{
                                "reference_mode":"by_ref",
                                "reference":"source.json",
                                "type":"source"
                            }
                            }
                        ]
                    },
                    {
                        "mode":"insert",
                        "dim_signature":{
                            "name":"dim_signature",
                            "exec":"exec_2",
                            "version":"1.0"
                        },
                        "source":{
                            "name":"source_2.json",
                            "reception_time":"2018-06-06T13:33:29",
                            "generation_time":"2018-07-05T02:07:03",
                            "validity_start":"2018-06-05T02:07:03",
                            "validity_stop":"2018-06-05T08:07:36"
                        },
                        "alerts":[
                            {
                            "message":"Alert message",
                            "generator":"test1",
                            "notification_time":"2019-06-06T08:07:36",
                            "alert_cnf":{
                                "name":"alert_name2",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_group"
                            },
                            "entity":{
                                "reference_mode":"by_ref",
                                "reference":"source_2.json",
                                "type":"source"
                            }
                            }
                        ]
                    },
                    {
                        "mode":"insert",
                        "dim_signature":{
                            "name":"dim_signature",
                            "exec":"exec",
                            "version":"1.0"
                        },
                        "source":{
                            "name":"source_3.json",
                            "reception_time":"2018-06-06T13:33:29",
                            "generation_time":"2018-07-05T02:07:03",
                            "validity_start":"2018-06-05T02:07:03",
                            "validity_stop":"2018-06-05T08:07:36"
                        },
                        "alerts":[
                            {
                            "message":"Alert message",
                            "generator":"test1",
                            "notification_time":"2019-06-06T08:07:36",
                            "alert_cnf":{
                                "name":"alert_name3",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_grou2"
                            },
                            "entity":{
                                "reference_mode":"by_ref",
                                "reference":"source_3.json",
                                "type":"source"
                            }
                            }
                        ]
                    }
                ]
                }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5)

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        # Fill the processor input
        input_element = self.driver.find_element_by_id("sources-processor-text")
        input_element.send_keys("exec_2")

        # Click on query button
        functions.click(submit_button)

        # Check table generatedd
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        # Fill the processor input
        input_element = self.driver.find_element_by_id("sources-processor-text")
        input_element.send_keys("exec_2")

        menu = Select(self.driver.find_element_by_id("sources-processor-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        functions.click(submit_button)

        # Check table generatedd
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
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
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
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
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

    def test_source_alerts_query_dim_signature_filter(self):

        # Insert data
        data = {
                "operations":[
                    {
                        "mode":"insert",
                        "dim_signature":{
                            "name":"DIM_SIGNATURE_1",
                            "exec":"exec",
                            "version":"1.0"
                        },
                        "source":{
                            "name":"source.json",
                            "reception_time":"2018-06-06T13:33:29",
                            "generation_time":"2018-07-05T02:07:03",
                            "validity_start":"2018-06-05T02:07:03",
                            "validity_stop":"2018-06-05T08:07:36"
                        },
                        "alerts":[
                            {
                            "message":"Alert message",
                            "generator":"test",
                            "notification_time":"2018-06-05T08:07:36",
                            "alert_cnf":{
                                "name":"alert_name1",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_group"
                            },
                            "entity":{
                                "reference_mode":"by_ref",
                                "reference":"source.json",
                                "type":"source"
                            }
                            }
                        ]
                    },
                    {
                        "mode":"insert",
                        "dim_signature":{
                            "name":"DIM_SIGNATURE_2",
                            "exec":"exec_2",
                            "version":"1.0"
                        },
                        "source":{
                            "name":"source_2.json",
                            "reception_time":"2018-06-06T13:33:29",
                            "generation_time":"2018-07-05T02:07:03",
                            "validity_start":"2018-06-05T02:07:03",
                            "validity_stop":"2018-06-05T08:07:36"
                        },
                        "alerts":[
                            {
                            "message":"Alert message",
                            "generator":"test1",
                            "notification_time":"2019-06-06T08:07:36",
                            "alert_cnf":{
                                "name":"alert_name2",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_group"
                            },
                            "entity":{
                                "reference_mode":"by_ref",
                                "reference":"source_2.json",
                                "type":"source"
                            }
                            }
                        ]
                    },
                    {
                        "mode":"insert",
                        "dim_signature":{
                            "name":"DIM_SIGNATURE_3",
                            "exec":"exec",
                            "version":"1.0"
                        },
                        "source":{
                            "name":"source_3.json",
                            "reception_time":"2018-06-06T13:33:29",
                            "generation_time":"2018-07-05T02:07:03",
                            "validity_start":"2018-06-05T02:07:03",
                            "validity_stop":"2018-06-05T08:07:36"
                        },
                        "alerts":[
                            {
                            "message":"Alert message",
                            "generator":"test1",
                            "notification_time":"2019-06-06T08:07:36",
                            "alert_cnf":{
                                "name":"alert_name3",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_grou2"
                            },
                            "entity":{
                                "reference_mode":"by_ref",
                                "reference":"source_3.json",
                                "type":"source"
                            }
                            }
                        ]
                    }
                ]
                }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5)

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        # Fill the dim_signature input
        input_element = self.driver.find_element_by_id("sources-dim-signature-text")
        input_element.send_keys("DIM_SIGNATURE_2")

        # Click on query button
        functions.click(submit_button)

        # Check table generatedd
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        # Fill the dim_signature input
        input_element = self.driver.find_element_by_id("sources-dim-signature-text")
        input_element.send_keys("DIM_SIGNATURE_2")

        menu = Select(self.driver.find_element_by_id("sources-dim-signature-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        functions.click(submit_button)

        # Check table generatedd
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
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
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
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
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

    def test_source_alerts_query_period(self):

        # Insert data
        data = {
                "operations":[
                    {
                        "mode":"insert",
                        "dim_signature":{
                            "name":"DIM_SIGNATURE_1",
                            "exec":"exec",
                            "version":"1.0"
                        },
                        "source":{
                            "name":"source.json",
                            "reception_time":"2018-06-06T13:33:29",
                            "generation_time":"2018-07-05T02:07:03",
                            "validity_start":"2018-06-05T02:00:00",
                            "validity_stop":"2018-06-05T03:00:00"
                        },
                        "alerts":[
                            {
                            "message":"Alert message",
                            "generator":"test",
                            "notification_time":"2018-06-05T08:07:36",
                            "alert_cnf":{
                                "name":"alert_name1",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_group"
                            },
                            "entity":{
                                "reference_mode":"by_ref",
                                "reference":"source.json",
                                "type":"source"
                            }
                            }
                        ]
                    },
                    {
                        "mode":"insert",
                        "dim_signature":{
                            "name":"DIM_SIGNATURE_2",
                            "exec":"exec_2",
                            "version":"1.0"
                        },
                        "source":{
                            "name":"source_2.json",
                            "reception_time":"2018-06-06T13:33:29",
                            "generation_time":"2018-07-05T02:07:03",
                            "validity_start":"2018-06-05T03:00:00",
                            "validity_stop":"2018-06-05T04:00:00"
                        },
                        "alerts":[
                            {
                            "message":"Alert message",
                            "generator":"test1",
                            "notification_time":"2019-06-06T08:07:36",
                            "alert_cnf":{
                                "name":"alert_name2",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_group"
                            },
                            "entity":{
                                "reference_mode":"by_ref",
                                "reference":"source_2.json",
                                "type":"source"
                            }
                            }
                        ]
                    },
                    {
                        "mode":"insert",
                        "dim_signature":{
                            "name":"DIM_SIGNATURE_3",
                            "exec":"exec",
                            "version":"1.0"
                        },
                        "source":{
                            "name":"source_3.json",
                            "reception_time":"2018-06-06T13:33:29",
                            "generation_time":"2018-07-05T02:07:03",
                            "validity_start":"2018-06-05T04:00:00",
                            "validity_stop":"2018-06-05T05:00:00"
                        },
                        "alerts":[
                            {
                            "message":"Alert message",
                            "generator":"test1",
                            "notification_time":"2019-06-06T08:07:36",
                            "alert_cnf":{
                                "name":"alert_name3",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_group2"
                            },
                            "entity":{
                                "reference_mode":"by_ref",
                                "reference":"source_3.json",
                                "type":"source"
                            }
                            }
                        ]
                    }
                ]
                }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5)

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_validity_period(self.driver, wait, "sources", 1, "2018-06-05T03:00:00", "==","2018-06-05T04:00:00", "==")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_validity_period(self.driver, wait, "sources", 1, start_value = "2018-06-05T03:00:00", start_operator = ">=")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_validity_period(self.driver, wait, "sources", 1, end_value = "2018-06-05T04:00:00", end_operator = "!=")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        ## > ## Only Start ## < ## Only Start ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_validity_period(self.driver, wait, "sources", 1, start_value = "2018-06-05T01:30:00", start_operator = ">")
        functions.click(self.driver.find_element_by_id("sources-add-validity-start-validity-stop"))

        functions.fill_validity_period(self.driver, wait, "sources", 2, start_value = "2018-06-05T03:00:00", start_operator = "<")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## <= ## Start ## > ## End ## != ## Start ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_validity_period(self.driver, wait, "sources", 1, start_value = "2018-06-05T03:00:00", start_operator = "<=", end_value = "2018-06-05T02:30:00", end_operator = ">")
        functions.click(self.driver.find_element_by_id("sources-add-validity-start-validity-stop"))
        functions.fill_validity_period(self.driver, wait, "sources", 2, start_value = "2018-06-05T04:00:00", start_operator = "!=", end_value = "2018-06-05T03:00:00", end_operator = ">=")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

    def test_source_alerts_query_ingestion_time(self):

        # Insert data
        data = {
                "operations":[
                    {
                        "mode":"insert",
                        "dim_signature":{
                            "name":"DIM_SIGNATURE_1",
                            "exec":"exec",
                            "version":"1.0"
                        },
                        "source":{
                            "name":"source.json",
                            "reception_time":"2018-06-06T13:33:29",
                            "generation_time":"2018-07-05T02:07:03",
                            "validity_start":"2018-06-05T02:00:00",
                            "validity_stop":"2018-06-05T03:00:00"
                        },
                        "alerts":[
                            {
                            "message":"Alert message",
                            "generator":"test",
                            "notification_time":"2018-06-05T08:07:36",
                            "alert_cnf":{
                                "name":"alert_name1",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_group"
                            },
                            "entity":{
                                "reference_mode":"by_ref",
                                "reference":"source.json",
                                "type":"source"
                            }
                            }
                        ]
                    }
                ]
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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_ingestion_time(self.driver, wait,"sources", ingestion_time, "==", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## == and < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_ingestion_time(self.driver, wait,"sources", ingestion_time, "==", 1)
        functions.click(self.driver.find_element_by_id("sources-add-ingestion-time"))
        functions.fill_ingestion_time(self.driver, wait,"sources", "9999-01-01T00:00:00", "<", 2)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_ingestion_time(self.driver, wait,"sources",ingestion_time, ">", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_ingestion_time(self.driver, wait,"sources", ingestion_time, ">=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_ingestion_time(self.driver, wait,"sources", ingestion_time, "<", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_ingestion_time(self.driver, wait,"sources", ingestion_time, "<=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_ingestion_time(self.driver, wait,"sources", ingestion_time, "!=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

    def test_source_alerts_query_generation_time(self):

        # Insert data
        data = {
                "operations":[
                    {
                        "mode":"insert",
                        "dim_signature":{
                            "name":"DIM_SIGNATURE_1",
                            "exec":"exec",
                            "version":"1.0"
                        },
                        "source":{
                            "name":"source.json",
                            "reception_time":"2018-06-06T13:33:29",
                            "generation_time": "2018-07-05T02:07:03",
                            "validity_start":"2018-06-05T02:00:00",
                            "validity_stop":"2018-06-05T03:00:00"
                        },
                        "alerts":[
                            {
                            "message":"Alert message",
                            "generator":"test",
                            "notification_time":"2018-06-05T08:07:36",
                            "alert_cnf":{
                                "name":"alert_name1",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_group"
                            },
                            "entity":{
                                "reference_mode":"by_ref",
                                "reference":"source.json",
                                "type":"source"
                            }
                            }
                        ]
                    }
                ]
                }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "generation-time", "2018-07-05T02:07:03", "==", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "generation-time", "2018-07-05T02:07:03", ">", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "generation-time", "2018-07-05T02:07:03", ">=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "generation-time", "2018-07-05T02:07:03", "<", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "generation-time", "2018-07-05T02:07:03", "<=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "generation-time", "2018-07-05T02:07:03", "!=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

    def test_source_alerts_query_value_ingestion_duration(self):

        # Insert data
        data = {
                "operations":[
                    {
                        "mode":"insert",
                        "dim_signature":{
                            "name":"DIM_SIGNATURE_1",
                            "exec":"exec",
                            "version":"1.0"
                        },
                        "source":{
                            "name":"source.json",
                            "reception_time":"2018-06-06T13:33:29",
                            "generation_time": "2018-07-05T02:07:03",
                            "validity_start":"2018-06-05T02:00:00",
                            "validity_stop":"2018-06-05T03:00:00"
                        },
                        "alerts":[
                            {
                            "message":"Alert message",
                            "generator":"test",
                            "notification_time":"2018-06-05T08:07:36",
                            "alert_cnf":{
                                "name":"alert_name1",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_group"
                            },
                            "entity":{
                                "reference_mode":"by_ref",
                                "reference":"source.json",
                                "type":"source"
                            }
                            }
                        ]
                    }
                ]
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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_ingestion_duration(self.driver, wait, "sources", ingestion_duration, "==", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_ingestion_duration(self.driver, wait, "sources", ingestion_duration, ">", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_ingestion_duration(self.driver, wait, "sources", ingestion_duration, ">=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_ingestion_duration(self.driver, wait, "sources", ingestion_duration, "<", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_ingestion_duration(self.driver, wait, "sources", ingestion_duration, "<=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_ingestion_duration(self.driver, wait, "sources", ingestion_duration, "!=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

    def test_source_alerts_query_reported_validity(self):

        # Insert data
        data = {
                "operations":[
                    {
                        "mode":"insert",
                        "dim_signature":{
                            "name":"DIM_SIGNATURE_1",
                            "exec":"exec",
                            "version":"1.0"
                        },
                        "source":{
                            "name":"source.json",
                            "reception_time":"2018-06-06T13:33:29",
                            "generation_time":"2018-07-05T02:07:03",
                            "validity_start":"2018-06-05T02:00:00",
                            "validity_stop":"2018-06-05T03:00:00"
                        },
                        "alerts":[
                            {
                            "message":"Alert message",
                            "generator":"test",
                            "notification_time":"2018-06-05T08:07:36",
                            "alert_cnf":{
                                "name":"alert_name1",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_group"
                            },
                            "entity":{
                                "reference_mode":"by_ref",
                                "reference":"source.json",
                                "type":"source"
                            }
                            }
                        ]
                    },
                    {
                        "mode":"insert",
                        "dim_signature":{
                            "name":"DIM_SIGNATURE_2",
                            "exec":"exec_2",
                            "version":"1.0"
                        },
                        "source":{
                            "name":"source_2.json",
                            "reception_time":"2018-06-06T13:33:29",
                            "generation_time":"2018-07-05T02:07:03",
                            "validity_start":"2018-06-05T03:00:00",
                            "validity_stop":"2018-06-05T04:00:00"
                        },
                        "alerts":[
                            {
                            "message":"Alert message",
                            "generator":"test1",
                            "notification_time":"2019-06-06T08:07:36",
                            "alert_cnf":{
                                "name":"alert_name2",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_group"
                            },
                            "entity":{
                                "reference_mode":"by_ref",
                                "reference":"source_2.json",
                                "type":"source"
                            }
                            }
                        ]
                    },
                    {
                        "mode":"insert",
                        "dim_signature":{
                            "name":"DIM_SIGNATURE_3",
                            "exec":"exec",
                            "version":"1.0"
                        },
                        "source":{
                            "name":"source_3.json",
                            "reception_time":"2018-06-06T13:33:29",
                            "generation_time":"2018-07-05T02:07:03",
                            "validity_start":"2018-06-05T04:00:00",
                            "validity_stop":"2018-06-05T05:00:00"
                        },
                        "alerts":[
                            {
                            "message":"Alert message",
                            "generator":"test1",
                            "notification_time":"2019-06-06T08:07:36",
                            "alert_cnf":{
                                "name":"alert_name3",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_group2"
                            },
                            "entity":{
                                "reference_mode":"by_ref",
                                "reference":"source_3.json",
                                "type":"source"
                            }
                            }
                        ]
                    }
                ]
                }
        

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5)

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_any_period(self.driver, wait, "sources", "reported-validity-start-reported-validity-stop", 1, "2018-06-05T03:00:00", "==","2018-06-05T04:00:00", "==")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_any_period(self.driver, wait, "sources", "reported-validity-start-reported-validity-stop", 1, start_value = "2018-06-05T03:00:00", start_operator = ">=")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_any_period(self.driver, wait, "sources", "reported-validity-start-reported-validity-stop", 1, end_value = "2018-06-05T04:00:00", end_operator = "!=")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        ## > ## Only Start ## < ## Only Start ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_any_period(self.driver, wait, "sources", "reported-validity-start-reported-validity-stop", 1, start_value = "2018-06-05T01:30:00", start_operator = ">")
        functions.click(self.driver.find_element_by_id("sources-add-reported-validity-start-reported-validity-stop"))

        functions.fill_any_period(self.driver, wait, "sources", "reported-validity-start-reported-validity-stop", 2, start_value = "2018-06-05T03:00:00", start_operator = "<")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## <= ## Start ## > ## End ## != ## Start ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_any_period(self.driver, wait, "sources", "reported-validity-start-reported-validity-stop", 1, start_value = "2018-06-05T03:00:00", start_operator = "<=", end_value = "2018-06-05T02:30:00", end_operator = ">")
        functions.click(self.driver.find_element_by_id("sources-add-reported-validity-start-reported-validity-stop"))
        functions.fill_any_period(self.driver, wait, "sources", "reported-validity-start-reported-validity-stop", 2, start_value = "2018-06-05T04:00:00", start_operator = "!=", end_value = "2018-06-05T03:00:00", end_operator = ">=")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

    def test_source_alerts_query_reception_time(self):

        # Insert data
        data = {
                "operations":[
                    {
                        "mode":"insert",
                        "dim_signature":{
                            "name":"DIM_SIGNATURE_1",
                            "exec":"exec",
                            "version":"1.0"
                        },
                        "source":{
                            "name":"source.json",
                            "reception_time":"2018-06-06T13:33:29",
                            "generation_time": "2018-07-05T02:07:03",
                            "validity_start":"2018-06-05T02:00:00",
                            "validity_stop":"2018-06-05T03:00:00"
                        },
                        "alerts":[
                            {
                            "message":"Alert message",
                            "generator":"test",
                            "notification_time":"2018-06-05T08:07:36",
                            "alert_cnf":{
                                "name":"alert_name1",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_group"
                            },
                            "entity":{
                                "reference_mode":"by_ref",
                                "reference":"source.json",
                                "type":"source"
                            }
                            }
                        ]
                    }
                ]
                }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        reception_time = self.session.query(Source).all()[0].reception_time.isoformat()

        wait = WebDriverWait(self.driver,5)

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "reception-time", reception_time, "==", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## == and < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "reception-time", reception_time, "==", 1)
        functions.click(self.driver.find_element_by_id("sources-add-reception-time"))
        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "reception-time", "9999-01-01T00:00:00", "<", 2)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "reception-time", reception_time, ">", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "reception-time", reception_time, ">=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "reception-time", reception_time, "<", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "reception-time", reception_time, "<=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "reception-time", reception_time, "!=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

    def test_source_alerts_query_processing_duration(self):

        # Insert data
        data = {
                "operations":[
                    {
                        "mode":"insert",
                        "dim_signature":{
                            "name":"DIM_SIGNATURE_1",
                            "exec":"exec",
                            "version":"1.0"
                        },
                        "source":{
                            "name":"source.json",
                            "reception_time":"2018-06-06T13:33:29",
                            "generation_time": "2018-07-05T02:07:03",
                            "validity_start":"2018-06-05T02:00:00",
                            "validity_stop":"2018-06-05T03:00:00"
                        },
                        "alerts":[
                            {
                            "message":"Alert message",
                            "generator":"test",
                            "notification_time":"2018-06-05T08:07:36",
                            "alert_cnf":{
                                "name":"alert_name1",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_group"
                            },
                            "entity":{
                                "reference_mode":"by_ref",
                                "reference":"source.json",
                                "type":"source"
                            }
                            }
                        ]
                    }
                ]
                }

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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_text_operator_with_more_option(self.driver, wait, "sources", "processing-duration", processing_duration, "==", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_text_operator_with_more_option(self.driver, wait, "sources", "processing-duration", processing_duration, ">", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_text_operator_with_more_option(self.driver, wait, "sources", "processing-duration", processing_duration, ">=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_text_operator_with_more_option(self.driver, wait, "sources", "processing-duration", processing_duration, "<", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_text_operator_with_more_option(self.driver, wait, "sources", "processing-duration", processing_duration, "<=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_text_operator_with_more_option(self.driver, wait, "sources", "processing-duration", processing_duration, "!=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

    def test_source_alerts_query_reported_generation_time(self):

        # Insert data
        data = {
                "operations":[
                    {
                        "mode":"insert",
                        "dim_signature":{
                            "name":"DIM_SIGNATURE_1",
                            "exec":"exec",
                            "version":"1.0"
                        },
                        "source":{
                            "name":"source.json",
                            "reception_time": "2018-07-05T02:07:03",
                            "generation_time": "2018-07-05T02:07:03",
                            "validity_start": "2018-06-05T02:07:03",
                            "validity_stop": "2018-06-05T08:07:36"
                        },
                        "alerts":[
                            {
                            "message":"Alert message",
                            "generator":"test",
                            "notification_time":"2018-06-05T08:07:36",
                            "alert_cnf":{
                                "name":"alert_name1",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_group"
                            },
                            "entity":{
                                "reference_mode":"by_ref",
                                "reference":"source.json",
                                "type":"source"
                            }
                            }
                        ]
                    }
                ]
                }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_text_operator_with_more_option(self.driver, wait, "sources", "reported-generation-time", "2018-07-05T02:07:03", "==", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "reported-generation-time", "2018-07-05T02:07:03", ">", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "reported-generation-time", "2018-07-05T02:07:03", ">=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "reported-generation-time", "2018-07-05T02:07:03", "<", 1)

        # Click on query button
        functions.click(submit_button)

       # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "reported-generation-time", "2018-07-05T02:07:03", "<=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        functions.fill_text_operator_with_more_option(self.driver, wait,"sources", "reported-generation-time", "2018-07-05T02:07:03", "!=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

    def test_source_alerts_query_ingestion_completeness(self):

        # Insert data
        data = {
                "operations":[
                    {
                        "mode":"insert",
                        "dim_signature":{
                            "name":"DIM_SIGNATURE_1",
                            "exec":"exec",
                            "version":"1.0"
                        },
                        "source":{
                            "name":"source.json",
                            "reception_time": "2018-07-05T02:07:03",
                            "generation_time": "2018-07-05T02:07:03",
                            "validity_start": "2018-06-05T02:07:03",
                            "validity_stop": "2018-06-05T08:07:36",
                            "priority": 10,
                            "ingestion_completeness":{
                                    "check": "false",
                                    "message": "MISSING DEPENDENCIES"
                            }
                        },
                        "alerts":[
                            {
                            "message":"Alert message",
                            "generator":"test",
                            "notification_time":"2018-06-05T08:07:36",
                            "alert_cnf":{
                                "name":"alert_name1",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_group"
                            },
                            "entity":{
                                "reference_mode":"by_ref",
                                "reference":"source.json",
                                "type":"source"
                            }
                            }
                        ]
                    }
                ]
                }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        option = Select(self.driver.find_element_by_id("sources-ingestion-completeness"))
        option.select_by_visible_text("")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        # true option
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        option = Select(self.driver.find_element_by_id("sources-ingestion-completeness"))
        option.select_by_visible_text("true")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

         # false option
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        option = Select(self.driver.find_element_by_id("sources-ingestion-completeness"))
        option.select_by_visible_text("false")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

    # def test_source_alerts_query_value_statuses(self):
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
    #     submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
    #     functions.click_no_graphs_sources(self.driver)

    #     # Fill the status_in input
    #     input_element = self.driver.find_element_by_id("sources-statuses-initial-in-text")
    #     functions.click(input_element)
    #     input_element.send_keys("OK")
    #     input_element.send_keys(Keys.RETURN)

    #     # Click on query button
    #     functions.click(submit_button)

    #     # Check table generatedd
    #     source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
    #     number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
    #     empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

    #     assert number_of_elements == 1 and empty_element is False

    #     ## Not OK Status ##
    #     self.driver.get("http://localhost:5000/eboa_nav/")

    #     # Go to tab
    #     functions.goToTab(self.driver,"Sources")
    #     submit_button = wait.until(EC.visibility_of_element_located((By.ID,'source-alerts-submit-button')))
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
    #     source_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
    #     number_of_elements = len(source_alerts_table.find_elements_by_xpath("tbody/tr"))
    #     empty_element = len(source_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

    #     assert number_of_elements == 1 and empty_element is False
