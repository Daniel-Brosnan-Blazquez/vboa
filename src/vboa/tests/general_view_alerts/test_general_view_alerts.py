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
        data = {"operations": [{
            "mode": "insert",
            "dim_signature": {"name": "dim_signature",
                              "exec": "exec",
                              "version": "1.0"},
            "source": {"name": "source.json",
                       "reception_time": "2018-06-06T13:33:29",
                       "generation_time": "2018-07-05T02:07:03",
                       "validity_start": "2018-06-05T02:07:03",
                       "validity_stop": "2018-06-05T08:07:36"},
            "alerts": [{
                "message": "Alert message",
                "generator": "test",
                "notification_time": "2018-06-05T08:07:36",
                "alert_cnf": {
                    "name": "alert_name1",
                    "severity": "critical",
                    "description": "Alert description",
                    "group": "alert_group"
                },
                "entity": {
                    "reference_mode": "by_ref",
                    "reference": "source.json",
                    "type": "source"
                }
            },{
                "message": "Alert message",
                "generator": "test1",
                "notification_time": "2019-06-06T08:07:36",
                "alert_cnf": {
                    "name": "alert_name2",
                    "severity": "critical",
                    "description": "Alert description",
                    "group": "alert_group"
                },
                "entity": {
                    "reference_mode": "by_ref",
                    "reference": "source.json",
                    "type": "source"
                }
            }]
        }]
        }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]
        
        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/general_view_alerts/")

        """ # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        # Click on query button
        functions.click(submit_button) """

    def test_events_alerts_query_no_filter(self):

        # Insert data
        data = {"operations": [{
            "mode": "insert",
            "dim_signature": {"name": "dim_signature",
                              "exec": "exec",
                              "version": "1.0"},
            "source": {"name": "source.json",
                       "reception_time": "2018-06-06T13:33:29",
                       "generation_time": "2018-07-05T02:07:03",
                       "validity_start": "2018-06-05T02:07:03",
                       "validity_stop": "2019-06-05T08:07:36",
                       "priority": 30},
            "events": [{
                "explicit_reference": "ER1",
                "gauge": {"name": "GAUGE_NAME",
                          "system": "GAUGE_SYSTEM",
                          "insertion_type": "SIMPLE_UPDATE"},
                "start": "2018-06-05T02:07:03",
                "stop": "2018-06-05T08:07:36",
                "values": [{"name": "VALUES",
                            "type": "object",
                            "values": [
                                {"type": "text",
                                 "name": "TEXT",
                                 "value": "TEXT"},
                                {"type": "boolean",
                                 "name": "BOOLEAN",
                                 "value": "true"}]
                            }],
                "alerts": [{
                    "message": "Alert message",
                    "generator": "test",
                    "notification_time": "2018-06-05T08:07:36",
                    "alert_cnf": {
                        "name": "alert_name1",
                        "severity": "critical",
                        "description": "Alert description",
                        "group": "alert_group"
                    }},
                           {
                               "message": "Alert message",
                               "generator": "test2",
                               "notification_time": "2019-06-05T08:07:36",
                               "alert_cnf": {
                                   "name": "alert_name2",
                                   "severity": "major",
                                   "description": "Alert description",
                                   "group": "alert_group2"
                               }}]
            },
                       {
                           "explicit_reference": "ER2",
                           "gauge": {"name": "GAUGE_NAME2",
                                     "system": "GAUGE_SYSTEM2",
                                     "insertion_type": "SIMPLE_UPDATE"},
                           "start": "2019-06-05T02:07:03",
                           "stop": "2019-06-05T08:07:36",
                           "alerts": [{
                               "message": "Alert message",
                               "generator": "test",
                               "notification_time": "2018-06-05T08:07:36",
                               "alert_cnf": {
                                   "name": "alert_name2",
                                   "severity": "critical",
                                   "description": "Alert description",
                                   "group": "alert_group"
                               }},
                                      {
                                          "message": "Alert message",
                                          "generator": "test2",
                                          "notification_time": "2019-06-05T08:07:36",
                                          "alert_cnf": {
                                              "name": "alert_name3",
                                              "severity": "major",
                                              "description": "Alert description",
                                              "group": "alert_group2"
                                          }}]
                       }]
        }]
                }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]
        
        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/general_view_alerts/")

        """ # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        # Click on query button
        functions.click(submit_button) """

    def test_annotations_alerts_query_no_filter(self):

        # Insert data
        data = {"operations": [{
            "mode": "insert",
            "dim_signature": {"name": "dim_signature",
                              "exec": "exec",
                              "version": "1.0"},
            "source": {"name": "source.json",
                       "reception_time": "2018-06-06T13:33:29",
                       "generation_time": "2018-07-05T02:07:03",
                       "validity_start": "2018-06-05T02:07:03",
                       "validity_stop": "2019-06-05T08:07:36",
                       "priority": 30},
            "annotations": [{
                "explicit_reference": "ER1",
                "annotation_cnf": {"name": "NAME",
                                   "system": "SYSTEM",
                                   "insertion_type": "SIMPLE_UPDATE"},
                "values": [{"name": "VALUES",
                            "type": "object",
                            "values": [
                                {"type": "text",
                                 "name": "TEXT",
                                 "value": "TEXT"},
                                {"type": "boolean",
                                 "name": "BOOLEAN",
                                 "value": "true"}]
                            }],
                "alerts": [{
                    "message": "Alert message",
                    "generator": "test",
                    "notification_time": "2018-06-05T08:07:36",
                    "alert_cnf": {
                        "name": "alert_name1",
                        "severity": "critical",
                        "description": "Alert description",
                        "group": "alert_group"
                    }},
                           {
                               "message": "Alert message",
                               "generator": "test2",
                               "notification_time": "2019-06-05T08:07:36",
                               "alert_cnf": {
                                   "name": "alert_name2",
                                   "severity": "major",
                                   "description": "Alert description",
                                   "group": "alert_group2"
                               }}]
            },
                       {
                           "explicit_reference": "ER1",
                           "annotation_cnf": {"name": "NAME",
                                              "system": "SYSTEM",
                                              "insertion_type": "SIMPLE_UPDATE"},
                           "alerts": [{
                               "message": "Alert message",
                               "generator": "test",
                               "notification_time": "2018-06-05T08:07:36",
                               "alert_cnf": {
                                   "name": "alert_name1",
                                   "severity": "critical",
                                   "description": "Alert description",
                                   "group": "alert_group"
                               }},
                                      {
                                          "message": "Alert message",
                                          "generator": "test2",
                                          "notification_time": "2019-06-05T08:07:36",
                                          "alert_cnf": {
                                              "name": "alert_name2",
                                              "severity": "major",
                                              "description": "Alert description",
                                              "group": "alert_group2"
                                          }}]
                       }]
        }]
                }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]
        
        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/general_view_alerts/")

        """ # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        # Click on query button
        functions.click(submit_button) """

    def test_explicit_refs_alerts_query_no_filter(self):

        # Insert data
        data = {"operations": [{
            "mode": "insert",
            "dim_signature": {"name": "dim_signature",
                              "exec": "exec",
                              "version": "1.0"},
            "source": {"name": "source.json",
                       "reception_time": "2018-06-06T13:33:29",
                       "generation_time": "2018-07-05T02:07:03",
                       "validity_start": "2018-06-05T02:07:03",
                       "validity_stop": "2019-06-05T08:07:36",
                       "priority": 30},
            "explicit_references": [{
                "name": "ER1",
                "group": "ER_GROUP",
                "alerts": [{
                    "message": "Alert message",
                    "generator": "test",
                    "notification_time": "2020-06-05T08:07:36",
                    "alert_cnf": {
                        "name": "alert_name1",
                        "severity": "critical",
                        "description": "Alert description",
                        "group": "alert_group"
                    }},
                           {
                               "message": "Alert message",
                               "generator": "test2",
                               "notification_time": "2019-06-05T08:07:36",
                               "alert_cnf": {
                                   "name": "alert_name2",
                                   "severity": "major",
                                   "description": "Alert description",
                                   "group": "alert_group2"
                               }}]
            }]
        }]
                }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]
        
        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/general_view_alerts/")

        """ # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        # Click on query button
        functions.click(submit_button) """

    def test_reports_alerts_query_no_filter(self):

        filename = "report.html"
        file_path = os.path.dirname(os.path.abspath(__file__)) + "/html_inputs/" + filename

        # Insert data
        data = {"operations": [{
            "mode": "insert",
            "report": {"name": filename,
                       "group": "report_group",
                       "group_description": "Group of reports for testing",
                       "path": file_path,
                       "compress": "true",
                       "generation_mode": "MANUAL",
                       "validity_start": "2018-06-05T02:07:03",
                       "validity_stop": "2018-06-05T08:07:36",
                       "triggering_time": "2018-07-05T02:07:03",
                       "generation_start": "2018-07-05T02:07:10",
                       "generation_stop": "2018-07-05T02:15:10",
                       "generator": "report_generator",
                       "generator_version": "1.0",
                       "values": [{"name": "VALUES",
                                   "type": "object",
                                   "values": [
                                       {"type": "text",
                                        "name": "TEXT",
                                        "value": "TEXT"},
                                       {"type": "boolean",
                                        "name": "BOOLEAN",
                                        "value": "true"},
                                       {"type": "double",
                                        "name": "DOUBLE",
                                        "value": "0.9"},
                                       {"type": "timestamp",
                                        "name": "TIMESTAMP",
                                        "value": "20180712T00:00:00"},
                                       {"type": "geometry",
                                        "name": "GEOMETRY",
                                        "value": "29.012974905944 -118.33483458667 28.8650301641571 -118.372028380632 28.7171766138274 -118.409121707686 28.5693112139334 -118.44612300623 28.4213994944367 -118.483058731035 28.2734085660472 -118.519970531113 28.1253606038163 -118.556849863134 27.9772541759126 -118.593690316835 27.8291247153939 -118.630472520505 27.7544158362332 -118.64900551674 27.7282373644786 -118.48032600682 27.7015162098732 -118.314168792268 27.6742039940042 -118.150246300849 27.6462511775992 -117.98827485961 27.6176070520608 -117.827974178264 27.5882197156561 -117.669066835177 27.5580360448116 -117.511277813618 27.5270016492436 -117.354334035359 27.4950608291016 -117.197963963877 27.4621565093409 -117.041897175848 27.4282301711374 -116.885863967864 27.3932217651372 -116.729594956238 27.3570696128269 -116.572820673713 27.3197103000253 -116.415271199941 27.2810785491022 -116.256675748617 27.241107085821 -116.09676229722 27.1997272484913 -115.935260563566 27.1524952198729 -115.755436839005 27.2270348347386 -115.734960009089 27.3748346522356 -115.694299254844 27.5226008861849 -115.653563616829 27.6702779354428 -115.612760542177 27.8178690071708 -115.571901649363 27.9653506439026 -115.531000691074 28.1127600020619 -115.490011752733 28.2601469756437 -115.44890306179 28.4076546372628 -115.407649898021 28.455192866856 -115.589486631416 28.4968374106496 -115.752807970928 28.5370603096399 -115.91452902381 28.575931293904 -116.074924211465 28.6135193777855 -116.234273707691 28.6498895688451 -116.392847129762 28.6851057860975 -116.550917254638 28.7192301322012 -116.708756374584 28.752323018501 -116.866636764481 28.7844432583843 -117.024831047231 28.8156481533955 -117.183612605748 28.8459935678779 -117.343255995623 28.8755339855462 -117.504037348554 28.9043225601122 -117.666234808407 28.9324111491586 -117.830128960026 28.9598503481156 -117.996003330616 28.9866878706574 -118.164136222141 29.012974905944 -118.33483458667"}
                                   ]
                       }]
            },
            "alerts": [{
                "message": "Alert message",
                "generator": "test",
                "notification_time": "2018-06-05T08:07:36",
                "alert_cnf": {
                    "name": "alert_name1",
                    "severity": "critical",
                    "description": "Alert description",
                    "group": "alert_group"
                }
            },{
                "message": "Alert message",
                "generator": "test",
                "notification_time": "2018-06-05T08:07:36",
                "alert_cnf": {
                    "name": "alert_name2",
                    "severity": "warning",
                    "description": "Alert description",
                    "group": "alert_group"
                }
            },{
                "message": "Alert message",
                "generator": "test",
                "notification_time": "2018-06-05T08:07:36",
                "alert_cnf": {
                    "name": "alert_name3",
                    "severity": "critical",
                    "description": "Alert description",
                    "group": "alert_group"
                }
            }]
        }]
        }

        # Check data is correctly inserted
        self.engine_rboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_rboa.treat_data()[0]["status"]
        
        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/general_view_alerts/")

        """ # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        # Click on query button
        functions.click(submit_button) """

    def test_all_alerts_query_no_filter(self):

        # Insert data
        data = {"operations": [{
            "mode": "insert",
            "dim_signature": {"name": "dim_signature",
                              "exec": "exec",
                              "version": "1.0"},
            "source": {"name": "source.json",
                       "reception_time": "2018-06-06T13:33:29",
                       "generation_time": "2018-07-05T02:07:03",
                       "validity_start": "2018-06-05T02:07:03",
                       "validity_stop": "2019-06-05T08:07:36",
                       "priority": 30},
            "events": [{
                "explicit_reference": "ER1",
                "gauge": {"name": "GAUGE_NAME",
                          "system": "GAUGE_SYSTEM",
                          "insertion_type": "SIMPLE_UPDATE"},
                "start": "2018-06-05T02:07:03",
                "stop": "2018-06-05T08:07:36",
                "values": [{"name": "VALUES",
                            "type": "object",
                            "values": [
                                {"type": "text",
                                 "name": "TEXT",
                                 "value": "TEXT"},
                                {"type": "boolean",
                                 "name": "BOOLEAN",
                                 "value": "true"}]
                            }],
                "alerts": [{
                    "message": "Alert message",
                    "generator": "test",
                    "notification_time": "2018-06-05T08:07:36",
                    "alert_cnf": {
                        "name": "alert_name1",
                        "severity": "critical",
                        "description": "Alert description",
                        "group": "alert_group"
                    }},
                           {
                               "message": "Alert message",
                               "generator": "test2",
                               "notification_time": "2019-06-05T08:07:36",
                               "alert_cnf": {
                                   "name": "alert_name2",
                                   "severity": "major",
                                   "description": "Alert description",
                                   "group": "alert_group2"
                               }}]
            },
                       {
                           "explicit_reference": "ER2",
                           "gauge": {"name": "GAUGE_NAME2",
                                     "system": "GAUGE_SYSTEM2",
                                     "insertion_type": "SIMPLE_UPDATE"},
                           "start": "2019-06-05T02:07:03",
                           "stop": "2019-06-05T08:07:36",
                           "alerts": [{
                               "message": "Alert message",
                               "generator": "test",
                               "notification_time": "2018-06-05T08:07:36",
                               "alert_cnf": {
                                   "name": "alert_name2",
                                   "severity": "critical",
                                   "description": "Alert description",
                                   "group": "alert_group"
                               }},
                                      {
                                          "message": "Alert message",
                                          "generator": "test2",
                                          "notification_time": "2019-06-05T08:07:36",
                                          "alert_cnf": {
                                              "name": "alert_name3",
                                              "severity": "major",
                                              "description": "Alert description",
                                              "group": "alert_group2"
                                          }}]
                       }],
                       "annotations": [{
                "explicit_reference": "ER1",
                "annotation_cnf": {"name": "NAME",
                                   "system": "SYSTEM",
                                   "insertion_type": "SIMPLE_UPDATE"},
                "values": [{"name": "VALUES",
                            "type": "object",
                            "values": [
                                {"type": "text",
                                 "name": "TEXT",
                                 "value": "TEXT"},
                                {"type": "boolean",
                                 "name": "BOOLEAN",
                                 "value": "true"}]
                            }],
                "alerts": [{
                    "message": "Alert message",
                    "generator": "test",
                    "notification_time": "2018-06-05T08:07:36",
                    "alert_cnf": {
                        "name": "alert_name1",
                        "severity": "critical",
                        "description": "Alert description",
                        "group": "alert_group"
                    }},
                           {
                               "message": "Alert message",
                               "generator": "test2",
                               "notification_time": "2019-06-05T08:07:36",
                               "alert_cnf": {
                                   "name": "alert_name2",
                                   "severity": "major",
                                   "description": "Alert description",
                                   "group": "alert_group2"
                               }}]
            },
                       {
                           "explicit_reference": "ER1",
                           "annotation_cnf": {"name": "NAME",
                                              "system": "SYSTEM",
                                              "insertion_type": "SIMPLE_UPDATE"},
                           "alerts": [{
                               "message": "Alert message",
                               "generator": "test",
                               "notification_time": "2018-06-05T08:07:36",
                               "alert_cnf": {
                                   "name": "alert_name1",
                                   "severity": "critical",
                                   "description": "Alert description",
                                   "group": "alert_group"
                               }},
                                      {
                                          "message": "Alert message",
                                          "generator": "test2",
                                          "notification_time": "2019-06-05T08:07:36",
                                          "alert_cnf": {
                                              "name": "alert_name2",
                                              "severity": "major",
                                              "description": "Alert description",
                                              "group": "alert_group2"
                                          }}]
                       }],
                       "explicit_references": [{
                "name": "ER1",
                "group": "ER_GROUP",
                "alerts": [{
                    "message": "Alert message",
                    "generator": "test",
                    "notification_time": "2020-06-05T08:07:36",
                    "alert_cnf": {
                        "name": "alert_name1",
                        "severity": "critical",
                        "description": "Alert description",
                        "group": "alert_group"
                    }},
                           {
                               "message": "Alert message",
                               "generator": "test2",
                               "notification_time": "2019-06-05T08:07:36",
                               "alert_cnf": {
                                   "name": "alert_name2",
                                   "severity": "major",
                                   "description": "Alert description",
                                   "group": "alert_group2"
                               }}]
            }],
            "alerts": [{
                "message": "Alert message",
                "generator": "test",
                "notification_time": "2018-06-05T08:07:36",
                "alert_cnf": {
                    "name": "alert_name1",
                    "severity": "critical",
                    "description": "Alert description",
                    "group": "alert_group"
                },
                "entity": {
                    "reference_mode": "by_ref",
                    "reference": "source.json",
                    "type": "source"
                }
            },{
                "message": "Alert message",
                "generator": "test1",
                "notification_time": "2019-06-06T08:07:36",
                "alert_cnf": {
                    "name": "alert_name2",
                    "severity": "critical",
                    "description": "Alert description",
                    "group": "alert_group"
                },
                "entity": {
                    "reference_mode": "by_ref",
                    "reference": "source.json",
                    "type": "source"
                }
            }]
        }]
        }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        filename = "report.html"
        file_path = os.path.dirname(os.path.abspath(__file__)) + "/html_inputs/" + filename

        # Insert data
        data = {"operations": [{
            "mode": "insert",
            "report": {"name": filename,
                       "group": "report_group",
                       "group_description": "Group of reports for testing",
                       "path": file_path,
                       "compress": "true",
                       "generation_mode": "MANUAL",
                       "validity_start": "2018-06-05T02:07:03",
                       "validity_stop": "2018-06-05T08:07:36",
                       "triggering_time": "2018-07-05T02:07:03",
                       "generation_start": "2018-07-05T02:07:10",
                       "generation_stop": "2018-07-05T02:15:10",
                       "generator": "report_generator",
                       "generator_version": "1.0",
                       "values": [{"name": "VALUES",
                                   "type": "object",
                                   "values": [
                                       {"type": "text",
                                        "name": "TEXT",
                                        "value": "TEXT"},
                                       {"type": "boolean",
                                        "name": "BOOLEAN",
                                        "value": "true"},
                                       {"type": "double",
                                        "name": "DOUBLE",
                                        "value": "0.9"},
                                       {"type": "timestamp",
                                        "name": "TIMESTAMP",
                                        "value": "20180712T00:00:00"},
                                       {"type": "geometry",
                                        "name": "GEOMETRY",
                                        "value": "29.012974905944 -118.33483458667 28.8650301641571 -118.372028380632 28.7171766138274 -118.409121707686 28.5693112139334 -118.44612300623 28.4213994944367 -118.483058731035 28.2734085660472 -118.519970531113 28.1253606038163 -118.556849863134 27.9772541759126 -118.593690316835 27.8291247153939 -118.630472520505 27.7544158362332 -118.64900551674 27.7282373644786 -118.48032600682 27.7015162098732 -118.314168792268 27.6742039940042 -118.150246300849 27.6462511775992 -117.98827485961 27.6176070520608 -117.827974178264 27.5882197156561 -117.669066835177 27.5580360448116 -117.511277813618 27.5270016492436 -117.354334035359 27.4950608291016 -117.197963963877 27.4621565093409 -117.041897175848 27.4282301711374 -116.885863967864 27.3932217651372 -116.729594956238 27.3570696128269 -116.572820673713 27.3197103000253 -116.415271199941 27.2810785491022 -116.256675748617 27.241107085821 -116.09676229722 27.1997272484913 -115.935260563566 27.1524952198729 -115.755436839005 27.2270348347386 -115.734960009089 27.3748346522356 -115.694299254844 27.5226008861849 -115.653563616829 27.6702779354428 -115.612760542177 27.8178690071708 -115.571901649363 27.9653506439026 -115.531000691074 28.1127600020619 -115.490011752733 28.2601469756437 -115.44890306179 28.4076546372628 -115.407649898021 28.455192866856 -115.589486631416 28.4968374106496 -115.752807970928 28.5370603096399 -115.91452902381 28.575931293904 -116.074924211465 28.6135193777855 -116.234273707691 28.6498895688451 -116.392847129762 28.6851057860975 -116.550917254638 28.7192301322012 -116.708756374584 28.752323018501 -116.866636764481 28.7844432583843 -117.024831047231 28.8156481533955 -117.183612605748 28.8459935678779 -117.343255995623 28.8755339855462 -117.504037348554 28.9043225601122 -117.666234808407 28.9324111491586 -117.830128960026 28.9598503481156 -117.996003330616 28.9866878706574 -118.164136222141 29.012974905944 -118.33483458667"}
                                   ]
                       }]
            },
            "alerts": [{
                "message": "Alert message",
                "generator": "test",
                "notification_time": "2018-06-05T08:07:36",
                "alert_cnf": {
                    "name": "alert_name1",
                    "severity": "critical",
                    "description": "Alert description",
                    "group": "alert_group"
                }
            },{
                "message": "Alert message",
                "generator": "test",
                "notification_time": "2018-06-05T08:07:36",
                "alert_cnf": {
                    "name": "alert_name2",
                    "severity": "warning",
                    "description": "Alert description",
                    "group": "alert_group"
                }
            },{
                "message": "Alert message",
                "generator": "test",
                "notification_time": "2018-06-05T08:07:36",
                "alert_cnf": {
                    "name": "alert_name3",
                    "severity": "critical",
                    "description": "Alert description",
                    "group": "alert_group"
                }
            }]
        }]
        }

        # Check data is correctly inserted
        self.engine_rboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_rboa.treat_data()[0]["status"]
        
        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/general_view_alerts/")

        """ # Go to tab
        functions.goToTab(self.driver,"Sources")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'sources-submit-button')))
        functions.click_no_graphs_sources(self.driver)

        # Click on query button
        functions.click(submit_button) """

