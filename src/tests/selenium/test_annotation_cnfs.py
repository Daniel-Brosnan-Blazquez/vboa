"""
Automated tests for the annotation_cnfs tab

Written by DEIMOS Space S.L. (femd)

module vboa
"""
import os
import sys
import unittest
import time
import subprocess
import datetime
import re
import tests.selenium.functions as functions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
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


class TestAnnotationCnfsTab(unittest.TestCase):

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

    def test_annotation_cnfs_query_no_filter(self):

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
            "annotations": [{
                "explicit_reference" : "EXPLICIT_REFERENCE",
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
            }]}

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5);

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotation Cnfs")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-cnfs-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annot_cnf_table = wait.until(EC.visibility_of_element_located((By.ID,"annotation-cnfs-table")))
        number_of_elements = len(annot_cnf_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        # Check name
        name = annot_cnf_table.find_elements_by_xpath("tbody/tr[1]/td[1]")

        assert name[0].text == "NAME_1"

        # Check system
        system = annot_cnf_table.find_elements_by_xpath("tbody/tr[1]/td[2]")

        assert system[0].text == "SYSTEM"

        # Check dim_signature
        dim_signature = annot_cnf_table.find_elements_by_xpath("tbody/tr[1]/td[3]")

        assert dim_signature[0].text == "DIM_SIGNATURE"

        # Check uuid
        uuid = annot_cnf_table.find_elements_by_xpath("tbody/tr[1]/td[4]")

        assert re.match("........-....-....-....-............", uuid[0].text)

    def test_annotation_cnfs_query_annotation_name_filter(self):

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

        wait = WebDriverWait(self.driver,5);

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotation Cnfs")

        # Fill the annotation_name_like input
        inputElement = self.driver.find_element_by_id("annotation-cnfs-annotation-names-like-text")
        inputElement.send_keys("NAME_2")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-cnfs-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annot_cnf_table = wait.until(EC.visibility_of_element_located((By.ID,"annotation-cnfs-table")))
        number_of_elements = len(annot_cnf_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annot_cnf_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotation Cnfs")

        # Fill the annotation_name_like input
        inputElement = self.driver.find_element_by_id("annotation-cnfs-annotation-names-like-text")
        inputElement.send_keys("NAME_2")

        notLikeButton = self.driver.find_element_by_id("annotation-cnfs-annotation-names-like-checkbox")
        if not notLikeButton.find_element_by_xpath("input").is_selected():
                    functions.select_checkbox(notLikeButton)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-cnfs-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annot_cnf_table = wait.until(EC.visibility_of_element_located((By.ID,"annotation-cnfs-table")))
        number_of_elements = len(annot_cnf_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotation Cnfs")
        # Fill the annotation_name_in input
        inputElement = self.driver.find_element_by_id("annotation-cnfs-annotation-names-in-text").find_element_by_xpath("../div/ul/li/input")
        functions.click(inputElement)

        assert len(self.driver.find_element_by_id("annotation-cnfs-annotation-names-in-text").find_elements_by_xpath("option")) == 2

        inputElement.send_keys("NAME_1")
        inputElement.send_keys(Keys.RETURN)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-cnfs-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annot_cnf_table = wait.until(EC.visibility_of_element_located((By.ID,"annotation-cnfs-table")))
        number_of_elements = len(annot_cnf_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotation Cnfs")


        # Fill the annotation_name_in input
        inputElement = self.driver.find_element_by_id("annotation-cnfs-annotation-names-in-text").find_element_by_xpath("../div/ul/li/input")
        functions.click(inputElement)

        assert len(self.driver.find_element_by_id("annotation-cnfs-annotation-names-in-text").find_elements_by_xpath("option")) == 2

        inputElement.send_keys("NAME_2")
        inputElement.send_keys(Keys.RETURN)

        notInButton = self.driver.find_element_by_id("annotation-cnfs-annotation-names-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-cnfs-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annot_cnf_table = wait.until(EC.visibility_of_element_located((By.ID,"annotation-cnfs-table")))
        number_of_elements = len(annot_cnf_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annot_cnf_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

    def test_annotation_cnfs_query_annotation_system_filter(self):

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

        wait = WebDriverWait(self.driver,5);

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotation Cnfs")

        # Fill the annotation_system_like input
        inputElement = self.driver.find_element_by_id("annotation-cnfs-annotation-system-like-text")
        inputElement.send_keys("SYSTEM_2")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-cnfs-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annot_cnf_table = wait.until(EC.visibility_of_element_located((By.ID,"annotation-cnfs-table")))
        number_of_elements = len(annot_cnf_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annot_cnf_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotation Cnfs")

        # Fill the annotation_system_like input
        inputElement = self.driver.find_element_by_id("annotation-cnfs-annotation-system-like-text")
        inputElement.send_keys("SYSTEM_2")

        notLikeButton = self.driver.find_element_by_id("annotation-cnfs-annotation-system-like-checkbox")
        if not notLikeButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notLikeButton)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-cnfs-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annot_cnf_table = wait.until(EC.visibility_of_element_located((By.ID,"annotation-cnfs-table")))
        number_of_elements = len(annot_cnf_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotation Cnfs")
        # Fill the annotation_system_in input
        inputElement = self.driver.find_element_by_id("annotation-cnfs-annotation-system-in-text").find_element_by_xpath("../div/ul/li/input")
        functions.click(inputElement)

        assert len(self.driver.find_element_by_id("annotation-cnfs-annotation-system-in-text").find_elements_by_xpath("option")) == 2

        inputElement.send_keys("SYSTEM_1")
        inputElement.send_keys(Keys.RETURN)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-cnfs-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annot_cnf_table = wait.until(EC.visibility_of_element_located((By.ID,"annotation-cnfs-table")))
        number_of_elements = len(annot_cnf_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotation Cnfs")

        # Fill the annotation_system_in input
        inputElement = self.driver.find_element_by_id("annotation-cnfs-annotation-system-in-text").find_element_by_xpath("../div/ul/li/input")
        functions.click(inputElement)

        assert len(self.driver.find_element_by_id("annotation-cnfs-annotation-system-in-text").find_elements_by_xpath("option")) == 2

        inputElement.send_keys("SYSTEM_2")
        inputElement.send_keys(Keys.RETURN)

        notInButton = self.driver.find_element_by_id("annotation-cnfs-annotation-system-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-cnfs-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annot_cnf_table = wait.until(EC.visibility_of_element_located((By.ID,"annotation-cnfs-table")))
        number_of_elements = len(annot_cnf_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annot_cnf_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

    def test_annotation_cnfs_query_dim_signature_filter(self):

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
                           "generation_time": "2018-07-05T14:14:14",
                           "validity_start": "2018-06-05T14:14:14",
                           "validity_stop": "2018-06-06T11:57:17"},
            "annotations": [{
                "explicit_reference" : "EXPLICIT_REFERENCE",
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
            },{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE_3",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_3.xml",
                        "reception_time": "2018-07-05T02:07:03",
                           "generation_time": "2018-07-05T02:07:13",
                           "validity_start": "2018-06-05T03:09:33",
                           "validity_stop": "2018-06-05T08:17:46"},
            "annotations": [{
                "explicit_reference" : "EXPLICIT_REFERENCE",
                "annotation_cnf": {
                    "name": "NAME_3",
                    "system": "SYSTEM_3"
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

        wait = WebDriverWait(self.driver,5);

        ## Like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotation Cnfs")

        # Fill the dim_signature_like input
        inputElement = self.driver.find_element_by_id("annotation-cnfs-dim-signature-like-text")
        inputElement.send_keys("DIM_SIGNATURE_2")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-cnfs-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annot_cnf_table = wait.until(EC.visibility_of_element_located((By.ID,"annotation-cnfs-table")))
        number_of_elements = len(annot_cnf_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annot_cnf_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotation Cnfs")

        # Fill the dim_signature_like input
        inputElement = self.driver.find_element_by_id("annotation-cnfs-dim-signature-like-text")
        inputElement.send_keys("DIM_SIGNATURE_2")

        notLikeButton = self.driver.find_element_by_id("annotation-cnfs-dim-signature-like-checkbox")
        if not notLikeButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notLikeButton)
        #end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-cnfs-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annot_cnf_table = wait.until(EC.visibility_of_element_located((By.ID,"annotation-cnfs-table")))
        number_of_elements = len(annot_cnf_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotation Cnfs")

        # Fill the dim_signature_in input
        inputElement = self.driver.find_element_by_id("annotation-cnfs-dim-signature-in-text").find_element_by_xpath("../div/ul/li/input")
        functions.click(inputElement)

        assert len(self.driver.find_element_by_id("annotation-cnfs-dim-signature-in-text").find_elements_by_xpath("option")) == 3

        inputElement.send_keys("DIM_SIGNATURE_1")
        inputElement.send_keys(Keys.RETURN)
        functions.click(inputElement)
        inputElement.send_keys("DIM_SIGNATURE_3")
        inputElement.send_keys(Keys.RETURN)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-cnfs-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annot_cnf_table = wait.until(EC.visibility_of_element_located((By.ID,"annotation-cnfs-table")))
        number_of_elements = len(annot_cnf_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotation Cnfs")

        # Fill the dim_signature_in input
        inputElement = self.driver.find_element_by_id("annotation-cnfs-dim-signature-in-text").find_element_by_xpath("../div/ul/li/input")
        functions.click(inputElement)

        assert len(self.driver.find_element_by_id("annotation-cnfs-dim-signature-in-text").find_elements_by_xpath("option")) == 3

        inputElement.send_keys("DIM_SIGNATURE_2")
        inputElement.send_keys(Keys.RETURN)

        notInButton = self.driver.find_element_by_id("annotation-cnfs-dim-signature-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.select_checkbox(notInButton)
        #end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotation-cnfs-submit-button')))
        functions.click(submitButton)

        # Check table generate
        annot_cnf_table = wait.until(EC.visibility_of_element_located((By.ID,"annotation-cnfs-table")))
        number_of_elements = len(annot_cnf_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annot_cnf_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2
