"""
Automated tests for the annotation alerts tab

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

class TestAnnotationAlertsTab(unittest.TestCase):

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

    def test_annotation_alerts_no_data(self):

        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

    def test_annotation_alerts_query_no_filter_with_timeline(self):

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
                                "name":"NAME",
                                "system":"SYSTEM",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "values":[
                                {
                                    "name":"VALUES",
                                    "type":"object",
                                    "values":[
                                        {
                                        "type":"text",
                                        "name":"TEXT",
                                        "value":"TEXT"
                                        },
                                        {
                                        "type":"boolean",
                                        "name":"BOOLEAN",
                                        "value":"true"
                                        }
                                    ]
                                }
                            ],
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
                            },
                            {
                            "explicit_reference":"ER1",
                            "annotation_cnf":{
                                "name":"NAME",
                                "system":"SYSTEM",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
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

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        timeline = self.driver.find_element_by_id('timeline-general-view-alerts')
        condition = timeline.is_displayed()

        assert condition

        # Check generated content for widgets
        kwargs ={}
        kwargs["order_by"] = {"field": "notification_time", "descending": False}
        annotations_alerts = self.query_eboa.get_annotation_alerts(**kwargs)

        assert len(annotations_alerts) == 2

        alerts = [
            {
                "alert_uuid": "<a href='/eboa_nav/query-alert/" + str(annotations_alerts[0].annotation_alert_uuid) + "'>" + str(annotations_alerts[0].annotation_alert_uuid) + "</a>",
                "description": "Alert description",
                "entity": "Annotation",
                "entity_uuid": "<a href='/eboa_nav/query-annotation/" + str(annotations_alerts[0].annotation_uuid) + "'>" + str(annotations_alerts[0].annotation_uuid) + "</a>",
                "generator": "test",
                "group": "ANNOTATIONS;alert_group1",
                "group_alert": "alert_group1",
                "id": str(annotations_alerts[0].annotation_alert_uuid),
                "ingestion_time": annotations_alerts[0].ingestion_time.isoformat(),
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
                "alert_uuid": "<a href='/eboa_nav/query-alert/" + str(annotations_alerts[1].annotation_alert_uuid) + "'>" + str(annotations_alerts[1].annotation_alert_uuid) + "</a>",
                "description": "Alert description",
                "entity": "Annotation",
                "entity_uuid": "<a href='/eboa_nav/query-annotation/" + str(annotations_alerts[1].annotation_uuid) + "'>" + str(annotations_alerts[1].annotation_uuid) + "</a>",
                "generator": "test",
                "group": "ANNOTATIONS;alert_group2",
                "group_alert": "alert_group2",
                "id": str(annotations_alerts[1].annotation_alert_uuid),
                "ingestion_time": annotations_alerts[1].ingestion_time.isoformat(),
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
            }
        ]

        returned_alerts = self.driver.execute_script('return alerts;')
        functions.assert_equal_list_dictionaries(returned_alerts, alerts)

        # Check annotation alerts table
        annotation_alerts_table = self.driver.find_element_by_id("alerts-table")

        # Row 1
        justification = annotation_alerts_table.find_element_by_xpath("tbody/tr[1]/td[1]")

        assert justification.text == "None"

        severity = annotation_alerts_table.find_element_by_xpath("tbody/tr[1]/td[2]")

        assert severity.text == "critical"

        group = annotation_alerts_table.find_element_by_xpath("tbody/tr[1]/td[3]")

        assert group.text == "alert_group1"

        name = annotation_alerts_table.find_element_by_xpath("tbody/tr[1]/td[4]")

        assert name.text == "alert_name1"

        message = annotation_alerts_table.find_element_by_xpath("tbody/tr[1]/td[5]")

        assert message.text == "Alert message"

        notification_time = annotation_alerts_table.find_element_by_xpath("tbody/tr[1]/td[6]")

        assert notification_time.text == "2018-06-05T08:07:36"

        solved = annotation_alerts_table.find_element_by_xpath("tbody/tr[1]/td[7]")

        assert solved.text == "None"

        solved_time = annotation_alerts_table.find_element_by_xpath("tbody/tr[1]/td[8]")

        assert solved_time.text == "None"

        description = annotation_alerts_table.find_element_by_xpath("tbody/tr[1]/td[9]")

        assert description.text == "Alert description"

        validated = annotation_alerts_table.find_element_by_xpath("tbody/tr[1]/td[10]")

        assert validated.text == "None"

        generator = annotation_alerts_table.find_element_by_xpath("tbody/tr[1]/td[11]")

        assert generator.text == "test"

        notified = annotation_alerts_table.find_element_by_xpath("tbody/tr[1]/td[12]")

        assert notified.text == "None"

        ingestion_time = annotation_alerts_table.find_element_by_xpath("tbody/tr[1]/td[13]")

        assert ingestion_time.text == annotations_alerts[0].ingestion_time.isoformat()

        alert_uuid = annotation_alerts_table.find_element_by_xpath("tbody/tr[1]/td[14]")

        assert alert_uuid.text == str(annotations_alerts[0].annotation_alert_uuid)

        annotation_uuid = annotation_alerts_table.find_element_by_xpath("tbody/tr[1]/td[15]")

        assert annotation_uuid.text == str(annotations_alerts[0].annotation_uuid)

        # Row 2
        justification = annotation_alerts_table.find_element_by_xpath("tbody/tr[2]/td[1]")

        assert justification.text == "None"

        severity = annotation_alerts_table.find_element_by_xpath("tbody/tr[2]/td[2]")

        assert severity.text == "critical"

        group = annotation_alerts_table.find_element_by_xpath("tbody/tr[2]/td[3]")

        assert group.text == "alert_group2"

        name = annotation_alerts_table.find_element_by_xpath("tbody/tr[2]/td[4]")

        assert name.text == "alert_name3"

        message = annotation_alerts_table.find_element_by_xpath("tbody/tr[2]/td[5]")

        assert message.text == "Alert message"

        notification_time = annotation_alerts_table.find_element_by_xpath("tbody/tr[2]/td[6]")

        assert notification_time.text == "2018-06-05T08:07:37"

        solved = annotation_alerts_table.find_element_by_xpath("tbody/tr[2]/td[7]")

        assert solved.text == "None"

        solved_time = annotation_alerts_table.find_element_by_xpath("tbody/tr[2]/td[8]")

        assert solved_time.text == "None"

        description = annotation_alerts_table.find_element_by_xpath("tbody/tr[2]/td[9]")

        assert description.text == "Alert description"

        validated = annotation_alerts_table.find_element_by_xpath("tbody/tr[2]/td[10]")

        assert validated.text == "None"

        generator = annotation_alerts_table.find_element_by_xpath("tbody/tr[2]/td[11]")

        assert generator.text == "test"

        notified = annotation_alerts_table.find_element_by_xpath("tbody/tr[2]/td[12]")

        assert notified.text == "None"

        ingestion_time = annotation_alerts_table.find_element_by_xpath("tbody/tr[2]/td[13]")

        assert ingestion_time.text == annotations_alerts[1].ingestion_time.isoformat()

        alert_uuid = annotation_alerts_table.find_element_by_xpath("tbody/tr[2]/td[14]")

        assert alert_uuid.text == str(annotations_alerts[1].annotation_alert_uuid)

        annotation_uuid = annotation_alerts_table.find_element_by_xpath("tbody/tr[2]/td[15]")

        assert annotation_uuid.text == str(annotations_alerts[1].annotation_uuid)

    def test_annotation_alerts_query_source(self):

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
                                "name":"NAME",
                                "system":"SYSTEM",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "values":[
                                {
                                    "name":"VALUES",
                                    "type":"object",
                                    "values":[
                                        {
                                        "type":"text",
                                        "name":"TEXT",
                                        "value":"TEXT"
                                        },
                                        {
                                        "type":"boolean",
                                        "name":"BOOLEAN",
                                        "value":"true"
                                        }
                                    ]
                                }
                            ],
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
                            "explicit_reference":"ER1",
                            "annotation_cnf":{
                                "name":"NAME",
                                "system":"SYSTEM",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
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

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        # Fill the source_like input
        input_element = self.driver.find_element_by_id("annotations-source-text")
        input_element.send_keys("source.json")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click_no_graphs_annotations(self.driver)

        # Fill the source_like input
        input_element = self.driver.find_element_by_id("annotations-source-text")
        input_element.send_keys("source.json")

        menu = Select(self.driver.find_element_by_id("annotations-source-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click_no_graphs_annotations(self.driver)

        # Fill the source_in input
        input_element = self.driver.find_element_by_id("annotations-sources-in-text")
        functions.click(input_element)

        input_element.send_keys("source_1.json")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("annotations-sources-in-select"))
        options.select_by_visible_text("source_1.json")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click_no_graphs_annotations(self.driver)

        # Fill the source_in input
        input_element = self.driver.find_element_by_id("annotations-sources-in-text")
        functions.click(input_element)

        input_element.send_keys("source.json")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("annotations-sources-in-select"))
        options.select_by_visible_text("source.json")

        notInButton = self.driver.find_element_by_id("annotations-sources-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        #end if

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

    def test_annotation_alerts_query_explicit_refs(self):

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
                                "name":"NAME",
                                "system":"SYSTEM",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "values":[
                                {
                                    "name":"VALUES",
                                    "type":"object",
                                    "values":[
                                        {
                                        "type":"text",
                                        "name":"TEXT",
                                        "value":"TEXT"
                                        },
                                        {
                                        "type":"boolean",
                                        "name":"BOOLEAN",
                                        "value":"true"
                                        }
                                    ]
                                }
                            ],
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
                            },
                            {
                            "explicit_reference":"ER2",
                            "annotation_cnf":{
                                "name":"NAME",
                                "system":"SYSTEM",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
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

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        # Fill the explicit_ref_like input
        input_element = self.driver.find_element_by_id("annotations-er-text")
        input_element.send_keys("ER1")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click_no_graphs_annotations(self.driver)

        # Fill the explicit_ref_like input
        input_element = self.driver.find_element_by_id("annotations-er-text")
        input_element.send_keys("ER1")

        menu = Select(self.driver.find_element_by_id("annotations-er-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click_no_graphs_annotations(self.driver)

        # Fill the explicit_ref_in input
        input_element = self.driver.find_element_by_id("annotations-ers-in-text")
        functions.click(input_element)

        input_element.send_keys("ER2")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("annotations-ers-in-select"))
        options.select_by_visible_text("ER2")
        
        # Click on query button
        functions.click(submit_button)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click_no_graphs_annotations(self.driver)

        # Fill the explicit_ref_in input
        input_element = self.driver.find_element_by_id("annotations-ers-in-text")
        functions.click(input_element)

        input_element.send_keys("ER1")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("annotations-ers-in-select"))
        options.select_by_visible_text("ER1")

        notInButton = self.driver.find_element_by_id("annotations-ers-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        #end if

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

    def test_annotation_alerts_query_annotation_names(self):

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
                                        "type":"text",
                                        "name":"TEXT",
                                        "value":"TEXT"
                                        },
                                        {
                                        "type":"boolean",
                                        "name":"BOOLEAN",
                                        "value":"true"
                                        }
                                    ]
                                }
                            ],
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
                            },
                            {
                            "explicit_reference":"ER2",
                            "annotation_cnf":{
                                "name":"NAME_2",
                                "system":"SYSTEM_2",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
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

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        # Fill the annotation_name_like input
        input_element = self.driver.find_element_by_id("annotations-annotation-name-text")
        input_element.send_keys("NAME_2")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click_no_graphs_annotations(self.driver)

        # Fill the annotation_name_like input
        input_element = self.driver.find_element_by_id("annotations-annotation-name-text")
        input_element.send_keys("NAME_2")

        menu = Select(self.driver.find_element_by_id("annotations-annotation-name-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click_no_graphs_annotations(self.driver)

        # Fill the annotation_name_in input
        input_element = self.driver.find_element_by_id("annotations-annotation-names-in-text")
        functions.click(input_element)

        input_element.send_keys("NAME_1")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("annotations-annotation-names-in-select"))
        options.select_by_visible_text("NAME_1")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click_no_graphs_annotations(self.driver)

        # Fill the annotation_name_in input
        input_element = self.driver.find_element_by_id("annotations-annotation-names-in-text")
        functions.click(input_element)

        input_element.send_keys("NAME_2")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("annotations-annotation-names-in-select"))
        options.select_by_visible_text("NAME_2")

        notInButton = self.driver.find_element_by_id("annotations-annotation-names-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        #end if

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

    def test_annotation_alerts_query_annotation_system(self):

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
                                        "type":"text",
                                        "name":"TEXT",
                                        "value":"TEXT"
                                        },
                                        {
                                        "type":"boolean",
                                        "name":"BOOLEAN",
                                        "value":"true"
                                        }
                                    ]
                                }
                            ],
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
                            },
                            {
                            "explicit_reference":"ER2",
                            "annotation_cnf":{
                                "name":"NAME_2",
                                "system":"SYSTEM_2",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
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

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        # Fill the annotation_system_like input
        input_element = self.driver.find_element_by_id("annotations-annotation-system-text")
        input_element.send_keys("SYSTEM_2")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click_no_graphs_annotations(self.driver)

        # Fill the annotation_system_like input
        input_element = self.driver.find_element_by_id("annotations-annotation-system-text")
        input_element.send_keys("SYSTEM_2")

        menu = Select(self.driver.find_element_by_id("annotations-annotation-system-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click_no_graphs_annotations(self.driver)

        # Fill the annotation_system_in input
        input_element = self.driver.find_element_by_id("annotations-annotation-systems-in-text")
        functions.click(input_element)

        input_element.send_keys("SYSTEM_1")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("annotations-annotation-systems-in-select"))
        options.select_by_visible_text("SYSTEM_1")

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click_no_graphs_annotations(self.driver)

        # # Fill the annotation_system_in input
        input_element = self.driver.find_element_by_id("annotations-annotation-systems-in-text")
        functions.click(input_element)

        input_element.send_keys("SYSTEM_2")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("annotations-annotation-systems-in-select"))
        options.select_by_visible_text("SYSTEM_2")

        notInButton = self.driver.find_element_by_id("annotations-annotation-systems-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        #end if

       # Click on query button
        functions.click(submit_button)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

    def test_annotation_alerts_query_value_text(self):

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
                                    "notification_time":"2018-06-05T08:07:36",
                                    "alert_cnf":{
                                        "name":"alert_name1",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group1"
                                    }
                                }
                            ]
                            },
                            {
                            "explicit_reference":"ER2",
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
                                        "name": "textname_2",
                                        "type": "text",
                                        "value": "textvalue_2"
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
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "text", "textname_1", "textvalue_1", "==", "==", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "text", "textname_1", "textvalue_2", "!=", "==", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert  number_of_elements == 1

    def test_annotation_alerts_query_value_timestamp(self):

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
                                        "name": "timestamp_name_1",
                                        "type": "timestamp",
                                        "value": "2019-04-26T14:14:14"
                                        }
                                    ]
                                }
                            ],
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
                            },
                            {
                            "explicit_reference":"ER2",
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
                                        "name": "textname_2",
                                        "type": "text",
                                        "value": "textvalue_2"
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
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", "==", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", "==", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", "==", ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", "==", ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", "==", "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", "==", "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", "==", "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

    def test_annotation_alerts_query_value_double(self):

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
                                        "name": "double_name_1",
                                        "type": "double",
                                        "value": "3.5"
                                        }
                                    ]
                                }
                            ],
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
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "double", "double_name_1", "3.5", "==", "==", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "double", "double_name_1", "3.5", "!=", "==", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "double", "double_name_1", "3.5", "==", ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "double", "double_name_1", "3.25", "==", ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "double", "double_name_1", "3.75", "==", ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "double", "double_name_1", "3.5", "==", ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "double", "double_name_1", "3.25", "==", ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "double", "double_name_1", "3.75", "==", ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "double", "double_name_1", "3.5", "==", "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "double", "double_name_1", "3.25", "==", "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "double", "double_name_1", "3.75", "==", "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "double", "double_name_1", "3.5", "==", "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "double", "double_name_1", "3.25", "==", "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "double", "double_name_1", "3.75", "==", "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "double", "double_name_1", "3.5", "==", "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "double", "double_name_1", "3.25", "==", "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "double", "double_name_1", "3.75", "==", "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

    def test_annotation_alerts_query_ingestion_time(self):

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
                                        "name": "double_name_1",
                                        "type": "double",
                                        "value": "3.5"
                                        }
                                    ]
                                }
                            ],
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

        ingestion_time = self.session.query(Annotation).all()[0].ingestion_time.isoformat()

        wait = WebDriverWait(self.driver,5)

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_ingestion_time(self.driver, wait, "annotations", ingestion_time, "==", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_ingestion_time(self.driver, wait,"annotations", ingestion_time, ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_ingestion_time(self.driver, wait,"annotations", ingestion_time, ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_ingestion_time(self.driver, wait,"annotations", ingestion_time, "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_ingestion_time(self.driver, wait,"annotations", ingestion_time, "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_ingestion_time(self.driver, wait,"annotations", ingestion_time, "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

    def test_annotation_alerts_query_two_values(self):

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
                            },
                            {
                            "explicit_reference":"ER2",
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
                                        "name": "textname_2",
                                        "type": "text",
                                        "value": "textvalue_2"
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

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait, "annotations", "text", "textname_1", "textvalue_1", "==", "==", 1)
        functions.click(self.driver.find_element_by_id("annotations-add-value"))
        functions.fill_value(self.driver, wait, "annotations", "double", "double_name_1", "1.4", "==", "==", 2)

        # Click on query butto
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False
