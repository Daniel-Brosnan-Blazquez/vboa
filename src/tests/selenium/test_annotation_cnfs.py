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
import tests.selenium.functions as functions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
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


class TestEngine(unittest.TestCase):
    def setUp(self):
        # Create the engine to manage the data
        self.engine_eboa = Engine()
        self.query_eboa = Query()

        # Create session to connect to the database
        self.session = Session()

        # Clear all tables before executing the test
        self.query_eboa.clear_db()

        self.options = Options()
        self.options.headless = True
        subprocess.call(["pkill", "firefox"])

    def tearDown(self):
        # Close connections to the DDBB
        self.engine_eboa.close_session()
        self.query_eboa.close_session()
        self.session.close()

    def test_annotation_cnfs_no_filter(self):

        # Insert data
        data = {"operations": [{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source.xml",
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

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Annotation Cnfs")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[6]/div/div/div/div/div/form/div[3]/button')))
        submitButton.click()

        # Check table generated
        annot_cnf_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(annot_cnf_table.find_elements_by_xpath("tbody/tr"))

        driver.quit()

        assert number_of_elements == 2

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

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        ## Like ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Annotation Cnfs")

        # Fill the annotation_name_like input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[6]/div/div/div/div/div/form/div[1]/div[1]/div[1]/input")
        inputElement.send_keys("NAME_2")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[6]/div/div/div/div/div/form/div[3]/button')))
        submitButton.click()

        # Check table generated
        annot_cnf_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(annot_cnf_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annot_cnf_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not like ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Annotation Cnfs")

        # Fill the annotation_name_like input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[6]/div/div/div/div/div/form/div[1]/div[1]/div[1]/input")
        inputElement.send_keys("NAME_2")

        notLikeButton = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[6]/div/div/div/div/div/form/div[1]/div[1]/div[1]/label")
        if not notLikeButton.find_element_by_xpath("input").is_selected():
                    notLikeButton.click()

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[6]/div/div/div/div/div/form/div[3]/button')))
        submitButton.click()

        # Check table generated
        annot_cnf_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(annot_cnf_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## In ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Annotation Cnfs")
        # Fill the annotation_name_in input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[6]/div/div/div/div/div/form/div[1]/div[2]/div[1]/div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("NAME_1")
        inputElement.send_keys(Keys.RETURN)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[6]/div/div/div/div/div/form/div[3]/button')))
        submitButton.click()

        # Check table generated
        annot_cnf_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(annot_cnf_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not in ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Annotation Cnfs")


        # Fill the annotation_name_in input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[6]/div/div/div/div/div/form/div[1]/div[2]/div[1]/div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("NAME_2")
        inputElement.send_keys(Keys.RETURN)

        notInButton = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[6]/div/div/div/div/div/form/div[1]/div[2]/div[1]/label")
        if not notInButton.find_element_by_xpath("input").is_selected():
            notInButton.click()

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[6]/div/div/div/div/div/form/div[3]/button')))
        submitButton.click()

        # Check table generated
        annot_cnf_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(annot_cnf_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annot_cnf_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        driver.quit()

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

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        ## Like ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Annotation Cnfs")

        # Fill the annotation_system_like input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[6]/div/div/div/div/div/form/div[1]/div[1]/div[2]/input")
        inputElement.send_keys("SYSTEM_2")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[6]/div/div/div/div/div/form/div[3]/button')))
        submitButton.click()

        # Check table generated
        annot_cnf_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(annot_cnf_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annot_cnf_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not like ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Annotation Cnfs")

        # Fill the annotation_system_like input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[6]/div/div/div/div/div/form/div[1]/div[1]/div[2]/input")
        inputElement.send_keys("SYSTEM_2")

        notLikeButton = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[6]/div/div/div/div/div/form/div[1]/div[1]/div[2]/label")
        if not notLikeButton.find_element_by_xpath("input").is_selected():
            notLikeButton.click()

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[6]/div/div/div/div/div/form/div[3]/button')))
        submitButton.click()

        # Check table generated
        annot_cnf_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(annot_cnf_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## In ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Annotation Cnfs")
        # Fill the annotation_system_in input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[6]/div/div/div/div/div/form/div[1]/div[2]/div[2]/div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("SYSTEM_1")
        inputElement.send_keys(Keys.RETURN)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[6]/div/div/div/div/div/form/div[3]/button')))
        submitButton.click()

        # Check table generated
        annot_cnf_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(annot_cnf_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not in ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Annotation Cnfs")

        # Fill the annotation_system_in input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[6]/div/div/div/div/div/form/div[1]/div[2]/div[2]/div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("SYSTEM_2")
        inputElement.send_keys(Keys.RETURN)

        notInButton = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[6]/div/div/div/div/div/form/div[1]/div[2]/div[2]/label")
        if not notInButton.find_element_by_xpath("input").is_selected():
            notInButton.click()

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[6]/div/div/div/div/div/form/div[3]/button')))
        submitButton.click()

        # Check table generated
        annot_cnf_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(annot_cnf_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annot_cnf_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        driver.quit()

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

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        ## Like ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Annotation Cnfs")

        # Fill the dim_signature_like input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[6]/div/div/div/div/div/form/div[2]/div[1]/input")
        inputElement.send_keys("DIM_SIGNATURE_2")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[6]/div/div/div/div/div/form/div[3]/button')))
        submitButton.click()

        # Check table generated
        annot_cnf_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(annot_cnf_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annot_cnf_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not like ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Annotation Cnfs")

        # Fill the dim_signature_like input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[6]/div/div/div/div/div/form/div[2]/div[1]/input")
        inputElement.send_keys("DIM_SIGNATURE_2")

        notLikeButton = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[6]/div/div/div/div/div/form/div[2]/div[1]/label")
        if not notLikeButton.find_element_by_xpath("input").is_selected():
            notLikeButton.click()
        #end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[6]/div/div/div/div/div/form/div[3]/button')))
        submitButton.click()

        # Check table generated
        annot_cnf_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(annot_cnf_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## In ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Annotation Cnfs")

        # Fill the dim_signature_in input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[6]/div/div/div/div/div/form/div[2]/div[2]/div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("DIM_SIGNATURE_1")
        inputElement.send_keys(Keys.RETURN)
        inputElement.click()
        inputElement.send_keys("DIM_SIGNATURE_3")
        inputElement.send_keys(Keys.RETURN)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[6]/div/div/div/div/div/form/div[3]/button')))
        submitButton.click()

        # Check table generated
        annot_cnf_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(annot_cnf_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not in ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Annotation Cnfs")

        # Fill the dim_signature_in input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[6]/div/div/div/div/div/form/div[2]/div[2]/div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("DIM_SIGNATURE_2")
        inputElement.send_keys(Keys.RETURN)

        notInButton = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[6]/div/div/div/div/div/form/div[2]/div[2]/label")
        if not notInButton.find_element_by_xpath("input").is_selected():
            notInButton.click()
        #end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[6]/div/div/div/div/div/form/div[3]/button')))
        submitButton.click()

        # Check table generate
        annot_cnf_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(annot_cnf_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annot_cnf_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        driver.quit()

        assert number_of_elements == 2
