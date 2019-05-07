"""
Automated tests for the sources tab

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

    #Sometimes fails (1 pass - 1 fail) no idea why
    def test_sources_query_no_filter_no_graphs(self):

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
                           "validity_stop": "2018-06-05T08:07:36"}
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
                           "validity_stop": "2018-06-06T11:57:17"}
            }]
        }

        #check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Sources")

        #Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[17]/button')))
        submit_button.click()

        #Check table generated
        annot_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(annot_table.find_elements_by_xpath("tbody/tr"))

        driver.quit()

        assert number_of_elements == 2

    def test_sources_query_no_filter_with_graphs(self):

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
                           "validity_stop": "2018-06-05T08:07:36"}
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
                           "validity_stop": "2018-06-06T11:57:17"}
            }]
        }


        #check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Sources")

        #Click on show map
        validity_timeline_button = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[12]/label")
        if not validity_timeline_button.find_element_by_xpath('input').is_selected():
            validity_timeline_button.click()
        #end if

        #Click on show map
        gen2ing_timeline_button = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[13]/label")
        if not gen2ing_timeline_button.find_element_by_xpath('input').is_selected():
            gen2ing_timeline_button.click()
        #end if

        #Click on show map
        number_events_per_source_button = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[14]/label")
        if not number_events_per_source_button.find_element_by_xpath('input').is_selected():
            number_events_per_source_button.click()
        #end if

        #Click on show map
        ingestion_duration_button = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[15]/label")
        if not ingestion_duration_button.find_element_by_xpath('input').is_selected():
            ingestion_duration_button.click()
        #end if

        #Click on show map
        gen2ing_times_button = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[16]/label")
        if not gen2ing_times_button.find_element_by_xpath('input').is_selected():
            gen2ing_times_button.click()
        #end if

        #Apply filters and click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[17]/button')))
        submit_button.click()

        time.sleep(10)

        validity_timeline = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[3]/div[3]/div[2]')

        validity_timeline.screenshot("validity_timeline_sources_screenshot.png")

        gen2ing_timeline = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[3]/div[4]/div[2]')

        gen2ing_timeline.screenshot("gen2ing_timeline_sources_screenshot.png")

        number_events_per_source = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[3]/div[5]/div[2]')

        number_events_per_source.screenshot("number_events_per_source_sources_screenshot.png")

        ingestion_duration = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[3]/div[6]/div[2]')

        ingestion_duration.screenshot("ingestion_duration_sources_screenshot.png")

        gen2ing_time = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[3]/div[7]/div[2]')

        gen2ing_time.screenshot("gen2ing_time_sources_screenshot.png")

        condition = validity_timeline.is_displayed() and gen2ing_timeline.is_displayed() and number_events_per_source.is_displayed() and ingestion_duration.is_displayed() and gen2ing_time.is_displayed()

        driver.quit()

        return condition

    def test_sources_query_name_filter(self):

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

        #check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        #Like
        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        # find the element that's name attribute is source_like
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[1]/div[1]/input")
        inputElement.send_keys("source_2.xml")

        #Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[17]/button')))
        submit_button.click()

        #Check table generated
        annot_table = wait.until(EC.visibility_of_element_located((By.ID,"events")))
        number_of_elements = len(annot_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annot_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        #Not Like
        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        # find the element that's name attribute is source_like
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[1]/div[1]/input")
        inputElement.send_keys("source_2.xml")

        notLikeButton = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[1]/div[1]/label")
        if not notLikeButton.find_element_by_xpath("input").is_selected():
            notLikeButton.click()
        #end if

        #Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[17]/button')))
        submit_button.click()

        #Check table generated
        annot_table = wait.until(EC.visibility_of_element_located((By.ID,"events")))
        number_of_elements = len(annot_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        #In
        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        # find the element that's name attribute is source_like
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[1]/div[2]/div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("source_1.xml")
        inputElement.send_keys(Keys.RETURN)

        #Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[17]/button')))
        submit_button.click()

        #Check table generated
        annot_table = wait.until(EC.visibility_of_element_located((By.ID,"events")))
        number_of_elements = len(annot_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        #Not in
        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        # find the element that's name attribute is source_like
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[1]/div[2]/div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("source_2.xml")
        inputElement.send_keys(Keys.RETURN)

        notInButton = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[1]/div[2]/label")
        if not notInButton.find_element_by_xpath("input").is_selected():
            notInButton.click()
        #end if

        #Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[17]/button')))
        submit_button.click()

        #Check table generate
        annot_table = wait.until(EC.visibility_of_element_located((By.ID,"events")))
        number_of_elements = len(annot_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annot_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        driver.quit()

        assert number_of_elements == 2

    def test_sources_query_processor_filter(self):

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

        #check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        #Like
        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        # find the element that's name attribute is source_like
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[1]/div[1]/input")
        inputElement.send_keys("source_2.xml")

        #Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[17]/button')))
        submit_button.click()

        #Check table generated
        annot_table = wait.until(EC.visibility_of_element_located((By.ID,"events")))
        number_of_elements = len(annot_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annot_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        #Not Like
        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        # find the element that's name attribute is source_like
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[1]/div[1]/input")
        inputElement.send_keys("source_2.xml")

        notLikeButton = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[1]/div[1]/label")
        if not notLikeButton.find_element_by_xpath("input").is_selected():
            notLikeButton.click()
        #end if

        #Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[17]/button')))
        submit_button.click()

        #Check table generated
        annot_table = wait.until(EC.visibility_of_element_located((By.ID,"events")))
        number_of_elements = len(annot_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        #In
        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        # find the element that's name attribute is source_like
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[1]/div[2]/div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("source_1.xml")
        inputElement.send_keys(Keys.RETURN)

        #Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[17]/button')))
        submit_button.click()

        #Check table generated
        annot_table = wait.until(EC.visibility_of_element_located((By.ID,"events")))
        number_of_elements = len(annot_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        #Not in
        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        # find the element that's name attribute is source_like
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[1]/div[2]/div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("source_2.xml")
        inputElement.send_keys(Keys.RETURN)

        notInButton = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[1]/div[2]/label")
        if not notInButton.find_element_by_xpath("input").is_selected():
            notInButton.click()
        #end if

        #Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[17]/button')))
        submit_button.click()

        #Check table generate
        annot_table = wait.until(EC.visibility_of_element_located((By.ID,"events")))
        number_of_elements = len(annot_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annot_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        driver.quit()

        assert number_of_elements == 2

    def test_sources_query_dim_signature_filter(self):

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

        #check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        #Like
        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        # find the element that's name attribute is source_like
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[1]/div[1]/input")
        inputElement.send_keys("source_2.xml")

        #Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[17]/button')))
        submit_button.click()

        #Check table generated
        annot_table = wait.until(EC.visibility_of_element_located((By.ID,"events")))
        number_of_elements = len(annot_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annot_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        #Not Like
        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        # find the element that's name attribute is source_like
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[1]/div[1]/input")
        inputElement.send_keys("source_2.xml")

        notLikeButton = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[1]/div[1]/label")
        if not notLikeButton.find_element_by_xpath("input").is_selected():
            notLikeButton.click()
        #end if

        #Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[17]/button')))
        submit_button.click()

        #Check table generated
        annot_table = wait.until(EC.visibility_of_element_located((By.ID,"events")))
        number_of_elements = len(annot_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        #In
        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        # find the element that's name attribute is source_like
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[1]/div[2]/div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("source_1.xml")
        inputElement.send_keys(Keys.RETURN)

        #Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[17]/button')))
        submit_button.click()

        #Check table generated
        annot_table = wait.until(EC.visibility_of_element_located((By.ID,"events")))
        number_of_elements = len(annot_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        #Not in
        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        # find the element that's name attribute is source_like
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[1]/div[2]/div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("source_2.xml")
        inputElement.send_keys(Keys.RETURN)

        notInButton = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[1]/div[2]/label")
        if not notInButton.find_element_by_xpath("input").is_selected():
            notInButton.click()
        #end if

        #Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[17]/button')))
        submit_button.click()

        #Check table generate
        annot_table = wait.until(EC.visibility_of_element_located((By.ID,"events")))
        number_of_elements = len(annot_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annot_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        driver.quit()

        assert number_of_elements == 2

    def test_events_query_period(self):

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
                           "validity_start": "2018-06-05T00:00:00",
                           "validity_stop": "2018-06-05T08:00:00"},
            "events": [{"gauge": {"name": "GAUGE_NAME",
                                  "system": "GAUGE_SYSTEM",
                                  "insertion_type": "SIMPLE_UPDATE"},
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

        #check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element =  functions.period_comparer(driver, wait, "2018-06-05T03:00:00", "==","2018-06-05T04:00:00", "==")

        assert number_of_elements == 1 and empty_element is False

        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element =  functions.period_comparer(driver, wait, start_value = "2018-06-05T03:00:00", start_operator = ">=")

        assert number_of_elements == 2

        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element =  functions.period_comparer(driver, wait, end_value = "2018-06-05T04:00:00", end_operator = "!=")

        assert number_of_elements == 2

        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element =  functions.two_periods_comparer(driver, wait, start_value_1 = "2018-06-05T01:30:00", start_operator_1 = ">", start_value_2 = "2018-06-05T03:00:00", start_operator_2 = "<")

        assert number_of_elements == 1 and empty_element is False

        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element =  functions.two_periods_comparer(driver, wait, start_value_1 = "2018-06-05T03:00:00", start_operator_1 = "<=", end_value_1 = "2018-06-05T02:30:00", end_operator_1 = ">",
        start_value_2 = "2018-06-05T04:00:00", start_operator_2 = "!=", end_value_2 = "2018-06-05T03:00:00", end_operator_2 = ">=")

        assert number_of_elements == 2

        driver.quit()

        assert True

    def test_sources_query_ingestion_time(self):

        #insert data
        data = {"operations":[{
                        "mode": "insert",
                        "dim_signature": {"name": "dim_signature",
                                          "exec": "exec",
                                          "version": "1.0"},
                        "source": {"name": "source.xml",
                                   "generation_time": "2018-07-05T02:07:03",
                                   "validity_start": "2018-06-05T02:07:03",
                                   "validity_stop": "2018-06-05T08:07:36"},
                        "events": [{"gauge": {"name": "GAUGE_NAME",
                                              "system": "GAUGE_SYSTEM",
                                              "insertion_type": "SIMPLE_UPDATE"},
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
                        }]
                    }]
                }

        #check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        ingestion_time = self.session.query(Event).all()[0].ingestion_time.isoformat()

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element =  functions.value_comparer("events", driver, wait, "ingestion_time", ingestion_time, None, True, "==")
        time = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div[2]/div[2]/div/div[3]/div[2]/table/tbody/tr/td[7]")
        driver.execute_script("arguments[0].scrollIntoView()", time)
        assert number_of_elements == 1 and empty_element is False

        #>
        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element =  functions.value_comparer("events", driver, wait, "ingestion_time", ingestion_time, None, True, ">")

        assert empty_element is True

        #>=
        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element =  functions.value_comparer("events", driver, wait, "ingestion_time", ingestion_time, None, True, ">=")

        assert number_of_elements == 1 and empty_element is False

        #<
        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element =  functions.value_comparer("events", driver, wait, "ingestion_time", ingestion_time, None, True, "<")

        assert empty_element is True

        #<=
        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element =  functions.value_comparer("events", driver, wait, "ingestion_time", ingestion_time, None, True, "<=")

        assert number_of_elements == 1 and empty_element is False

        #!=
        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element =  functions.value_comparer("events", driver, wait, "ingestion_time", ingestion_time, None, True, "!=")

        assert empty_element is True

    def test_sources_query_generation_time(self):

        #insert data
        data = {"operations":[{
                        "mode": "insert",
                        "dim_signature": {"name": "dim_signature",
                                          "exec": "exec",
                                          "version": "1.0"},
                        "source": {"name": "source.xml",
                                   "generation_time": "2018-07-05T02:07:03",
                                   "validity_start": "2018-06-05T02:07:03",
                                   "validity_stop": "2018-06-05T08:07:36"},
                        "events": [{"gauge": {"name": "GAUGE_NAME",
                                              "system": "GAUGE_SYSTEM",
                                              "insertion_type": "SIMPLE_UPDATE"},
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
                        }]
                    }]
                }

        #check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        ingestion_time = self.session.query(Event).all()[0].ingestion_time.isoformat()

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element =  functions.value_comparer("events", driver, wait, "ingestion_time", ingestion_time, None, True, "==")
        time = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div[2]/div[2]/div/div[3]/div[2]/table/tbody/tr/td[7]")
        driver.execute_script("arguments[0].scrollIntoView()", time)
        assert number_of_elements == 1 and empty_element is False

        #>
        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element =  functions.value_comparer("events", driver, wait, "ingestion_time", ingestion_time, None, True, ">")

        assert empty_element is True

        #>=
        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element =  functions.value_comparer("events", driver, wait, "ingestion_time", ingestion_time, None, True, ">=")

        assert number_of_elements == 1 and empty_element is False

        #<
        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element =  functions.value_comparer("events", driver, wait, "ingestion_time", ingestion_time, None, True, "<")

        assert empty_element is True

        #<=
        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element =  functions.value_comparer("events", driver, wait, "ingestion_time", ingestion_time, None, True, "<=")

        assert number_of_elements == 1 and empty_element is False

        #!=
        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element =  functions.value_comparer("events", driver, wait, "ingestion_time", ingestion_time, None, True, "!=")

        assert empty_element is True

    def test_sources_query_value_ingestion_duration(self):

        data = {"operations":[{
                        "mode": "insert",
                        "dim_signature": {"name": "dim_signature",
                                          "exec": "exec",
                                          "version": "1.0"},
                        "source": {"name": "source.xml",
                                   "generation_time": "2018-07-05T02:07:03",
                                   "validity_start": "2018-06-05T02:07:03",
                                   "validity_stop": "2018-06-05T08:07:36"},
                        "events": [{"gauge": {"name": "GAUGE_NAME",
                                              "system": "GAUGE_SYSTEM",
                                              "insertion_type": "SIMPLE_UPDATE"},
                                    "start": "2018-06-05T02:07:03",
                                    "stop": "2018-06-05T08:07:36",
                                    "values": [{"name": "VALUES",
                                               "type": "object",
                                               "values": [
                                                   {"type": "text",
                                                    "name": "text_name_1",
                                                    "value": "text_value_1"
                                                    }]
                                                }]
                        }]
                    }]
                }

        #check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer("events",driver, wait, "text", "text_name_1", "text_value_1", True, "==")

        assert number_of_elements == 1 and empty_element is False

        #Not like
        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer("events", driver, wait, "text", "text_name_1", "text_value_2", False, "==")

        driver.quit()

        assert  number_of_elements == 1 and empty_element is True

    def test_sources_query_value_statuses(self):

        #insert data
        data = {"operations":[{
                        "mode": "insert",
                        "dim_signature": {"name": "dim_signature",
                                          "exec": "exec",
                                          "version": "1.0"},
                        "source": {"name": "source.xml",
                                   "generation_time": "2018-07-05T02:07:03",
                                   "validity_start": "2018-06-05T02:07:03",
                                   "validity_stop": "2018-06-05T08:07:36"},
                        "events": [{"gauge": {"name": "GAUGE_NAME",
                                              "system": "GAUGE_SYSTEM",
                                              "insertion_type": "SIMPLE_UPDATE"},
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
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer("events", driver, wait, "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", True, "==")

        assert number_of_elements == 1 and empty_element is False

        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer("events", driver, wait, "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", True, "==")

        assert empty_element is True

        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer("events", driver, wait, "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", True, ">")

        assert empty_element is True

        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer("events", driver, wait, "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", True, ">")

        assert number_of_elements == 1 and empty_element is False

        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer("events", driver, wait, "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", True, ">")

        assert empty_element == True

        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer("events", driver, wait, "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", True, ">=")

        assert number_of_elements == 1 and empty_element is False

        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer("events", driver, wait, "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", True, ">=")

        assert number_of_elements == 1 and empty_element is False

        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer("events", driver, wait, "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", True, ">=")

        assert empty_element == True

        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer("events", driver, wait, "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", True, "<")

        assert empty_element is True

        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer("events", driver, wait, "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", True, "<")

        assert empty_element is True

        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer("events", driver, wait, "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", True, "<")

        assert number_of_elements == 1 and empty_element is False

        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer("events", driver, wait, "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", True, "<=")

        assert number_of_elements == 1 and empty_element is False

        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer("events", driver, wait, "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", True, "<=")

        assert empty_element is True

        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer("events", driver, wait, "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", True, "<=")

        assert number_of_elements == 1 and empty_element is False

        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer("events", driver, wait, "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", True, "!=")

        assert empty_element is True

        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer("events", driver, wait, "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", True, "!=")

        assert number_of_elements == 1 and empty_element is False

        driver.get("http://localhost:5000/eboa_nav/")

        #Go to tab
        functions.goToTab(driver,"Events")

        number_of_elements, empty_element = functions.value_comparer("events", driver, wait, "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", True, "!=")

        driver.quit()

        assert number_of_elements == 1 and empty_element is False
