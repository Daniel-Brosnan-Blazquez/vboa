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
import rboa.engine.engine as rboa_engine
from rboa.engine.engine import Engine as EngineReport

class TestReportAlertsTab(unittest.TestCase):

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

    def test_report_alerts_no_data(self):
        
        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'report-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

    def test_report_alerts_query_no_filter_with_timeline(self):

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

        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"report-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        report_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(report_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 3

        # Check whether the timeline is displayed
        timeline_section = self.driver.find_element_by_id("alerts-nav-timeline")

        condition = timeline_section.is_displayed()
        assert condition is True

        # Check generated content for widgets
        kwargs ={}
        kwargs["order_by"] = {"field": "notification_time", "descending": False}
        report_alerts = self.query_eboa.get_report_alerts(kwargs)

        assert len(report_alerts) == 3

        alerts = [
            {
                "alert_uuid": "<a href='/rboa_nav/query-alert/" + str(report_alerts[0].report_alert_uuid) + "'>" + str(report_alerts[0].report_alert_uuid) + "</a>",
                "description": "Alert description",
                "entity": "Report",
                "entity_uuid": "<a href='/rboa_nav/query-report/" + str(report_alerts[0].report_uuid) + "'>" + str(report_alerts[0].report_uuid) + "</a>",
                "generator": "test",
                "group": "REPORTS;alert_group",
                "group_alert": "alert_group",
                "id": str(report_alerts[0].report_alert_uuid),
                "ingestion_time": report_alerts[0].ingestion_time.isoformat(),
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
                "alert_uuid": "<a href='/rboa_nav/query-alert/" + str(report_alerts[1].report_alert_uuid) + "'>" + str(report_alerts[1].report_alert_uuid) + "</a>",
                "description": "Alert description",
                "entity": "Report",
                "entity_uuid": "<a href='/rboa_nav/query-report/" + str(report_alerts[1].report_uuid) + "'>" + str(report_alerts[1].report_uuid) + "</a>",
                "generator": "test",
                "group": "REPORTS;alert_group",
                "group_alert": "alert_group",
                "id": str(report_alerts[1].report_alert_uuid),
                "ingestion_time": report_alerts[1].ingestion_time.isoformat(),
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
                "alert_uuid": "<a href='/rboa_nav/query-alert/" + str(report_alerts[2].report_alert_uuid) + "'>" + str(report_alerts[2].report_alert_uuid) + "</a>",
                "description": "Alert description",
                "entity": "Report",
                "entity_uuid": "<a href='/rboa_nav/query-report/" + str(report_alerts[2].report_uuid) + "'>" + str(report_alerts[2].report_uuid) + "</a>",
                "generator": "test",
                "group": "REPORTS;alert_group",
                "group_alert": "alert_group",
                "id": str(report_alerts[2].report_alert_uuid),
                "ingestion_time": report_alerts[2].ingestion_time.isoformat(),
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
        functions.assert_equal_list_dictionaries(returned_alerts, alerts)

        # Check report alerts table
        report_alerts_table = self.driver.find_element_by_id("alerts-table")

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

        assert ingestion_time.text == report_alerts[0].ingestion_time.isoformat()

        alert_uuid = report_alerts_table.find_element_by_xpath("tbody/tr[1]/td[14]")

        assert alert_uuid.text == str(report_alerts[0].report_alert_uuid)

        report_uuid = report_alerts_table.find_element_by_xpath("tbody/tr[1]/td[15]")

        assert report_uuid.text == str(report_alerts[0].report_uuid)

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

        assert ingestion_time.text == report_alerts[1].ingestion_time.isoformat()

        alert_uuid = report_alerts_table.find_element_by_xpath("tbody/tr[2]/td[14]")

        assert alert_uuid.text == str(report_alerts[1].report_alert_uuid)

        report_uuid = report_alerts_table.find_element_by_xpath("tbody/tr[2]/td[15]")

        assert report_uuid.text == str(report_alerts[1].report_uuid)

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

        assert ingestion_time.text == report_alerts[2].ingestion_time.isoformat()

        alert_uuid = report_alerts_table.find_element_by_xpath("tbody/tr[3]/td[14]")

        assert alert_uuid.text == str(report_alerts[2].report_alert_uuid)

        report_uuid = report_alerts_table.find_element_by_xpath("tbody/tr[3]/td[15]")

        assert report_uuid.text == str(report_alerts[2].report_uuid)

    def test_report_alerts_query_report_filter(self):

        filename = "report.html"
        file_path = os.path.dirname(os.path.abspath(__file__)) + "/../html_inputs/" + filename

        filename1 = "report_1.html"
        file_path1 = os.path.dirname(os.path.abspath(__file__)) + "/../html_inputs/" + filename

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
                            "notification_time":"2018-06-05T08:07:37",
                            "alert_cnf":{
                                "name":"alert_name2",
                                "severity":"warning",
                                "description":"Alert description",
                                "group":"alert_group"
                            }
                            }
                        ]
                    },
                    {
                        "mode":"insert",
                        "report":{
                            "name":filename1,
                            "group":"report_group",
                            "group_description":"Group of reports for testing",
                            "path":file_path1,
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
                            }
                        ]
                    }
                ]
                }

        # Check data is correctly inserted
        self.engine_rboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_rboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"report-alerts-submit-button")))
        functions.click(submit_button)

        ## Like ##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")

        # Fill the explicit_ref_like input
        input_element = self.driver.find_element_by_id("reports-report-name-text")
        input_element.send_keys("report.html")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"report-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        report_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(report_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not like ##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")

        # Fill the explicit_ref_like input
        input_element = self.driver.find_element_by_id("reports-report-name-text")
        input_element.send_keys("report.html")

        menu = Select(self.driver.find_element_by_id("reports-report-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"report-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        report_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(report_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## In ##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")

        # Fill the explicit_ref_in input
        input_element = self.driver.find_element_by_id("reports-report-names-in-text")
        functions.click(input_element)

        input_element.send_keys("report.html")
        input_element.send_keys(Keys.LEFT_SHIFT)
        input_element.clear()
        input_element.send_keys("report_1.html")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("reports-report-names-in-select"))
        options.select_by_visible_text("report.html")
        options.select_by_visible_text("report_1.html")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"report-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        report_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(report_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not in ##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")

        # Fill the explicit_ref_in input
        input_element = self.driver.find_element_by_id("reports-report-names-in-text")
        functions.click(input_element)

        input_element.send_keys("report_1.html")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("reports-report-names-in-select"))
        options.select_by_visible_text("report_1.html")

        notInButton = self.driver.find_element_by_id("reports-report-names-in-checkbox")        
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        #end if

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"report-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generate
        report_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(report_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

    def test_report_alerts_query_generator_filter(self):

        filename = "report.html"
        file_path = os.path.dirname(os.path.abspath(__file__)) + "/../html_inputs/" + filename

        filename1 = "report_1.html"
        file_path1 = os.path.dirname(os.path.abspath(__file__)) + "/../html_inputs/" + filename

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
                            "notification_time":"2018-06-05T08:07:37",
                            "alert_cnf":{
                                "name":"alert_name2",
                                "severity":"warning",
                                "description":"Alert description",
                                "group":"alert_group"
                            }
                            }
                        ]
                    },
                    {
                        "mode":"insert",
                        "report":{
                            "name":filename1,
                            "group":"report_group1",
                            "group_description":"Group of reports for testing",
                            "path":file_path1,
                            "compress":"true",
                            "generation_mode":"MANUAL",
                            "validity_start":"2018-06-05T02:07:03",
                            "validity_stop":"2018-06-05T08:07:36",
                            "triggering_time":"2018-07-06T02:07:03",
                            "generation_start":"2018-07-05T02:07:10",
                            "generation_stop":"2018-07-05T02:15:10",
                            "generator":"report_generator1",
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
                            }
                        ]
                    }
                ]
                }

        # Check data is correctly inserted
        self.engine_rboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_rboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"report-alerts-submit-button")))
        functions.click(submit_button)

        ## Like ##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")

        # Fill the explicit_ref_like input
        input_element = self.driver.find_element_by_id("reports-generator-text")
        input_element.send_keys("report_generator")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"report-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        report_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(report_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not like ##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")

        # Fill the explicit_ref_like input
        input_element = self.driver.find_element_by_id("reports-generator-text")
        input_element.send_keys("report_generator")

        menu = Select(self.driver.find_element_by_id("reports-generator-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"report-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        report_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(report_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## In ##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")

        # Fill the explicit_ref_in input
        input_element = self.driver.find_element_by_id("reports-generators-in-text")
        functions.click(input_element)

        input_element.send_keys("report_generator")
        input_element.send_keys(Keys.LEFT_SHIFT)
        input_element.clear()
        input_element.send_keys("report_generator1")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("reports-generators-in-select"))
        options.select_by_visible_text("report_generator")
        options.select_by_visible_text("report_generator1")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"report-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        report_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(report_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not in ##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")

        # Fill the explicit_ref_in input
        input_element = self.driver.find_element_by_id("reports-generators-in-text")
        functions.click(input_element)

        input_element.send_keys("report_generator")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("reports-generators-in-select"))
        options.select_by_visible_text("report_generator1")

        notInButton = self.driver.find_element_by_id("reports-generators-in-checkbox")        
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        #end if

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"report-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generate
        report_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(report_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

    def test_report_alerts_query_groups_filter(self):

        filename = "report.html"
        file_path = os.path.dirname(os.path.abspath(__file__)) + "/../html_inputs/" + filename

        filename1 = "report_1.html"
        file_path1 = os.path.dirname(os.path.abspath(__file__)) + "/../html_inputs/" + filename

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
                            "notification_time":"2018-06-05T08:07:37",
                            "alert_cnf":{
                                "name":"alert_name2",
                                "severity":"warning",
                                "description":"Alert description",
                                "group":"alert_group"
                            }
                            }
                        ]
                    },
                    {
                        "mode":"insert",
                        "report":{
                            "name":filename1,
                            "group":"report_group1",
                            "group_description":"Group of reports for testing",
                            "path":file_path1,
                            "compress":"true",
                            "generation_mode":"MANUAL",
                            "validity_start":"2018-06-05T02:07:03",
                            "validity_stop":"2018-06-05T08:07:36",
                            "triggering_time":"2018-07-06T02:07:03",
                            "generation_start":"2018-07-05T02:07:10",
                            "generation_stop":"2018-07-05T02:15:10",
                            "generator":"report_generator1",
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
                            }
                        ]
                    }
                ]
                }

        # Check data is correctly inserted
        self.engine_rboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_rboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"report-alerts-submit-button")))
        functions.click(submit_button)

        ## Like ##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")

        # Fill the explicit_ref_like input
        input_element = self.driver.find_element_by_id("reports-report-group-text")
        input_element.send_keys("report_group")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"report-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        report_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(report_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not like ##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")

        # Fill the explicit_ref_like input
        input_element = self.driver.find_element_by_id("reports-report-group-text")
        input_element.send_keys("report_group")

        menu = Select(self.driver.find_element_by_id("reports-report-group-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"report-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        report_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(report_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## In ##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")

        # Fill the explicit_ref_in input
        input_element = self.driver.find_element_by_id("reports-report-groups-in-text")
        functions.click(input_element)

        input_element.send_keys("report_group")
        input_element.send_keys(Keys.LEFT_SHIFT)
        input_element.clear()
        input_element.send_keys("report_group1")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("reports-report-groups-in-select"))
        options.select_by_visible_text("report_group")
        options.select_by_visible_text("report_group1")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"report-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generated
        report_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(report_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not in ##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")

        # Fill the explicit_ref_in input
        input_element = self.driver.find_element_by_id("reports-report-groups-in-text")
        functions.click(input_element)

        input_element.send_keys("report_group")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("reports-report-groups-in-select"))
        options.select_by_visible_text("report_group1")

        notInButton = self.driver.find_element_by_id("reports-report-groups-in-checkbox")        
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        #end if

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"report-alerts-submit-button")))
        functions.click(submit_button)

        # Check table generate
        report_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(report_alerts_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

    def test_report_alerts_query_validity_period(self):

        filename = "report.html"
        file_path = os.path.dirname(os.path.abspath(__file__)) + "/../html_inputs/" + filename

        filename1 = "report_1.html"
        file_path1 = os.path.dirname(os.path.abspath(__file__)) + "/../html_inputs/" + filename

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
                            "validity_start":"2018-06-05T02:00:00",
                            "validity_stop":"2018-06-05T03:00:00",
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
                            "notification_time":"2018-06-05T08:07:37",
                            "alert_cnf":{
                                "name":"alert_name2",
                                "severity":"warning",
                                "description":"Alert description",
                                "group":"alert_group"
                            }
                            }
                        ]
                    },
                    {
                        "mode":"insert",
                        "report":{
                            "name":filename1,
                            "group":"report_group1",
                            "group_description":"Group of reports for testing",
                            "path":file_path1,
                            "compress":"true",
                            "generation_mode":"MANUAL",
                            "validity_start":"2018-06-05T04:00:00",
                            "validity_stop":"2018-06-05T05:00:00",
                            "triggering_time":"2018-07-06T02:07:03",
                            "generation_start":"2018-07-05T02:07:10",
                            "generation_stop":"2018-07-05T02:15:10",
                            "generator":"report_generator1",
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
                            }
                        ]
                    }
                ]
                }

        # Check data is correctly inserted
        self.engine_rboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_rboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")
        
        functions.fill_validity_period(self.driver, wait, "reports", 1,  start_value = "2018-06-05T02:00:00", start_operator = "==", end_value = "2018-06-05T03:00:00", end_operator = "==")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'report-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        report_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(report_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(report_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## >= ## Only Start##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")

        functions.fill_validity_period(self.driver, wait, "reports", 1,  start_value = "2018-06-05T02:00:00", start_operator = ">=")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'report-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        report_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(report_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(report_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        ## != ## Only End##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")

        functions.fill_validity_period(self.driver, wait, "reports", 1,  end_value = "2018-06-05T04:00:00", end_operator = "!=")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'report-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        report_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(report_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(report_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        ## > ## Only Start## < ## Only Start##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")
        
        functions.fill_validity_period(self.driver, wait, "reports", 1, start_value = "2018-06-05T01:00:00", start_operator = ">")
        functions.click(self.driver.find_element_by_id("reports-add-validity-start-validity-stop"))
        functions.fill_validity_period(self.driver, wait, "reports", 2, start_value = "2018-06-05T03:00:00", start_operator = "<")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'report-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        report_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(report_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(report_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## <= ## Start## > ## End## != ## Start## >= ## End##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")

        functions.fill_validity_period(self.driver, wait, "reports", 1, start_value = "2018-06-05T03:00:00", start_operator = "<=", end_value = "2018-06-05T02:30:00", end_operator = ">")
        functions.click(self.driver.find_element_by_id("reports-add-validity-start-validity-stop"))
        functions.fill_validity_period(self.driver, wait, "reports", 2, start_value = "2018-06-05T04:00:00", start_operator = "!=", end_value = "2018-06-05T03:00:00", end_operator = ">=")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'report-alerts-submit-button')))
        functions.click(submitButton)

        # Check table generated
        report_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(report_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(report_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

    def test_report_alerts_query_report_validity_duration(self):

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
                            "validity_start":"2018-06-05T02:00:00",
                            "validity_stop":"2018-06-07T08:00:00",
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
                            }
                        ]
                    }
                ]
                }

        # Check data is correctly inserted
        self.engine_rboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_rboa.treat_data()[0]["status"]

        reports = self.query_eboa.get_reports()
        validity_duration_in_days = str((reports[0].validity_stop - reports[0].validity_start).total_seconds()/86400)

        wait = WebDriverWait(self.driver,5)

        ## == ##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'report-alerts-submit-button')))

        functions.fill_any_duration(self.driver, wait, "reports", "report-validity", validity_duration_in_days, "==", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        report_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(report_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(report_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## > ##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'report-alerts-submit-button')))

        functions.fill_any_duration(self.driver, wait, "reports", "report-validity", validity_duration_in_days, ">", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## >= ##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'report-alerts-submit-button')))
    
        functions.fill_any_duration(self.driver, wait, "reports", "report-validity", validity_duration_in_days, ">=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        report_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(report_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(report_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## < ##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'report-alerts-submit-button')))

        functions.fill_any_duration(self.driver, wait, "reports", "report-validity", validity_duration_in_days, "<", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## <= ##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'report-alerts-submit-button')))

        functions.fill_any_duration(self.driver, wait, "reports", "report-validity", validity_duration_in_days, "<=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        report_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(report_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(report_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'report-alerts-submit-button')))

        functions.fill_any_duration(self.driver, wait, "reports", "report-validity", validity_duration_in_days, "!=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

    def test_report_alerts_query_triggering_time(self):

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
                            "validity_start":"2018-06-05T02:00:00",
                            "validity_stop":"2018-06-07T08:00:00",
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
                            }
                        ]
                    }
                ]
                }

        # Check data is correctly inserted
        self.engine_rboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_rboa.treat_data()[0]["status"]

        triggering_time = self.query_eboa.get_reports()[0].triggering_time.isoformat()

        wait = WebDriverWait(self.driver,5)

        ## == ##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'report-alerts-submit-button')))

        functions.fill_any_time(self.driver, wait, "reports", "triggering", triggering_time, "==", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        report_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(report_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(report_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## > ##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'report-alerts-submit-button')))

        functions.fill_any_time(self.driver, wait, "reports", "triggering", triggering_time, ">", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## >= ##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'report-alerts-submit-button')))
    
        functions.fill_any_time(self.driver, wait, "reports", "triggering", triggering_time, ">=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        report_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(report_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(report_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## < ##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'report-alerts-submit-button')))

        functions.fill_any_time(self.driver, wait, "reports", "triggering", triggering_time, "<", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data

        ## <= ##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'report-alerts-submit-button')))

        functions.fill_any_time(self.driver, wait, "reports", "triggering", triggering_time, "<=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        report_alerts_table = wait.until(EC.visibility_of_element_located((By.ID,"alerts-table")))
        number_of_elements = len(report_alerts_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(report_alerts_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'report-alerts-submit-button')))

        functions.fill_any_time(self.driver, wait, "reports", "triggering", triggering_time, "!=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"alerts-nav-no-data")))

        assert no_data