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
import tests.selenium.functions as functions
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
                },
                "alerts": [{
                    "message": "The input source.xml has been received to be ingested",
                    "generator": "source.xml",
                    "notification_time": "2018-06-05T04:07:03",
                    "alert_cnf": {
                        "name": "PENDING_INGESTION_OF_SOURCE",
                        "severity": "fatal",
                        "description": "Alert refers to the pending ingestion of the relative input",
                        "group": "INGESTION_CONTROL"
                    },
                    "entity": {
                        "reference_mode": "by_ref",
                        "reference": "source.xml",
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