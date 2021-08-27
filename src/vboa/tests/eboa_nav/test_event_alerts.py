"""
Automated tests for the event alerts tab

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

class TestEventAlertsTab(unittest.TestCase):

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
    
    def test_event_alerts_no_data(self):

        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

    def test_event_alerts_query_no_filter_with_timeline(self):

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
                            "validity_stop":"2019-06-05T08:07:36",
                            "priority":30
                        },
                        "events":[
                            {
                            "explicit_reference":"ER2",
                            "gauge":{
                                "name":"GAUGE_NAME2",
                                "system":"GAUGE_SYSTEM2",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2019-06-05T02:07:03",
                            "stop":"2019-06-05T08:07:36",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:37",
                                    "alert_cnf":{
                                        "name":"alert_name3",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group2"
                                    }
                                },
                                {
                                    "message":"Alert message",
                                    "generator":"test2",
                                    "notification_time":"2018-06-05T08:07:38",
                                    "alert_cnf":{
                                        "name":"alert_name4",
                                        "severity":"major",
                                        "description":"Alert description",
                                        "group":"alert_group3"
                                    }
                                }
                            ]
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
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        # Apply filters and click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        timeline = self.driver.find_element_by_id('alerts-nav-timeline')
        condition = timeline.is_displayed()

        assert condition

        # Check generated content for widgets
        kwargs ={}
        kwargs["order_by"] = {"field": "notification_time", "descending": False}
        events_alerts = self.query_eboa.get_event_alerts(**kwargs)

        assert len(events_alerts) == 2

        alerts = [
            {
                "alert_uuid": "<a href='/eboa_nav/query-alert/" + str(events_alerts[0].event_alert_uuid) + "'>" + str(events_alerts[0].event_alert_uuid) + "</a>",
                "description": "Alert description",
                "entity": "Event",
                "entity_uuid": "<a href='/eboa_nav/query-event-links/" + str(events_alerts[0].event_uuid) + "'>" + str(events_alerts[0].event_uuid) + "</a>",
                "generator": "test",
                "group": "EVENTS;alert_group2",
                "group_alert": "alert_group2",
                "id": str(events_alerts[0].event_alert_uuid),
                "ingestion_time": events_alerts[0].ingestion_time.isoformat(),
                "justification": "None",
                "message": "Alert message",
                "name": "alert_name3",
                "notification_time": "2018-06-05T08:07:37",
                "notified": "<span class='bold-orange'>None</span>",
                "severity": "critical",
                "solved": "<span class='bold-orange'>None</span>",
                "solved_time": "None",
                "start": "2018-06-05T08:07:37",
                "stop": "2018-06-05T08:07:37",
                "timeline": "alert_name3",
                "validated": "<span class='bold-orange'>None</span>"
            },
            {
                "alert_uuid": "<a href='/eboa_nav/query-alert/" + str(events_alerts[1].event_alert_uuid) + "'>" + str(events_alerts[1].event_alert_uuid) + "</a>",
                "description": "Alert description",
                "entity": "Event",
                "entity_uuid": "<a href='/eboa_nav/query-event-links/" + str(events_alerts[1].event_uuid) + "'>" + str(events_alerts[1].event_uuid) + "</a>",
                "generator": "test2",
                "group": "EVENTS;alert_group3",
                "group_alert": "alert_group3",
                "id": str(events_alerts[1].event_alert_uuid),
                "ingestion_time": events_alerts[1].ingestion_time.isoformat(),
                "justification": "None",
                "message": "Alert message",
                "name": "alert_name4",
                "notification_time": "2018-06-05T08:07:38",
                "notified": "<span class='bold-orange'>None</span>",
                "severity": "major",
                "solved": "<span class='bold-orange'>None</span>",
                "solved_time": "None",
                "start": "2018-06-05T08:07:38",
                "stop": "2018-06-05T08:07:38",
                "timeline": "alert_name4",
                "validated": "<span class='bold-orange'>None</span>"
            },
        ]

        returned_alerts = self.driver.execute_script('return alerts;')
        functions.assert_equal_list_dictionaries(returned_alerts, alerts)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        # Row 1
        justification = event_alerts_table.find_element_by_xpath("tbody/tr[1]/td[1]")

        assert justification.text == "None"

        severity = event_alerts_table.find_element_by_xpath("tbody/tr[1]/td[2]")

        assert severity.text == "critical"

        group = event_alerts_table.find_element_by_xpath("tbody/tr[1]/td[3]")

        assert group.text == "alert_group2"

        name = event_alerts_table.find_element_by_xpath("tbody/tr[1]/td[4]")

        assert name.text == "alert_name3"

        message = event_alerts_table.find_element_by_xpath("tbody/tr[1]/td[5]")

        assert message.text == "Alert message"

        notification_time = event_alerts_table.find_element_by_xpath("tbody/tr[1]/td[6]")

        assert notification_time.text == "2018-06-05T08:07:37"

        solved = event_alerts_table.find_element_by_xpath("tbody/tr[1]/td[7]")

        assert solved.text == "None"

        solved_time = event_alerts_table.find_element_by_xpath("tbody/tr[1]/td[8]")

        assert solved_time.text == "None"

        description = event_alerts_table.find_element_by_xpath("tbody/tr[1]/td[9]")

        assert description.text == "Alert description"

        validated = event_alerts_table.find_element_by_xpath("tbody/tr[1]/td[10]")

        assert validated.text == "None"

        generator = event_alerts_table.find_element_by_xpath("tbody/tr[1]/td[11]")

        assert generator.text == "test"

        notified = event_alerts_table.find_element_by_xpath("tbody/tr[1]/td[12]")

        assert notified.text == "None"

        ingestion_time = event_alerts_table.find_element_by_xpath("tbody/tr[1]/td[13]")

        assert ingestion_time.text == events_alerts[0].ingestion_time.isoformat()

        alert_uuid = event_alerts_table.find_element_by_xpath("tbody/tr[1]/td[14]")

        assert alert_uuid.text == str(events_alerts[0].event_alert_uuid)

        event_uuid = event_alerts_table.find_element_by_xpath("tbody/tr[1]/td[15]")

        assert event_uuid.text == str(events_alerts[0].event_uuid)

        # Row 2
        justification = event_alerts_table.find_element_by_xpath("tbody/tr[2]/td[1]")

        assert justification.text == "None"

        severity = event_alerts_table.find_element_by_xpath("tbody/tr[2]/td[2]")

        assert severity.text == "major"

        group = event_alerts_table.find_element_by_xpath("tbody/tr[2]/td[3]")

        assert group.text == "alert_group3"

        name = event_alerts_table.find_element_by_xpath("tbody/tr[2]/td[4]")

        assert name.text == "alert_name4"

        message = event_alerts_table.find_element_by_xpath("tbody/tr[2]/td[5]")

        assert message.text == "Alert message"

        notification_time = event_alerts_table.find_element_by_xpath("tbody/tr[2]/td[6]")

        assert notification_time.text == "2018-06-05T08:07:38"

        solved = event_alerts_table.find_element_by_xpath("tbody/tr[2]/td[7]")

        assert solved.text == "None"

        solved_time = event_alerts_table.find_element_by_xpath("tbody/tr[2]/td[8]")

        assert solved_time.text == "None"

        description = event_alerts_table.find_element_by_xpath("tbody/tr[2]/td[9]")

        assert description.text == "Alert description"

        validated = event_alerts_table.find_element_by_xpath("tbody/tr[2]/td[10]")

        assert validated.text == "None"

        generator = event_alerts_table.find_element_by_xpath("tbody/tr[2]/td[11]")

        assert generator.text == "test2"

        notified = event_alerts_table.find_element_by_xpath("tbody/tr[2]/td[12]")

        assert notified.text == "None"

        ingestion_time = event_alerts_table.find_element_by_xpath("tbody/tr[2]/td[13]")

        assert ingestion_time.text == events_alerts[1].ingestion_time.isoformat()

        alert_uuid = event_alerts_table.find_element_by_xpath("tbody/tr[2]/td[14]")

        assert alert_uuid.text == str(events_alerts[1].event_alert_uuid)

        event_uuid = event_alerts_table.find_element_by_xpath("tbody/tr[2]/td[15]")

        assert event_uuid.text == str(events_alerts[1].event_uuid)

    def test_event_alerts_query_source_filter(self):

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
                            "validity_stop":"2019-06-05T08:07:36",
                            "priority":30
                        },
                        "events":[
                            {
                            "explicit_reference":"ER2",
                            "gauge":{
                                "name":"GAUGE_NAME2",
                                "system":"GAUGE_SYSTEM2",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2019-06-05T02:07:03",
                            "stop":"2019-06-05T08:07:36",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:37",
                                    "alert_cnf":{
                                        "name":"alert_name3",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group2"
                                    }
                                }
                            ]
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
                            "name":"source_1.json",
                            "reception_time":"2018-06-06T13:33:29",
                            "generation_time":"2018-07-05T02:07:03",
                            "validity_start":"2018-06-05T02:07:03",
                            "validity_stop":"2019-06-05T08:07:36",
                            "priority":30
                        },
                        "events":[
                            {
                            "explicit_reference":"ER2",
                            "gauge":{
                                "name":"GAUGE_NAME2",
                                "system":"GAUGE_SYSTEM2",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2019-06-05T02:07:03",
                            "stop":"2019-06-05T08:07:36",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test2",
                                    "notification_time":"2018-06-05T08:07:38",
                                    "alert_cnf":{
                                        "name":"alert_name4",
                                        "severity":"major",
                                        "description":"Alert description",
                                        "group":"alert_group3"
                                    }
                                }
                            ]
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
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        # Fill the source_like input
        input_element = self.driver.find_element_by_id("events-source-text")
        input_element.send_keys("source.json")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click_no_graphs_events(self.driver)

        # Fill the source input
        input_element = self.driver.find_element_by_id("events-source-text")
        input_element.send_keys("source.json")

        menu = Select(self.driver.find_element_by_id("events-source-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click_no_graphs_events(self.driver)

        # Fill the source_in input
        input_element = self.driver.find_element_by_id("events-sources-in-text")
        functions.click(input_element)

        input_element.send_keys("source.json")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("events-sources-in-select"))
        options.select_by_visible_text("source.json")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click_no_graphs_events(self.driver)

        # Fill the source_in input
        input_element = self.driver.find_element_by_id("events-sources-in-text")
        functions.click(input_element)

        input_element.send_keys("source_1.json")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("events-sources-in-select"))
        options.select_by_visible_text("source_1.json")

        notInButton = self.driver.find_element_by_id("events-sources-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        # end if

        # Click on query button
        functions.click(submit_button)

        # Check table generate
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

    def test_event_alerts_query_explicit_ref_filter(self):

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
                            "validity_stop":"2019-06-05T08:07:36",
                            "priority":30
                        },
                        "events":[
                            {
                            "explicit_reference":"ER2",
                            "gauge":{
                                "name":"GAUGE_NAME2",
                                "system":"GAUGE_SYSTEM2",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2019-06-05T02:07:03",
                            "stop":"2019-06-05T08:07:36",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:37",
                                    "alert_cnf":{
                                        "name":"alert_name3",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group2"
                                    }
                                }
                            ]
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
                            "name":"source_1.json",
                            "reception_time":"2018-06-06T13:33:29",
                            "generation_time":"2018-07-05T02:07:03",
                            "validity_start":"2018-06-05T02:07:03",
                            "validity_stop":"2019-06-05T08:07:36",
                            "priority":30
                        },
                        "events":[
                            {
                            "explicit_reference":"ER",
                            "gauge":{
                                "name":"GAUGE_NAME",
                                "system":"GAUGE_SYSTEM",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2019-06-05T02:07:03",
                            "stop":"2019-06-05T08:07:36",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test2",
                                    "notification_time":"2018-06-05T08:07:38",
                                    "alert_cnf":{
                                        "name":"alert_name4",
                                        "severity":"major",
                                        "description":"Alert description",
                                        "group":"alert_group3"
                                    }
                                }
                            ]
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
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        # Fill the explicit_ref_like input
        input_element = self.driver.find_element_by_id("events-er-text")
        input_element.send_keys("ER2")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click_no_graphs_events(self.driver)

        # Fill the explicit reference input
        input_element = self.driver.find_element_by_id("events-er-text")
        input_element.send_keys("ER2")

        menu = Select(self.driver.find_element_by_id("events-er-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click_no_graphs_events(self.driver)

        # Fill the explicit_reference_in input
        input_element = self.driver.find_element_by_id("events-ers-in-text")
        functions.click(input_element)

        input_element.send_keys("ER")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("events-ers-in-select"))
        options.select_by_visible_text("ER")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click_no_graphs_events(self.driver)

        # Fill the explicit_ref_in input
        input_element = self.driver.find_element_by_id("events-ers-in-text")
        functions.click(input_element)

        input_element.send_keys("ER2")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("events-ers-in-select"))
        options.select_by_visible_text("ER2")

        notInButton = self.driver.find_element_by_id("events-ers-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        # end if

        # Click on query button
        functions.click(submit_button)

        # Check table generate
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

    def test_event_alerts_query_key_filter(self):

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
                            "validity_stop":"2019-06-05T08:07:36",
                            "priority":30
                        },
                        "events":[
                            {
                            "explicit_reference":"ER2",
                            "gauge":{
                                "name":"GAUGE_NAME2",
                                "system":"GAUGE_SYSTEM2",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2019-06-05T02:07:03",
                            "stop":"2019-06-05T08:07:36",
                            "key":"EVENT_KEY",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:37",
                                    "alert_cnf":{
                                        "name":"alert_name3",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group2"
                                    }
                                }
                            ]
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
                            "name":"source_1.json",
                            "reception_time":"2018-06-06T13:33:29",
                            "generation_time":"2018-07-05T02:07:03",
                            "validity_start":"2018-06-05T02:07:03",
                            "validity_stop":"2019-06-05T08:07:36",
                            "priority":30
                        },
                        "events":[
                            {
                            "explicit_reference":"ER",
                            "gauge":{
                                "name":"GAUGE_NAME",
                                "system":"GAUGE_SYSTEM",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2019-06-05T02:07:03",
                            "stop":"2019-06-05T08:07:36",
                            "key":"EVENT_KEY_2",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test2",
                                    "notification_time":"2018-06-05T08:07:38",
                                    "alert_cnf":{
                                        "name":"alert_name4",
                                        "severity":"major",
                                        "description":"Alert description",
                                        "group":"alert_group3"
                                    }
                                }
                            ]
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
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        # Fill the key_like input
        input_element = self.driver.find_element_by_id("events-key-text")
        input_element.send_keys("EVENT_KEY")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click_no_graphs_events(self.driver)

        # Fill the key input
        input_element = self.driver.find_element_by_id("events-key-text")
        input_element.send_keys("EVENT_KEY")

        menu = Select(self.driver.find_element_by_id("events-key-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
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
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

       ## Not In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
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
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

    def test_event_alerts_query_gauge_name_filter(self):
        
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
                            "validity_stop":"2019-06-05T08:07:36",
                            "priority":30
                        },
                        "events":[
                            {
                            "explicit_reference":"ER2",
                            "gauge":{
                                "name":"GAUGE_NAME2",
                                "system":"GAUGE_SYSTEM2",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2019-06-05T02:07:03",
                            "stop":"2019-06-05T08:07:36",
                            "key":"EVENT_KEY",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:37",
                                    "alert_cnf":{
                                        "name":"alert_name3",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group2"
                                    }
                                }
                            ]
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
                            "name":"source_1.json",
                            "reception_time":"2018-06-06T13:33:29",
                            "generation_time":"2018-07-05T02:07:03",
                            "validity_start":"2018-06-05T02:07:03",
                            "validity_stop":"2019-06-05T08:07:36",
                            "priority":30
                        },
                        "events":[
                            {
                            "explicit_reference":"ER",
                            "gauge":{
                                "name":"GAUGE_NAME",
                                "system":"GAUGE_SYSTEM",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2019-06-05T02:07:03",
                            "stop":"2019-06-05T08:07:36",
                            "key":"EVENT_KEY_2",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test2",
                                    "notification_time":"2018-06-05T08:07:38",
                                    "alert_cnf":{
                                        "name":"alert_name4",
                                        "severity":"major",
                                        "description":"Alert description",
                                        "group":"alert_group3"
                                    }
                                }
                            ]
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
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        # Fill the gauge_name_like input
        input_element = self.driver.find_element_by_id("events-gauge-name-text")
        input_element.send_keys("GAUGE_NAME")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click_no_graphs_events(self.driver)

        # Fill the gauge name input
        input_element = self.driver.find_element_by_id("events-gauge-name-text")
        input_element.send_keys("GAUGE_NAME")

        menu = Select(self.driver.find_element_by_id("events-gauge-name-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click_no_graphs_events(self.driver)

        # Fill the gauge_name_in input
        input_element = self.driver.find_element_by_id("events-gauge-names-in-text")
        functions.click(input_element)

        input_element.send_keys("GAUGE_NAME2")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("events-gauge-names-in-select"))
        options.select_by_visible_text("GAUGE_NAME2")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

        ## Not In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click_no_graphs_events(self.driver)

        # Fill the gauge_name_in input
        input_element = self.driver.find_element_by_id("events-gauge-names-in-text")
        functions.click(input_element)

        input_element.send_keys("GAUGE_NAME")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("events-gauge-names-in-select"))
        options.select_by_visible_text("GAUGE_NAME")

        notInButton = self.driver.find_element_by_id("events-gauge-names-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        # end if

        # Click on query button
        functions.click(submit_button)

        # Check table generate
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

    def test_event_alerts_query_gauge_system_filter(self):

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
                            "validity_stop":"2019-06-05T08:07:36",
                            "priority":30
                        },
                        "events":[
                            {
                            "explicit_reference":"ER2",
                            "gauge":{
                                "name":"GAUGE_NAME2",
                                "system":"GAUGE_SYSTEM2",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2019-06-05T02:07:03",
                            "stop":"2019-06-05T08:07:36",
                            "key":"EVENT_KEY",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:37",
                                    "alert_cnf":{
                                        "name":"alert_name3",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group2"
                                    }
                                }
                            ]
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
                            "name":"source_1.json",
                            "reception_time":"2018-06-06T13:33:29",
                            "generation_time":"2018-07-05T02:07:03",
                            "validity_start":"2018-06-05T02:07:03",
                            "validity_stop":"2019-06-05T08:07:36",
                            "priority":30
                        },
                        "events":[
                            {
                            "explicit_reference":"ER",
                            "gauge":{
                                "name":"GAUGE_NAME",
                                "system":"GAUGE_SYSTEM",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2019-06-05T02:07:03",
                            "stop":"2019-06-05T08:07:36",
                            "key":"EVENT_KEY_2",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test2",
                                    "notification_time":"2018-06-05T08:07:38",
                                    "alert_cnf":{
                                        "name":"alert_name4",
                                        "severity":"major",
                                        "description":"Alert description",
                                        "group":"alert_group3"
                                    }
                                }
                            ]
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
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        # Fill the gauge_system_like input
        input_element = self.driver.find_element_by_id("events-gauge-system-text")
        input_element.send_keys("GAUGE_SYSTEM")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click_no_graphs_events(self.driver)

        # Fill the gauge system input
        input_element = self.driver.find_element_by_id("events-gauge-system-text")
        input_element.send_keys("GAUGE_SYSTEM")

        menu = Select(self.driver.find_element_by_id("events-gauge-system-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click_no_graphs_events(self.driver)

        # Fill the gauge_system_in input
        input_element = self.driver.find_element_by_id("events-gauge-systems-in-text")
        functions.click(input_element)

        input_element.send_keys("GAUGE_SYSTEM2")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("events-gauge-systems-in-select"))
        options.select_by_visible_text("GAUGE_SYSTEM2")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

        ## Not In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click_no_graphs_events(self.driver)

        # Fill the gauge_system_in input
        input_element = self.driver.find_element_by_id("events-gauge-systems-in-text")
        functions.click(input_element)

        input_element.send_keys("GAUGE_SYSTEM")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("events-gauge-systems-in-select"))
        options.select_by_visible_text("GAUGE_SYSTEM")

        notInButton = self.driver.find_element_by_id("events-gauge-systems-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        # end if

        # Click on query button
        functions.click(submit_button)

        # Check table generate
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0
        
        assert number_of_elements == 1

    def test_event_alerts_query_value_text(self):

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
                            "validity_stop":"2019-06-05T08:07:36",
                            "priority":30
                        },
                        "events":[
                            {
                            "explicit_reference":"ER2",
                            "gauge":{
                                "name":"GAUGE_NAME2",
                                "system":"GAUGE_SYSTEM2",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2019-06-05T02:07:03",
                            "stop":"2019-06-05T08:07:36",
                            "values": [
                                {
                                "name":"VALUES",
                                "type":"object",
                                "values":[
                                    {
                                    "type": "text",
                                    "name": "textname_1",
                                    "value": "textvalue_1"
                                }
                                ]
                            }
                            ],
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:37",
                                    "alert_cnf":{
                                        "name":"alert_name3",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group2"
                                    }
                                }
                            ]
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
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "text", "textname_1", "textvalue_1", "==", "==", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "text", "textname_1", "textvalue_2", "!=", "==", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

    def test_event_alerts_query_value_timestamp(self):

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
                            "validity_stop":"2019-06-05T08:07:36",
                            "priority":30
                        },
                        "events":[
                            {
                            "explicit_reference":"ER2",
                            "gauge":{
                                "name":"GAUGE_NAME2",
                                "system":"GAUGE_SYSTEM2",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2019-06-05T02:07:03",
                            "stop":"2019-06-05T08:07:36",
                            "values": [
                                {
                                "name":"VALUES",
                                "type":"object",
                                "values":[
                                    {
                                    "type": "timestamp",
                                    "name": "timestamp_name_1",
                                    "value": "2019-04-26T14:14:14"
                                }
                                ]
                            }
                            ],
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:37",
                                    "alert_cnf":{
                                        "name":"alert_name3",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group2"
                                    }
                                }
                            ]
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
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", "==", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", "==", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", "==", ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", "==", ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", "==", "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", "==", "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", "==", "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

    def test_event_alerts_query_value_double(self):

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
                            "validity_stop":"2019-06-05T08:07:36",
                            "priority":30
                        },
                        "events":[
                            {
                            "explicit_reference":"ER2",
                            "gauge":{
                                "name":"GAUGE_NAME2",
                                "system":"GAUGE_SYSTEM2",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2019-06-05T02:07:03",
                            "stop":"2019-06-05T08:07:36",
                            "values": [
                                {
                                "name":"VALUES",
                                "type":"object",
                                "values":[
                                    {
                                    "type": "double",
                                    "name": "double_name_1",
                                    "value": "3.5"
                                }
                                ]
                            }
                            ],
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:37",
                                    "alert_cnf":{
                                        "name":"alert_name3",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group2"
                                    }
                                }
                            ]
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
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.5", "==", "==", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.5", "!=", "==", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.5", "==", ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.25", "==", ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.75", "==", ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.5", "==", ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.25", "==", ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.75", "==", ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.5", "==", "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.25", "==", "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.75", "==", "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.5", "==", "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.25", "==", "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.75", "==", "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.5", "==", "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.25", "==", "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "3.75", "==", "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

    def test_event_alerts_query_ingestion_time(self):

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
                            "validity_stop":"2019-06-05T08:07:36",
                            "priority":30
                        },
                        "events":[
                            {
                            "explicit_reference":"ER2",
                            "gauge":{
                                "name":"GAUGE_NAME2",
                                "system":"GAUGE_SYSTEM2",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2019-06-05T02:07:03",
                            "stop":"2019-06-05T08:07:36",
                            "values": [
                                {
                                "name":"VALUES",
                                "type":"object",
                                "values":[
                                    {
                                    "type": "double",
                                    "name": "double_name_1",
                                    "value": "3.5"
                                }
                                ]
                            }
                            ],
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:37",
                                    "alert_cnf":{
                                        "name":"alert_name3",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group2"
                                    }
                                }
                            ]
                            }
                        ]
                    }
                ]
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
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_ingestion_time(self.driver, wait, "events", ingestion_time, ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_ingestion_time(self.driver, wait, "events", ingestion_time, ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_ingestion_time(self.driver, wait, "events", ingestion_time, "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_ingestion_time(self.driver, wait, "events", ingestion_time, "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_ingestion_time(self.driver, wait, "events", ingestion_time, "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

    def test_event_alerts_query_two_values(self):

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
                            "validity_stop":"2019-06-05T08:07:36",
                            "priority":30
                        },
                        "events":[
                            {
                            "explicit_reference":"ER3",
                            "gauge":{
                                "name":"GAUGE_NAME3",
                                "system":"GAUGE_SYSTEM3",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2019-06-05T02:07:03",
                            "stop":"2019-06-05T08:07:36",
                            "values": [
                                {
                                "name":"VALUES",
                                "type":"object",
                                "values":[
                                    {
                                    "name": "textname_1",
                                    "type": "text",
                                    "value": "textvalue_1"
                                }
                                ]
                            }
                            ],
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:37",
                                    "alert_cnf":{
                                        "name":"alert_name3",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group2"
                                    }
                                }
                            ]
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
                            "name":"source_1.json",
                            "reception_time":"2018-06-06T13:33:29",
                            "generation_time":"2018-07-05T02:07:03",
                            "validity_start":"2018-06-05T02:07:03",
                            "validity_stop":"2019-06-05T08:07:36",
                            "priority":30
                        },
                        "events":[
                            {
                            "explicit_reference":"ER2",
                            "gauge":{
                                "name":"GAUGE_NAME2",
                                "system":"GAUGE_SYSTEM2",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2019-06-05T02:07:03",
                            "stop":"2019-06-05T08:07:36",
                            "values": [
                                {
                                "name":"VALUES",
                                "type":"object",
                                "values":[
                                    {
                                    "name": "textname_1",
                                    "type": "text",
                                    "value": "textvalue_1"
                                    },
                                    {
                                    "name": "double_name_1",
                                    "type": "double",
                                    "value": "1.4"
                                    }
                                ]
                            }
                            ],
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test2",
                                    "notification_time":"2018-06-05T08:07:38",
                                    "alert_cnf":{
                                        "name":"alert_name4",
                                        "severity":"major",
                                        "description":"Alert description",
                                        "group":"alert_group3"
                                    }
                                }
                            ]
                            },
                            {
                            "explicit_reference":"ER",
                            "gauge":{
                                "name":"GAUGE_NAME",
                                "system":"GAUGE_SYSTEM",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2019-06-05T02:07:03",
                            "stop":"2019-06-05T08:07:36",
                            "values": [
                                {
                                "name":"VALUES",
                                "type":"object",
                                "values":[
                                    {
                                    "name": "textname_3",
                                    "type": "text",
                                    "value": "textvalue_2"
                                }
                                ]
                            }
                            ],
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test2",
                                    "notification_time":"2019-06-05T08:07:36",
                                    "alert_cnf":{
                                        "name":"alert_name2",
                                        "severity":"major",
                                        "description":"Alert description",
                                        "group":"alert_group1"
                                    }
                                }
                            ]
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
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_value(self.driver, wait, "events", "text", "textname_1", "textvalue_1", "==", "==", 1)
        functions.click(self.driver.find_element_by_id("events-add-value"))
        functions.fill_value(self.driver, wait, "events", "double", "double_name_1", "1.4", "==", "==", 2)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

    def test_event_alerts_query_period(self):

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
                            "validity_stop":"2019-06-05T08:07:36",
                            "priority":30
                        },
                        "events":[
                            {
                            "explicit_reference":"ER3",
                            "gauge":{
                                "name":"GAUGE_NAME3",
                                "system":"GAUGE_SYSTEM3",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2019-06-05T02:00:00",
                            "stop":"2019-06-05T03:00:00",
                            "values": [
                                {
                                "name":"VALUES",
                                "type":"object",
                                "values":[
                                    {
                                    "name": "textname_1",
                                    "type": "text",
                                    "value": "textvalue_1"
                                }
                                ]
                            }
                            ],
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:37",
                                    "alert_cnf":{
                                        "name":"alert_name3",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group2"
                                    }
                                }
                            ]
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
                            "name":"source_1.json",
                            "reception_time":"2018-06-06T13:33:29",
                            "generation_time":"2018-07-05T02:07:03",
                            "validity_start":"2018-06-05T02:07:03",
                            "validity_stop":"2019-06-05T08:07:36",
                            "priority":30
                        },
                        "events":[
                            {
                            "explicit_reference":"ER2",
                            "gauge":{
                                "name":"GAUGE_NAME2",
                                "system":"GAUGE_SYSTEM2",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2019-06-05T03:00:00",
                            "stop":"2019-06-05T04:00:00",
                            "values": [
                                {
                                "name":"VALUES",
                                "type":"object",
                                "values":[
                                    {
                                    "name": "textname_1",
                                    "type": "text",
                                    "value": "textvalue_1"
                                    },
                                    {
                                    "name": "double_name_1",
                                    "type": "double",
                                    "value": "1.4"
                                    }
                                ]
                            }
                            ],
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test2",
                                    "notification_time":"2018-06-05T08:07:38",
                                    "alert_cnf":{
                                        "name":"alert_name4",
                                        "severity":"major",
                                        "description":"Alert description",
                                        "group":"alert_group3"
                                    }
                                }
                            ]
                            },
                            {
                            "explicit_reference":"ER",
                            "gauge":{
                                "name":"GAUGE_NAME",
                                "system":"GAUGE_SYSTEM",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2019-06-05T04:00:00",
                            "stop":"2019-06-05T05:00:00",
                            "values": [
                                {
                                "name":"VALUES",
                                "type":"object",
                                "values":[
                                    {
                                    "name": "textname_3",
                                    "type": "text",
                                    "value": "textvalue_2"
                                }
                                ]
                            }
                            ],
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test2",
                                    "notification_time":"2019-06-05T08:07:36",
                                    "alert_cnf":{
                                        "name":"alert_name2",
                                        "severity":"major",
                                        "description":"Alert description",
                                        "group":"alert_group1"
                                    }
                                }
                            ]
                            }
                        ]
                    }
                ]
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

        functions.fill_period(self.driver, wait, "events", 1,  start_value = "2019-06-05T03:00:00", start_operator = "==", end_value = "2019-06-05T04:00:00", end_operator = "==")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## >= ## Only Start##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_period(self.driver, wait, "events", 1,  start_value = "2019-06-05T03:00:00", start_operator = ">=")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        ## != ## Only End##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_period(self.driver, wait, "events", 1,  end_value = "2019-06-05T04:00:00", end_operator = "!=")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        ## > ## Only Start## < ## Only Start##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_period(self.driver, wait, "events", 1, start_value = "2019-06-05T01:30:00", start_operator = ">")
        functions.click(self.driver.find_element_by_id("events-add-start-stop"))
        functions.fill_period(self.driver, wait, "events", 2, start_value = "2019-06-05T03:00:00", start_operator = "<")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## <= ## Start## > ## End## != ## Start## >= ## End##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Events")
        functions.click_no_graphs_events(self.driver)

        functions.fill_period(self.driver, wait, "events", 1, start_value = "2019-06-05T03:00:00", start_operator = "<=", end_value = "2019-06-05T02:30:00", end_operator = ">")
        functions.click(self.driver.find_element_by_id("events-add-start-stop"))
        functions.fill_period(self.driver, wait, "events", 2, start_value = "2019-06-05T04:00:00", start_operator = "!=", end_value = "2019-06-05T03:00:00", end_operator = ">=")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'event-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        event_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(event_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(event_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2
