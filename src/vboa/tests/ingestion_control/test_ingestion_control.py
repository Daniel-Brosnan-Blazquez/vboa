"""
Automated tests for the ingestion control module

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
import shutil

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

# Import service management
import vboa.service_management as service_management

class TestIngestionControl(unittest.TestCase):

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

        # Switch off ORC
        status = service_management.execute_command("orcBolg --command stop")
        assert status["return_code"] == 0

        # Clear ORC tables
        status = service_management.execute_command("boa_init.py -o -y")
        assert status["return_code"] == 0
        
    def tearDown(self):
        status = service_management.execute_command("orcValidateConfig -C")
        assert status["return_code"] == 0
        path_to_orc_config = status["output"]

        try:
            os.rename("/resources_path/triggering_bak.xml", "/resources_path/triggering.xml")
        except FileNotFoundError:
            pass
        # end try
        try:
            os.rename(path_to_orc_config + "/orchestratorConfigFile_bak.xml", path_to_orc_config + "/orchestratorConfigFile.xml")
        except FileNotFoundError:
            pass
        # end try
        # Close connections to the DDBB
        self.engine_eboa.close_session()
        self.query_eboa.close_session()
        self.session.close()

    @classmethod
    def tearDownClass(self):
        self.driver.quit()

    def test_no_sources(self):
        
        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/ingestion_control/ingestion_control")

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"no-sources-ingestion-control")))

        assert no_data

        # Check number of widgets in summary
        summary_section = wait.until(EC.visibility_of_element_located((By.ID,"summary-ingestion-control")))

        assert summary_section and len(summary_section.find_elements_by_xpath("div")) == 1

        # Check summary expected
        summary_expected = wait.until(EC.visibility_of_element_located((By.ID,"summary-ingestion-control-expected")))

        assert summary_expected and summary_expected.text == "0"

    def test_no_alerts(self):
        
        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/ingestion_control/ingestion_control?template=alerts")

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"no-ingestion-alerts")))

        assert no_data

        # Check number of widgets in summary
        summary_section = wait.until(EC.visibility_of_element_located((By.ID,"summary-ingestion-control")))

        assert summary_section and len(summary_section.find_elements_by_xpath("div")) == 1

        # Check summary alerts
        summary_alerts = wait.until(EC.visibility_of_element_located((By.ID,"summary-ingestion-control-no-alerts")))

        assert summary_alerts and summary_alerts.text == "0"

    def test_no_errors(self):
        
        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/ingestion_control/ingestion_control?template=errors")

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"no-ingestion-errors")))

        assert no_data

        # Check number of widgets in summary
        summary_section = wait.until(EC.visibility_of_element_located((By.ID,"summary-ingestion-control")))

        assert summary_section and len(summary_section.find_elements_by_xpath("div")) == 2

        # Check summary errors
        summary_errors = wait.until(EC.visibility_of_element_located((By.ID,"summary-ingestion-control-no-errors")))

        assert summary_errors and summary_errors.text == "0"

        # Check summary incomplete
        summary_incomplete = wait.until(EC.visibility_of_element_located((By.ID,"summary-ingestion-control-no-incomplete")))

        assert summary_incomplete and summary_incomplete.text == "0"

    def test_show_successfully_finished_ingestions(self):
        
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
                            "priority": 10
                }
        }]}

        # Check data is correctly inserted
        exit_status = self.engine_eboa.treat_data(data)
        assert len([item for item in exit_status if item["status"] != eboa_engine.exit_codes["OK"]["status"]]) == 0
        
        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/ingestion_control/ingestion_control")

        functions.query(self.driver, wait, start = "2014-07-20T00:00:14", stop = "2030-07-21T23:55:14")

        # Check number of widgets in summary
        summary_section = wait.until(EC.visibility_of_element_located((By.ID,"summary-ingestion-control")))
        assert summary_section and len(summary_section.find_elements_by_xpath("div")) == 2

        # Check summary expected
        summary_expected = wait.until(EC.visibility_of_element_located((By.ID,"summary-ingestion-control-expected")))

        assert summary_expected and summary_expected.text == "1"

        # Check summary successful
        summary_successful = wait.until(EC.visibility_of_element_located((By.ID,"summary-ingestion-control-successful")))

        assert summary_successful and summary_successful.text == "1"

        # table
        table = self.driver.find_element_by_id("ingestions-status-ingestion-control-table")

        name = table.find_element_by_xpath("tbody/tr[last()]/td[3]")

        assert name.text == "source.xml"

        dim_signature = table.find_element_by_xpath("tbody/tr[last()]/td[4]")

        assert dim_signature.text == "dim_signature"

        ingestion_completeness = table.find_element_by_xpath("tbody/tr[last()]/td[7]")

        assert ingestion_completeness.text == "True"

        number_of_events = table.find_element_by_xpath("tbody/tr[last()]/td[15]")

        assert number_of_events.text == "0"

        # Check generated content for widgets
        sources = self.query_eboa.get_sources()

        assert len(sources) == 1
        
        sources = [
            {
                "id": str(sources[0].source_uuid),
                "name": "source.xml",
                "dim_signature": "dim_signature",
                "processor": "exec",
                "version": "1.0",
                "validity_start": "2018-06-05T02:07:03",
                "validity_stop": "2018-06-05T08:07:36",
                "reported_validity_start": "2018-06-05T02:07:03",
                "reported_validity_stop": "2018-06-05T08:07:36",
                "reception_time": "2018-07-05T02:07:03",
                "ingestion_time": sources[0].ingestion_time.isoformat(),
                "processing_duration": "0:00:00",
                "ingestion_duration": str(sources[0].ingestion_duration),
                "generation_time": "2018-07-05T02:07:03",
                "reported_generation_time": "2018-07-05T02:07:03",
                "number_of_events": "0",
                "priority": "10",
                "ingestion_completeness": "True",
                "ingestion_completeness_message": "None",
                "ingestion_error": "False"
            }
        ]

        assert sources == self.driver.execute_script('return sources;')
        
        # Check validity timeline
        validity_timeline = self.driver.find_element_by_id("ingestion-control-validity-timeline")

        assert validity_timeline.is_displayed()
        
        # Check generation to ingestion timeline
        generation_to_ingestion_timeline = self.driver.find_element_by_id("ingestion-control-generation-to-ingestion-timeline")

        assert generation_to_ingestion_timeline.is_displayed()
        
        # Check number of events xy
        number_of_events_xy = self.driver.find_element_by_id("ingestion-control-number-events-xy")

        assert number_of_events_xy.is_displayed()
        
        # Check ingestion duration xy
        ingestion_duration_xy = self.driver.find_element_by_id("ingestion-control-ingestion-duration-xy")

        assert ingestion_duration_xy.is_displayed()
        
        # Check generation time to ingestion time xy
        generation_to_ingestion_xy = self.driver.find_element_by_id("ingestion-control-generation-time-to-ingestion-time-xy")

        assert generation_to_ingestion_xy.is_displayed()

    def test_show_ingestion_error(self):
        
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
                       "priority": 10
                    },
            "events": [{
                "gauge": {"name": "GAUGE_NAME",
                          "system": "GAUGE_SYSTEM",
                          "insertion_type": "SIMPLE_UPDATE"},
                "start": "2020-06-05T04:07:03",
                "stop": "2018-06-05T06:07:36"
            }]
        }]}

        # Check data is correctly inserted
        exit_status = self.engine_eboa.treat_data(data)
        
        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/ingestion_control/ingestion_control")

        functions.query(self.driver, wait, start = "2014-07-20T00:00:14", stop = "2030-07-21T23:55:14")

        # Check number of widgets in summary
        summary_section = wait.until(EC.visibility_of_element_located((By.ID,"summary-ingestion-control")))
        assert summary_section and len(summary_section.find_elements_by_xpath("div")) == 2

        # Check summary expected
        summary_expected = wait.until(EC.visibility_of_element_located((By.ID,"summary-ingestion-control-expected")))

        assert summary_expected and summary_expected.text == "1"

        # Check summary errors
        summary_errors = wait.until(EC.visibility_of_element_located((By.ID,"summary-ingestion-control-error")))

        assert summary_errors and summary_errors.text == "1"

        # general table
        table = self.driver.find_element_by_id("ingestions-status-ingestion-control-table")

        name = table.find_element_by_xpath("tbody/tr[last()]/td[3]")

        assert name.text == "source.xml"

        dim_signature = table.find_element_by_xpath("tbody/tr[last()]/td[4]")

        assert dim_signature.text == "dim_signature"

        ingestion_completeness = table.find_element_by_xpath("tbody/tr[last()]/td[7]")

        assert ingestion_completeness.text == "True"

        number_of_events = table.find_element_by_xpath("tbody/tr[last()]/td[15]")

        assert number_of_events.text == "0"

        # errors table
        table = self.driver.find_element_by_id("ingestion-errors-table")

        name = table.find_element_by_xpath("tbody/tr[last()]/td[3]")

        assert name.text == "source.xml"

        dim_signature = table.find_element_by_xpath("tbody/tr[last()]/td[4]")

        assert dim_signature.text == "dim_signature"

        ingestion_completeness = table.find_element_by_xpath("tbody/tr[last()]/td[7]")

        assert ingestion_completeness.text == "True"

        number_of_events = table.find_element_by_xpath("tbody/tr[last()]/td[15]")

        assert number_of_events.text == "0"

        # Check generated content for widgets
        sources = self.query_eboa.get_sources()

        assert len(sources) == 1
        
        sources = [
            {
                "id": str(sources[0].source_uuid),
                "name": "source.xml",
                "dim_signature": "dim_signature",
                "processor": "exec",
                "version": "1.0",
                "validity_start": "2018-06-05T02:07:03",
                "validity_stop": "2018-06-05T08:07:36",
                "reported_validity_start": "2018-06-05T02:07:03",
                "reported_validity_stop": "2018-06-05T08:07:36",
                "reception_time": "2018-07-05T02:07:03",
                "ingestion_time": sources[0].reception_time.isoformat(),
                "processing_duration": "0:00:00",
                "ingestion_duration": "0:00:00",
                "generation_time": "2018-07-05T02:07:03",
                "reported_generation_time": "2018-07-05T02:07:03",
                "number_of_events": "0",
                "priority": "10",
                "ingestion_completeness": "True",
                "ingestion_completeness_message": "None",
                "ingestion_error": "True"
            }
        ]

        assert sources == self.driver.execute_script('return sources;')
        
        # Check validity timeline
        validity_timeline = self.driver.find_element_by_id("ingestion-control-validity-timeline")

        assert validity_timeline.is_displayed()
        
        # Check generation to ingestion timeline
        generation_to_ingestion_timeline = self.driver.find_element_by_id("ingestion-control-generation-to-ingestion-timeline")

        assert generation_to_ingestion_timeline.is_displayed()
        
        # Check number of events xy
        number_of_events_xy = self.driver.find_element_by_id("ingestion-control-number-events-xy")

        assert number_of_events_xy.is_displayed()
        
        # Check ingestion duration xy
        ingestion_duration_xy = self.driver.find_element_by_id("ingestion-control-ingestion-duration-xy")

        assert ingestion_duration_xy.is_displayed()
        
        # Check generation time to ingestion time xy
        generation_to_ingestion_xy = self.driver.find_element_by_id("ingestion-control-generation-time-to-ingestion-time-xy")

        assert generation_to_ingestion_xy.is_displayed()

    def test_show_incomplete_ingestion(self):
        
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
        exit_status = self.engine_eboa.treat_data(data)
        
        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/ingestion_control/ingestion_control")

        functions.query(self.driver, wait, start = "2014-07-20T00:00:14", stop = "2030-07-21T23:55:14")

        # Check number of widgets in summary
        summary_section = wait.until(EC.visibility_of_element_located((By.ID,"summary-ingestion-control")))
        assert summary_section and len(summary_section.find_elements_by_xpath("div")) == 3

        # Check summary expected
        summary_expected = wait.until(EC.visibility_of_element_located((By.ID,"summary-ingestion-control-expected")))

        assert summary_expected and summary_expected.text == "1"

        # Check summary successful
        summary_successful = wait.until(EC.visibility_of_element_located((By.ID,"summary-ingestion-control-successful")))

        assert summary_successful and summary_successful.text == "1"

        # Check summary incomplete
        summary_incomplete = wait.until(EC.visibility_of_element_located((By.ID,"summary-ingestion-control-incomplete")))

        assert summary_incomplete and summary_incomplete.text == "1"

        # general table
        table = self.driver.find_element_by_id("ingestions-status-ingestion-control-table")

        name = table.find_element_by_xpath("tbody/tr[last()]/td[3]")

        assert name.text == "source.xml"

        dim_signature = table.find_element_by_xpath("tbody/tr[last()]/td[4]")

        assert dim_signature.text == "dim_signature"

        ingestion_completeness = table.find_element_by_xpath("tbody/tr[last()]/td[7]")

        assert ingestion_completeness.text == "False"

        ingestion_completeness = table.find_element_by_xpath("tbody/tr[last()]/td[8]")

        assert ingestion_completeness.text == "MISSING DEPENDENCIES"

        number_of_events = table.find_element_by_xpath("tbody/tr[last()]/td[15]")

        assert number_of_events.text == "0"

        # incomplete table
        table = self.driver.find_element_by_id("incomplete-ingestions-table")

        name = table.find_element_by_xpath("tbody/tr[last()]/td[3]")

        assert name.text == "source.xml"

        dim_signature = table.find_element_by_xpath("tbody/tr[last()]/td[4]")

        assert dim_signature.text == "dim_signature"

        ingestion_completeness = table.find_element_by_xpath("tbody/tr[last()]/td[7]")

        assert ingestion_completeness.text == "False"

        ingestion_completeness = table.find_element_by_xpath("tbody/tr[last()]/td[8]")

        assert ingestion_completeness.text == "MISSING DEPENDENCIES"

        number_of_events = table.find_element_by_xpath("tbody/tr[last()]/td[15]")

        assert number_of_events.text == "0"

        # Check generated content for widgets
        sources = self.query_eboa.get_sources()

        assert len(sources) == 1
        
        sources = [
            {
                "id": str(sources[0].source_uuid),
                "name": "source.xml",
                "dim_signature": "dim_signature",
                "processor": "exec",
                "version": "1.0",
                "validity_start": "2018-06-05T02:07:03",
                "validity_stop": "2018-06-05T08:07:36",
                "reported_validity_start": "2018-06-05T02:07:03",
                "reported_validity_stop": "2018-06-05T08:07:36",
                "reception_time": "2018-07-05T02:07:03",
                "ingestion_time": sources[0].ingestion_time.isoformat(),
                "processing_duration": "0:00:00",
                "ingestion_duration": str(sources[0].ingestion_duration),
                "generation_time": "2018-07-05T02:07:03",
                "reported_generation_time": "2018-07-05T02:07:03",
                "number_of_events": "0",
                "priority": "10",
                "ingestion_completeness": "False",
                "ingestion_completeness_message": "MISSING DEPENDENCIES",
                "ingestion_error": "False"
            }
        ]

        assert sources == self.driver.execute_script('return sources;')
        
        # Check validity timeline
        validity_timeline = self.driver.find_element_by_id("ingestion-control-validity-timeline")

        assert validity_timeline.is_displayed()
        
        # Check generation to ingestion timeline
        generation_to_ingestion_timeline = self.driver.find_element_by_id("ingestion-control-generation-to-ingestion-timeline")

        assert generation_to_ingestion_timeline.is_displayed()
        
        # Check number of events xy
        number_of_events_xy = self.driver.find_element_by_id("ingestion-control-number-events-xy")

        assert number_of_events_xy.is_displayed()
        
        # Check ingestion duration xy
        ingestion_duration_xy = self.driver.find_element_by_id("ingestion-control-ingestion-duration-xy")

        assert ingestion_duration_xy.is_displayed()
        
        # Check generation time to ingestion time xy
        generation_to_ingestion_xy = self.driver.find_element_by_id("ingestion-control-generation-time-to-ingestion-time-xy")

        assert generation_to_ingestion_xy.is_displayed()

    def test_show_ingestion_alert(self):
        
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
                           }]
                           }
        }]}

        # Check data is correctly inserted
        exit_status = self.engine_eboa.treat_data(data)
        assert len([item for item in exit_status if item["status"] != eboa_engine.exit_codes["OK"]["status"]]) == 0
        
        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/ingestion_control/ingestion_control")

        functions.query(self.driver, wait, start = "2014-07-20T00:00:14", stop = "2030-07-21T23:55:14")

        # Check number of widgets in summary
        summary_section = wait.until(EC.visibility_of_element_located((By.ID,"summary-ingestion-control")))
        assert summary_section and len(summary_section.find_elements_by_xpath("div")) == 3

        # Check summary expected
        summary_expected = wait.until(EC.visibility_of_element_located((By.ID,"summary-ingestion-control-expected")))

        assert summary_expected and summary_expected.text == "1"

        # Check summary successful
        summary_successful = wait.until(EC.visibility_of_element_located((By.ID,"summary-ingestion-control-successful")))

        assert summary_successful and summary_successful.text == "1"

        # Check summary alert
        summary_alert = wait.until(EC.visibility_of_element_located((By.ID,"summary-ingestion-control-alert")))

        assert summary_alert and summary_alert.text == "1"

        # table
        table = self.driver.find_element_by_id("ingestions-status-ingestion-control-table")

        name = table.find_element_by_xpath("tbody/tr[last()]/td[3]")

        assert name.text == "source.xml"

        dim_signature = table.find_element_by_xpath("tbody/tr[last()]/td[4]")

        assert dim_signature.text == "dim_signature"

        ingestion_completeness = table.find_element_by_xpath("tbody/tr[last()]/td[7]")

        assert ingestion_completeness.text == "True"

        number_of_events = table.find_element_by_xpath("tbody/tr[last()]/td[15]")

        assert number_of_events.text == "0"

        # alerts table
        table = self.driver.find_element_by_id("ingestion-control-alerts-details-table")

        severity = table.find_element_by_xpath("tbody/tr[last()]/td[2]")

        assert severity.text == "critical"

        group = table.find_element_by_xpath("tbody/tr[last()]/td[3]")

        assert group.text == "alert_group"

        alert_name = table.find_element_by_xpath("tbody/tr[last()]/td[4]")

        assert alert_name.text == "alert_name1"

        name = table.find_element_by_xpath("tbody/tr[last()]/td[5]")

        assert name.text == "source.xml"

        alert_message = table.find_element_by_xpath("tbody/tr[last()]/td[6]")

        assert alert_message.text == "Alert message"

        validated = table.find_element_by_xpath("tbody/tr[last()]/td[7]")

        assert validated.text == "None"

        generator = table.find_element_by_xpath("tbody/tr[last()]/td[8]")

        assert generator.text == "test"

        notified = table.find_element_by_xpath("tbody/tr[last()]/td[9]")

        assert notified.text == "None"

        notification_time = table.find_element_by_xpath("tbody/tr[last()]/td[10]")

        assert notification_time.text == "2018-06-05 08:07:36"

        # Check generated content for widgets
        sources = self.query_eboa.get_sources()

        assert len(sources) == 1
        
        sources = [
            {
                "id": str(sources[0].source_uuid),
                "name": "source.xml",
                "dim_signature": "dim_signature",
                "processor": "exec",
                "version": "1.0",
                "validity_start": "2018-06-05T02:07:03",
                "validity_stop": "2018-06-05T08:07:36",
                "reported_validity_start": "2018-06-05T02:07:03",
                "reported_validity_stop": "2018-06-05T08:07:36",
                "reception_time": "2018-07-05T02:07:03",
                "ingestion_time": sources[0].ingestion_time.isoformat(),
                "processing_duration": "0:00:00",
                "ingestion_duration": str(sources[0].ingestion_duration),
                "generation_time": "2018-07-05T02:07:03",
                "reported_generation_time": "2018-07-05T02:07:03",
                "number_of_events": "0",
                "priority": "10",
                "ingestion_completeness": "True",
                "ingestion_completeness_message": "None",
                "ingestion_error": "False"
            }
        ]

        assert sources == self.driver.execute_script('return sources;')
        
        # Check validity timeline
        validity_timeline = self.driver.find_element_by_id("ingestion-control-validity-timeline")

        assert validity_timeline.is_displayed()
        
        # Check generation to ingestion timeline
        generation_to_ingestion_timeline = self.driver.find_element_by_id("ingestion-control-generation-to-ingestion-timeline")

        assert generation_to_ingestion_timeline.is_displayed()
        
        # Check number of events xy
        number_of_events_xy = self.driver.find_element_by_id("ingestion-control-number-events-xy")

        assert number_of_events_xy.is_displayed()
        
        # Check ingestion duration xy
        ingestion_duration_xy = self.driver.find_element_by_id("ingestion-control-ingestion-duration-xy")

        assert ingestion_duration_xy.is_displayed()
        
        # Check generation time to ingestion time xy
        generation_to_ingestion_xy = self.driver.find_element_by_id("ingestion-control-generation-time-to-ingestion-time-xy")

        assert generation_to_ingestion_xy.is_displayed()

    def test_manual_ingestion_one_file(self):

        # Copy test configuration for ORC
        status = service_management.execute_command("orcValidateConfig -C")
        assert status["return_code"] == 0
        path_to_orc_config = status["output"]
        os.rename(path_to_orc_config + "/orchestratorConfigFile.xml", path_to_orc_config + "/orchestratorConfigFile_bak.xml")
        shutil.copyfile(os.path.dirname(os.path.abspath(__file__)) + "/inputs/orchestratorConfigFile.xml", path_to_orc_config + "/orchestratorConfigFile.xml")

        # Copy test configuration for triggering
        os.rename("/resources_path/triggering.xml", "/resources_path/triggering_bak.xml")
        shutil.copyfile(os.path.dirname(os.path.abspath(__file__)) + "/inputs/triggering.xml", "/resources_path/triggering.xml")

        wait = WebDriverWait(self.driver,5)
        self.driver.get("http://localhost:5000/ingestion_control/manual-ingestion")

        # Browse file
        browse_file = self.driver.find_element_by_id("manual-ingestion-files-browse-files")

        filename = "source.json"
        file_path = os.path.dirname(os.path.abspath(__file__)) + "/inputs/" + filename
    
        browse_file.send_keys(file_path)

        # Trigger input files table
        table = self.driver.find_element_by_id("manual-ingestion-files-table")

        name = table.find_element_by_xpath("tbody/tr[last()]/td[2]")

        assert name.text == "source.json"

        size = table.find_element_by_xpath("tbody/tr[last()]/td[3]")

        assert size.text == "467 B"

        # Trigger ingestion
        trigger_ingestion_button = self.driver.find_element_by_id("manual-ingestion-files-trigger-button")
        trigger_ingestion_button.click()

        time.sleep(1)
        
        # Confirm ORC switch on
        alert = self.driver.switch_to.alert
        alert.accept()

        time.sleep(40)
        
        # Confirm ingestion
        alert = self.driver.switch_to.alert
        alert.accept()
        
        # Check ingested sources
        time.sleep(60)

        # Check sources inserted
        sources = self.query_eboa.get_sources(validity_start_filters = [{"date": "2018-06-05T02:07:03", "op": "=="}],
                                              validity_stop_filters = [{"date": "2018-06-05T02:07:36", "op": "=="}],
                                              processors = {"filter": "exec", "op": "=="},
                                              dim_signatures = {"filter": "dim_signature", "op": "=="},
                                              names = {"filter": "source.json", "op": "=="},
                                              ingestion_completeness = True)

        assert len(sources) == 1

        os.rename("/resources_path/triggering_bak.xml", "/resources_path/triggering.xml")
        os.rename(path_to_orc_config + "/orchestratorConfigFile_bak.xml", path_to_orc_config + "/orchestratorConfigFile.xml")
    
    def test_manual_ingestion_two_files(self):

        # Copy test configuration for ORC
        status = service_management.execute_command("orcValidateConfig -C")

        assert status["return_code"] == 0
        path_to_orc_config = status["output"]
        os.rename(path_to_orc_config + "/orchestratorConfigFile.xml", path_to_orc_config + "/orchestratorConfigFile_bak.xml")
        shutil.copyfile(os.path.dirname(os.path.abspath(__file__)) + "/inputs/orchestratorConfigFile.xml", path_to_orc_config + "/orchestratorConfigFile.xml")

        # Copy test configuration for triggering
        os.rename("/resources_path/triggering.xml", "/resources_path/triggering_bak.xml")
        shutil.copyfile(os.path.dirname(os.path.abspath(__file__)) + "/inputs/triggering.xml", "/resources_path/triggering.xml")
        
        self.driver.get("http://localhost:5000/ingestion_control/manual-ingestion")

        # Browse first file
        browse_file = self.driver.find_element_by_id("manual-ingestion-files-browse-files")

        filename = "source.json"
        file_path = os.path.dirname(os.path.abspath(__file__)) + "/inputs/" + filename
    
        browse_file.send_keys(file_path)

        # Trigger input files table
        table = self.driver.find_element_by_id("manual-ingestion-files-table")

        name = table.find_element_by_xpath("tbody/tr[last()]/td[2]")

        assert name.text == "source.json"

        size = table.find_element_by_xpath("tbody/tr[last()]/td[3]")

        assert size.text == "467 B"

        # Browse second file
        browse_file = self.driver.find_element_by_id("manual-ingestion-files-browse-files")

        filename = "source2.json"
        file_path = os.path.dirname(os.path.abspath(__file__)) + "/inputs/" + filename
    
        browse_file.send_keys(file_path)

        # Trigger input files table
        table = self.driver.find_element_by_id("manual-ingestion-files-table")

        name = table.find_element_by_xpath("tbody/tr[last()]/td[2]")

        assert name.text == "source2.json"

        size = table.find_element_by_xpath("tbody/tr[last()]/td[3]")

        assert size.text == "468 B"

        # Trigger ingestion
        trigger_ingestion_button = self.driver.find_element_by_id("manual-ingestion-files-trigger-button")
        trigger_ingestion_button.click()

        time.sleep(1)
        
        # Confirm ORC switch on
        alert = self.driver.switch_to.alert
        alert.accept()

        time.sleep(40)
        
        # Confirm ingestion
        alert = self.driver.switch_to.alert
        alert.accept()
        
        # Check ingested sources
        time.sleep(60)

        # Check sources inserted
        sources = self.query_eboa.get_sources(validity_start_filters = [{"date": "2018-06-05T02:07:03", "op": "=="}],
                                              validity_stop_filters = [{"date": "2018-06-05T02:07:36", "op": "=="}],
                                              processors = {"filter": "exec", "op": "=="},
                                              dim_signatures = {"filter": "dim_signature", "op": "=="},
                                              names = {"filter": "source.json", "op": "=="},
                                              ingestion_completeness = True)

        assert len(sources) == 1

        sources = self.query_eboa.get_sources(validity_start_filters = [{"date": "2018-06-05T02:07:03", "op": "=="}],
                                              validity_stop_filters = [{"date": "2018-06-05T02:07:36", "op": "=="}],
                                              processors = {"filter": "exec", "op": "=="},
                                              dim_signatures = {"filter": "dim_signature", "op": "=="},
                                              names = {"filter": "source2.json", "op": "=="},
                                              ingestion_completeness = True)

        assert len(sources) == 1

        os.rename("/resources_path/triggering_bak.xml", "/resources_path/triggering.xml")
        os.rename(path_to_orc_config + "/orchestratorConfigFile_bak.xml", path_to_orc_config + "/orchestratorConfigFile.xml")
        
    def test_manual_ingestion_remove_file(self):

        self.driver.get("http://localhost:5000/ingestion_control/manual-ingestion")

        # Browse file
        browse_file = self.driver.find_element_by_id("manual-ingestion-files-browse-files")

        filename = "source.json"
        file_path = os.path.dirname(os.path.abspath(__file__)) + "/inputs/" + filename
    
        browse_file.send_keys(file_path)

        # Trigger input files table
        table = self.driver.find_element_by_id("manual-ingestion-files-table")

        name = table.find_element_by_xpath("tbody/tr[last()]/td[2]")

        assert name.text == "source.json"

        size = table.find_element_by_xpath("tbody/tr[last()]/td[3]")

        assert size.text == "467 B"

        # Clear button
        clear_button = self.driver.find_element_by_id("manual-ingestion-files-clear-button")
        clear_button.click()

        table = self.driver.find_element_by_id("manual-ingestion-files-table")

        empty_table = table.find_element_by_xpath("tbody/tr[last()]/td[1]")

        assert empty_table.text == "No data available in table"

