"""
Automated tests for the sources tab

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
import vboa.tests.functions as functions_vboa

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
import rboa.engine.engine as rboa_engine
from rboa.engine.engine import Engine as EngineReport
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

class TestGeneralViewAlerts(unittest.TestCase):

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('window-size=1920,1080')
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)

    def setUp(self):
        # Create the engine to manage the data
        self.engine_eboa = Engine()
        self.engine_rboa = EngineReport()
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

    def test_sources_alerts_query_no_filter(self):

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
                            },
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

        self.driver.get("http://localhost:5000/general-view-alerts/")

        functions.query(self.driver, wait, start = "2018-06-05T08:07:36", stop = "2018-06-05T08:07:36")

        # Check number of widgets in summary
        summary_section = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts")))
        assert summary_section and len(summary_section.find_elements_by_xpath("div")) == 5

        # Check summary number sources alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-sources")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number annotations alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-annotations")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Check summary number events alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-events")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Check summary number reports alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-reports")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Check summary number ers alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-ers")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Check whether the timeline is displayed
        timeline_section = self.driver.find_element_by_id("timeline-general-view-alerts")

        condition = timeline_section.is_displayed()
        assert condition is True

        # Check generated content for widgets
        
        kwargs ={}
        kwargs["order_by"] = {"field": "notification_time", "descending": False}
        sources_alerts = self.query_eboa.get_source_alerts(kwargs)

        assert len(sources_alerts) == 2

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
        functions_vboa.assert_equal_list_dictionaries(returned_alerts, alerts)

        # Check source alerts table
        source_alerts_table = self.driver.find_element_by_id("associated-general-view-alerts-sources-details-table")

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

    def test_events_alerts_query_no_filter(self):

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
                                "name":"GAUGE_NAME",
                                "system":"GAUGE_SYSTEM",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2018-06-05T02:07:03",
                            "stop":"2018-06-05T08:07:36",
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
                            },
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

        self.driver.get("http://localhost:5000/general-view-alerts/")

        functions.query(self.driver, wait, start = "2018-06-05T08:07:36", stop = "2018-06-05T08:07:38")

        # Check number of widgets in summary
        summary_section = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts")))
        assert summary_section and len(summary_section.find_elements_by_xpath("div")) == 5

        # Check summary number sources alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-sources")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Check summary number annotations alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-annotations")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Check summary number events alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-events")))

        assert summary_number_alerts and summary_number_alerts.text == "3"

        # Check summary number reports alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-reports")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Check summary number ers alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-ers")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Check whether the timeline is displayed
        timeline_section = self.driver.find_element_by_id("timeline-general-view-alerts")

        condition = timeline_section.is_displayed()
        assert condition is True

        # Check generated content for widgets
        kwargs ={}
        kwargs["order_by"] = {"field": "notification_time", "descending": False}
        events_alerts = self.query_eboa.get_event_alerts(kwargs)

        assert len(events_alerts) == 4

        alerts = [
            {
                "alert_uuid": "<a href='/eboa_nav/query-alert/" + str(events_alerts[0].event_alert_uuid) + "'>" + str(events_alerts[0].event_alert_uuid) + "</a>",
                "description": "Alert description",
                "entity": "Event",
                "entity_uuid": "<a href='/eboa_nav/query-event-links/" + str(events_alerts[0].event_uuid) + "'>" + str(events_alerts[0].event_uuid) + "</a>",
                "generator": "test",
                "group": "EVENTS;alert_group1",
                "group_alert": "alert_group1",
                "id": str(events_alerts[0].event_alert_uuid),
                "ingestion_time": events_alerts[0].ingestion_time.isoformat(),
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
                "alert_uuid": "<a href='/eboa_nav/query-alert/" + str(events_alerts[1].event_alert_uuid) + "'>" + str(events_alerts[1].event_alert_uuid) + "</a>",
                "description": "Alert description",
                "entity": "Event",
                "entity_uuid": "<a href='/eboa_nav/query-event-links/" + str(events_alerts[1].event_uuid) + "'>" + str(events_alerts[1].event_uuid) + "</a>",
                "generator": "test",
                "group": "EVENTS;alert_group2",
                "group_alert": "alert_group2",
                "id": str(events_alerts[1].event_alert_uuid),
                "ingestion_time": events_alerts[1].ingestion_time.isoformat(),
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
                "alert_uuid": "<a href='/eboa_nav/query-alert/" + str(events_alerts[2].event_alert_uuid) + "'>" + str(events_alerts[2].event_alert_uuid) + "</a>",
                "description": "Alert description",
                "entity": "Event",
                "entity_uuid": "<a href='/eboa_nav/query-event-links/" + str(events_alerts[2].event_uuid) + "'>" + str(events_alerts[2].event_uuid) + "</a>",
                "generator": "test2",
                "group": "EVENTS;alert_group3",
                "group_alert": "alert_group3",
                "id": str(events_alerts[2].event_alert_uuid),
                "ingestion_time": events_alerts[2].ingestion_time.isoformat(),
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
        functions_vboa.assert_equal_list_dictionaries(returned_alerts, alerts)

        # Check event alerts table
        event_alerts_table = self.driver.find_element_by_id("associated-general-view-alerts-events-details-table")

        # Row 1
        justification = event_alerts_table.find_element_by_xpath("tbody/tr[1]/td[1]")

        assert justification.text == "None"

        severity = event_alerts_table.find_element_by_xpath("tbody/tr[1]/td[2]")

        assert severity.text == "critical"

        group = event_alerts_table.find_element_by_xpath("tbody/tr[1]/td[3]")

        assert group.text == "alert_group1"

        name = event_alerts_table.find_element_by_xpath("tbody/tr[1]/td[4]")

        assert name.text == "alert_name1"

        message = event_alerts_table.find_element_by_xpath("tbody/tr[1]/td[5]")

        assert message.text == "Alert message"

        notification_time = event_alerts_table.find_element_by_xpath("tbody/tr[1]/td[6]")

        assert notification_time.text == "2018-06-05T08:07:36"

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

        assert severity.text == "critical"

        group = event_alerts_table.find_element_by_xpath("tbody/tr[2]/td[3]")

        assert group.text == "alert_group2"

        name = event_alerts_table.find_element_by_xpath("tbody/tr[2]/td[4]")

        assert name.text == "alert_name3"

        message = event_alerts_table.find_element_by_xpath("tbody/tr[2]/td[5]")

        assert message.text == "Alert message"

        notification_time = event_alerts_table.find_element_by_xpath("tbody/tr[2]/td[6]")

        assert notification_time.text == "2018-06-05T08:07:37"

        solved = event_alerts_table.find_element_by_xpath("tbody/tr[2]/td[7]")

        assert solved.text == "None"

        solved_time = event_alerts_table.find_element_by_xpath("tbody/tr[2]/td[8]")

        assert solved_time.text == "None"

        description = event_alerts_table.find_element_by_xpath("tbody/tr[2]/td[9]")

        assert description.text == "Alert description"

        validated = event_alerts_table.find_element_by_xpath("tbody/tr[2]/td[10]")

        assert validated.text == "None"

        generator = event_alerts_table.find_element_by_xpath("tbody/tr[2]/td[11]")

        assert generator.text == "test"

        notified = event_alerts_table.find_element_by_xpath("tbody/tr[2]/td[12]")

        assert notified.text == "None"

        ingestion_time = event_alerts_table.find_element_by_xpath("tbody/tr[2]/td[13]")

        assert ingestion_time.text == events_alerts[1].ingestion_time.isoformat()

        alert_uuid = event_alerts_table.find_element_by_xpath("tbody/tr[2]/td[14]")

        assert alert_uuid.text == str(events_alerts[1].event_alert_uuid)

        event_uuid = event_alerts_table.find_element_by_xpath("tbody/tr[2]/td[15]")

        assert event_uuid.text == str(events_alerts[1].event_uuid)

        # Row 3
        justification = event_alerts_table.find_element_by_xpath("tbody/tr[3]/td[1]")

        assert justification.text == "None"

        severity = event_alerts_table.find_element_by_xpath("tbody/tr[3]/td[2]")

        assert severity.text == "major"

        group = event_alerts_table.find_element_by_xpath("tbody/tr[3]/td[3]")

        assert group.text == "alert_group3"

        name = event_alerts_table.find_element_by_xpath("tbody/tr[3]/td[4]")

        assert name.text == "alert_name4"

        message = event_alerts_table.find_element_by_xpath("tbody/tr[3]/td[5]")

        assert message.text == "Alert message"

        notification_time = event_alerts_table.find_element_by_xpath("tbody/tr[3]/td[6]")

        assert notification_time.text == "2018-06-05T08:07:38"

        solved = event_alerts_table.find_element_by_xpath("tbody/tr[3]/td[7]")

        assert solved.text == "None"

        solved_time = event_alerts_table.find_element_by_xpath("tbody/tr[3]/td[8]")

        assert solved_time.text == "None"

        description = event_alerts_table.find_element_by_xpath("tbody/tr[3]/td[9]")

        assert description.text == "Alert description"

        validated = event_alerts_table.find_element_by_xpath("tbody/tr[3]/td[10]")

        assert validated.text == "None"

        generator = event_alerts_table.find_element_by_xpath("tbody/tr[3]/td[11]")

        assert generator.text == "test2"

        notified = event_alerts_table.find_element_by_xpath("tbody/tr[3]/td[12]")

        assert notified.text == "None"

        ingestion_time = event_alerts_table.find_element_by_xpath("tbody/tr[3]/td[13]")

        assert ingestion_time.text == events_alerts[2].ingestion_time.isoformat()

        alert_uuid = event_alerts_table.find_element_by_xpath("tbody/tr[3]/td[14]")

        assert alert_uuid.text == str(events_alerts[2].event_alert_uuid)

        event_uuid = event_alerts_table.find_element_by_xpath("tbody/tr[3]/td[15]")

        assert event_uuid.text == str(events_alerts[2].event_uuid)

    def test_annotations_alerts_query_no_filter(self):

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
                                },
                                {
                                    "message":"Alert message",
                                    "generator":"test2",
                                    "notification_time":"2019-06-05T08:07:36",
                                    "alert_cnf":{
                                        "name":"alert_name4",
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

        self.driver.get("http://localhost:5000/general-view-alerts/")

        functions.query(self.driver, wait, start = "2018-06-05T08:07:36", stop = "2018-06-05T08:07:37")

        # Check number of widgets in summary
        summary_section = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts")))
        assert summary_section and len(summary_section.find_elements_by_xpath("div")) == 5

        # Check summary number sources alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-sources")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Check summary number annotations alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-annotations")))

        assert summary_number_alerts and summary_number_alerts.text == "2"

        # Check summary number events alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-events")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Check summary number reports alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-reports")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Check summary number ers alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-ers")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Check whether the timeline is displayed
        timeline_section = self.driver.find_element_by_id("timeline-general-view-alerts")

        condition = timeline_section.is_displayed()
        assert condition is True

        # Check generated content for widgets
        kwargs ={}
        kwargs["order_by"] = {"field": "notification_time", "descending": False}
        annotations_alerts = self.query_eboa.get_annotation_alerts(kwargs)

        assert len(annotations_alerts) == 4

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
        functions_vboa.assert_equal_list_dictionaries(returned_alerts, alerts)

        # Check annotation alerts table
        annotation_alerts_table = self.driver.find_element_by_id("associated-general-view-alerts-annotations-details-table")

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

    def test_explicit_refs_alerts_query_no_filter(self):

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

        self.driver.get("http://localhost:5000/general-view-alerts/")

        functions.query(self.driver, wait, start = "2018-06-05T08:07:36", stop = "2018-06-05T08:07:36")

        # Check number of widgets in summary
        summary_section = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts")))
        assert summary_section and len(summary_section.find_elements_by_xpath("div")) == 5

        # Check summary number sources alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-sources")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Check summary number annotations alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-annotations")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Check summary number events alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-events")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Check summary number reports alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-reports")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Check summary number ers alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-ers")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check whether the timeline is displayed
        timeline_section = self.driver.find_element_by_id("timeline-general-view-alerts")

        condition = timeline_section.is_displayed()
        assert condition is True

        # Check generated content for widgets
        kwargs ={}
        kwargs["order_by"] = {"field": "notification_time", "descending": False}
        explicit_refs_alerts = self.query_eboa.get_explicit_ref_alerts(kwargs)

        assert len(explicit_refs_alerts) == 2

        alerts = [
            {
                "alert_uuid": "<a href='/eboa_nav/query-alert/" + str(explicit_refs_alerts[0].explicit_ref_alert_uuid) + "'>" + str(explicit_refs_alerts[0].explicit_ref_alert_uuid) + "</a>",
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
            }
        ]

        returned_alerts = self.driver.execute_script('return alerts;')
        functions_vboa.assert_equal_list_dictionaries(returned_alerts, alerts)

        # Check er alerts table
        explicit_ref_alerts_table = self.driver.find_element_by_id("associated-general-view-alerts-ers-details-table")

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

    def test_reports_alerts_query_no_filter(self):

        filename = "report.html"
        file_path = os.path.dirname(os.path.abspath(__file__)) + "/../html_inputs/" + filename

        # Insert data
        data = {
                "operations":[
                    {
                        "mode":"insert",
                        "report":{
                            "name":filename,
                            "group":"report_group",
                            "group_description":"Group of reports for testing",
                            "path":file_path,
                            "compress":"true",
                            "generation_mode":"MANUAL",
                            "validity_start":"2018-06-05T02:07:03",
                            "validity_stop":"2018-06-05T08:07:36",
                            "triggering_time":"2018-07-05T02:07:03",
                            "generation_start":"2018-07-05T02:07:10",
                            "generation_stop":"2018-07-05T02:15:10",
                            "generator":"report_generator",
                            "generator_version":"1.0",
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
                                    },
                                    {
                                        "type":"double",
                                        "name":"DOUBLE",
                                        "value":"0.9"
                                    },
                                    {
                                        "type":"timestamp",
                                        "name":"TIMESTAMP",
                                        "value":"20180712T00:00:00"
                                    },
                                    {
                                        "type":"geometry",
                                        "name":"GEOMETRY",
                                        "value":"29.012974905944 -118.33483458667 28.8650301641571 -118.372028380632 28.7171766138274 -118.409121707686 28.5693112139334 -118.44612300623 28.4213994944367 -118.483058731035 28.2734085660472 -118.519970531113 28.1253606038163 -118.556849863134 27.9772541759126 -118.593690316835 27.8291247153939 -118.630472520505 27.7544158362332 -118.64900551674 27.7282373644786 -118.48032600682 27.7015162098732 -118.314168792268 27.6742039940042 -118.150246300849 27.6462511775992 -117.98827485961 27.6176070520608 -117.827974178264 27.5882197156561 -117.669066835177 27.5580360448116 -117.511277813618 27.5270016492436 -117.354334035359 27.4950608291016 -117.197963963877 27.4621565093409 -117.041897175848 27.4282301711374 -116.885863967864 27.3932217651372 -116.729594956238 27.3570696128269 -116.572820673713 27.3197103000253 -116.415271199941 27.2810785491022 -116.256675748617 27.241107085821 -116.09676229722 27.1997272484913 -115.935260563566 27.1524952198729 -115.755436839005 27.2270348347386 -115.734960009089 27.3748346522356 -115.694299254844 27.5226008861849 -115.653563616829 27.6702779354428 -115.612760542177 27.8178690071708 -115.571901649363 27.9653506439026 -115.531000691074 28.1127600020619 -115.490011752733 28.2601469756437 -115.44890306179 28.4076546372628 -115.407649898021 28.455192866856 -115.589486631416 28.4968374106496 -115.752807970928 28.5370603096399 -115.91452902381 28.575931293904 -116.074924211465 28.6135193777855 -116.234273707691 28.6498895688451 -116.392847129762 28.6851057860975 -116.550917254638 28.7192301322012 -116.708756374584 28.752323018501 -116.866636764481 28.7844432583843 -117.024831047231 28.8156481533955 -117.183612605748 28.8459935678779 -117.343255995623 28.8755339855462 -117.504037348554 28.9043225601122 -117.666234808407 28.9324111491586 -117.830128960026 28.9598503481156 -117.996003330616 28.9866878706574 -118.164136222141 29.012974905944 -118.33483458667"
                                    }
                                ]
                            }
                            ]
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
                            }
                            },
                            {
                            "message":"Alert message",
                            "generator":"test",
                            "notification_time":"2018-06-05T08:07:37",
                            "alert_cnf":{
                                "name":"alert_name2",
                                "severity":"warning",
                                "description":"Alert description",
                                "group":"alert_group"
                            }
                            },
                            {
                            "message":"Alert message",
                            "generator":"test",
                            "notification_time":"2018-06-05T08:07:38",
                            "alert_cnf":{
                                "name":"alert_name3",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_group"
                            }
                            }
                        ]
                    }
                ]
                }

        # Check data is correctly inserted
        self.engine_rboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_rboa.treat_data()[0]["status"]
        
        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/general-view-alerts/")

        functions.query(self.driver, wait, start = "2018-06-05T08:07:36", stop = "2018-06-05T08:07:38")

        # Check number of widgets in summary
        summary_section = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts")))
        assert summary_section and len(summary_section.find_elements_by_xpath("div")) == 5

        # Check summary number sources alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-sources")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Check summary number annotations alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-annotations")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Check summary number events alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-events")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Check summary number reports alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-reports")))

        assert summary_number_alerts and summary_number_alerts.text == "3"

        # Check summary number ers alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-ers")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Check whether the timeline is displayed
        timeline_section = self.driver.find_element_by_id("timeline-general-view-alerts")

        condition = timeline_section.is_displayed()
        assert condition is True

        # Check generated content for widgets
        reports_alerts = self.query_eboa.get_report_alerts()

        assert len(reports_alerts) == 3

        alerts = [
            {
                "alert_uuid": "<a href='/rboa_nav/query-alert/" + str(reports_alerts[0].report_alert_uuid) + "'>" + str(reports_alerts[0].report_alert_uuid) + "</a>",
                "description": "Alert description",
                "entity": "Report",
                "entity_uuid": "<a href='/rboa_nav/query-report/" + str(reports_alerts[0].report_uuid) + "'>" + str(reports_alerts[0].report_uuid) + "</a>",
                "generator": "test",
                "group": "REPORTS;alert_group",
                "group_alert": "alert_group",
                "id": str(reports_alerts[0].report_alert_uuid),
                "ingestion_time": reports_alerts[0].ingestion_time.isoformat(),
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
                "alert_uuid": "<a href='/rboa_nav/query-alert/" + str(reports_alerts[1].report_alert_uuid) + "'>" + str(reports_alerts[1].report_alert_uuid) + "</a>",
                "description": "Alert description",
                "entity": "Report",
                "entity_uuid": "<a href='/rboa_nav/query-report/" + str(reports_alerts[1].report_uuid) + "'>" + str(reports_alerts[1].report_uuid) + "</a>",
                "generator": "test",
                "group": "REPORTS;alert_group",
                "group_alert": "alert_group",
                "id": str(reports_alerts[1].report_alert_uuid),
                "ingestion_time": reports_alerts[1].ingestion_time.isoformat(),
                "justification": "None",
                "message": "Alert message",
                "name": "alert_name2",
                "notification_time": "2018-06-05T08:07:37",
                "notified": "<span class='bold-orange'>None</span>",
                "severity": "warning",
                "solved": "<span class='bold-orange'>None</span>",
                "solved_time": "None",
                "start": "2018-06-05T08:07:37",
                "stop": "2018-06-05T08:07:37",
                "timeline": "alert_name2",
                "validated": "<span class='bold-orange'>None</span>"
            },
            {
                "alert_uuid": "<a href='/rboa_nav/query-alert/" + str(reports_alerts[2].report_alert_uuid) + "'>" + str(reports_alerts[2].report_alert_uuid) + "</a>",
                "description": "Alert description",
                "entity": "Report",
                "entity_uuid": "<a href='/rboa_nav/query-report/" + str(reports_alerts[2].report_uuid) + "'>" + str(reports_alerts[2].report_uuid) + "</a>",
                "generator": "test",
                "group": "REPORTS;alert_group",
                "group_alert": "alert_group",
                "id": str(reports_alerts[2].report_alert_uuid),
                "ingestion_time": reports_alerts[2].ingestion_time.isoformat(),
                "justification": "None",
                "message": "Alert message",
                "name": "alert_name3",
                "notification_time": "2018-06-05T08:07:38",
                "notified": "<span class='bold-orange'>None</span>",
                "severity": "critical",
                "solved": "<span class='bold-orange'>None</span>",
                "solved_time": "None",
                "start": "2018-06-05T08:07:38",
                "stop": "2018-06-05T08:07:38",
                "timeline": "alert_name3",
                "validated": "<span class='bold-orange'>None</span>"
            },
        ]

        returned_alerts = self.driver.execute_script('return alerts;')
        functions_vboa.assert_equal_list_dictionaries(returned_alerts, alerts)

        # Check report alerts table
        report_alerts_table = self.driver.find_element_by_id("associated-general-view-alerts-reports-details-table")

        # Row 1
        justification = report_alerts_table.find_element_by_xpath("tbody/tr[1]/td[1]")

        assert justification.text == "None"

        severity = report_alerts_table.find_element_by_xpath("tbody/tr[1]/td[2]")

        assert severity.text == "critical"

        group = report_alerts_table.find_element_by_xpath("tbody/tr[1]/td[3]")

        assert group.text == "alert_group"

        name = report_alerts_table.find_element_by_xpath("tbody/tr[1]/td[4]")

        assert name.text == "alert_name1"

        message = report_alerts_table.find_element_by_xpath("tbody/tr[1]/td[5]")

        assert message.text == "Alert message"

        notification_time = report_alerts_table.find_element_by_xpath("tbody/tr[1]/td[6]")

        assert notification_time.text == "2018-06-05T08:07:36"

        solved = report_alerts_table.find_element_by_xpath("tbody/tr[1]/td[7]")

        assert solved.text == "None"

        solved_time = report_alerts_table.find_element_by_xpath("tbody/tr[1]/td[8]")

        assert solved_time.text == "None"

        description = report_alerts_table.find_element_by_xpath("tbody/tr[1]/td[9]")

        assert description.text == "Alert description"

        validated = report_alerts_table.find_element_by_xpath("tbody/tr[1]/td[10]")

        assert validated.text == "None"

        generator = report_alerts_table.find_element_by_xpath("tbody/tr[1]/td[11]")

        assert generator.text == "test"

        notified = report_alerts_table.find_element_by_xpath("tbody/tr[1]/td[12]")

        assert notified.text == "None"

        ingestion_time = report_alerts_table.find_element_by_xpath("tbody/tr[1]/td[13]")

        assert ingestion_time.text == reports_alerts[0].ingestion_time.isoformat()

        alert_uuid = report_alerts_table.find_element_by_xpath("tbody/tr[1]/td[14]")

        assert alert_uuid.text == str(reports_alerts[0].report_alert_uuid)

        report_uuid = report_alerts_table.find_element_by_xpath("tbody/tr[1]/td[15]")

        assert report_uuid.text == str(reports_alerts[0].report_uuid)

        # Row 2
        justification = report_alerts_table.find_element_by_xpath("tbody/tr[2]/td[1]")

        assert justification.text == "None"

        severity = report_alerts_table.find_element_by_xpath("tbody/tr[2]/td[2]")

        assert severity.text == "warning"

        group = report_alerts_table.find_element_by_xpath("tbody/tr[2]/td[3]")

        assert group.text == "alert_group"

        name = report_alerts_table.find_element_by_xpath("tbody/tr[2]/td[4]")

        assert name.text == "alert_name2"

        message = report_alerts_table.find_element_by_xpath("tbody/tr[2]/td[5]")

        assert message.text == "Alert message"

        notification_time = report_alerts_table.find_element_by_xpath("tbody/tr[2]/td[6]")

        assert notification_time.text == "2018-06-05T08:07:37"

        solved = report_alerts_table.find_element_by_xpath("tbody/tr[2]/td[7]")

        assert solved.text == "None"

        solved_time = report_alerts_table.find_element_by_xpath("tbody/tr[2]/td[8]")

        assert solved_time.text == "None"

        description = report_alerts_table.find_element_by_xpath("tbody/tr[2]/td[9]")

        assert description.text == "Alert description"

        validated = report_alerts_table.find_element_by_xpath("tbody/tr[2]/td[10]")

        assert validated.text == "None"

        generator = report_alerts_table.find_element_by_xpath("tbody/tr[2]/td[11]")

        assert generator.text == "test"

        notified = report_alerts_table.find_element_by_xpath("tbody/tr[2]/td[12]")

        assert notified.text == "None"

        ingestion_time = report_alerts_table.find_element_by_xpath("tbody/tr[2]/td[13]")

        assert ingestion_time.text == reports_alerts[1].ingestion_time.isoformat()

        alert_uuid = report_alerts_table.find_element_by_xpath("tbody/tr[2]/td[14]")

        assert alert_uuid.text == str(reports_alerts[1].report_alert_uuid)

        report_uuid = report_alerts_table.find_element_by_xpath("tbody/tr[2]/td[15]")

        assert report_uuid.text == str(reports_alerts[1].report_uuid)

        # Row 3
        justification = report_alerts_table.find_element_by_xpath("tbody/tr[3]/td[1]")

        assert justification.text == "None"

        severity = report_alerts_table.find_element_by_xpath("tbody/tr[3]/td[2]")

        assert severity.text == "critical"

        group = report_alerts_table.find_element_by_xpath("tbody/tr[3]/td[3]")

        assert group.text == "alert_group"

        name = report_alerts_table.find_element_by_xpath("tbody/tr[3]/td[4]")

        assert name.text == "alert_name3"

        message = report_alerts_table.find_element_by_xpath("tbody/tr[3]/td[5]")

        assert message.text == "Alert message"

        notification_time = report_alerts_table.find_element_by_xpath("tbody/tr[3]/td[6]")

        assert notification_time.text == "2018-06-05T08:07:38"

        solved = report_alerts_table.find_element_by_xpath("tbody/tr[3]/td[7]")

        assert solved.text == "None"

        solved_time = report_alerts_table.find_element_by_xpath("tbody/tr[3]/td[8]")

        assert solved_time.text == "None"

        description = report_alerts_table.find_element_by_xpath("tbody/tr[3]/td[9]")

        assert description.text == "Alert description"

        validated = report_alerts_table.find_element_by_xpath("tbody/tr[3]/td[10]")

        assert validated.text == "None"

        generator = report_alerts_table.find_element_by_xpath("tbody/tr[3]/td[11]")

        assert generator.text == "test"

        notified = report_alerts_table.find_element_by_xpath("tbody/tr[3]/td[12]")

        assert notified.text == "None"

        ingestion_time = report_alerts_table.find_element_by_xpath("tbody/tr[3]/td[13]")

        assert ingestion_time.text == reports_alerts[2].ingestion_time.isoformat()

        alert_uuid = report_alerts_table.find_element_by_xpath("tbody/tr[3]/td[14]")

        assert alert_uuid.text == str(reports_alerts[2].report_alert_uuid)

        report_uuid = report_alerts_table.find_element_by_xpath("tbody/tr[3]/td[15]")

        assert report_uuid.text == str(reports_alerts[2].report_uuid)

    def test_all_alerts_query_no_filter(self):

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
                        ],
                        "events":[
                            {
                            "explicit_reference":"ER1",
                            "gauge":{
                                "name":"GAUGE_NAME",
                                "system":"GAUGE_SYSTEM",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2018-06-05T02:07:03",
                            "stop":"2018-06-05T08:07:36",
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
                                        "name":"alert_name2",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group1"
                                    }
                                }
                            ]
                            }
                        ],
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
                                        "name":"alert_name3",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group2"
                                    }
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
                                "name":"alert_name4",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_group3"
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

        filename = "report.html"
        file_path = os.path.dirname(os.path.abspath(__file__)) + "/../html_inputs/" + filename

        # Insert data
        data = {
                "operations":[
                    {
                        "mode":"insert",
                        "report":{
                            "name":filename,
                            "group":"report_group",
                            "group_description":"Group of reports for testing",
                            "path":file_path,
                            "compress":"true",
                            "generation_mode":"MANUAL",
                            "validity_start":"2018-06-05T02:07:03",
                            "validity_stop":"2018-06-05T08:07:36",
                            "triggering_time":"2018-07-05T02:07:03",
                            "generation_start":"2018-07-05T02:07:10",
                            "generation_stop":"2018-07-05T02:15:10",
                            "generator":"report_generator",
                            "generator_version":"1.0",
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
                                    },
                                    {
                                        "type":"double",
                                        "name":"DOUBLE",
                                        "value":"0.9"
                                    },
                                    {
                                        "type":"timestamp",
                                        "name":"TIMESTAMP",
                                        "value":"20180712T00:00:00"
                                    },
                                    {
                                        "type":"geometry",
                                        "name":"GEOMETRY",
                                        "value":"29.012974905944 -118.33483458667 28.8650301641571 -118.372028380632 28.7171766138274 -118.409121707686 28.5693112139334 -118.44612300623 28.4213994944367 -118.483058731035 28.2734085660472 -118.519970531113 28.1253606038163 -118.556849863134 27.9772541759126 -118.593690316835 27.8291247153939 -118.630472520505 27.7544158362332 -118.64900551674 27.7282373644786 -118.48032600682 27.7015162098732 -118.314168792268 27.6742039940042 -118.150246300849 27.6462511775992 -117.98827485961 27.6176070520608 -117.827974178264 27.5882197156561 -117.669066835177 27.5580360448116 -117.511277813618 27.5270016492436 -117.354334035359 27.4950608291016 -117.197963963877 27.4621565093409 -117.041897175848 27.4282301711374 -116.885863967864 27.3932217651372 -116.729594956238 27.3570696128269 -116.572820673713 27.3197103000253 -116.415271199941 27.2810785491022 -116.256675748617 27.241107085821 -116.09676229722 27.1997272484913 -115.935260563566 27.1524952198729 -115.755436839005 27.2270348347386 -115.734960009089 27.3748346522356 -115.694299254844 27.5226008861849 -115.653563616829 27.6702779354428 -115.612760542177 27.8178690071708 -115.571901649363 27.9653506439026 -115.531000691074 28.1127600020619 -115.490011752733 28.2601469756437 -115.44890306179 28.4076546372628 -115.407649898021 28.455192866856 -115.589486631416 28.4968374106496 -115.752807970928 28.5370603096399 -115.91452902381 28.575931293904 -116.074924211465 28.6135193777855 -116.234273707691 28.6498895688451 -116.392847129762 28.6851057860975 -116.550917254638 28.7192301322012 -116.708756374584 28.752323018501 -116.866636764481 28.7844432583843 -117.024831047231 28.8156481533955 -117.183612605748 28.8459935678779 -117.343255995623 28.8755339855462 -117.504037348554 28.9043225601122 -117.666234808407 28.9324111491586 -117.830128960026 28.9598503481156 -117.996003330616 28.9866878706574 -118.164136222141 29.012974905944 -118.33483458667"
                                    }
                                ]
                            }
                            ]
                        },
                        "alerts":[
                            {
                            "message":"Alert message",
                            "generator":"test",
                            "notification_time":"2018-06-05T08:07:36",
                            "alert_cnf":{
                                "name":"alert_name5",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_group4"
                            }
                            }
                        ]
                    }
                ]
                }

        # Check data is correctly inserted
        self.engine_rboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_rboa.treat_data()[0]["status"]
        
        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/general-view-alerts/")

        functions.query(self.driver, wait, start = "2018-06-05T08:07:36", stop = "2018-06-05T08:07:36")

        # Check number of widgets in summary
        summary_section = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts")))
        assert summary_section and len(summary_section.find_elements_by_xpath("div")) == 5

        # Check summary number sources alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-sources")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number annotations alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-annotations")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number events alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-events")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number reports alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-reports")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number ers alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-ers")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check whether the timeline is displayed
        timeline_section = self.driver.find_element_by_id("timeline-general-view-alerts")

        condition = timeline_section.is_displayed()
        assert condition is True

        # Check generated content for widgets
        sources_alerts = self.query_eboa.get_source_alerts()

        assert len(sources_alerts) == 1

        events_alerts = self.query_eboa.get_event_alerts()

        assert len(events_alerts) == 1

        annotations_alerts = self.query_eboa.get_annotation_alerts()

        assert len(annotations_alerts) == 1

        explicit_refs_alerts = self.query_eboa.get_explicit_ref_alerts()

        assert len(explicit_refs_alerts) == 1

        reports_alerts = self.query_eboa.get_report_alerts()

        assert len(reports_alerts) == 1

        alerts = [
            {
                "alert_uuid": "<a href='/eboa_nav/query-alert/" + str(sources_alerts[0].source_alert_uuid) + "'>" + str(sources_alerts[0].source_alert_uuid) + "</a>",
                "description": "Alert description",
                "entity": "Source",
                "entity_uuid": "<a href='/eboa_nav/query-source/" + str(sources_alerts[0].source_uuid) + "'>" + str(sources_alerts[0].source_uuid) + "</a>",
                "generator": "test",
                "group": "SOURCES;alert_group3",
                "group_alert": "alert_group3",
                "id": str(sources_alerts[0].source_alert_uuid),
                "ingestion_time": sources_alerts[0].ingestion_time.isoformat(),
                "justification": "None",
                "message": "Alert message",
                "name": "alert_name4",
                "notification_time": "2018-06-05T08:07:36",
                "notified": "<span class='bold-orange'>None</span>",
                "severity": "critical",
                "solved": "<span class='bold-orange'>None</span>",
                "solved_time": "None",
                "start": "2018-06-05T08:07:36",
                "stop": "2018-06-05T08:07:36",
                "timeline": "alert_name4",
                "validated": "<span class='bold-orange'>None</span>"
            },
            {
                "alert_uuid": "<a href='/eboa_nav/query-alert/" + str(events_alerts[0].event_alert_uuid) + "'>" + str(events_alerts[0].event_alert_uuid) + "</a>",
                "description": "Alert description",
                "entity": "Event",
                "entity_uuid": "<a href='/eboa_nav/query-event-links/" + str(events_alerts[0].event_uuid) + "'>" + str(events_alerts[0].event_uuid) + "</a>",
                "generator": "test",
                "group": "EVENTS;alert_group1",
                "group_alert": "alert_group1",
                "id": str(events_alerts[0].event_alert_uuid),
                "ingestion_time": events_alerts[0].ingestion_time.isoformat(),
                "justification": "None",
                "message": "Alert message",
                "name": "alert_name2",
                "notification_time": "2018-06-05T08:07:36",
                "notified": "<span class='bold-orange'>None</span>",
                "severity": "critical",
                "solved": "<span class='bold-orange'>None</span>",
                "solved_time": "None",
                "start": "2018-06-05T08:07:36",
                "stop": "2018-06-05T08:07:36",
                "timeline": "alert_name2",
                "validated": "<span class='bold-orange'>None</span>"
            },
            {
                "alert_uuid": "<a href='/eboa_nav/query-alert/" + str(annotations_alerts[0].annotation_alert_uuid) + "'>" + str(annotations_alerts[0].annotation_alert_uuid) + "</a>",
                "description": "Alert description",
                "entity": "Annotation",
                "entity_uuid": "<a href='/eboa_nav/query-annotation/" + str(annotations_alerts[0].annotation_uuid) + "'>" + str(annotations_alerts[0].annotation_uuid) + "</a>",
                "generator": "test",
                "group": "ANNOTATIONS;alert_group2",
                "group_alert": "alert_group2",
                "id": str(annotations_alerts[0].annotation_alert_uuid),
                "ingestion_time": annotations_alerts[0].ingestion_time.isoformat(),
                "justification": "None",
                "message": "Alert message",
                "name": "alert_name3",
                "notification_time": "2018-06-05T08:07:36",
                "notified": "<span class='bold-orange'>None</span>",
                "severity": "critical",
                "solved": "<span class='bold-orange'>None</span>",
                "solved_time": "None",
                "start": "2018-06-05T08:07:36",
                "stop": "2018-06-05T08:07:36",
                "timeline": "alert_name3",
                "validated": "<span class='bold-orange'>None</span>"
            },
            {
                "alert_uuid": "<a href='/eboa_nav/query-alert/" + str(explicit_refs_alerts[0].explicit_ref_alert_uuid) + "'>" + str(explicit_refs_alerts[0].explicit_ref_alert_uuid) + "</a>",
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
                "alert_uuid": "<a href='/rboa_nav/query-alert/" + str(reports_alerts[0].report_alert_uuid) + "'>" + str(reports_alerts[0].report_alert_uuid) + "</a>",
                "description": "Alert description",
                "entity": "Report",
                "entity_uuid": "<a href='/rboa_nav/query-report/" + str(reports_alerts[0].report_uuid) + "'>" + str(reports_alerts[0].report_uuid) + "</a>",
                "generator": "test",
                "group": "REPORTS;alert_group4",
                "group_alert": "alert_group4",
                "id": str(reports_alerts[0].report_alert_uuid),
                "ingestion_time": reports_alerts[0].ingestion_time.isoformat(),
                "justification": "None",
                "message": "Alert message",
                "name": "alert_name5",
                "notification_time": "2018-06-05T08:07:36",
                "notified": "<span class='bold-orange'>None</span>",
                "severity": "critical",
                "solved": "<span class='bold-orange'>None</span>",
                "solved_time": "None",
                "start": "2018-06-05T08:07:36",
                "stop": "2018-06-05T08:07:36",
                "timeline": "alert_name5",
                "validated": "<span class='bold-orange'>None</span>"
            },
        ]

        returned_alerts = self.driver.execute_script('return alerts;')
        functions_vboa.assert_equal_list_dictionaries(returned_alerts, alerts)  
        
        # Check source alerts table
        source_alerts_table = self.driver.find_element_by_id("associated-general-view-alerts-sources-details-table")

        # Row 1
        justification = source_alerts_table.find_element_by_xpath("tbody/tr[1]/td[1]")

        assert justification.text == "None"

        severity = source_alerts_table.find_element_by_xpath("tbody/tr[1]/td[2]")

        assert severity.text == "critical"

        group = source_alerts_table.find_element_by_xpath("tbody/tr[1]/td[3]")

        assert group.text == "alert_group3"

        name = source_alerts_table.find_element_by_xpath("tbody/tr[1]/td[4]")

        assert name.text == "alert_name4"

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

        # Check event alerts table
        event_alerts_table = self.driver.find_element_by_id("associated-general-view-alerts-events-details-table")

        # Row 1
        justification = event_alerts_table.find_element_by_xpath("tbody/tr[1]/td[1]")

        assert justification.text == "None"

        severity = event_alerts_table.find_element_by_xpath("tbody/tr[1]/td[2]")

        assert severity.text == "critical"

        group = event_alerts_table.find_element_by_xpath("tbody/tr[1]/td[3]")

        assert group.text == "alert_group1"

        name = event_alerts_table.find_element_by_xpath("tbody/tr[1]/td[4]")

        assert name.text == "alert_name2"

        message = event_alerts_table.find_element_by_xpath("tbody/tr[1]/td[5]")

        assert message.text == "Alert message"

        notification_time = event_alerts_table.find_element_by_xpath("tbody/tr[1]/td[6]")

        assert notification_time.text == "2018-06-05T08:07:36"

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
        
        # Check annotation alerts table
        annotation_alerts_table = self.driver.find_element_by_id("associated-general-view-alerts-annotations-details-table")

        # Row 1
        justification = annotation_alerts_table.find_element_by_xpath("tbody/tr[1]/td[1]")

        assert justification.text == "None"

        severity = annotation_alerts_table.find_element_by_xpath("tbody/tr[1]/td[2]")

        assert severity.text == "critical"

        group = annotation_alerts_table.find_element_by_xpath("tbody/tr[1]/td[3]")

        assert group.text == "alert_group2"

        name = annotation_alerts_table.find_element_by_xpath("tbody/tr[1]/td[4]")

        assert name.text == "alert_name3"

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

        # Check er alerts table
        explicit_ref_alerts_table = self.driver.find_element_by_id("associated-general-view-alerts-ers-details-table")

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

        # Check report alerts table
        report_alerts_table = self.driver.find_element_by_id("associated-general-view-alerts-reports-details-table")

        # Row 1
        justification = report_alerts_table.find_element_by_xpath("tbody/tr[1]/td[1]")

        assert justification.text == "None"

        severity = report_alerts_table.find_element_by_xpath("tbody/tr[1]/td[2]")

        assert severity.text == "critical"

        group = report_alerts_table.find_element_by_xpath("tbody/tr[1]/td[3]")

        assert group.text == "alert_group4"

        name = report_alerts_table.find_element_by_xpath("tbody/tr[1]/td[4]")

        assert name.text == "alert_name5"

        message = report_alerts_table.find_element_by_xpath("tbody/tr[1]/td[5]")

        assert message.text == "Alert message"

        notification_time = report_alerts_table.find_element_by_xpath("tbody/tr[1]/td[6]")

        assert notification_time.text == "2018-06-05T08:07:36"

        solved = report_alerts_table.find_element_by_xpath("tbody/tr[1]/td[7]")

        assert solved.text == "None"

        solved_time = report_alerts_table.find_element_by_xpath("tbody/tr[1]/td[8]")

        assert solved_time.text == "None"

        description = report_alerts_table.find_element_by_xpath("tbody/tr[1]/td[9]")

        assert description.text == "Alert description"

        validated = report_alerts_table.find_element_by_xpath("tbody/tr[1]/td[10]")

        assert validated.text == "None"

        generator = report_alerts_table.find_element_by_xpath("tbody/tr[1]/td[11]")

        assert generator.text == "test"

        notified = report_alerts_table.find_element_by_xpath("tbody/tr[1]/td[12]")

        assert notified.text == "None"

        ingestion_time = report_alerts_table.find_element_by_xpath("tbody/tr[1]/td[13]")

        assert ingestion_time.text == reports_alerts[0].ingestion_time.isoformat()

        alert_uuid = report_alerts_table.find_element_by_xpath("tbody/tr[1]/td[14]")

        assert alert_uuid.text == str(reports_alerts[0].report_alert_uuid)

        report_uuid = report_alerts_table.find_element_by_xpath("tbody/tr[1]/td[15]")

        assert report_uuid.text == str(reports_alerts[0].report_uuid)

    def test_pagination_sources(self):

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
                        ],
                        "events":[
                            {
                            "explicit_reference":"ER1",
                            "gauge":{
                                "name":"GAUGE_NAME",
                                "system":"GAUGE_SYSTEM",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2018-06-05T02:07:03",
                            "stop":"2018-06-05T08:07:36",
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
                                        "name":"alert_name2",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group1"
                                    }
                                }
                            ]
                            }
                        ],
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
                                        "name":"alert_name3",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group2"
                                    }
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
                                "name":"alert_name4",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_group3"
                            },
                            "entity":{
                                "reference_mode":"by_ref",
                                "reference":"source.json",
                                "type":"source"
                            }
                            },
                            {
                            "message":"Alert message",
                            "generator":"test",
                            "notification_time":"2018-06-05T08:07:36",
                            "alert_cnf":{
                                "name":"alert_name5",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_group3"
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

        filename = "report.html"
        file_path = os.path.dirname(os.path.abspath(__file__)) + "/../html_inputs/" + filename

        # Insert data
        data = {
                "operations":[
                    {
                        "mode":"insert",
                        "report":{
                            "name":filename,
                            "group":"report_group",
                            "group_description":"Group of reports for testing",
                            "path":file_path,
                            "compress":"true",
                            "generation_mode":"MANUAL",
                            "validity_start":"2018-06-05T02:07:03",
                            "validity_stop":"2018-06-05T08:07:36",
                            "triggering_time":"2018-07-05T02:07:03",
                            "generation_start":"2018-07-05T02:07:10",
                            "generation_stop":"2018-07-05T02:15:10",
                            "generator":"report_generator",
                            "generator_version":"1.0",
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
                                    },
                                    {
                                        "type":"double",
                                        "name":"DOUBLE",
                                        "value":"0.9"
                                    },
                                    {
                                        "type":"timestamp",
                                        "name":"TIMESTAMP",
                                        "value":"20180712T00:00:00"
                                    },
                                    {
                                        "type":"geometry",
                                        "name":"GEOMETRY",
                                        "value":"29.012974905944 -118.33483458667 28.8650301641571 -118.372028380632 28.7171766138274 -118.409121707686 28.5693112139334 -118.44612300623 28.4213994944367 -118.483058731035 28.2734085660472 -118.519970531113 28.1253606038163 -118.556849863134 27.9772541759126 -118.593690316835 27.8291247153939 -118.630472520505 27.7544158362332 -118.64900551674 27.7282373644786 -118.48032600682 27.7015162098732 -118.314168792268 27.6742039940042 -118.150246300849 27.6462511775992 -117.98827485961 27.6176070520608 -117.827974178264 27.5882197156561 -117.669066835177 27.5580360448116 -117.511277813618 27.5270016492436 -117.354334035359 27.4950608291016 -117.197963963877 27.4621565093409 -117.041897175848 27.4282301711374 -116.885863967864 27.3932217651372 -116.729594956238 27.3570696128269 -116.572820673713 27.3197103000253 -116.415271199941 27.2810785491022 -116.256675748617 27.241107085821 -116.09676229722 27.1997272484913 -115.935260563566 27.1524952198729 -115.755436839005 27.2270348347386 -115.734960009089 27.3748346522356 -115.694299254844 27.5226008861849 -115.653563616829 27.6702779354428 -115.612760542177 27.8178690071708 -115.571901649363 27.9653506439026 -115.531000691074 28.1127600020619 -115.490011752733 28.2601469756437 -115.44890306179 28.4076546372628 -115.407649898021 28.455192866856 -115.589486631416 28.4968374106496 -115.752807970928 28.5370603096399 -115.91452902381 28.575931293904 -116.074924211465 28.6135193777855 -116.234273707691 28.6498895688451 -116.392847129762 28.6851057860975 -116.550917254638 28.7192301322012 -116.708756374584 28.752323018501 -116.866636764481 28.7844432583843 -117.024831047231 28.8156481533955 -117.183612605748 28.8459935678779 -117.343255995623 28.8755339855462 -117.504037348554 28.9043225601122 -117.666234808407 28.9324111491586 -117.830128960026 28.9598503481156 -117.996003330616 28.9866878706574 -118.164136222141 29.012974905944 -118.33483458667"
                                    }
                                ]
                            }
                            ]
                        },
                        "alerts":[
                            {
                            "message":"Alert message",
                            "generator":"test",
                            "notification_time":"2018-06-05T08:07:36",
                            "alert_cnf":{
                                "name":"alert_name5",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_group4"
                            }
                            }
                        ]
                    }
                ]
                }

        # Check data is correctly inserted
        self.engine_rboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_rboa.treat_data()[0]["status"]
        
        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/general-view-alerts/")

        functions.query(self.driver, wait, start = "2018-06-05T08:07:36", stop = "2018-06-05T08:07:36", limit = "1")

        # Check number of widgets in summary
        summary_section = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts")))
        assert summary_section and len(summary_section.find_elements_by_xpath("div")) == 5

        # Check summary number sources alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-sources")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number annotations alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-annotations")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number events alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-events")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number reports alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-reports")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number ers alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-ers")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        functions.click(self.driver.find_element_by_xpath("//*[contains(text(), 'Next >>')]"))
        
        # Use staleness_of to avoid StaleElement Exception
        wait.until(EC.staleness_of(summary_section))

        # Check number of widgets in summary
        summary_section = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts")))
        assert summary_section and len(summary_section.find_elements_by_xpath("div")) == 5

        # Check summary number sources alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-sources")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number annotations alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-annotations")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Check summary number events alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-events")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Check summary number reports alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-reports")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Check summary number ers alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-ers")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Use presence_of_element_located to avoid StaleElement Exception
        functions.click(self.driver.find_element_by_xpath("//*[contains(text(), '<< Show all >>')]"))

        # Use staleness_of to avoid StaleElement Exception
        wait.until(EC.staleness_of(summary_section))
        
        # Check number of widgets in summary
        summary_section = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts")))
        assert summary_section and len(summary_section.find_elements_by_xpath("div")) == 5

        # Check summary number sources alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-sources")))

        assert summary_number_alerts and summary_number_alerts.text == "2"

        # Check summary number annotations alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-annotations")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number events alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-events")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number reports alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-reports")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number ers alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-ers")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

    def test_pagination_events(self):

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
                        ],
                        "events":[
                            {
                            "explicit_reference":"ER1",
                            "gauge":{
                                "name":"GAUGE_NAME",
                                "system":"GAUGE_SYSTEM",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2018-06-05T02:07:03",
                            "stop":"2018-06-05T08:07:36",
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
                                        "name":"alert_name2",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group1"
                                    }
                                },
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:36",
                                    "alert_cnf":{
                                        "name":"alert_name5",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group3"
                                    }
                                }
                            ]
                            }
                        ],
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
                                        "name":"alert_name3",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group2"
                                    }
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
                                "name":"alert_name4",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_group3"
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

        filename = "report.html"
        file_path = os.path.dirname(os.path.abspath(__file__)) + "/../html_inputs/" + filename

        # Insert data
        data = {
                "operations":[
                    {
                        "mode":"insert",
                        "report":{
                            "name":filename,
                            "group":"report_group",
                            "group_description":"Group of reports for testing",
                            "path":file_path,
                            "compress":"true",
                            "generation_mode":"MANUAL",
                            "validity_start":"2018-06-05T02:07:03",
                            "validity_stop":"2018-06-05T08:07:36",
                            "triggering_time":"2018-07-05T02:07:03",
                            "generation_start":"2018-07-05T02:07:10",
                            "generation_stop":"2018-07-05T02:15:10",
                            "generator":"report_generator",
                            "generator_version":"1.0",
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
                                    },
                                    {
                                        "type":"double",
                                        "name":"DOUBLE",
                                        "value":"0.9"
                                    },
                                    {
                                        "type":"timestamp",
                                        "name":"TIMESTAMP",
                                        "value":"20180712T00:00:00"
                                    },
                                    {
                                        "type":"geometry",
                                        "name":"GEOMETRY",
                                        "value":"29.012974905944 -118.33483458667 28.8650301641571 -118.372028380632 28.7171766138274 -118.409121707686 28.5693112139334 -118.44612300623 28.4213994944367 -118.483058731035 28.2734085660472 -118.519970531113 28.1253606038163 -118.556849863134 27.9772541759126 -118.593690316835 27.8291247153939 -118.630472520505 27.7544158362332 -118.64900551674 27.7282373644786 -118.48032600682 27.7015162098732 -118.314168792268 27.6742039940042 -118.150246300849 27.6462511775992 -117.98827485961 27.6176070520608 -117.827974178264 27.5882197156561 -117.669066835177 27.5580360448116 -117.511277813618 27.5270016492436 -117.354334035359 27.4950608291016 -117.197963963877 27.4621565093409 -117.041897175848 27.4282301711374 -116.885863967864 27.3932217651372 -116.729594956238 27.3570696128269 -116.572820673713 27.3197103000253 -116.415271199941 27.2810785491022 -116.256675748617 27.241107085821 -116.09676229722 27.1997272484913 -115.935260563566 27.1524952198729 -115.755436839005 27.2270348347386 -115.734960009089 27.3748346522356 -115.694299254844 27.5226008861849 -115.653563616829 27.6702779354428 -115.612760542177 27.8178690071708 -115.571901649363 27.9653506439026 -115.531000691074 28.1127600020619 -115.490011752733 28.2601469756437 -115.44890306179 28.4076546372628 -115.407649898021 28.455192866856 -115.589486631416 28.4968374106496 -115.752807970928 28.5370603096399 -115.91452902381 28.575931293904 -116.074924211465 28.6135193777855 -116.234273707691 28.6498895688451 -116.392847129762 28.6851057860975 -116.550917254638 28.7192301322012 -116.708756374584 28.752323018501 -116.866636764481 28.7844432583843 -117.024831047231 28.8156481533955 -117.183612605748 28.8459935678779 -117.343255995623 28.8755339855462 -117.504037348554 28.9043225601122 -117.666234808407 28.9324111491586 -117.830128960026 28.9598503481156 -117.996003330616 28.9866878706574 -118.164136222141 29.012974905944 -118.33483458667"
                                    }
                                ]
                            }
                            ]
                        },
                        "alerts":[
                            {
                            "message":"Alert message",
                            "generator":"test",
                            "notification_time":"2018-06-05T08:07:36",
                            "alert_cnf":{
                                "name":"alert_name5",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_group4"
                            }
                            }
                        ]
                    }
                ]
                }

        # Check data is correctly inserted
        self.engine_rboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_rboa.treat_data()[0]["status"]
        
        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/general-view-alerts/")

        functions.query(self.driver, wait, start = "2018-06-05T08:07:36", stop = "2018-06-05T08:07:36", limit = "1")

        # Check number of widgets in summary
        summary_section = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts")))
        assert summary_section and len(summary_section.find_elements_by_xpath("div")) == 5

        # Check summary number sources alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-sources")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number annotations alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-annotations")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number events alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-events")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number reports alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-reports")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number ers alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-ers")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        functions.click(self.driver.find_element_by_xpath("//*[contains(text(), 'Next >>')]"))
        
        # Use staleness_of to avoid StaleElement Exception
        wait.until(EC.staleness_of(summary_section))

        # Check number of widgets in summary
        summary_section = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts")))
        assert summary_section and len(summary_section.find_elements_by_xpath("div")) == 5

        # Check summary number sources alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-sources")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Check summary number annotations alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-annotations")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Check summary number events alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-events")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number reports alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-reports")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Check summary number ers alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-ers")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Use presence_of_element_located to avoid StaleElement Exception
        functions.click(self.driver.find_element_by_xpath("//*[contains(text(), '<< Show all >>')]"))

        # Use staleness_of to avoid StaleElement Exception
        wait.until(EC.staleness_of(summary_section))
        
        # Check number of widgets in summary
        summary_section = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts")))
        assert summary_section and len(summary_section.find_elements_by_xpath("div")) == 5

        # Check summary number sources alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-sources")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number annotations alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-annotations")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number events alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-events")))

        assert summary_number_alerts and summary_number_alerts.text == "2"

        # Check summary number reports alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-reports")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number ers alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-ers")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

    def test_pagination_annotations(self):

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
                        ],
                        "events":[
                            {
                            "explicit_reference":"ER1",
                            "gauge":{
                                "name":"GAUGE_NAME",
                                "system":"GAUGE_SYSTEM",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2018-06-05T02:07:03",
                            "stop":"2018-06-05T08:07:36",
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
                                        "name":"alert_name2",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group1"
                                    }
                                }
                            ]
                            }
                        ],
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
                                        "name":"alert_name3",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group2"
                                    }
                                },
                                {
                                    "message":"Alert message",
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:36",
                                    "alert_cnf":{
                                        "name":"alert_name5",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group3"
                                    }
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
                                "name":"alert_name4",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_group3"
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

        filename = "report.html"
        file_path = os.path.dirname(os.path.abspath(__file__)) + "/../html_inputs/" + filename

        # Insert data
        data = {
                "operations":[
                    {
                        "mode":"insert",
                        "report":{
                            "name":filename,
                            "group":"report_group",
                            "group_description":"Group of reports for testing",
                            "path":file_path,
                            "compress":"true",
                            "generation_mode":"MANUAL",
                            "validity_start":"2018-06-05T02:07:03",
                            "validity_stop":"2018-06-05T08:07:36",
                            "triggering_time":"2018-07-05T02:07:03",
                            "generation_start":"2018-07-05T02:07:10",
                            "generation_stop":"2018-07-05T02:15:10",
                            "generator":"report_generator",
                            "generator_version":"1.0",
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
                                    },
                                    {
                                        "type":"double",
                                        "name":"DOUBLE",
                                        "value":"0.9"
                                    },
                                    {
                                        "type":"timestamp",
                                        "name":"TIMESTAMP",
                                        "value":"20180712T00:00:00"
                                    },
                                    {
                                        "type":"geometry",
                                        "name":"GEOMETRY",
                                        "value":"29.012974905944 -118.33483458667 28.8650301641571 -118.372028380632 28.7171766138274 -118.409121707686 28.5693112139334 -118.44612300623 28.4213994944367 -118.483058731035 28.2734085660472 -118.519970531113 28.1253606038163 -118.556849863134 27.9772541759126 -118.593690316835 27.8291247153939 -118.630472520505 27.7544158362332 -118.64900551674 27.7282373644786 -118.48032600682 27.7015162098732 -118.314168792268 27.6742039940042 -118.150246300849 27.6462511775992 -117.98827485961 27.6176070520608 -117.827974178264 27.5882197156561 -117.669066835177 27.5580360448116 -117.511277813618 27.5270016492436 -117.354334035359 27.4950608291016 -117.197963963877 27.4621565093409 -117.041897175848 27.4282301711374 -116.885863967864 27.3932217651372 -116.729594956238 27.3570696128269 -116.572820673713 27.3197103000253 -116.415271199941 27.2810785491022 -116.256675748617 27.241107085821 -116.09676229722 27.1997272484913 -115.935260563566 27.1524952198729 -115.755436839005 27.2270348347386 -115.734960009089 27.3748346522356 -115.694299254844 27.5226008861849 -115.653563616829 27.6702779354428 -115.612760542177 27.8178690071708 -115.571901649363 27.9653506439026 -115.531000691074 28.1127600020619 -115.490011752733 28.2601469756437 -115.44890306179 28.4076546372628 -115.407649898021 28.455192866856 -115.589486631416 28.4968374106496 -115.752807970928 28.5370603096399 -115.91452902381 28.575931293904 -116.074924211465 28.6135193777855 -116.234273707691 28.6498895688451 -116.392847129762 28.6851057860975 -116.550917254638 28.7192301322012 -116.708756374584 28.752323018501 -116.866636764481 28.7844432583843 -117.024831047231 28.8156481533955 -117.183612605748 28.8459935678779 -117.343255995623 28.8755339855462 -117.504037348554 28.9043225601122 -117.666234808407 28.9324111491586 -117.830128960026 28.9598503481156 -117.996003330616 28.9866878706574 -118.164136222141 29.012974905944 -118.33483458667"
                                    }
                                ]
                            }
                            ]
                        },
                        "alerts":[
                            {
                            "message":"Alert message",
                            "generator":"test",
                            "notification_time":"2018-06-05T08:07:36",
                            "alert_cnf":{
                                "name":"alert_name5",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_group4"
                            }
                            }
                        ]
                    }
                ]
                }

        # Check data is correctly inserted
        self.engine_rboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_rboa.treat_data()[0]["status"]
        
        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/general-view-alerts/")

        functions.query(self.driver, wait, start = "2018-06-05T08:07:36", stop = "2018-06-05T08:07:36", limit = "1")

        # Check number of widgets in summary
        summary_section = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts")))
        assert summary_section and len(summary_section.find_elements_by_xpath("div")) == 5

        # Check summary number sources alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-sources")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number annotations alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-annotations")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number events alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-events")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number reports alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-reports")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number ers alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-ers")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        functions.click(self.driver.find_element_by_xpath("//*[contains(text(), 'Next >>')]"))
        
        # Use staleness_of to avoid StaleElement Exception
        wait.until(EC.staleness_of(summary_section))

        # Check number of widgets in summary
        summary_section = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts")))
        assert summary_section and len(summary_section.find_elements_by_xpath("div")) == 5

        # Check summary number sources alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-sources")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Check summary number annotations alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-annotations")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number events alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-events")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Check summary number reports alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-reports")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Check summary number ers alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-ers")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Use presence_of_element_located to avoid StaleElement Exception
        functions.click(self.driver.find_element_by_xpath("//*[contains(text(), '<< Show all >>')]"))

        # Use staleness_of to avoid StaleElement Exception
        wait.until(EC.staleness_of(summary_section))
        
        # Check number of widgets in summary
        summary_section = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts")))
        assert summary_section and len(summary_section.find_elements_by_xpath("div")) == 5

        # Check summary number sources alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-sources")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number annotations alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-annotations")))

        assert summary_number_alerts and summary_number_alerts.text == "2"

        # Check summary number events alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-events")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number reports alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-reports")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number ers alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-ers")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

    def test_pagination_ers(self):

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
                                    "generator":"test",
                                    "notification_time":"2018-06-05T08:07:36",
                                    "alert_cnf":{
                                        "name":"alert_name5",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group3"
                                    }
                                } 
                            ]
                            }
                        ],
                        "events":[
                            {
                            "explicit_reference":"ER1",
                            "gauge":{
                                "name":"GAUGE_NAME",
                                "system":"GAUGE_SYSTEM",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2018-06-05T02:07:03",
                            "stop":"2018-06-05T08:07:36",
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
                                        "name":"alert_name2",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group1"
                                    }
                                }
                            ]
                            }
                        ],
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
                                        "name":"alert_name3",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group2"
                                    }
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
                                "name":"alert_name4",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_group3"
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

        filename = "report.html"
        file_path = os.path.dirname(os.path.abspath(__file__)) + "/../html_inputs/" + filename

        # Insert data
        data = {
                "operations":[
                    {
                        "mode":"insert",
                        "report":{
                            "name":filename,
                            "group":"report_group",
                            "group_description":"Group of reports for testing",
                            "path":file_path,
                            "compress":"true",
                            "generation_mode":"MANUAL",
                            "validity_start":"2018-06-05T02:07:03",
                            "validity_stop":"2018-06-05T08:07:36",
                            "triggering_time":"2018-07-05T02:07:03",
                            "generation_start":"2018-07-05T02:07:10",
                            "generation_stop":"2018-07-05T02:15:10",
                            "generator":"report_generator",
                            "generator_version":"1.0",
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
                                    },
                                    {
                                        "type":"double",
                                        "name":"DOUBLE",
                                        "value":"0.9"
                                    },
                                    {
                                        "type":"timestamp",
                                        "name":"TIMESTAMP",
                                        "value":"20180712T00:00:00"
                                    },
                                    {
                                        "type":"geometry",
                                        "name":"GEOMETRY",
                                        "value":"29.012974905944 -118.33483458667 28.8650301641571 -118.372028380632 28.7171766138274 -118.409121707686 28.5693112139334 -118.44612300623 28.4213994944367 -118.483058731035 28.2734085660472 -118.519970531113 28.1253606038163 -118.556849863134 27.9772541759126 -118.593690316835 27.8291247153939 -118.630472520505 27.7544158362332 -118.64900551674 27.7282373644786 -118.48032600682 27.7015162098732 -118.314168792268 27.6742039940042 -118.150246300849 27.6462511775992 -117.98827485961 27.6176070520608 -117.827974178264 27.5882197156561 -117.669066835177 27.5580360448116 -117.511277813618 27.5270016492436 -117.354334035359 27.4950608291016 -117.197963963877 27.4621565093409 -117.041897175848 27.4282301711374 -116.885863967864 27.3932217651372 -116.729594956238 27.3570696128269 -116.572820673713 27.3197103000253 -116.415271199941 27.2810785491022 -116.256675748617 27.241107085821 -116.09676229722 27.1997272484913 -115.935260563566 27.1524952198729 -115.755436839005 27.2270348347386 -115.734960009089 27.3748346522356 -115.694299254844 27.5226008861849 -115.653563616829 27.6702779354428 -115.612760542177 27.8178690071708 -115.571901649363 27.9653506439026 -115.531000691074 28.1127600020619 -115.490011752733 28.2601469756437 -115.44890306179 28.4076546372628 -115.407649898021 28.455192866856 -115.589486631416 28.4968374106496 -115.752807970928 28.5370603096399 -115.91452902381 28.575931293904 -116.074924211465 28.6135193777855 -116.234273707691 28.6498895688451 -116.392847129762 28.6851057860975 -116.550917254638 28.7192301322012 -116.708756374584 28.752323018501 -116.866636764481 28.7844432583843 -117.024831047231 28.8156481533955 -117.183612605748 28.8459935678779 -117.343255995623 28.8755339855462 -117.504037348554 28.9043225601122 -117.666234808407 28.9324111491586 -117.830128960026 28.9598503481156 -117.996003330616 28.9866878706574 -118.164136222141 29.012974905944 -118.33483458667"
                                    }
                                ]
                            }
                            ]
                        },
                        "alerts":[
                            {
                            "message":"Alert message",
                            "generator":"test",
                            "notification_time":"2018-06-05T08:07:36",
                            "alert_cnf":{
                                "name":"alert_name5",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_group4"
                            }
                            }
                        ]
                    }
                ]
                }

        # Check data is correctly inserted
        self.engine_rboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_rboa.treat_data()[0]["status"]
        
        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/general-view-alerts/")

        functions.query(self.driver, wait, start = "2018-06-05T08:07:36", stop = "2018-06-05T08:07:36", limit = "1")

        # Check number of widgets in summary
        summary_section = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts")))
        assert summary_section and len(summary_section.find_elements_by_xpath("div")) == 5

        # Check summary number sources alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-sources")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number annotations alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-annotations")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number events alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-events")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number reports alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-reports")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number ers alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-ers")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        functions.click(self.driver.find_element_by_xpath("//*[contains(text(), 'Next >>')]"))
        
        # Use staleness_of to avoid StaleElement Exception
        wait.until(EC.staleness_of(summary_section))

        # Check number of widgets in summary
        summary_section = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts")))
        assert summary_section and len(summary_section.find_elements_by_xpath("div")) == 5

        # Check summary number sources alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-sources")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Check summary number annotations alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-annotations")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Check summary number events alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-events")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Check summary number reports alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-reports")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Check summary number ers alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-ers")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Use presence_of_element_located to avoid StaleElement Exception
        functions.click(self.driver.find_element_by_xpath("//*[contains(text(), '<< Show all >>')]"))

        # Use staleness_of to avoid StaleElement Exception
        wait.until(EC.staleness_of(summary_section))
        
        # Check number of widgets in summary
        summary_section = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts")))
        assert summary_section and len(summary_section.find_elements_by_xpath("div")) == 5

        # Check summary number sources alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-sources")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number annotations alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-annotations")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number events alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-events")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number reports alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-reports")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number ers alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-ers")))

        assert summary_number_alerts and summary_number_alerts.text == "2"

    def test_pagination_reports(self):

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
                        ],
                        "events":[
                            {
                            "explicit_reference":"ER1",
                            "gauge":{
                                "name":"GAUGE_NAME",
                                "system":"GAUGE_SYSTEM",
                                "insertion_type":"SIMPLE_UPDATE"
                            },
                            "start":"2018-06-05T02:07:03",
                            "stop":"2018-06-05T08:07:36",
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
                                        "name":"alert_name2",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group1"
                                    }
                                }
                            ]
                            }
                        ],
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
                                        "name":"alert_name3",
                                        "severity":"critical",
                                        "description":"Alert description",
                                        "group":"alert_group2"
                                    }
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
                                "name":"alert_name4",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_group3"
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

        filename = "report.html"
        file_path = os.path.dirname(os.path.abspath(__file__)) + "/../html_inputs/" + filename

        # Insert data
        data = {
                "operations":[
                    {
                        "mode":"insert",
                        "report":{
                            "name":filename,
                            "group":"report_group",
                            "group_description":"Group of reports for testing",
                            "path":file_path,
                            "compress":"true",
                            "generation_mode":"MANUAL",
                            "validity_start":"2018-06-05T02:07:03",
                            "validity_stop":"2018-06-05T08:07:36",
                            "triggering_time":"2018-07-05T02:07:03",
                            "generation_start":"2018-07-05T02:07:10",
                            "generation_stop":"2018-07-05T02:15:10",
                            "generator":"report_generator",
                            "generator_version":"1.0",
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
                                    },
                                    {
                                        "type":"double",
                                        "name":"DOUBLE",
                                        "value":"0.9"
                                    },
                                    {
                                        "type":"timestamp",
                                        "name":"TIMESTAMP",
                                        "value":"20180712T00:00:00"
                                    },
                                    {
                                        "type":"geometry",
                                        "name":"GEOMETRY",
                                        "value":"29.012974905944 -118.33483458667 28.8650301641571 -118.372028380632 28.7171766138274 -118.409121707686 28.5693112139334 -118.44612300623 28.4213994944367 -118.483058731035 28.2734085660472 -118.519970531113 28.1253606038163 -118.556849863134 27.9772541759126 -118.593690316835 27.8291247153939 -118.630472520505 27.7544158362332 -118.64900551674 27.7282373644786 -118.48032600682 27.7015162098732 -118.314168792268 27.6742039940042 -118.150246300849 27.6462511775992 -117.98827485961 27.6176070520608 -117.827974178264 27.5882197156561 -117.669066835177 27.5580360448116 -117.511277813618 27.5270016492436 -117.354334035359 27.4950608291016 -117.197963963877 27.4621565093409 -117.041897175848 27.4282301711374 -116.885863967864 27.3932217651372 -116.729594956238 27.3570696128269 -116.572820673713 27.3197103000253 -116.415271199941 27.2810785491022 -116.256675748617 27.241107085821 -116.09676229722 27.1997272484913 -115.935260563566 27.1524952198729 -115.755436839005 27.2270348347386 -115.734960009089 27.3748346522356 -115.694299254844 27.5226008861849 -115.653563616829 27.6702779354428 -115.612760542177 27.8178690071708 -115.571901649363 27.9653506439026 -115.531000691074 28.1127600020619 -115.490011752733 28.2601469756437 -115.44890306179 28.4076546372628 -115.407649898021 28.455192866856 -115.589486631416 28.4968374106496 -115.752807970928 28.5370603096399 -115.91452902381 28.575931293904 -116.074924211465 28.6135193777855 -116.234273707691 28.6498895688451 -116.392847129762 28.6851057860975 -116.550917254638 28.7192301322012 -116.708756374584 28.752323018501 -116.866636764481 28.7844432583843 -117.024831047231 28.8156481533955 -117.183612605748 28.8459935678779 -117.343255995623 28.8755339855462 -117.504037348554 28.9043225601122 -117.666234808407 28.9324111491586 -117.830128960026 28.9598503481156 -117.996003330616 28.9866878706574 -118.164136222141 29.012974905944 -118.33483458667"
                                    }
                                ]
                            }
                            ]
                        },
                        "alerts":[
                            {
                            "message":"Alert message",
                            "generator":"test",
                            "notification_time":"2018-06-05T08:07:36",
                            "alert_cnf":{
                                "name":"alert_name5",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_group4"
                            }
                            },
                            {
                            "message":"Alert message",
                            "generator":"test",
                            "notification_time":"2018-06-05T08:07:36",
                            "alert_cnf":{
                                "name":"alert_name4",
                                "severity":"critical",
                                "description":"Alert description",
                                "group":"alert_group3"
                            }
                            }
                        ]
                    }
                ]
                }

        # Check data is correctly inserted
        self.engine_rboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_rboa.treat_data()[0]["status"]
        
        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/general-view-alerts/")

        functions.query(self.driver, wait, start = "2018-06-05T08:07:36", stop = "2018-06-05T08:07:36", limit = "1")

        # Check number of widgets in summary
        summary_section = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts")))
        assert summary_section and len(summary_section.find_elements_by_xpath("div")) == 5

        # Check summary number sources alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-sources")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number annotations alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-annotations")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number events alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-events")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number reports alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-reports")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number ers alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-ers")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        functions.click(self.driver.find_element_by_xpath("//*[contains(text(), 'Next >>')]"))
        
        # Use staleness_of to avoid StaleElement Exception
        wait.until(EC.staleness_of(summary_section))

        # Check number of widgets in summary
        summary_section = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts")))
        assert summary_section and len(summary_section.find_elements_by_xpath("div")) == 5

        # Check summary number sources alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-sources")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Check summary number annotations alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-annotations")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Check summary number events alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-events")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Check summary number reports alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-reports")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number ers alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-no-ers")))

        assert summary_number_alerts and summary_number_alerts.text == "0"

        # Use presence_of_element_located to avoid StaleElement Exception
        functions.click(self.driver.find_element_by_xpath("//*[contains(text(), '<< Show all >>')]"))

        # Use staleness_of to avoid StaleElement Exception
        wait.until(EC.staleness_of(summary_section))
        
        # Check number of widgets in summary
        summary_section = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts")))
        assert summary_section and len(summary_section.find_elements_by_xpath("div")) == 5

        # Check summary number sources alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-sources")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number annotations alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-annotations")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number events alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-events")))

        assert summary_number_alerts and summary_number_alerts.text == "1"

        # Check summary number reports alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-reports")))

        assert summary_number_alerts and summary_number_alerts.text == "2"

        # Check summary number ers alerts
        summary_number_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-general-view-alerts-ers")))

        assert summary_number_alerts and summary_number_alerts.text == "1"