"""
Automated tests for the explicit_refs tab

Written by DEIMOS Space S.L. (femd)

module vboa
"""
import os
import sys
import unittest
import time
import subprocess
import datetime
import tests.selenium.functions as functions
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
from eboa.datamodel.alerts import Alert
from eboa.datamodel.events import Event, EventLink, EventKey, EventText, EventDouble, EventObject, EventGeometry, EventBoolean, EventTimestamp
from eboa.datamodel.gauges import Gauge
from eboa.datamodel.sources import Source, SourceStatus
from eboa.datamodel.explicit_refs import ExplicitRef, ExplicitRefGrp, ExplicitRefLink
from eboa.datamodel.annotations import Annotation, AnnotationCnf, AnnotationText, AnnotationDouble, AnnotationObject, AnnotationGeometry, AnnotationBoolean, AnnotationTimestamp


class TestExplicitReferencesTab(unittest.TestCase):

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

    def test_explicit_refs_no_data(self):

        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        empty_element = len(explicit_refs_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element is True

    @debug
    def test_explicit_refs_query_no_filter(self):

        # Insert data
        data = {"operations": [{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source.xml",
                        "reception_time": "2018-07-05T02:07:03",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "explicit_references": [{
                "name": "EXPLICIT_REFERENCE",
                "links": [{
                    "back_ref": "BACK_REF_LINK",
                    "link": "EXPLICIT_REFERENCE_2",
                    "name": "EXPLICIT_REFERENCE_LINK"
                }],
                "group": "EXPLICIT_REFERENCE_GROUP"
            }],
            "events": [{
                "explicit_reference": "EXPLICIT_REFERENCE",
                "gauge": {"name": "GAUGE_NAME",
                          "system": "GAUGE_SYSTEM",
                          "insertion_type": "SIMPLE_UPDATE"},
                "start": "2018-06-05T04:07:03",
                "stop": "2018-06-05T06:07:36"
                },{
                "explicit_reference": "EXPLICIT_REFERENCE_2",
                "gauge": {"name": "GAUGE_NAME_2",
                          "system": "GAUGE_SYSTEM_2",
                          "insertion_type": "SIMPLE_UPDATE"},
                "start": "2018-06-05T04:07:12",
                "stop": "2018-06-05T06:07:24"
                }]
            }]}

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        # Check explicit reference
        explicit_reference_1 = explicit_refs_table.find_elements_by_xpath("tbody/tr[td[text() = 'EXPLICIT_REFERENCE']]/td[1]")

        assert explicit_reference_1[0].text == "EXPLICIT_REFERENCE"

        # Check group
        group = explicit_refs_table.find_elements_by_xpath("tbody/tr[td[text() = 'EXPLICIT_REFERENCE']]/td[2]")

        assert group[0].text == "EXPLICIT_REFERENCE_GROUP"

        # Check group
        ingestion_time = explicit_refs_table.find_elements_by_xpath("tbody/tr[td[text() = 'EXPLICIT_REFERENCE']]/td[5]")

        assert re.match("....-..-..T..:..:...*", ingestion_time[0].text)

        # Check uuid
        uuid = explicit_refs_table.find_elements_by_xpath("tbody/tr[td[text() = 'EXPLICIT_REFERENCE']]/td[7]")

        assert re.match("........-....-....-....-............", uuid[0].text)

        # Linked explicit refs table
        wait = WebDriverWait(self.driver,5)

        explicit_ref = self.session.query(ExplicitRef).all()[0]

        self.driver.get("http://localhost:5000/eboa_nav/query-er-links/" + str(explicit_ref.explicit_ref_uuid))

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"linked-explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 3

        # Row 1
        # Check description
        gauge_name = explicit_refs_table.find_elements_by_xpath("tbody/tr[1]/td[1]")

        assert gauge_name[0].text == "PRIME"

        # Check explicit reference
        explicit_reference = explicit_refs_table.find_elements_by_xpath("tbody/tr[1]/td[2]")

        assert explicit_reference[0].text == "EXPLICIT_REFERENCE"

        # Check group
        group = explicit_refs_table.find_elements_by_xpath("tbody/tr[1]/td[3]")

        assert group[0].text == "EXPLICIT_REFERENCE_GROUP"

        # Check group
        ingestion_time = explicit_refs_table.find_elements_by_xpath("tbody/tr[1]/td[6]")

        assert re.match("....-..-..T..:..:...*", ingestion_time[0].text)

        # Check uuid
        uuid = explicit_refs_table.find_elements_by_xpath("tbody/tr[1]/td[8]")

        assert re.match("........-....-....-....-............", uuid[0].text)

        # Row 2
        # Check description
        gauge_name = explicit_refs_table.find_elements_by_xpath("tbody/tr[2]/td[1]")

        assert gauge_name[0].text == "LINK FROM: EXPLICIT_REFERENCE_LINK"

        # Check explicit reference
        explicit_reference = explicit_refs_table.find_elements_by_xpath("tbody/tr[2]/td[2]")

        assert explicit_reference[0].text == "EXPLICIT_REFERENCE_2"

        # Check group
        group = explicit_refs_table.find_elements_by_xpath("tbody/tr[2]/td[3]")

        assert group[0].text == ""

        # Check group
        ingestion_time = explicit_refs_table.find_elements_by_xpath("tbody/tr[2]/td[6]")

        assert re.match("....-..-..T..:..:...*", ingestion_time[0].text)

        # Check uuid
        uuid = explicit_refs_table.find_elements_by_xpath("tbody/tr[2]/td[8]")

        assert re.match("........-....-....-....-............", uuid[0].text)

        # Row 3
        # Check description
        gauge_name = explicit_refs_table.find_elements_by_xpath("tbody/tr[3]/td[1]")

        assert gauge_name[0].text == "LINK TO: BACK_REF_LINK"

        # Check explicit reference
        explicit_reference = explicit_refs_table.find_elements_by_xpath("tbody/tr[3]/td[2]")

        assert explicit_reference[0].text == "EXPLICIT_REFERENCE_2"

        # Check group
        group = explicit_refs_table.find_elements_by_xpath("tbody/tr[3]/td[3]")

        assert group[0].text == ""

        # Check group
        ingestion_time = explicit_refs_table.find_elements_by_xpath("tbody/tr[3]/td[6]")

        assert re.match("....-..-..T..:..:...*", ingestion_time[0].text)

        # Check uuid
        uuid = explicit_refs_table.find_elements_by_xpath("tbody/tr[3]/td[8]")

        assert re.match("........-....-....-....-............", uuid[0].text)

    @debug
    def test_explicit_refs_query_explicit_ref_filter(self):

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
                           "validity_stop": "2018-06-05T08:07:36"},
            "events": [{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT_1",
                "gauge": {"name": "GAUGE_NAME",
                          "system": "GAUGE_SYSTEM",
                          "insertion_type": "SIMPLE_UPDATE"},
                "start": "2018-06-05T04:07:03",
                "stop": "2018-06-05T06:07:36"
                },{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT_2",
                "gauge": {"name": "GAUGE_NAME_2",
                          "system": "GAUGE_SYSTEM_2",
                          "insertion_type": "SIMPLE_UPDATE"},
                "start": "2018-06-05T04:07:12",
                "stop": "2018-06-05T06:07:24"
                }]
            },{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_2.xml",
                        "reception_time": "2018-07-05T02:07:03",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "events": [{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT_3",
                "gauge": {"name": "GAUGE_NAME_3",
                          "system": "GAUGE_SYSTEM_3",
                          "insertion_type": "SIMPLE_UPDATE"},
                "start": "2018-06-05T04:07:05",
                "stop": "2018-06-05T06:07:31"
                }]
            }
        ]}

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
        input_element.send_keys("EXPLICIT_REFERENCE_EVENT_2")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the explicit_ref_like input
        input_element = self.driver.find_element_by_id("explicit-refs-er-text")
        input_element.send_keys("EXPLICIT_REFERENCE_EVENT_2")

        menu = Select(self.driver.find_element_by_id("explicit-refs-er-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the explicit_ref_in input
        input_element = self.driver.find_element_by_id("explicit-refs-ers-in-text")
        functions.click(input_element)

        input_element.send_keys("EXPLICIT_REFERENCE_EVENT_1")
        input_element.send_keys(Keys.LEFT_SHIFT)
        input_element.clear()
        input_element.send_keys("EXPLICIT_REFERENCE_EVENT_3")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("explicit-refs-ers-in-select"))
        options.select_by_visible_text("EXPLICIT_REFERENCE_EVENT_1")
        options.select_by_visible_text("EXPLICIT_REFERENCE_EVENT_3")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the explicit_ref_in input
        input_element = self.driver.find_element_by_id("explicit-refs-ers-in-text")
        functions.click(input_element)

        input_element.send_keys("EXPLICIT_REFERENCE_EVENT_2")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("explicit-refs-ers-in-select"))
        options.select_by_visible_text("EXPLICIT_REFERENCE_EVENT_2")

        notInButton = self.driver.find_element_by_id("explicit-refs-ers-in-checkbox")        
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        #end if

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generate
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

    def test_explicit_refs_query_group_filter(self):

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
                           "validity_stop": "2018-06-05T08:07:36"},
            "explicit_references": [{
                "group": "EXPL_GROUP_1",
                "name": "EXPLICIT_REFERENCE_1",
                "links": [{"name": "LINK_NAME_1",
                       "link": "EXPLICIT_REFERENCE_LINK_1"}]
                },{
                "group": "EXPL_GROUP_2",
                "name": "EXPLICIT_REFERENCE_2",
                "links": [{"name": "LINK_NAME_2",
                       "link": "EXPLICIT_REFERENCE_LINK_2"}]
                }]
            },{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_2.xml",
                        "reception_time": "2018-07-05T02:07:03",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "explicit_references": [{
                "group": "EXPL_GROUP_1",
                "name": "EXPLICIT_REFERENCE_3",
                "links": [{"name": "LINK_NAME_3",
                       "link": "EXPLICIT_REFERENCE_LINK_3"}]
                }]
            }
        ]}

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
        input_element.send_keys("EXPL_GROUP_2")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the group_like input
        input_element = self.driver.find_element_by_id("explicit-refs-group-text")
        input_element.send_keys("EXPL_GROUP_2")

        menu = Select(self.driver.find_element_by_id("explicit-refs-group-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the group_in input
        input_element = self.driver.find_element_by_id("explicit-refs-groups-in-text")
        functions.click(input_element)

        input_element.send_keys("EXPL_GROUP_1")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("explicit-refs-groups-in-select"))
        options.select_by_visible_text("EXPL_GROUP_1")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the group_in input
        input_element = self.driver.find_element_by_id("explicit-refs-groups-in-text")
        functions.click(input_element)

        input_element.send_keys("EXPL_GROUP_2")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("explicit-refs-groups-in-select"))
        options.select_by_visible_text("EXPL_GROUP_2")

        notInButton = self.driver.find_element_by_id("explicit-refs-groups-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        #end if

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generate
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

    def test_explicit_refs_query_source_filter(self):

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
                           "validity_stop": "2018-06-05T08:07:36"},
            "explicit_references": [{
                "group": "EXPL_GROUP_1",
                "name": "EXPLICIT_REFERENCE_1"
                },{
                "group": "EXPL_GROUP_2",
                "name": "EXPLICIT_REFERENCE_2"
                }],
            "events": [{
                "explicit_reference": "EXPLICIT_REFERENCE_1",
                "gauge": {"name": "GAUGE_NAME_1",
                          "system": "GAUGE_SYSTEM_1",
                          "insertion_type": "SIMPLE_UPDATE"},
                "start": "2018-06-05T04:07:05",
                "stop": "2018-06-05T06:07:31"
                }]
            },{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_2.xml",
                        "reception_time": "2018-07-05T02:07:03",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "explicit_references": [{
                "group": "EXPL_GROUP_1",
                "name": "EXPLICIT_REFERENCE_3"
                }]
            }
        ]}

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
        input_element.send_keys("source_1.xml")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the source_like input
        input_element = self.driver.find_element_by_id("explicit-refs-source-text")
        input_element.send_keys("source_1.xml")

        menu = Select(self.driver.find_element_by_id("explicit-refs-source-operator"))
        menu.select_by_visible_text("notlike")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the source_in input
        input_element = self.driver.find_element_by_id("explicit-refs-sources-in-text")
        functions.click(input_element)

        input_element.send_keys("source_1.xml")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("explicit-refs-sources-in-select"))
        options.select_by_visible_text("source_1.xml")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        # Fill the source_in input
        input_element = self.driver.find_element_by_id("explicit-refs-sources-in-text")
        functions.click(input_element)

        input_element.send_keys("source_2.xml")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("explicit-refs-sources-in-select"))
        options.select_by_visible_text("source_2.xml")

        notInButton = self.driver.find_element_by_id("explicit-refs-sources-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        #end if

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generate
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

    def test_explicit_refs_query_key_filter(self):

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
                           "validity_stop": "2018-06-05T08:07:36"},
            "events": [{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT_1",
                "gauge": {"name": "GAUGE_NAME_1",
                          "system": "GAUGE_SYSTEM_1",
                          "insertion_type": "EVENT_KEYS"},
                "start": "2018-06-05T04:07:03",
                "stop": "2018-06-05T06:07:36",
                "key": "EVENT_KEY_1"
                },{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT_2",
                "gauge": {"name": "GAUGE_NAME_2",
                          "system": "GAUGE_SYSTEM_2",
                          "insertion_type": "EVENT_KEYS"},
                "start": "2018-06-05T04:07:12",
                "stop": "2018-06-05T06:07:24",
                "key": "EVENT_KEY_2"
                }]
            },{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_2.xml",
                        "reception_time": "2018-07-05T02:07:03",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "events": [{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT_3",
                "gauge": {"name": "GAUGE_NAME_2",
                          "system": "GAUGE_SYSTEM_2",
                          "insertion_type": "EVENT_KEYS"},
                "start": "2018-06-05T04:07:05",
                "stop": "2018-06-05T06:07:31",
                "key": "EVENT_KEY_3"
                }]
            }
        ]}

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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

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
        input_element.send_keys("EVENT_KEY_3")
        input_element.send_keys(Keys.LEFT_SHIFT)

        options = Select(self.driver.find_element_by_id("explicit-refs-keys-in-select"))
        options.select_by_visible_text("EVENT_KEY_2")
        options.select_by_visible_text("EVENT_KEY_3")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generate
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

    def test_explicit_refs_query_gauge_name_filter(self):

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
                           "validity_stop": "2018-06-05T08:07:36"},
            "events": [{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT_1",
                "gauge": {"name": "GAUGE_NAME_1",
                          "system": "GAUGE_SYSTEM_1",
                          "insertion_type": "EVENT_KEYS"},
                "start": "2018-06-05T04:07:03",
                "stop": "2018-06-05T06:07:36",
                "key": "EVENT_KEY"
                },{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT_2",
                "gauge": {"name": "GAUGE_NAME_2",
                          "system": "GAUGE_SYSTEM_2",
                          "insertion_type": "EVENT_KEYS"},
                "start": "2018-06-05T04:07:12",
                "stop": "2018-06-05T06:07:24",
                "key": "EVENT_KEY_2"
                }]
            },{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_2.xml",
                        "reception_time": "2018-07-05T02:07:03",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "events": [{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT_3",
                "gauge": {"name": "GAUGE_NAME_2",
                          "system": "GAUGE_SYSTEM_2",
                          "insertion_type": "EVENT_KEYS"},
                "start": "2018-06-05T04:07:05",
                "stop": "2018-06-05T06:07:31",
                "key": "EVENT_KEY_3"
                }]
            }
        ]}

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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generate
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

    def test_explicit_refs_query_gauge_system_filter(self):

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
                           "validity_stop": "2018-06-05T08:07:36"},
            "events": [{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT",
                "gauge": {"name": "GAUGE_NAME_1",
                          "system": "GAUGE_SYSTEM_1",
                          "insertion_type": "EVENT_KEYS"},
                "start": "2018-06-05T04:07:03",
                "stop": "2018-06-05T06:07:36",
                "key": "EVENT_KEY"
                },{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT_2",
                "gauge": {"name": "GAUGE_NAME_2",
                          "system": "GAUGE_SYSTEM_2",
                          "insertion_type": "EVENT_KEYS"},
                "start": "2018-06-05T04:07:12",
                "stop": "2018-06-05T06:07:24",
                "key": "EVENT_KEY_2"
                }]
            },{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_2.xml",
                        "reception_time": "2018-07-05T02:07:03",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "events": [{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT",
                "gauge": {"name": "GAUGE_NAME_2",
                          "system": "GAUGE_SYSTEM_2",
                          "insertion_type": "EVENT_KEYS"},
                "start": "2018-06-05T04:07:05",
                "stop": "2018-06-05T06:07:31",
                "key": "EVENT_KEY_3"
                }]
            }
        ]}

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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generate
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

    def test_explicit_refs_query_events_value_text(self):

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
                        "events": [{"gauge": {"name": "GAUGE_NAME",
                                              "system": "GAUGE_SYSTEM",
                                              "insertion_type": "SIMPLE_UPDATE"},
                                    "explicit_reference": "EXPLICIT_REFERENCE_1",
                                    "start": "2018-06-05T02:07:03",
                                    "stop": "2018-06-05T08:07:36",
                                    "values": [{"name": "VALUES",
                                               "type": "object",
                                               "values": [
                                                   {"type": "text",
                                                    "name": "textname_1",
                                                    "value": "textvalue_1"
                                                    }]
                                                }]
                                    },
                                    {"gauge": {"name": "GAUGE_NAME",
                                              "system": "GAUGE_SYSTEM",
                                              "insertion_type": "SIMPLE_UPDATE"},
                                    "explicit_reference": "EXPLICIT_REFERENCE_2",
                                    "start": "2018-06-05T02:07:03",
                                    "stop": "2018-06-05T08:07:36"}
                        ]
                    }]
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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "text", "textname_1", "textvalue_1", "!=", "==", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

    def test_explicit_refs_query_events_value_timestamp(self):

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
                        "events": [{"gauge": {"name": "GAUGE_NAME",
                                              "system": "GAUGE_SYSTEM",
                                              "insertion_type": "SIMPLE_UPDATE"},
                                    "explicit_reference": "EXPLICIT_REFERENCE_1",
                                    "start": "2018-06-05T02:07:03",
                                    "stop": "2018-06-05T08:07:36",
                                    "values": [{"name": "VALUES",
                                               "type": "object",
                                               "values": [
                                                   {"type": "timestamp",
                                                    "name": "timestamp_name_1",
                                                    "value": "2019-04-26T14:14:14"
                                                    }]
                                                }]
                        },
                                    {"gauge": {"name": "GAUGE_NAME",
                                              "system": "GAUGE_SYSTEM",
                                              "insertion_type": "SIMPLE_UPDATE"},
                                    "explicit_reference": "EXPLICIT_REFERENCE_2",
                                    "start": "2018-06-05T02:07:03",
                                    "stop": "2018-06-05T08:07:36"}]
                    }]}

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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", "==",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", ">", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", "==", ">", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", ">", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", ">=", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", "==", ">=", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", ">=",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", "<",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", "<", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", "<=", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", "==", "<=",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", "<=", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", "!=",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", "==", "!=", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

    def test_explicit_refs_query_events_value_double(self):

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
                        "events": [{"gauge": {"name": "GAUGE_NAME",
                                              "system": "GAUGE_SYSTEM",
                                              "insertion_type": "SIMPLE_UPDATE"},
                                    "explicit_reference": "EXPLICIT_REFERENCE_1",
                                    "start": "2018-06-05T02:07:03",
                                    "stop": "2018-06-05T08:07:36",
                                    "values": [{"name": "VALUES",
                                               "type": "object",
                                               "values": [
                                                   {"type": "double",
                                                    "name": "double_name_1",
                                                    "value": "3.5"
                                                    }]
                                                }]
                        },
                                    {"gauge": {"name": "GAUGE_NAME",
                                              "system": "GAUGE_SYSTEM",
                                              "insertion_type": "SIMPLE_UPDATE"},
                                    "explicit_reference": "EXPLICIT_REFERENCE_2",
                                    "start": "2018-06-05T02:07:03",
                                    "stop": "2018-06-05T08:07:36"}]
                    }]
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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "double", "double_name_1", "3.5", "!=", "==",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "double", "double_name_1", "3.5", "==", ">",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "double", "double_name_1", "3.25", "==", ">", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "double", "double_name_1", "3.75", "==", ">",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "double", "double_name_1", "3.5", "==", ">=", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "double", "double_name_1", "3.25", "==", ">=", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "double", "double_name_1", "3.75", "==", ">=",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "double", "double_name_1", "3.5", "==", "<",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "double", "double_name_1", "3.25", "==", "<",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "double", "double_name_1", "3.75", "==", "<", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "double", "double_name_1", "3.5", "==", "<=", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "double", "double_name_1", "3.25", "==", "<=",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "double", "double_name_1", "3.75", "==", "<=", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "double", "double_name_1", "3.5", "==", "!=",1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait, "explicit-refs-events", "double", "double_name_1", "3.25", "==", "!=", 1)
        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

    def test_explicit_refs_query_events_two_values(self):

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
                           "validity_stop": "2018-06-05T08:07:36"},
            "events": [{"gauge": {"name": "GAUGE_NAME",
                                  "system": "GAUGE_SYSTEM",
                                  "insertion_type": "SIMPLE_UPDATE"},
                        "explicit_reference": "EXPLICIT_REFERENCE_1",
                        "start": "2018-06-05T02:07:03",
                        "stop": "2018-06-05T08:07:36",
                        "values": [{"name": "VALUES",
                                   "type": "object",
                                   "values": [
                                       {"name": "text_name_1",
                                        "type": "text",
                                        "value": "text_value_1"
                                       }]
                                   }]
                    }]
            },{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE_2",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_2.xml",
                        "reception_time": "2018-07-05T02:07:03",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "events": [{"gauge": {"name": "GAUGE_NAME",
                                  "system": "GAUGE_SYSTEM",
                                  "insertion_type": "SIMPLE_UPDATE"},
                        "explicit_reference": "EXPLICIT_REFERENCE_2",
                        "start": "2018-06-05T02:07:03",
                        "stop": "2018-06-05T08:07:36",
                        "values": [{"name": "VALUES",
                                   "type": "object",
                                   "values":  [
                                   {"name": "text_name_1",
                                    "type": "text",
                                    "value": "text_value_1"
                                       },
                                   {"name": "double_name_1",
                                    "type": "double",
                                    "value": "1.4"
                                       }]
                                   }]
                        },{"gauge": {"name": "GAUGE_NAME",
                                              "system": "GAUGE_SYSTEM",
                                              "insertion_type": "SIMPLE_UPDATE"},
                                    "explicit_reference": "EXPLICIT_REFERENCE_3",
                                    "start": "2018-06-05T02:07:03",
                                    "stop": "2018-06-05T08:07:36",
                                    "values": [{"name": "VALUES",
                                               "type": "object",
                                               "values": [
                                                   {"name": "text_name_3",
                                                    "type": "text",
                                                    "value": "text_value_2"
                                                   }]
                                               }]
                                    }]
            }]
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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

    def test_explicit_refs_query_annotation_name_filter(self):

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
                           "validity_stop": "2018-06-05T08:07:36"},
            "annotations": [{
                "explicit_reference" : "EXPLICIT_REFERENCE_1",
                "annotation_cnf": {
                    "name": "NAME_1",
                    "system": "SYSTEM"
                    },
                "values": [{
                    "name": "details",
                    "type": "object",
                    "values": []
                    }]
                }]
            },{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE_2",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_2.xml",
                        "reception_time": "2018-07-05T02:07:03",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "annotations": [{
                "explicit_reference" : "EXPLICIT_REFERENCE_2",
                "annotation_cnf": {
                    "name": "NAME_1",
                    "system": "SYSTEM"
                    },
                "values": [{
                    "name": "details",
                    "type": "object",
                    "values": []
                    }]
                },{
                "explicit_reference" : "EXPLICIT_REFERENCE_2",
                "annotation_cnf": {
                    "name": "NAME_2",
                    "system": "SYSTEM"
                    },
                "values": [{
                    "name": "details",
                    "type": "object",
                    "values": []
                    }]
                }]
            }]
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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(explicit_refs_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generate
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(explicit_refs_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

    def test_explicit_refs_query_annotation_system_filter(self):

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
                           "validity_stop": "2018-06-05T08:07:36"},
            "annotations": [{
                "explicit_reference" : "EXPLICIT_REFERENCE_1",
                "annotation_cnf": {
                    "name": "NAME_1",
                    "system": "SYSTEM_1"
                    },
                "values": [{
                    "name": "details",
                    "type": "object",
                    "values": []
                    }]
                }]
            },{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE_2",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_2.xml",
                        "reception_time": "2018-07-05T02:07:03",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "annotations": [{
                "explicit_reference" : "EXPLICIT_REFERENCE_2",
                "annotation_cnf": {
                    "name": "NAME_1",
                    "system": "SYSTEM_1"
                    },
                "values": [{
                    "name": "details",
                    "type": "object",
                    "values": []
                    }]
                },{
                "explicit_reference" : "EXPLICIT_REFERENCE_2",
                "annotation_cnf": {
                    "name": "NAME_2",
                    "system": "SYSTEM_2"
                    },
                "values": [{
                    "name": "details",
                    "type": "object",
                    "values": []
                    }]
                }]
            }]
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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(explicit_refs_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(explicit_refs_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generate
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(explicit_refs_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

    def test_explicit_refs_query_ingestion_time(self):

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
                        "explicit_references": [{
                            "group": "EXPL_GROUP_1",
                            "name": "EXPLICIT_REFERENCE_1"
                            }]
                    }]
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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_ingestion_time(self.driver, wait, "explicit-refs-annotations", ingestion_time, ">", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_ingestion_time(self.driver, wait, "explicit-refs-annotations", ingestion_time, ">=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_ingestion_time(self.driver, wait, "explicit-refs-annotations", ingestion_time, "<", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_ingestion_time(self.driver, wait, "explicit-refs-annotations", ingestion_time,"<=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_ingestion_time(self.driver, wait, "explicit-refs-annotations", ingestion_time, "!=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

    def test_explicit_refs_query_annotations_value_text(self):

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
                           "validity_stop": "2018-06-05T08:07:36"},
            "annotations": [{
                "explicit_reference" : "EXPLICIT_REFERENCE",
                "annotation_cnf": {
                    "name": "NAME_1",
                    "system": "SYSTEM"
                    },
                "values": [{
                    "name": "details",
                    "type": "object",
                    "values": [
                        {"name": "text_name_1",
                         "type": "text",
                         "value": "text_value_1"
                        }]
                    }]
                }]
            },{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE_2",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_2.xml",
                        "reception_time": "2018-07-05T02:07:03",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "annotations": [{
                "explicit_reference" : "EXPLICIT_REFERENCE2",
                "annotation_cnf": {
                    "name": "NAME_1",
                    "system": "SYSTEM"
                    },
                "values": [{
                    "name": "details",
                    "type": "object",
                    "values":  [
                    {"name": "text_name_2",
                     "type": "text",
                     "value": "text_value_2"
                        }]
                    }]
                },{
                "explicit_reference" : "EXPLICIT_REFERENCE3",
                "annotation_cnf": {
                    "name": "NAME_2",
                    "system": "SYSTEM"
                    },
                "values": [{
                    "name": "details",
                    "type": "object",
                    "values": [
                        {"name": "text_name_3",
                         "type": "text",
                         "value": "text_value_2"
                        }]
                    }]
                }]
            }]
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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "text", "text_name_1", "text_value_2", "!=", "==", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert  number_of_elements == 2

    def test_explicit_refs_query_annotations_value_timestamp(self):

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
                           "validity_stop": "2018-06-05T08:07:36"},
            "annotations": [{
                "explicit_reference" : "EXPLICIT_REFERENCE",
                "annotation_cnf": {
                    "name": "NAME_1",
                    "system": "SYSTEM"
                    },
                "values": [{
                    "name": "details",
                    "type": "object",
                    "values": [
                        {"name": "timestamp_name_1",
                         "type": "timestamp",
                         "value": "2019-04-26T14:14:14"
                        }]
                    }]
                }]
            }]
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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", "==", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", ">", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", "==", ">", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", ">", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", ">=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", "==", ">=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", ">=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", "<", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", "==", "<", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", "<", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", "<=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", "==", "<=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", "<=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", "==", "!=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", "==", "!=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", "==", "!=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

    def test_explicit_refs_query_annotations_value_double(self):

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
                           "validity_stop": "2018-06-05T08:07:36"},
            "annotations": [{
                "explicit_reference" : "EXPLICIT_REFERENCE",
                "annotation_cnf": {
                    "name": "NAME_1",
                    "system": "SYSTEM"
                    },
                "values": [{
                    "name": "details",
                    "type": "object",
                    "values": [
                        {"name": "double_name_1",
                         "type": "double",
                         "value": "3.5"
                        }]
                    }]
                }]
            }]
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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "double", "double_name_1", "3.5", "!=", "==", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "double", "double_name_1", "3.5", "==", ">", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "double", "double_name_1", "3.25", "==", ">", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "double", "double_name_1", "3.75", "==", ">", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "double", "double_name_1", "3.5", "==", ">=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "double", "double_name_1", "3.25", "==", ">=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "double", "double_name_1", "3.75", "==", ">=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "double", "double_name_1", "3.5", "==", "<", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "double", "double_name_1", "3.25", "==", "<", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "double", "double_name_1", "3.75", "==", "<", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "double", "double_name_1", "3.5", "==", "<=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "double", "double_name_1", "3.25", "==", "<=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "double", "double_name_1", "3.75", "==", "<=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "double", "double_name_1", "3.5", "==", "!=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "double", "double_name_1", "3.25", "==", "!=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_value(self.driver, wait,"explicit-refs-annotations", "double", "double_name_1", "3.75", "==", "!=", 1)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

    def test_explicit_refs_query_annotations_two_values(self):

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
                           "validity_stop": "2018-06-05T08:07:36"},
            "annotations": [{
                "explicit_reference" : "EXPLICIT_REFERENCE_1",
                "annotation_cnf": {
                    "name": "NAME_1",
                    "system": "SYSTEM"
                    },
                "values": [{
                    "name": "details",
                    "type": "object",
                    "values": [
                        {"name": "text_name_1",
                         "type": "text",
                         "value": "text_value_1"
                        }]
                    }]
                }]
            },{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE_2",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_2.xml",
                        "reception_time": "2018-07-05T02:07:03",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "annotations": [{
                "explicit_reference" : "EXPLICIT_REFERENCE_2",
                "annotation_cnf": {
                    "name": "NAME_1",
                    "system": "SYSTEM"
                    },
                "values": [{
                    "name": "details",
                    "type": "object",
                    "values":  [
                    {"name": "text_name_1",
                     "type": "text",
                     "value": "text_value_1"
                        },
                    {"name": "double_name_1",
                     "type": "double",
                     "value": "1.4"
                        }]
                    }]
                },{
                "explicit_reference" : "EXPLICIT_REFERENCE_3",
                "annotation_cnf": {
                    "name": "NAME_2",
                    "system": "SYSTEM"
                    },
                "values": [{
                    "name": "details",
                    "type": "object",
                    "values": [
                        {"name": "text_name_3",
                         "type": "text",
                         "value": "text_value_2"
                        }]
                    }]
                }]
            }]
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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        assert True

    def test_explicit_refs_query_period(self):

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
                           "validity_start": "2018-06-05T00:00:00",
                           "validity_stop": "2018-06-05T08:00:00"},
            "events": [{"gauge": {"name": "GAUGE_NAME",
                                  "system": "GAUGE_SYSTEM",
                                  "insertion_type": "SIMPLE_UPDATE"},
                        "explicit_reference": "EXPLICIT_REFERENCE_EVENT_1",
                        "start": "2018-06-05T02:00:00",
                        "stop": "2018-06-05T03:00:00",
                        "values": [{"name": "VALUES",
                                   "type": "object",
                                   "values": [
                                       {"name": "text_name_1",
                                        "type": "text",
                                        "value": "text_value_1"
                                       }]
                                   }]
                    },{"gauge": {"name": "GAUGE_NAME_2",
                                  "system": "GAUGE_SYSTEM_2",
                                  "insertion_type": "SIMPLE_UPDATE"},
                        "explicit_reference": "EXPLICIT_REFERENCE_EVENT_2",
                        "start": "2018-06-05T03:00:00",
                        "stop": "2018-06-05T04:00:00",
                        "values": [{"name": "VALUES",
                                   "type": "object",
                                   "values": [
                                       {"name": "text_name_2",
                                        "type": "text",
                                        "value": "text_value_2"
                                       }]
                                   }]
                    },{"gauge": {"name": "GAUGE_NAME_3",
                                  "system": "GAUGE_SYSTEM_3",
                                  "insertion_type": "SIMPLE_UPDATE"},
                        "explicit_reference": "EXPLICIT_REFERENCE_EVENT_3",
                        "start": "2018-06-05T04:00:00",
                        "stop": "2018-06-05T05:00:00",
                        "values": [{"name": "VALUES",
                                   "type": "object",
                                   "values": [
                                       {"name": "text_name_3",
                                        "type": "text",
                                        "value": "text_value_3"
                                       }]
                                   }]
                    }]
            }]
        }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5)

        ## == ## Full period##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_period(self.driver, wait, "explicit-refs-events", 1,  "2018-06-05T03:00:00", "==","2018-06-05T04:00:00", "==")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## >= ## Only Start##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_period(self.driver, wait, "explicit-refs-events", 1, start_value = "2018-06-05T03:00:00", start_operator = ">=")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## != ## Only End##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_period(self.driver, wait, "explicit-refs-events", 1, end_value = "2018-06-05T04:00:00", end_operator = "!=")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## > ## Only Start## < ## Only Start##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_period(self.driver, wait, "explicit-refs-events", 1, start_value = "2018-06-05T01:30:00", start_operator = ">")
        functions.click(self.driver.find_element_by_id("explicit-refs-events-start-stop-add-value"))
        functions.fill_period(self.driver, wait, "explicit-refs-events", 2, start_value = "2018-06-05T03:00:00", start_operator = "<")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        ## <= ## Start## > ## End## != ## Start## >= ## End##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Explicit references")

        functions.fill_period(self.driver, wait, "explicit-refs-events", 1, start_value = "2018-06-05T03:00:00", start_operator = "<=", end_value = "2018-06-05T02:30:00", end_operator = ">")
        functions.click(self.driver.find_element_by_id("explicit-refs-events-start-stop-add-value"))
        functions.fill_period(self.driver, wait, "explicit-refs-events", 2, start_value = "2018-06-05T04:00:00", start_operator = "!=", end_value = "2018-06-05T03:00:00", end_operator = ">=")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-submit-button")))
        functions.click(submit_button)

        # Check table generated
        explicit_refs_table = wait.until(EC.visibility_of_element_located((By.ID,"explicit-refs-table")))
        number_of_elements = len(explicit_refs_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2
