"""
Automated tests for the gauges tab

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

    def test_gauges_no_filter_no_network(self):

        #insert data
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
            "events": [{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT",
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
            }]}

        #check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Gauges")

        #Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[5]/div/div/div/div/div/form/div[4]/button')))
        submitButton.click()

        #Check table generated
        annot_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(annot_table.find_elements_by_xpath("tbody/tr"))

        driver.quit()

        assert number_of_elements == 2

    def test_gauges_no_filter_with_network(self):

        #insert data
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
            "events": [{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT",
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
            }]}

        #check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Gauges")

        #Click on show network
        networkButton = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[5]/div/div/div/div/div/form/div[3]/label")
        if not networkButton.find_element_by_xpath('input').is_selected():
            networkButton.click()
        #end if

        #Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[5]/div/div/div/div/div/form/div[4]/button')))
        submitButton.click()

        #Check table generated
        annot_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(annot_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        time.sleep(5)

        network = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[5]/div[3]/div[2]')
        #driver.execute_script("arguments[0].scrollIntoView();", element)

        network.screenshot("network_of_gauges_screenshot.png")

        condition = network.is_displayed()

        driver.quit()

        assert condition

    def test_gauges_query_gauge_name_filter(self):
        #insert data
        data = {"operations": [{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_1.xml",
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
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "events": [{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT",
                "gauge": {"name": "GAUGE_NAME_3",
                          "system": "GAUGE_SYSTEM_3",
                          "insertion_type": "EVENT_KEYS"},
                "start": "2018-06-05T04:07:05",
                "stop": "2018-06-05T06:07:31",
                "key": "EVENT_KEY_3"
                }]
            }
        ]}

        #check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        #Like
        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Gauges")

        # find the element that's name attribute is gauge_name_like
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[5]/div/div/div/div/div/form/div[1]/div[1]/div[1]/input")
        inputElement.send_keys("GAUGE_NAME_1")

        #Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[5]/div/div/div/div/div/form/div[4]/button')))
        submitButton.click()

        #Check table generated
        annot_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(annot_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annot_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        #Not Like
        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Gauges")

        # find the element that's name attribute is gauge_name_like
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[5]/div/div/div/div/div/form/div[1]/div[1]/div[1]/input")
        inputElement.send_keys("GAUGE_NAME_1")

        notLikeButton = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[5]/div/div/div/div/div/form/div[1]/div[1]/div[1]/label")
        if not notLikeButton.find_element_by_xpath("input").is_selected():
            notLikeButton.click()
        #end if

        #Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[5]/div/div/div/div/div/form/div[4]/button')))
        submitButton.click()

        #Check table generated
        annot_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(annot_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annot_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        #In
        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Gauges")

        # find the element that's name attribute is gauge_name_in
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[5]/div/div/div/div/div/form/div[1]/div[2]/div[1]/div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("GAUGE_NAME_2")
        inputElement.send_keys(Keys.RETURN)
        inputElement.click()
        inputElement.send_keys("GAUGE_NAME_3")
        inputElement.send_keys(Keys.RETURN)

        #Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[5]/div/div/div/div/div/form/div[4]/button')))
        submitButton.click()

        #Check table generated
        annot_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(annot_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annot_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        #Not in
        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Gauges")

        # find the element that's name attribute is gauge_name_in
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[5]/div/div/div/div/div/form/div[1]/div[2]/div[1]/div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("GAUGE_NAME_1")
        inputElement.send_keys(Keys.RETURN)

        notInButton = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[5]/div/div/div/div/div/form/div[1]/div[2]/div[1]/label")
        if not notInButton.find_element_by_xpath("input").is_selected():
            notInButton.click()
        #end if

        #Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[5]/div/div/div/div/div/form/div[4]/button')))
        submitButton.click()

        #Check table generate
        annot_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(annot_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annot_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        driver.quit()

        assert number_of_elements == 2

    def test_gauges_query_gauge_system_filter(self):

        #insert data
        data = {"operations": [{
            "mode": "insert",
            "dim_signature": {
                  "name": "DIM_SIGNATURE",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_1.xml",
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
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "events": [{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT",
                "gauge": {"name": "GAUGE_NAME_3",
                          "system": "GAUGE_SYSTEM_3",
                          "insertion_type": "EVENT_KEYS"},
                "start": "2018-06-05T04:07:05",
                "stop": "2018-06-05T06:07:31",
                "key": "EVENT_KEY_3"
                }]
            }
        ]}

        #check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        #Like
        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Gauges")

        # find the element that's name attribute is gauge_system_in
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[5]/div/div/div/div/div/form/div[1]/div[1]/div[2]/input")
        inputElement.send_keys("GAUGE_SYSTEM_1")

        #Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[5]/div/div/div/div/div/form/div[4]/button')))
        submitButton.click()

        #Check table generated
        annot_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(annot_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annot_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        #Not Like
        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Gauges")

        # find the element that's name attribute is gauge_system_like
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[5]/div/div/div/div/div/form/div[1]/div[1]/div[2]/input")
        inputElement.send_keys("GAUGE_SYSTEM_1")

        notLikeButton = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[5]/div/div/div/div/div/form/div[1]/div[1]/div[2]/label")
        if not notLikeButton.find_element_by_xpath("input").is_selected():
            notLikeButton.click()
        #end if

        #Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[5]/div/div/div/div/div/form/div[4]/button')))
        submitButton.click()

        #Check table generated
        annot_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(annot_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annot_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        #In
        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Gauges")

        # find the element that's name attribute is gauge_system_in
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[5]/div/div/div/div/div/form/div[1]/div[2]/div[2]/div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("GAUGE_SYSTEM_1")
        inputElement.send_keys(Keys.RETURN)
        inputElement.click()
        inputElement.send_keys("GAUGE_SYSTEM_2")
        inputElement.send_keys(Keys.RETURN)

        #Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[5]/div/div/div/div/div/form/div[4]/button')))
        submitButton.click()

        #Check table generated
        annot_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(annot_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annot_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        #Not in
        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Gauges")

        # find the element that's name attribute is gauge_system_in
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[5]/div/div/div/div/div/form/div[1]/div[2]/div[2]/div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("GAUGE_SYSTEM_1")
        inputElement.send_keys(Keys.RETURN)

        notInButton = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[5]/div/div/div/div/div/form/div[1]/div[2]/div[2]/label")
        if not notInButton.find_element_by_xpath("input").is_selected():
            notInButton.click()
        #end if

        #Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[5]/div/div/div/div/div/form/div[4]/button')))
        submitButton.click()

        #Check table generate
        annot_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(annot_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annot_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        driver.quit()

        assert number_of_elements == 2

    def test_gauges_query_dim_signature_filter(self):

        #insert data
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
                  "name": "DIM_SIGNATURE_2",
                  "exec": "exec",
                  "version": "1.0"
            },
            "source":  {"name": "source_2.xml",
                           "generation_time": "2018-07-05T02:07:03",
                           "validity_start": "2018-06-05T02:07:03",
                           "validity_stop": "2018-06-05T08:07:36"},
            "events": [{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT",
                "gauge": {"name": "GAUGE_NAME_3",
                          "system": "GAUGE_SYSTEM_3",
                          "insertion_type": "EVENT_KEYS"},
                "start": "2018-06-05T04:07:05",
                "stop": "2018-06-05T06:07:31",
                "key": "EVENT_KEY_3"
                }]
            }
        ]}

        #check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        #Like
        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Gauges")

        # find the element that's name attribute is dim_signature_like
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[5]/div/div/div/div/div/form/div[2]/div[1]/input")
        inputElement.send_keys("DIM_SIGNATURE_2")

        #Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[5]/div/div/div/div/div/form/div[4]/button')))
        submitButton.click()

        #Check table generated
        annot_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(annot_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annot_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        #Not Like
        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Gauges")

        # find the element that's name attribute is dim_signature_like
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[5]/div/div/div/div/div/form/div[2]/div[1]/input")
        inputElement.send_keys("DIM_SIGNATURE_2")

        notLikeButton = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[5]/div/div/div/div/div/form/div[2]/div[1]/label")
        if not notLikeButton.find_element_by_xpath("input").is_selected():
            notLikeButton.click()
        #end if

        #Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[5]/div/div/div/div/div/form/div[4]/button')))
        submitButton.click()

        #Check table generated
        annot_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(annot_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        #In
        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Gauges")

        # find the element that's name attribute is dim_signature_like
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[5]/div/div/div/div/div/form/div[2]/div[2]/div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("DIM_SIGNATURE_1")
        inputElement.send_keys(Keys.RETURN)

        #Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[5]/div/div/div/div/div/form/div[4]/button')))
        submitButton.click()

        #Check table generated
        annot_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(annot_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        #Not in
        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Gauges")

        # find the element that's name attribute is dim_signature_like
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[5]/div/div/div/div/div/form/div[2]/div[2]/div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("DIM_SIGNATURE_2")
        inputElement.send_keys(Keys.RETURN)

        notInButton = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[5]/div/div/div/div/div/form/div[2]/div[2]/label")
        if not notInButton.find_element_by_xpath("input").is_selected():
            notInButton.click()
        #end if

        #Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[5]/div/div/div/div/div/form/div[4]/button')))
        submitButton.click()

        #Check table generate
        annot_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(annot_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annot_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        driver.quit()

        assert number_of_elements == 2
