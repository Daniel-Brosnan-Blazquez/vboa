"""
Automated tests for the explicit_ref alerts tab

Written by DEIMOS Space S.L. (jubv)

module vboa
"""
import os
import sys
import unittest
import time
import subprocess
import datetime
import vboa.tests.functions as functions
import re
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
from eboa.debugging import debug

# Import datamodel
from eboa.datamodel.dim_signatures import DimSignature
from eboa.datamodel.alerts import Alert, ExplicitRefAlert
from eboa.datamodel.events import Event, EventLink, EventKey, EventText, EventDouble, EventObject, EventGeometry, EventBoolean, EventTimestamp
from eboa.datamodel.gauges import Gauge
from eboa.datamodel.sources import Source, SourceStatus
from eboa.datamodel.explicit_refs import ExplicitRef, ExplicitRefGrp, ExplicitRefLink
from eboa.datamodel.annotations import Annotation, AnnotationCnf, AnnotationText, AnnotationDouble, AnnotationObject, AnnotationGeometry, AnnotationBoolean, AnnotationTimestamp


class TestExplicitReferenceAlertsTab(unittest.TestCase):

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

    def test_explicit_ref_alerts_no_data(self):

        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'explicit-ref-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

    def test_explicit_ref_alerts_query_no_filter_with_timeline(self):

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
                        "explicit_references":[
                            {
                            "name":"ER1",
                            "group":"ER_GROUP",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:36",
                                    "alert_cnf":{
                                        "name":"alert_name1",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group1"
                                    }
                                },
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
        functions.goToTab(self.driver,"Explicit references")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        # Check whether the timeline is displayed
        timeline_section = self.driver.find_element_by_id("timeline-general-view-alerts")

        condition = timeline_section.is_displayed()
        assert condition is True

        # Check generated content for widgets
        kwargs ={}
        kwargs["order_by"] = {"field": "notification_time", "descending": False}
        explicit_refs_alerts = self.query_eboa.get_explicit_ref_alerts(**kwargs)

        assert len(explicit_refs_alerts) == 2

        alerts = [
            {
                "alert_uuid": "<a href='/eboa_nav/query-er-alert/" + str(explicit_refs_alerts[0].explicit_ref_alert_uuid) + "'>" + str(explicit_refs_alerts[0].explicit_ref_alert_uuid) + "</a>",
                "description": "Alert description",
                "entity": "Explicit reference",
                "entity_uuid": "<a href='/eboa_nav/query-er/" + str(explicit_refs_alerts[0].explicit_ref_uuid) + "'>" + str(explicit_refs_alerts[0].explicit_ref_uuid) + "</a>",
                "generator": "test",
                "group": "EXPLICIT_REFERENCES;alert_group1",
                "group_alert": "alert_group1",
                "id": str(explicit_refs_alerts[0].explicit_ref_alert_uuid),
                "ingestion_time": explicit_refs_alerts[0].ingestion_time.isoformat(),
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
            {
                "alert_uuid": "<a href='/eboa_nav/query-er-alert/" + str(explicit_refs_alerts[1].explicit_ref_alert_uuid) + "'>" + str(explicit_refs_alerts[1].explicit_ref_alert_uuid) + "</a>",
                "description": "Alert description",
                "entity": "Explicit reference",
                "entity_uuid": "<a href='/eboa_nav/query-er/" + str(explicit_refs_alerts[1].explicit_ref_uuid) + "'>" + str(explicit_refs_alerts[1].explicit_ref_uuid) + "</a>",
                "generator": "test2",
                "group": "EXPLICIT_REFERENCES;alert_group1",
                "group_alert": "alert_group1",
                "id": str(explicit_refs_alerts[1].explicit_ref_alert_uuid),
                "ingestion_time": explicit_refs_alerts[1].ingestion_time.isoformat(),
                "justification": "None",
                "message": "Alert message",
                "name": "alert_name2",
                "notification_time": "2019-06-05T08:07:36",
                "notified": "<span class='bold-orange'>None</span>",
                "severity": "major",
                "solved": "<span class='bold-orange'>None</span>",
                "solved_time": "None",
                "start": "2019-06-05T08:07:36",
                "stop": "2019-06-05T08:07:36",
                "timeline": "alert_name2",
                "validated": "<span class='bold-orange'>None</span>"
            }
        ]

        returned_alerts = self.driver.execute_script('return alerts;')
        functions.assert_equal_list_dictionaries(returned_alerts, alerts)

        # Check er alerts table
        explicit_ref_alerts_table = self.driver.find_element_by_id("alerts-table")

        # Row 1
        justification = explicit_ref_alerts_table.find_element_by_xpath("tbody/tr[1]/td[1]")

        assert justification.text == "None"

        severity = explicit_ref_alerts_table.find_element_by_xpath("tbody/tr[1]/td[2]")

        assert severity.text == "critical"

        group = explicit_ref_alerts_table.find_element_by_xpath("tbody/tr[1]/td[3]")

        assert group.text == "alert_group1"

        name = explicit_ref_alerts_table.find_element_by_xpath("tbody/tr[1]/td[4]")

        assert name.text == "alert_name1"

        message = explicit_ref_alerts_table.find_element_by_xpath("tbody/tr[1]/td[5]")

        assert message.text == "Alert message"

        notification_time = explicit_ref_alerts_table.find_element_by_xpath("tbody/tr[1]/td[6]")

        assert notification_time.text == "2018-06-05T08:07:36"

        solved = explicit_ref_alerts_table.find_element_by_xpath("tbody/tr[1]/td[7]")

        assert solved.text == "None"

        solved_time = explicit_ref_alerts_table.find_element_by_xpath("tbody/tr[1]/td[8]")

        assert solved_time.text == "None"

        description = explicit_ref_alerts_table.find_element_by_xpath("tbody/tr[1]/td[9]")

        assert description.text == "Alert description"

        validated = explicit_ref_alerts_table.find_element_by_xpath("tbody/tr[1]/td[10]")

        assert validated.text == "None"

        generator = explicit_ref_alerts_table.find_element_by_xpath("tbody/tr[1]/td[11]")

        assert generator.text == "test"

        notified = explicit_ref_alerts_table.find_element_by_xpath("tbody/tr[1]/td[12]")

        assert notified.text == "None"

        ingestion_time = explicit_ref_alerts_table.find_element_by_xpath("tbody/tr[1]/td[13]")

        assert ingestion_time.text == explicit_refs_alerts[0].ingestion_time.isoformat()

        alert_uuid = explicit_ref_alerts_table.find_element_by_xpath("tbody/tr[1]/td[14]")

        assert alert_uuid.text == str(explicit_refs_alerts[0].explicit_ref_alert_uuid)

        explicit_ref_uuid = explicit_ref_alerts_table.find_element_by_xpath("tbody/tr[1]/td[15]")

        assert explicit_ref_uuid.text == str(explicit_refs_alerts[0].explicit_ref_uuid)

        # Row 2
        justification = explicit_ref_alerts_table.find_element_by_xpath("tbody/tr[2]/td[1]")

        assert justification.text == "None"

        severity = explicit_ref_alerts_table.find_element_by_xpath("tbody/tr[2]/td[2]")

        assert severity.text == "major"

        group = explicit_ref_alerts_table.find_element_by_xpath("tbody/tr[2]/td[3]")

        assert group.text == "alert_group1"

        name = explicit_ref_alerts_table.find_element_by_xpath("tbody/tr[2]/td[4]")

        assert name.text == "alert_name2"

        message = explicit_ref_alerts_table.find_element_by_xpath("tbody/tr[2]/td[5]")

        assert message.text == "Alert message"

        notification_time = explicit_ref_alerts_table.find_element_by_xpath("tbody/tr[2]/td[6]")

        assert notification_time.text == "2019-06-05T08:07:36"

        solved = explicit_ref_alerts_table.find_element_by_xpath("tbody/tr[2]/td[7]")

        assert solved.text == "None"

        solved_time = explicit_ref_alerts_table.find_element_by_xpath("tbody/tr[2]/td[8]")

        assert solved_time.text == "None"

        description = explicit_ref_alerts_table.find_element_by_xpath("tbody/tr[2]/td[9]")

        assert description.text == "Alert description"

        validated = explicit_ref_alerts_table.find_element_by_xpath("tbody/tr[2]/td[10]")

        assert validated.text == "None"

        generator = explicit_ref_alerts_table.find_element_by_xpath("tbody/tr[2]/td[11]")

        assert generator.text == "test2"

        notified = explicit_ref_alerts_table.find_element_by_xpath("tbody/tr[2]/td[12]")

        assert notified.text == "None"

        ingestion_time = explicit_ref_alerts_table.find_element_by_xpath("tbody/tr[2]/td[13]")

        assert ingestion_time.text == explicit_refs_alerts[1].ingestion_time.isoformat()

        alert_uuid = explicit_ref_alerts_table.find_element_by_xpath("tbody/tr[2]/td[14]")

        assert alert_uuid.text == str(explicit_refs_alerts[1].explicit_ref_alert_uuid)

        explicit_ref_uuid = explicit_ref_alerts_table.find_element_by_xpath("tbody/tr[2]/td[15]")

        assert explicit_ref_uuid.text == str(explicit_refs_alerts[1].explicit_ref_uuid)

    def test_explicit_ref_alerts_query_explicit_ref_filter(self):

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
                        "explicit_references":[
                            {
                            "name":"ER1",
                            "group":"ER_GROUP",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:36",
                                    "alert_cnf":{
                                        "name":"alert_name1",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group1"
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
                            "name":"source1.json",
                            "reception_time":"2018-06-06T13:33:29",
                            "generation_time":"2018-07-05T02:07:03",
                            "validity_start":"2018-06-05T02:07:03",
                            "validity_stop":"2019-06-05T08:07:36",
                            "priority":30
                        },
                        "explicit_references":[
                            {
                            "name":"ER2",
                            "group":"ER_GROUP",
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

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the explicit_ref_like input
        input_element = self.driver.find_element_by_id("explicit-refs-er-text")
        input_element.send_keys("ER2")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the explicit_ref_like input
        input_element = self.driver.find_element_by_id("explicit-refs-er-text")
        input_element.send_keys("ER2")

        menu = Select(self.driver.find_element_by_id("explicit-refs-er-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the explicit_ref_in input
        input_element = self.driver.find_element_by_id("explicit-refs-ers-in-text")
        functions.click(input_element)

        input_element.send_keys("ER1")
        input_element.send_keys(Keys.LEFT_SHIFT)
        input_element.clear()
        input_element.send_keys("ER2")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("explicit-refs-ers-in-select"))
        options.select_by_visible_text("ER1")
        options.select_by_visible_text("ER2")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the explicit_ref_in input
        input_element = self.driver.find_element_by_id("explicit-refs-ers-in-text")
        functions.click(input_element)

        input_element.send_keys("ER2")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("explicit-refs-ers-in-select"))
        options.select_by_visible_text("ER2")

        notInButton = self.driver.find_element_by_id("explicit-refs-ers-in-checkbox")        
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        #end if

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generate
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

    def test_explicit_ref_alerts_query_group_filter(self):

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
                        "explicit_references":[
                            {
                            "name":"ER1",
                            "group":"ER_GROUP1",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:36",
                                    "alert_cnf":{
                                        "name":"alert_name1",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group1"
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
                            "name":"source1.json",
                            "reception_time":"2018-06-06T13:33:29",
                            "generation_time":"2018-07-05T02:07:03",
                            "validity_start":"2018-06-05T02:07:03",
                            "validity_stop":"2019-06-05T08:07:36",
                            "priority":30
                        },
                        "explicit_references":[
                            {
                            "name":"ER2",
                            "group":"ER_GROUP2",
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

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the group_like input
        input_element = self.driver.find_element_by_id("explicit-refs-group-text")
        input_element.send_keys("ER_GROUP2")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the group_like input
        input_element = self.driver.find_element_by_id("explicit-refs-group-text")
        input_element.send_keys("ER_GROUP2")

        menu = Select(self.driver.find_element_by_id("explicit-refs-group-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the group_in input
        input_element = self.driver.find_element_by_id("explicit-refs-groups-in-text")
        functions.click(input_element)

        input_element.send_keys("ER_GROUP1")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("explicit-refs-groups-in-select"))
        options.select_by_visible_text("ER_GROUP1")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the group_in input
        input_element = self.driver.find_element_by_id("explicit-refs-groups-in-text")
        functions.click(input_element)

        input_element.send_keys("ER_GROUP2")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("explicit-refs-groups-in-select"))
        options.select_by_visible_text("ER_GROUP2")

        notInButton = self.driver.find_element_by_id("explicit-refs-groups-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        #end if

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generate
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

    def test_explicit_ref_alerts_query_source_filter(self):

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
                            "explicit_reference":"ER1",
                            "gauge":{
                                "name":"GAUGE_NAME2",
                                "system":"GAUGE_SYSTEM2",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2019-06-05T02:07:03",
                            "stop":"2019-06-05T08:07:36",
                            "key":"EVENT_KEY_1",
                            }
                        ],
                        "explicit_references":[
                            {
                            "name":"ER1",
                            "group":"ER_GROUP1",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:36",
                                    "alert_cnf":{
                                        "name":"alert_name1",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group1"
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
                                "name":"GAUGE_NAME",
                                "system":"GAUGE_SYSTEM",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2019-06-05T02:07:03",
                            "stop":"2019-06-05T08:07:36",
                            "key":"EVENT_KEY_2"
                            }
                        ],
                        "explicit_references":[
                            {
                            "name":"ER2",
                            "group":"ER_GROUP2",
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

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the source_like input
        input_element = self.driver.find_element_by_id("explicit-refs-source-text")
        input_element.send_keys("source.json")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the source_like input
        input_element = self.driver.find_element_by_id("explicit-refs-source-text")
        input_element.send_keys("source_1.json")

        menu = Select(self.driver.find_element_by_id("explicit-refs-source-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the source_in input
        input_element = self.driver.find_element_by_id("explicit-refs-sources-in-text")
        functions.click(input_element)

        input_element.send_keys("source.json")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("explicit-refs-sources-in-select"))
        options.select_by_visible_text("source.json")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the source_in input
        input_element = self.driver.find_element_by_id("explicit-refs-sources-in-text")
        functions.click(input_element)

        input_element.send_keys("source_1.json")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("explicit-refs-sources-in-select"))
        options.select_by_visible_text("source_1.json")

        notInButton = self.driver.find_element_by_id("explicit-refs-sources-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        #end if

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generate
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

    def test_explicit_ref_alerts_query_key_filter(self):

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
                            "explicit_reference":"ER1",
                            "gauge":{
                                "name":"GAUGE_NAME2",
                                "system":"GAUGE_SYSTEM2",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2019-06-05T02:07:03",
                            "stop":"2019-06-05T08:07:36",
                            "key":"EVENT_KEY_1",
                            }
                        ],
                        "explicit_references":[
                            {
                            "name":"ER1",
                            "group":"ER_GROUP1",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:36",
                                    "alert_cnf":{
                                        "name":"alert_name1",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group1"
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
                                "name":"GAUGE_NAME",
                                "system":"GAUGE_SYSTEM",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2019-06-05T02:07:03",
                            "stop":"2019-06-05T08:07:36",
                            "key":"EVENT_KEY_2"
                            }
                        ],
                        "explicit_references":[
                            {
                            "name":"ER2",
                            "group":"ER_GROUP2",
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

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the gauge_name_like input
        input_element = self.driver.find_element_by_id("explicit-refs-key-text")
        input_element.send_keys("EVENT_KEY_1")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the gauge_name_like input
        input_element = self.driver.find_element_by_id("explicit-refs-key-text")
        input_element.send_keys("EVENT_KEY_1")

        menu = Select(self.driver.find_element_by_id("explicit-refs-key-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the gauge_name_in input
        input_element = self.driver.find_element_by_id("explicit-refs-keys-in-text")
        functions.click(input_element)

        input_element.send_keys("EVENT_KEY_2")
        input_element.send_keys(Keys.LEFT_SHIFT)
        input_element.clear()
        input_element.send_keys("EVENT_KEY_1")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("explicit-refs-keys-in-select"))
        options.select_by_visible_text("EVENT_KEY_2")
        options.select_by_visible_text("EVENT_KEY_1")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the gauge_name_in input
        input_element = self.driver.find_element_by_id("explicit-refs-keys-in-text")
        functions.click(input_element)

        input_element.send_keys("EVENT_KEY_1")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("explicit-refs-keys-in-select"))
        options.select_by_visible_text("EVENT_KEY_1")

        notInButton = self.driver.find_element_by_id("explicit-refs-keys-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        #end if

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generate
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

    def test_explicit_ref_alerts_query_gauge_name_filter(self):

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
                            "explicit_reference":"ER1",
                            "gauge":{
                                "name":"GAUGE_NAME_2",
                                "system":"GAUGE_SYSTEM2",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2019-06-05T02:07:03",
                            "stop":"2019-06-05T08:07:36",
                            "key":"EVENT_KEY_1",
                            }
                        ],
                        "explicit_references":[
                            {
                            "name":"ER1",
                            "group":"ER_GROUP1",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:36",
                                    "alert_cnf":{
                                        "name":"alert_name1",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group1"
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
                                "name":"GAUGE_NAME_1",
                                "system":"GAUGE_SYSTEM",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2019-06-05T02:07:03",
                            "stop":"2019-06-05T08:07:36",
                            "key":"EVENT_KEY_2"
                            }
                        ],
                        "explicit_references":[
                            {
                            "name":"ER2",
                            "group":"ER_GROUP2",
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

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the gauge_name_like input
        input_element = self.driver.find_element_by_id("explicit-refs-gauge-name-text")
        input_element.send_keys("GAUGE_NAME_1")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the gauge_name_like input
        input_element = self.driver.find_element_by_id("explicit-refs-gauge-name-text")
        input_element.send_keys("GAUGE_NAME_1")

        menu = Select(self.driver.find_element_by_id("explicit-refs-gauge-name-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the gauge_name_in input
        input_element = self.driver.find_element_by_id("explicit-refs-gauge-names-in-text")
        functions.click(input_element)

        input_element.send_keys("GAUGE_NAME_2")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("explicit-refs-gauge-names-in-select"))
        options.select_by_visible_text("GAUGE_NAME_2")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the gauge_name_in input
        input_element = self.driver.find_element_by_id("explicit-refs-gauge-names-in-text")
        functions.click(input_element)

        input_element.send_keys("GAUGE_NAME_1")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("explicit-refs-gauge-names-in-select"))
        options.select_by_visible_text("GAUGE_NAME_1")

        notInButton = self.driver.find_element_by_id("explicit-refs-gauge-names-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        #end if

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generate
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

    def test_explicit_ref_alerts_query_gauge_system_filter(self):

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
                            "explicit_reference":"ER1",
                            "gauge":{
                                "name":"GAUGE_NAME_2",
                                "system":"GAUGE_SYSTEM_2",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2019-06-05T02:07:03",
                            "stop":"2019-06-05T08:07:36",
                            "key":"EVENT_KEY_1",
                            }
                        ],
                        "explicit_references":[
                            {
                            "name":"ER1",
                            "group":"ER_GROUP1",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:36",
                                    "alert_cnf":{
                                        "name":"alert_name1",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group1"
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
                                "name":"GAUGE_NAME_1",
                                "system":"GAUGE_SYSTEM_1",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2019-06-05T02:07:03",
                            "stop":"2019-06-05T08:07:36",
                            "key":"EVENT_KEY_2"
                            }
                        ],
                        "explicit_references":[
                            {
                            "name":"ER2",
                            "group":"ER_GROUP2",
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

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the gauge_system_like input
        input_element = self.driver.find_element_by_id("explicit-refs-gauge-system-text")
        input_element.send_keys("GAUGE_SYSTEM_1")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the gauge_system_like input
        input_element = self.driver.find_element_by_id("explicit-refs-gauge-system-text")
        input_element.send_keys("GAUGE_SYSTEM_1")

        menu = Select(self.driver.find_element_by_id("explicit-refs-gauge-system-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the gauge_system_in input
        input_element = self.driver.find_element_by_id("explicit-refs-gauge-systems-in-text")
        functions.click(input_element)

        input_element.send_keys("GAUGE_SYSTEM_2")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("explicit-refs-gauge-systems-in-select"))
        options.select_by_visible_text("GAUGE_SYSTEM_2")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the gauge_system_in input
        input_element = self.driver.find_element_by_id("explicit-refs-gauge-systems-in-text")
        functions.click(input_element)

        input_element.send_keys("GAUGE_SYSTEM_1")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("explicit-refs-gauge-systems-in-select"))
        options.select_by_visible_text("GAUGE_SYSTEM_1")

        notInButton = self.driver.find_element_by_id("explicit-refs-gauge-systems-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        #end if

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generate
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

    def test_explicit_ref_alerts_query_events_value_text(self):

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
                            "explicit_reference":"ER1",
                            "gauge":{
                                "name":"GAUGE_NAME_2",
                                "system":"GAUGE_SYSTEM_2",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2019-06-05T02:07:03",
                            "stop":"2019-06-05T08:07:36",
                            "key":"EVENT_KEY_1",
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
                            ]
                            }
                        ],
                        "explicit_references":[
                            {
                            "name":"ER1",
                            "group":"ER_GROUP1",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:36",
                                    "alert_cnf":{
                                        "name":"alert_name1",
                                        "severity":"critical",
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

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "text", "textname_1", "textvalue_1", "==", "==", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "text", "textname_1", "textvalue_1", "!=", "==", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

    def test_explicit_ref_alerts_query_events_value_timestamp(self):

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
                            "explicit_reference":"ER1",
                            "gauge":{
                                "name":"GAUGE_NAME_2",
                                "system":"GAUGE_SYSTEM_2",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2019-06-05T02:07:03",
                            "stop":"2019-06-05T08:07:36",
                            "key":"EVENT_KEY_1",
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
                            ]
                            }
                        ],
                        "explicit_references":[
                            {
                            "name":"ER1",
                            "group":"ER_GROUP1",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:36",
                                    "alert_cnf":{
                                        "name":"alert_name1",
                                        "severity":"critical",
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

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", "==", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", "==",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", ">", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", "==", ">", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", ">", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", ">=", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", "==", ">=", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", ">=",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", "<",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", "<", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", "<=", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", "==", "<=",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", "<=", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", "!=",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", "==", "!=", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

    def test_explicit_ref_alerts_query_events_value_double(self):

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
                            "explicit_reference":"ER1",
                            "gauge":{
                                "name":"GAUGE_NAME_2",
                                "system":"GAUGE_SYSTEM_2",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2019-06-05T02:07:03",
                            "stop":"2019-06-05T08:07:36",
                            "key":"EVENT_KEY_1",
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
                            ]
                            }
                        ],
                        "explicit_references":[
                            {
                            "name":"ER1",
                            "group":"ER_GROUP1",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:36",
                                    "alert_cnf":{
                                        "name":"alert_name1",
                                        "severity":"critical",
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

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "double", "double_name_1", "3.5", "==", "==", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "double", "double_name_1", "3.5", "!=", "==",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "double", "double_name_1", "3.5", "==", ">",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "double", "double_name_1", "3.25", "==", ">", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "double", "double_name_1", "3.75", "==", ">",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "double", "double_name_1", "3.5", "==", ">=", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "double", "double_name_1", "3.25", "==", ">=", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "double", "double_name_1", "3.75", "==", ">=",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "double", "double_name_1", "3.5", "==", "<",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "double", "double_name_1", "3.25", "==", "<",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "double", "double_name_1", "3.75", "==", "<", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "double", "double_name_1", "3.5", "==", "<=", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "double", "double_name_1", "3.25", "==", "<=",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "double", "double_name_1", "3.75", "==", "<=", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "double", "double_name_1", "3.5", "==", "!=",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "double", "double_name_1", "3.25", "==", "!=", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

    def test_explicit_ref_alerts_query_events_two_values(self):

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
                            "explicit_reference":"ER1",
                            "gauge":{
                                "name":"GAUGE_NAME_2",
                                "system":"GAUGE_SYSTEM_2",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2019-06-05T02:07:03",
                            "stop":"2019-06-05T08:07:36",
                            "key":"EVENT_KEY_1",
                            "values": [
                                {
                                "name":"VALUES",
                                "type":"object",
                                "values":[
                                    {
                                    "name": "text_name_1",
                                    "type": "text",
                                    "value": "text_value_1"
                                    },
                                    {
                                    "name": "double_name_1",
                                    "type": "double",
                                    "value": "1.4"
                                    }
                                ]
                            }
                            ]
                            }
                        ],
                        "explicit_references":[
                            {
                            "name":"ER1",
                            "group":"ER_GROUP1",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:36",
                                    "alert_cnf":{
                                        "name":"alert_name1",
                                        "severity":"critical",
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
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "text", "text_name_1", "text_value_1", "==", "==", 1)
        functions.click(self.driver.find_element_by_id("explicit-refs-events-add-value"))
        functions.fill_value(self.driver, wait, "explicit-refs-events", "double", "double_name_1", "1.4", "==", "==", 2)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

    def test_explicit_ref_alerts_query_annotation_name_filter(self):

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
                        "annotations":[
                            {
                            "explicit_reference":"ER1",
                            "annotation_cnf":{
                                "name":"NAME_2",
                                "system":"SYSTEM_2",
                                "insertion_type":"SIMPLE_UPDATE"
                            }
                            }
                        ],
                        "explicit_references":[
                            {
                            "name":"ER1",
                            "group":"ER_GROUP1",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:36",
                                    "alert_cnf":{
                                        "name":"alert_name1",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group1"
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
                        "annotations":[
                            {
                            "explicit_reference":"ER2",
                            "annotation_cnf":{
                                "name":"NAME_1",
                                "system":"SYSTEM_1",
                                "insertion_type":"SIMPLE_UPDATE"
                            }
                            }
                        ],
                        "explicit_references":[
                            {
                            "name":"ER2",
                            "group":"ER_GROUP2",
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

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the annotation_name_like input
        # Fill the gauge_name_like input
        input_element = self.driver.find_element_by_id("explicit-refs-annotation-name-text")
        input_element.send_keys("NAME_2")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the annotation_name_like input
        input_element = self.driver.find_element_by_id("explicit-refs-annotation-name-text")
        input_element.send_keys("NAME_2")

        menu = Select(self.driver.find_element_by_id("explicit-refs-annotation-name-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the annotation_name_in input
        input_element = self.driver.find_element_by_id("explicit-refs-annotation-names-in-text")
        functions.click(input_element)

        input_element.send_keys("NAME_1")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("explicit-refs-annotation-names-in-select"))
        options.select_by_visible_text("NAME_1")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the annotation_name_in input
        input_element = self.driver.find_element_by_id("explicit-refs-annotation-names-in-text")
        functions.click(input_element)

        input_element.send_keys("NAME_2")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("explicit-refs-annotation-names-in-select"))
        options.select_by_visible_text("NAME_2")

        notInButton = self.driver.find_element_by_id("explicit-refs-annotation-names-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        #end if

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generate
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

    def test_explicit_ref_alerts_query_annotation_system_filter(self):

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
                        "annotations":[
                            {
                            "explicit_reference":"ER1",
                            "annotation_cnf":{
                                "name":"NAME_2",
                                "system":"SYSTEM_2",
                                "insertion_type":"SIMPLE_UPDATE"
                            }
                            }
                        ],
                        "explicit_references":[
                            {
                            "name":"ER1",
                            "group":"ER_GROUP1",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:36",
                                    "alert_cnf":{
                                        "name":"alert_name1",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group1"
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
                        "annotations":[
                            {
                            "explicit_reference":"ER2",
                            "annotation_cnf":{
                                "name":"NAME_1",
                                "system":"SYSTEM_1",
                                "insertion_type":"SIMPLE_UPDATE"
                            }
                            }
                        ],
                        "explicit_references":[
                            {
                            "name":"ER2",
                            "group":"ER_GROUP2",
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

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the annotation_system_like input
        input_element = self.driver.find_element_by_id("explicit-refs-annotation-system-text")
        input_element.send_keys("SYSTEM_2")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # find the element that's name attribute is gauge_system_like
        input_element = self.driver.find_element_by_id("explicit-refs-annotation-system-text")
        input_element.send_keys("SYSTEM_2")

        menu = Select(self.driver.find_element_by_id("explicit-refs-annotation-system-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # find the element that's name attribute is gauge_system_in
        input_element = self.driver.find_element_by_id("explicit-refs-annotation-systems-in-text")
        functions.click(input_element)

        input_element.send_keys("SYSTEM_1")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("explicit-refs-annotation-systems-in-select"))
        options.select_by_visible_text("SYSTEM_1")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # find the element that's name attribute is gauge_system_in
        input_element = self.driver.find_element_by_id("explicit-refs-annotation-systems-in-text")
        functions.click(input_element)

        input_element.send_keys("SYSTEM_2")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("explicit-refs-annotation-systems-in-select"))
        options.select_by_visible_text("SYSTEM_2")

        notInButton = self.driver.find_element_by_id("explicit-refs-annotation-systems-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        #end if

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generate
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

    def test_explicit_ref_alerts_query_ingestion_time(self):

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
                        "annotations":[
                            {
                            "explicit_reference":"ER1",
                            "annotation_cnf":{
                                "name":"NAME_2",
                                "system":"SYSTEM_2",
                                "insertion_type":"SIMPLE_UPDATE"
                            }
                            }
                        ],
                        "explicit_references":[
                            {
                            "name":"ER1",
                            "group":"ER_GROUP1",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:36",
                                    "alert_cnf":{
                                        "name":"alert_name1",
                                        "severity":"critical",
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

        ingestion_time = self.session.query(ExplicitRef).all()[0].ingestion_time.isoformat()

        wait = WebDriverWait(self.driver,5)

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_ingestion_time(self.driver, wait, "explicit-refs-annotations", ingestion_time, "==", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_ingestion_time(self.driver, wait, "explicit-refs-annotations", ingestion_time, ">", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_ingestion_time(self.driver, wait, "explicit-refs-annotations", ingestion_time, ">=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_ingestion_time(self.driver, wait, "explicit-refs-annotations", ingestion_time, "<", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_ingestion_time(self.driver, wait, "explicit-refs-annotations", ingestion_time,"<=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_ingestion_time(self.driver, wait, "explicit-refs-annotations", ingestion_time, "!=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

    def test_explicit_ref_alerts_query_annotations_value_text(self):

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
                        "annotations":[
                            {
                            "explicit_reference":"ER1",
                            "annotation_cnf":{
                                "name":"NAME_2",
                                "system":"SYSTEM_2",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "values":[
                                {
                                    "name":"VALUES",
                                    "type":"object",
                                    "values":[
                                        {
                                        "name": "text_name_1",
                                        "type": "text",
                                        "value": "text_value_1"
                                        }
                                    ]
                                }
                            ]
                            }
                        ],
                        "explicit_references":[
                            {
                            "name":"ER1",
                            "group":"ER_GROUP1",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:36",
                                    "alert_cnf":{
                                        "name":"alert_name1",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group1"
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
                        "annotations":[
                            {
                            "explicit_reference":"ER2",
                            "annotation_cnf":{
                                "name":"NAME_1",
                                "system":"SYSTEM_1",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "values":[
                                {
                                    "name":"VALUES",
                                    "type":"object",
                                    "values":[
                                        {
                                        "name": "text_name_2",
                                        "type": "text",
                                        "value": "text_value_2"
                                        }
                                    ]
                                }
                            ]
                            }
                        ],
                        "explicit_references":[
                            {
                            "name":"ER2",
                            "group":"ER_GROUP2",
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

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "text", "text_name_1", "text_value_1", "==", "==", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "text", "text_name_1", "text_value_2", "!=", "==", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert  number_of_elements == 1

    def test_explicit_ref_alerts_query_annotations_value_timestamp(self):

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
                        "annotations":[
                            {
                            "explicit_reference":"ER1",
                            "annotation_cnf":{
                                "name":"NAME_2",
                                "system":"SYSTEM_2",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "values":[
                                {
                                    "name":"VALUES",
                                    "type":"object",
                                    "values":[
                                        {
                                        "name": "timestamp_name_1",
                                        "type": "timestamp",
                                        "value": "2019-04-26T14:14:14"
                                        }
                                    ]
                                }
                            ]
                            }
                        ],
                        "explicit_references":[
                            {
                            "name":"ER1",
                            "group":"ER_GROUP1",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:36",
                                    "alert_cnf":{
                                        "name":"alert_name1",
                                        "severity":"critical",
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

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", "==", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", "==", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", ">", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", "==", ">", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", ">", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", ">=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", "==", ">=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", ">=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", "<", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", "==", "<", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", "<", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", "<=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", "==", "<=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", "<=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", "!=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", "==", "!=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", "!=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

    def test_explicit_ref_alerts_query_annotations_value_double(self):

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
                        "annotations":[
                            {
                            "explicit_reference":"ER1",
                            "annotation_cnf":{
                                "name":"NAME_2",
                                "system":"SYSTEM_2",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "values":[
                                {
                                    "name":"VALUES",
                                    "type":"object",
                                    "values":[
                                        {
                                        "name": "double_name_1",
                                        "type": "double",
                                        "value": "3.5"
                                        }
                                    ]
                                }
                            ]
                            }
                        ],
                        "explicit_references":[
                            {
                            "name":"ER1",
                            "group":"ER_GROUP1",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:36",
                                    "alert_cnf":{
                                        "name":"alert_name1",
                                        "severity":"critical",
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

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "double", "double_name_1", "3.5", "==", "==", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "double", "double_name_1", "3.5", "!=", "==", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "double", "double_name_1", "3.5", "==", ">", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "double", "double_name_1", "3.25", "==", ">", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "double", "double_name_1", "3.75", "==", ">", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "double", "double_name_1", "3.5", "==", ">=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "double", "double_name_1", "3.25", "==", ">=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "double", "double_name_1", "3.75", "==", ">=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "double", "double_name_1", "3.5", "==", "<", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "double", "double_name_1", "3.25", "==", "<", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "double", "double_name_1", "3.75", "==", "<", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "double", "double_name_1", "3.5", "==", "<=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "double", "double_name_1", "3.25", "==", "<=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "double", "double_name_1", "3.75", "==", "<=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "double", "double_name_1", "3.5", "==", "!=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "double", "double_name_1", "3.25", "==", "!=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "double", "double_name_1", "3.75", "==", "!=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

    def test_explicit_ref_alerts_query_annotations_two_values(self):

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
                        "annotations":[
                            {
                            "explicit_reference":"ER1",
                            "annotation_cnf":{
                                "name":"NAME_2",
                                "system":"SYSTEM_2",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "values":[
                                {
                                    "name":"VALUES",
                                    "type":"object",
                                    "values":[
                                        {
                                        "name": "text_name_1",
                                        "type": "text",
                                        "value": "text_value_1"
                                        },
                                        {
                                        "name": "double_name_1",
                                        "type": "double",
                                        "value": "1.4"
                                        }
                                    ]
                                }
                            ]
                            }
                        ],
                        "explicit_references":[
                            {
                            "name":"ER1",
                            "group":"ER_GROUP1",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:36",
                                    "alert_cnf":{
                                        "name":"alert_name1",
                                        "severity":"critical",
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
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-annotations", "text", "text_name_1", "text_value_1", "==", "==", 1)
        functions.click(self.driver.find_element_by_id("explicit-refs-annotations-add-value"))
        functions.fill_value(self.driver,wait,"explicit-refs-annotations", "double", "double_name_1", "1.4", "==", "==", 2)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

    def test_explicit_ref_alerts_query_period(self):

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
                            "explicit_reference":"ER1",
                            "gauge":{
                                "name":"GAUGE_NAME_2",
                                "system":"GAUGE_SYSTEM_2",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2019-06-05T02:00:00",
                            "stop":"2019-06-05T03:00:00",
                            "key":"EVENT_KEY_1",
                            }
                        ],
                        "explicit_references":[
                            {
                            "name":"ER1",
                            "group":"ER_GROUP1",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:36",
                                    "alert_cnf":{
                                        "name":"alert_name1",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group1"
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
                                "name":"GAUGE_NAME_1",
                                "system":"GAUGE_SYSTEM_1",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2019-06-05T03:00:00",
                            "stop":"2019-06-05T04:00:00",
                            "key":"EVENT_KEY_2"
                            }
                        ],
                        "explicit_references":[
                            {
                            "name":"ER2",
                            "group":"ER_GROUP2",
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
                            "validity_stop":"2019-06-05T08:07:36",
                            "priority":30
                        },
                        "events":[
                            {
                            "explicit_reference":"ER3",
                            "gauge":{
                                "name":"GAUGE_NAME_1",
                                "system":"GAUGE_SYSTEM_1",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2019-06-05T04:00:00",
                            "stop":"2019-06-05T05:00:00",
                            "key":"EVENT_KEY_2"
                            }
                        ],
                        "explicit_references":[
                            {
                            "name":"ER3",
                            "group":"ER_GROUP3",
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
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_period(self.driver, wait, "explicit-refs-events", 1,  "2019-06-05T03:00:00", "==","2019-06-05T04:00:00", "==")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## >= ## Only Start##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_period(self.driver, wait, "explicit-refs-events", 1, start_value = "2019-06-05T03:00:00", start_operator = ">=")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## != ## Only End##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_period(self.driver, wait, "explicit-refs-events", 1, end_value = "2019-06-05T04:00:00", end_operator = "!=")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## > ## Only Start## < ## Only Start##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_period(self.driver, wait, "explicit-refs-events", 1, start_value = "2019-06-05T01:30:00", start_operator = ">")
        functions.click(self.driver.find_element_by_id("explicit-refs-events-start-stop-add-value"))
        functions.fill_period(self.driver, wait, "explicit-refs-events", 2, start_value = "2019-06-05T03:00:00", start_operator = "<")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## <= ## Start## > ## End## != ## Start## >= ## End##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_period(self.driver, wait, "explicit-refs-events", 1, start_value = "2019-06-05T03:00:00", start_operator = "<=", end_value = "2019-06-05T02:30:00", end_operator = ">")
        functions.click(self.driver.find_element_by_id("explicit-refs-events-start-stop-add-value"))
        functions.fill_period(self.driver, wait, "explicit-refs-events", 2, start_value = "2019-06-05T04:00:00", start_operator = "!=", end_value = "2019-06-05T03:00:00", end_operator = ">=")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-ref-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

    def test_explicit_ref_alerts_name_alert_filter(self):

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
                        "explicit_references":[
                            {
                            "name":"ER1",
                            "group":"ER_GROUP1",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:36",
                                    "alert_cnf":{
                                        "name":"alert_name1",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group1"
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
                            "name":"source1.json",
                            "reception_time":"2018-06-06T13:33:29",
                            "generation_time":"2018-07-05T02:07:03",
                            "validity_start":"2018-06-05T02:07:03",
                            "validity_stop":"2019-06-05T08:07:36",
                            "priority":30
                        },
                        "explicit_references":[
                            {
                            "name":"ER2",
                            "group":"ER_GROUP2",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test2",
                                    "notification_time":"2019-06-05T08:07:36",
                                    "alert_cnf":{
                                        "name":"alert_name2",
                                        "severity":"major",
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

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")
        
        functions.display_specific_alert_filters(self.driver)

        # Fill the name input
        input_element = self.driver.find_element_by_id("explicit-ref-alerts-name-text")
        input_element.send_keys("alert_name1")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'explicit-ref-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'explicit-ref-alerts-submit-button')))
        
        functions.display_specific_alert_filters(self.driver)

        # Fill the name input
        input_element = self.driver.find_element_by_id("explicit-ref-alerts-name-text")
        input_element.send_keys("alert_name1")

        menu = Select(self.driver.find_element_by_id("explicit-ref-alerts-name-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'explicit-ref-alerts-submit-button')))
        
        functions.display_specific_alert_filters(self.driver)

        # Fill the name input
        input_element = self.driver.find_element_by_id("explicit-ref-alerts-names-in-text")
        functions.click(input_element)

        input_element.send_keys("alert_name1")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("explicit-ref-alerts-names-in-select"))
        options.select_by_visible_text("alert_name1")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'explicit-ref-alerts-submit-button')))
        
        functions.display_specific_alert_filters(self.driver)

        # Fill the name input
        input_element = self.driver.find_element_by_id("explicit-ref-alerts-names-in-text")
        functions.click(input_element)

        input_element.send_keys("alert_name2")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("explicit-ref-alerts-names-in-select"))
        options.select_by_visible_text("alert_name2")

        notInButton = self.driver.find_element_by_id("explicit-ref-alerts-names-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        # end if

        # Click on query button
        functions.click(submit_button)

        # Check table generate
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

    def test_explicit_ref_alerts_group_alert_filter(self):

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
                        "explicit_references":[
                            {
                            "name":"ER1",
                            "group":"ER_GROUP1",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:36",
                                    "alert_cnf":{
                                        "name":"alert_name1",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group1"
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
                            "name":"source1.json",
                            "reception_time":"2018-06-06T13:33:29",
                            "generation_time":"2018-07-05T02:07:03",
                            "validity_start":"2018-06-05T02:07:03",
                            "validity_stop":"2019-06-05T08:07:36",
                            "priority":30
                        },
                        "explicit_references":[
                            {
                            "name":"ER2",
                            "group":"ER_GROUP2",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test2",
                                    "notification_time":"2019-06-05T08:07:36",
                                    "alert_cnf":{
                                        "name":"alert_name2",
                                        "severity":"major",
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

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")
        
        functions.display_specific_alert_filters(self.driver)

        # Fill the group input
        input_element = self.driver.find_element_by_id("explicit-ref-alerts-group-text")
        input_element.send_keys("alert_group1")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'explicit-ref-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'explicit-ref-alerts-submit-button')))
        
        functions.display_specific_alert_filters(self.driver)

        # Fill the group input
        input_element = self.driver.find_element_by_id("explicit-ref-alerts-group-text")
        input_element.send_keys("alert_group1")

        menu = Select(self.driver.find_element_by_id("explicit-ref-alerts-group-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'explicit-ref-alerts-submit-button')))
        
        functions.display_specific_alert_filters(self.driver)

        # Fill the group input
        input_element = self.driver.find_element_by_id("explicit-ref-alerts-groups-in-text")
        functions.click(input_element)

        input_element.send_keys("alert_group1")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("explicit-ref-alerts-groups-in-select"))
        options.select_by_visible_text("alert_group1")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'explicit-ref-alerts-submit-button')))
        
        functions.display_specific_alert_filters(self.driver)

        # Fill the group input
        input_element = self.driver.find_element_by_id("explicit-ref-alerts-groups-in-text")
        functions.click(input_element)

        input_element.send_keys("alert_group2")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("explicit-ref-alerts-groups-in-select"))
        options.select_by_visible_text("alert_group2")

        notInButton = self.driver.find_element_by_id("explicit-ref-alerts-groups-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        # end if

        # Click on query button
        functions.click(submit_button)

        # Check table generate
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

    def test_explicit_ref_alerts_generator_alert_filter(self):

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
                        "explicit_references":[
                            {
                            "name":"ER1",
                            "group":"ER_GROUP1",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:36",
                                    "alert_cnf":{
                                        "name":"alert_name1",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group1"
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
                            "name":"source1.json",
                            "reception_time":"2018-06-06T13:33:29",
                            "generation_time":"2018-07-05T02:07:03",
                            "validity_start":"2018-06-05T02:07:03",
                            "validity_stop":"2019-06-05T08:07:36",
                            "priority":30
                        },
                        "explicit_references":[
                            {
                            "name":"ER2",
                            "group":"ER_GROUP2",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test2",
                                    "notification_time":"2019-06-05T08:07:36",
                                    "alert_cnf":{
                                        "name":"alert_name2",
                                        "severity":"major",
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

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")
        
        functions.display_specific_alert_filters(self.driver)

        # Fill the generator input
        input_element = self.driver.find_element_by_id("explicit-ref-alerts-generator-text")
        input_element.send_keys("test")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'explicit-ref-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'explicit-ref-alerts-submit-button')))
        
        functions.display_specific_alert_filters(self.driver)

        # Fill the generator input
        input_element = self.driver.find_element_by_id("explicit-ref-alerts-generator-text")
        input_element.send_keys("test")

        menu = Select(self.driver.find_element_by_id("explicit-ref-alerts-generator-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'explicit-ref-alerts-submit-button')))
        
        functions.display_specific_alert_filters(self.driver)

        # Fill the generator input
        input_element = self.driver.find_element_by_id("explicit-ref-alerts-generators-in-text")
        functions.click(input_element)

        input_element.send_keys("test")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("explicit-ref-alerts-generators-in-select"))
        options.select_by_visible_text("test")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'explicit-ref-alerts-submit-button')))
        
        functions.display_specific_alert_filters(self.driver)

        # Fill the generator input
        input_element = self.driver.find_element_by_id("explicit-ref-alerts-generators-in-text")
        functions.click(input_element)

        input_element.send_keys("test2")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("explicit-ref-alerts-generators-in-select"))
        options.select_by_visible_text("test2")

        notInButton = self.driver.find_element_by_id("explicit-ref-alerts-generators-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        # end if

        # Click on query button
        functions.click(submit_button)

        # Check table generate
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

    def test_explicit_ref_alerts_query_ingestion_time_alert_filter(self):

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
                        "annotations":[
                            {
                            "explicit_reference":"ER1",
                            "annotation_cnf":{
                                "name":"NAME_2",
                                "system":"SYSTEM_2",
                                "insertion_type":"SIMPLE_UPDATE"
                            }
                            }
                        ],
                        "explicit_references":[
                            {
                            "name":"ER1",
                            "group":"ER_GROUP1",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:36",
                                    "alert_cnf":{
                                        "name":"alert_name1",
                                        "severity":"critical",
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

        ingestion_time = self.session.query(ExplicitRefAlert).all()[0].ingestion_time.isoformat()

        wait = WebDriverWait(self.driver,5)

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")
        
        functions.display_specific_alert_filters(self.driver)

        functions.fill_any_time(self.driver, wait, "explicit-ref-alerts", "ingestion", ingestion_time, "==", 1)
        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'explicit-ref-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")
        
        functions.display_specific_alert_filters(self.driver)

        functions.fill_any_time(self.driver, wait, "explicit-ref-alerts", "ingestion", ingestion_time, ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'explicit-ref-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")
        
        functions.display_specific_alert_filters(self.driver)

        functions.fill_any_time(self.driver, wait, "explicit-ref-alerts", "ingestion", ingestion_time, ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'explicit-ref-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")
        
        functions.display_specific_alert_filters(self.driver)

        functions.fill_any_time(self.driver, wait, "explicit-ref-alerts", "ingestion", ingestion_time, "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'explicit-ref-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")
        
        functions.display_specific_alert_filters(self.driver)

        functions.fill_any_time(self.driver, wait, "explicit-ref-alerts", "ingestion", ingestion_time, "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'explicit-ref-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")
        
        functions.display_specific_alert_filters(self.driver)

        functions.fill_any_time(self.driver, wait, "explicit-ref-alerts", "ingestion", ingestion_time, "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'explicit-ref-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

    """ def test_explicit_ref_alerts_query_solved_time_alert_filter(self):

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
                        "annotations":[
                            {
                            "explicit_reference":"ER1",
                            "annotation_cnf":{
                                "name":"NAME_2",
                                "system":"SYSTEM_2",
                                "insertion_type":"SIMPLE_UPDATE"
                            }
                            }
                        ],
                        "explicit_references":[
                            {
                            "name":"ER1",
                            "group":"ER_GROUP1",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:36",
                                    "alert_cnf":{
                                        "name":"alert_name1",
                                        "severity":"critical",
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

        solved_time = "2018-06-05T10:07:37"

        wait = WebDriverWait(self.driver,5)

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")
        
        functions.display_specific_alert_filters(self.driver)

        functions.fill_any_time(self.driver, wait, "explicit-ref-alerts", "solved", solved_time, "==", 1)
        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'explicit-ref-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")
        
        functions.display_specific_alert_filters(self.driver)

        functions.fill_any_time(self.driver, wait, "explicit-ref-alerts", "solved", solved_time, ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'explicit-ref-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")
        
        functions.display_specific_alert_filters(self.driver)

        functions.fill_any_time(self.driver, wait, "explicit-ref-alerts", "solved", solved_time, ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'explicit-ref-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")
        
        functions.display_specific_alert_filters(self.driver)

        functions.fill_any_time(self.driver, wait, "explicit-ref-alerts", "solved", solved_time, "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'explicit-ref-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")
        
        functions.display_specific_alert_filters(self.driver)

        functions.fill_any_time(self.driver, wait, "explicit-ref-alerts", "solved", solved_time, "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'explicit-ref-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")
        
        functions.display_specific_alert_filters(self.driver)

        functions.fill_any_time(self.driver, wait, "explicit-ref-alerts", "solved", solved_time, "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'explicit-ref-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data """

    def test_explicit_ref_alerts_query_notification_time_alert_filter(self):

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
                        "annotations":[
                            {
                            "explicit_reference":"ER1",
                            "annotation_cnf":{
                                "name":"NAME_2",
                                "system":"SYSTEM_2",
                                "insertion_type":"SIMPLE_UPDATE"
                            }
                            }
                        ],
                        "explicit_references":[
                            {
                            "name":"ER1",
                            "group":"ER_GROUP1",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:37",
                                    "alert_cnf":{
                                        "name":"alert_name1",
                                        "severity":"critical",
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

        notification_time = "2018-06-05T08:07:37"

        wait = WebDriverWait(self.driver,5)

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")
        
        functions.display_specific_alert_filters(self.driver)

        functions.fill_any_time(self.driver, wait, "explicit-ref-alerts", "notification", notification_time, "==", 1)
        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'explicit-ref-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")
        
        functions.display_specific_alert_filters(self.driver)

        functions.fill_any_time(self.driver, wait, "explicit-ref-alerts", "notification", notification_time, ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'explicit-ref-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")
        
        functions.display_specific_alert_filters(self.driver)

        functions.fill_any_time(self.driver, wait, "explicit-ref-alerts", "notification", notification_time, ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'explicit-ref-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")
        
        functions.display_specific_alert_filters(self.driver)

        functions.fill_any_time(self.driver, wait, "explicit-ref-alerts", "notification", notification_time, "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'explicit-ref-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")
        
        functions.display_specific_alert_filters(self.driver)

        functions.fill_any_time(self.driver, wait, "explicit-ref-alerts", "notification", notification_time, "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'explicit-ref-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")
        
        functions.display_specific_alert_filters(self.driver)

        functions.fill_any_time(self.driver, wait, "explicit-ref-alerts", "notification", notification_time, "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'explicit-ref-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

    def test_explicit_ref_alerts_severities_alert_filter(self):

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
                        "explicit_references":[
                            {
                            "name":"ER1",
                            "group":"ER_GROUP1",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:36",
                                    "alert_cnf":{
                                        "name":"alert_name1",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group1"
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
                            "name":"source1.json",
                            "reception_time":"2018-06-06T13:33:29",
                            "generation_time":"2018-07-05T02:07:03",
                            "validity_start":"2018-06-05T02:07:03",
                            "validity_stop":"2019-06-05T08:07:36",
                            "priority":30
                        },
                        "explicit_references":[
                            {
                            "name":"ER2",
                            "group":"ER_GROUP2",
                            "alerts":[
                                {
                                    "message":"Alert message",
                                    "generator":"test2",
                                    "notification_time":"2019-06-05T08:07:36",
                                    "alert_cnf":{
                                        "name":"alert_name2",
                                        "severity":"major",
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

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'explicit-ref-alerts-submit-button')))
        
        functions.display_specific_alert_filters(self.driver)

        # Fill the select option
        functions.select_option_dropdown(self.driver, "explicit-ref-alerts-severities-in-select", "critical")
        
        # Click on query button
        functions.click(submit_button)

        # Check table generated
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'explicit-ref-alerts-submit-button')))
        
        functions.display_specific_alert_filters(self.driver)

        # Fill the select option
        functions.select_option_dropdown(self.driver, "explicit-ref-alerts-severities-in-select", "critical")

        notInButton = self.driver.find_element_by_id("explicit-ref-alerts-severities-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        # end if

        # Click on query button
        functions.click(submit_button)

        # Check table generate
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

        ## Multiple selection ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'explicit-ref-alerts-submit-button')))
        
        functions.display_specific_alert_filters(self.driver)

        # Fill the select option
        functions.select_option_dropdown(self.driver, "explicit-ref-alerts-severities-in-select", "critical")
        functions.select_option_dropdown(self.driver, "explicit-ref-alerts-severities-in-select", "major")

        # Click on query button
        functions.click(submit_button)

        # Check table generate
        explicit_ref_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(explicit_ref_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2
