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

    def test_sources_query_no_filter_no_graphs(self):

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

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[17]/button')))
        submit_button.click()

        # Check table generatedd
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))

        driver.quit()

        assert number_of_elements == 2

    def test_sources_query_no_filter_with_graphs(self):

        screenshot_path = os.path.dirname(os.path.abspath(__file__)) + "/screenshots/sources/"

        if not os.path.exists(screenshot_path):
            os.makedirs(screenshot_path)
        #end if

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
                           "validity_stop": "2018-06-05T08:07:36"}
            }]
        }


        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        # Click on show validity_timeline
        validity_timeline_button = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[12]/label")
        if not validity_timeline_button.find_element_by_xpath('input').is_selected():
            validity_timeline_button.click()
        #end if

        # # Click on show gen2ing_timeline
        # gen2ing_timeline_button = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[13]/label")
        # if not gen2ing_timeline_button.find_element_by_xpath('input').is_selected():
        #     gen2ing_timeline_button.click()
        # #end if
        #
        # # Click on show number_events_per_source
        # number_events_per_source_button = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[14]/label")
        # if not number_events_per_source_button.find_element_by_xpath('input').is_selected():
        #     number_events_per_source_button.click()
        # #end if
        #
        # # Click on show ingestion_duration
        # ingestion_duration_button = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[15]/label")
        # if not ingestion_duration_button.find_element_by_xpath('input').is_selected():
        #     ingestion_duration_button.click()
        # #end if
        #
        # # Click on show gen2ing_times
        # gen2ing_times_button = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[16]/label")
        # if not gen2ing_times_button.find_element_by_xpath('input').is_selected():
        #     gen2ing_times_button.click()
        # #end if

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[17]/button')))
        submit_button.click()

        source = self.session.query(Source).all()[0]

        assert driver.execute_script('return sources;') == {
            "sources":[{
                "id": str(source.source_uuid),
                "name": "source_1.xml",
                "dim_signature": "DIM_SIGNATURE_1",
                "processor": "exec",
                "version": "1.0",
                "validity_start": "2018-06-05 02:07:03",
                "validity_stop": "2018-06-05 08:07:36",
                "ingestion_time": source.ingestion_time.isoformat().replace("T"," "),
                "ingestion_duration": str(source.ingestion_duration),
                "generation_time": "2018-07-05 02:07:03",
                "number_of_events": "0"
                }
                ]
            }

        # validity_timeline = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[3]/div[3]/div[2]')
        #
        # #validity_timeline.screenshot(screenshot_path + "validity_timeline_sources_screenshot.png")
        #
        # gen2ing_timeline = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[3]/div[4]/div[2]')
        # #driver.execute_script("arguments[0].scrollIntoView();", gen2ing_timeline)
        #
        # #gen2ing_timeline.screenshot(screenshot_path + "gen2ing_timeline_sources_screenshot.png")
        #
        # number_events_per_source = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[3]/div[5]/div[2]')
        # #driver.execute_script("arguments[0].scrollIntoView();", number_events_per_source)
        #
        # #number_events_per_source.screenshot(screenshot_path + "number_events_per_source_sources_screenshot.png")
        #
        # ingestion_duration = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[3]/div[6]/div[2]')
        # #driver.execute_script("arguments[0].scrollIntoView();", ingestion_duration)
        #
        # #ingestion_duration.screenshot(screenshot_path + "ingestion_duration_sources_screenshot.png")
        #
        # gen2ing_time = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[3]/div[7]/div[2]')
        # #driver.execute_script("arguments[0].scrollIntoView();", gen2ing_time)
        #
        # #gen2ing_time.screenshot(screenshot_path + "gen2ing_time_sources_screenshot.png")

        # condition = validity_timeline.is_displayed() and gen2ing_timeline.is_displayed() and number_events_per_source.is_displayed() and ingestion_duration.is_displayed() and gen2ing_time.is_displayed()

        # assert condition

        driver.quit()

    def test_sources_query_name_filter(self):

        # Insert data
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
                               "validity_stop": "2018-06-05T02:08:12"}
            },{
                "mode": "insert",
                "dim_signature": {
                      "name": "DIM_SIGNATURE_2",
                      "exec": "exec_2",
                      "version": "1.0"
                },
                "source":  {"name": "source_2.xml",
                               "generation_time": "2018-07-06T12:35:24",
                               "validity_start": "2018-06-06T12:35:28",
                               "validity_stop": "2018-06-06T12:38:14"}
            },{
                "mode": "insert",
                "dim_signature": {
                      "name": "DIM_SIGNATURE_2",
                      "exec": "exec",
                      "version": "1.0"
                },
                "source":  {"name": "source_3.xml",
                               "generation_time": "2018-07-06T14:10:04",
                               "validity_start": "2018-06-06T22:02:04",
                               "validity_stop": "2018-06-06T23:08:45"}
                }
        ]}

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        ## Like ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        # Fill the source_like input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[1]/div[1]/input")
        inputElement.send_keys("source_2.xml")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[17]/button')))
        submit_button.click()

        # Check table generatedd
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not like ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        # Fill the source_like input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[1]/div[1]/input")
        inputElement.send_keys("source_2.xml")

        notLikeButton = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[1]/div[1]/label")
        if not notLikeButton.find_element_by_xpath("input").is_selected():
            notLikeButton.click()
        #end if

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[17]/button')))
        submit_button.click()

        # Check table generatedd
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## In ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        # Fill the source_in input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[1]/div[2]/div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("source_2.xml")
        inputElement.send_keys(Keys.RETURN)
        inputElement.click()
        inputElement.send_keys("source_3.xml")
        inputElement.send_keys(Keys.RETURN)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[17]/button')))
        submit_button.click()

        # Check table generatedd
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not in ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        # Fill the source_in input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[1]/div[2]/div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("source_3.xml")
        inputElement.send_keys(Keys.RETURN)

        notInButton = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[1]/div[2]/label")
        if not notInButton.find_element_by_xpath("input").is_selected():
            notInButton.click()
        #end if

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[17]/button')))
        submit_button.click()

        # Check table generated
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        driver.quit()

        assert number_of_elements == 2

    def test_sources_query_processor_filter(self):

        # Insert data
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
                               "validity_stop": "2018-06-05T02:08:12"}
            },{
                "mode": "insert",
                "dim_signature": {
                      "name": "DIM_SIGNATURE_2",
                      "exec": "exec_2",
                      "version": "1.0"
                },
                "source":  {"name": "source_2.xml",
                               "generation_time": "2018-07-06T12:35:24",
                               "validity_start": "2018-06-06T12:35:28",
                               "validity_stop": "2018-06-06T12:38:14"}
            },{
                "mode": "insert",
                "dim_signature": {
                      "name": "DIM_SIGNATURE_2",
                      "exec": "exec",
                      "version": "1.0"
                },
                "source":  {"name": "source_3.xml",
                               "generation_time": "2018-07-06T14:10:04",
                               "validity_start": "2018-06-06T22:02:04",
                               "validity_stop": "2018-06-06T23:08:45"}
                }
        ]}

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        ## Like ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        # Fill the processor_like input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[2]/div[1]/input")
        inputElement.send_keys("exec_2")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[17]/button')))
        submit_button.click()

        # Check table generatedd
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not like ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        # Fill the processor_like input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[2]/div[1]/input")
        inputElement.send_keys("exec_2")

        notLikeButton = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[2]/div[1]/label")
        if not notLikeButton.find_element_by_xpath("input").is_selected():
            notLikeButton.click()
        #end if

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[17]/button')))
        submit_button.click()

        # Check table generatedd
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## In ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        # Fill the processor_in input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[2]/div[2]/div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("exec")
        inputElement.send_keys(Keys.RETURN)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[17]/button')))
        submit_button.click()

        # Check table generatedd
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not in ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        # Fill the processor_in input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[2]/div[2]/div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("exec_2")
        inputElement.send_keys(Keys.RETURN)

        notInButton = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[2]/div[2]/label")
        if not notInButton.find_element_by_xpath("input").is_selected():
            notInButton.click()
        #end if

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[17]/button')))
        submit_button.click()

        # Check table generated
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        driver.quit()

        assert number_of_elements == 2

    def test_sources_query_dim_signature_filter(self):

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
                               "validity_stop": "2018-06-05T02:08:12"}
            },{
                "mode": "insert",
                "dim_signature": {
                      "name": "DIM_SIGNATURE_2",
                      "exec": "exec_2",
                      "version": "1.0"
                },
                "source":  {"name": "source_2.xml",
                               "generation_time": "2018-07-06T12:35:24",
                               "validity_start": "2018-06-06T12:35:28",
                               "validity_stop": "2018-06-06T12:38:14"}
            },{
                "mode": "insert",
                "dim_signature": {
                      "name": "DIM_SIGNATURE_3",
                      "exec": "exec",
                      "version": "1.0"
                },
                "source":  {"name": "source_3.xml",
                               "generation_time": "2018-07-06T14:10:04",
                               "validity_start": "2018-06-06T22:02:04",
                               "validity_stop": "2018-06-06T23:08:45"}
                }
        ]}

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        ## Like ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        # Fill the dim_signature_like input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[3]/div[1]/input")
        inputElement.send_keys("DIM_SIGNATURE_2")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[17]/button')))
        submit_button.click()

        # Check table generatedd
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not like ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        # Fill the dim_signature_like input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[3]/div[1]/input")
        inputElement.send_keys("DIM_SIGNATURE_2")

        notLikeButton = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[3]/div[1]/label")
        if not notLikeButton.find_element_by_xpath("input").is_selected():
            notLikeButton.click()
        #end if

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[17]/button')))
        submit_button.click()

        # Check table generatedd
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## In ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        # Fill the dim_signature_in input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[3]/div[2]/div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("DIM_SIGNATURE_1")
        inputElement.send_keys(Keys.RETURN)
        inputElement.click()
        inputElement.send_keys("DIM_SIGNATURE_2")
        inputElement.send_keys(Keys.RETURN)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[17]/button')))
        submit_button.click()

        # Check table generatedd
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not in ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        # Fill the dim_signature_in input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[3]/div[2]/div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("DIM_SIGNATURE_3")
        inputElement.send_keys(Keys.RETURN)

        notInButton = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[3]/div[2]/label")
        if not notInButton.find_element_by_xpath("input").is_selected():
            notInButton.click()
        #end if

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[17]/button')))
        submit_button.click()

        # Check table generated
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        driver.quit()

        assert number_of_elements == 2

    #Two periods (only start dates) crash
    def unstable_test_sources_query_period(self):

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
                               "validity_start": "2018-06-05T02:00:00",
                               "validity_stop": "2018-06-05T03:00:00"}
            },{
                "mode": "insert",
                "dim_signature": {
                      "name": "DIM_SIGNATURE_2",
                      "exec": "exec_2",
                      "version": "1.0"
                },
                "source":  {"name": "source_2.xml",
                               "generation_time": "2018-07-05T02:07:03",
                               "validity_start": "2018-06-05T03:00:00",
                               "validity_stop": "2018-06-05T04:00:00"}
            },{
                "mode": "insert",
                "dim_signature": {
                      "name": "DIM_SIGNATURE_3",
                      "exec": "exec",
                      "version": "1.0"
                },
                "source":  {"name": "source_3.xml",
                               "generation_time": "2018-07-05T02:07:03",
                               "validity_start": "2018-06-05T04:00:00",
                               "validity_stop": "2018-06-05T05:00:00"}
                }
        ]}

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        ## == ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        number_of_elements, empty_element =  functions.period_comparer(driver, wait, "sources", "2018-06-05T03:00:00", "==","2018-06-05T04:00:00", "==")

        assert number_of_elements == 1 and empty_element is False

        ## >= ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        number_of_elements, empty_element =  functions.period_comparer(driver, wait, "sources", start_value = "2018-06-05T03:00:00", start_operator = ">=")

        assert number_of_elements == 2

        ## != ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        number_of_elements, empty_element =  functions.period_comparer(driver, wait, "sources", end_value = "2018-06-05T04:00:00", end_operator = "!=")

        assert number_of_elements == 2

        ## > ## Only Start ## < ## Only Start ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        number_of_elements, empty_element =  functions.two_periods_comparer(driver, wait, "sources", start_value_1 = "2018-06-05T01:30:00", start_operator_1 = ">", start_value_2 = "2018-06-05T03:00:00", start_operator_2 = "<")

        assert number_of_elements == 1 and empty_element is False

        ## <= ## Start ## > ## End ## != ## Start ## >= ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        number_of_elements, empty_element =  functions.two_periods_comparer(driver, wait, "sources", start_value_1 = "2018-06-05T03:00:00", start_operator_1 = "<=", end_value_1 = "2018-06-05T02:30:00", end_operator_1 = ">",
        start_value_2 = "2018-06-05T04:00:00", start_operator_2 = "!=", end_value_2 = "2018-06-05T03:00:00", end_operator_2 = ">=")

        assert number_of_elements == 2

        driver.quit()

        assert True

    def test_sources_query_ingestion_time(self):

        # Insert data
        data = {"operations":[{
                        "mode": "insert",
                        "dim_signature": {"name": "dim_signature",
                                          "exec": "exec",
                                          "version": "1.0"},
                        "source": {"name": "source.xml",
                                   "generation_time": "2018-07-05T02:07:03",
                                   "validity_start": "2018-06-05T02:07:03",
                                   "validity_stop": "2018-06-05T08:07:36"},
                    }]
                }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        ingestion_time = self.session.query(Source).all()[0].ingestion_time.isoformat()

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        number_of_elements, empty_element =  functions.value_comparer(driver, wait,"sources", "ingestion_time", ingestion_time, None, True, "==")

        assert number_of_elements == 1 and empty_element is False

        ## > ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        number_of_elements, empty_element =  functions.value_comparer(driver, wait,"sources", "ingestion_time", ingestion_time, None, True, ">")

        assert empty_element is True

        ## >= ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        number_of_elements, empty_element =  functions.value_comparer(driver, wait,"sources", "ingestion_time", ingestion_time, None, True, ">=")

        assert number_of_elements == 1 and empty_element is False

        ## < ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        number_of_elements, empty_element =  functions.value_comparer(driver, wait,"sources", "ingestion_time", ingestion_time, None, True, "<")

        assert empty_element is True

        ## <= ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        number_of_elements, empty_element =  functions.value_comparer(driver, wait,"sources", "ingestion_time", ingestion_time, None, True, "<=")

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        number_of_elements, empty_element =  functions.value_comparer(driver, wait,"sources", "ingestion_time", ingestion_time, None, True, "!=")

        assert empty_element is True

        driver.quit()

    def test_sources_query_generation_time(self):

        # Insert data
        data = {"operations":[{
                        "mode": "insert",
                        "dim_signature": {"name": "dim_signature",
                                          "exec": "exec",
                                          "version": "1.0"},
                        "source": {"name": "source.xml",
                                   "generation_time": "2018-07-05T02:07:03",
                                   "validity_start": "2018-06-05T02:07:03",
                                   "validity_stop": "2018-06-05T08:07:36"},
                    }]
                }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        number_of_elements, empty_element =  functions.value_comparer(driver, wait,"sources", "generation_time", "2018-07-05T02:07:03", None, True, "==")

        assert number_of_elements == 1 and empty_element is False

        ## > ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        number_of_elements, empty_element =  functions.value_comparer(driver, wait,"sources", "generation_time", "2018-07-05T02:07:03", None, True, ">")

        assert empty_element is True

        ## >= ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        number_of_elements, empty_element =  functions.value_comparer(driver, wait,"sources", "generation_time", "2018-07-05T02:07:03", None, True, ">=")

        assert number_of_elements == 1 and empty_element is False

        ## < ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        number_of_elements, empty_element =  functions.value_comparer(driver, wait,"sources", "generation_time", "2018-07-05T02:07:03", None, True, "<")

        assert empty_element is True

        ## <= ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        number_of_elements, empty_element =  functions.value_comparer(driver, wait,"sources", "generation_time", "2018-07-05T02:07:03", None, True, "<=")

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        number_of_elements, empty_element =  functions.value_comparer(driver, wait,"sources", "generation_time", "2018-07-05T02:07:03", None, True, "!=")

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
                    }]
                }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        ingestion_duration = str(self.session.query(Source).all()[0].ingestion_duration.total_seconds())

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        ## == ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "sources", "ingestion_duration", ingestion_duration, 0, 0, "==")

        assert number_of_elements == 1 and empty_element is False

        ## > ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "sources", "ingestion_duration", ingestion_duration, 0, 0, ">")

        assert number_of_elements == 1 and empty_element is True

        ## >= ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "sources", "ingestion_duration", ingestion_duration, 0, 0, ">=")

        assert number_of_elements == 1 and empty_element is False

        ## < ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "sources", "ingestion_duration", ingestion_duration, 0, 0, "<")

        assert number_of_elements == 1 and empty_element is True

        ## <= ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "sources", "ingestion_duration", ingestion_duration, 0, 0, "<=")

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        number_of_elements, empty_element = functions.value_comparer(driver, wait, "sources", "ingestion_duration", ingestion_duration, 0, 0, "!=")

        assert number_of_elements == 1 and empty_element is True

        driver.quit()

    def test_sources_query_value_statuses(self):
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
                               "validity_stop": "2018-06-05T02:08:12"}
            }
        ]}

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        assert eboa_engine.exit_codes["SOURCE_ALREADY_INGESTED"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        # Create a new instance of the Firefox driver
        driver = webdriver.Firefox(options=self.options)

        wait = WebDriverWait(driver,30);

        ## OK Status ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        # Fill the status_in input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[11]/div/div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("OK")
        inputElement.send_keys(Keys.RETURN)

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[17]/button')))
        submit_button.click()

        # Check table generatedd
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not OK Status ##
        driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(driver,"Sources")

        # Fill the status_in input
        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[11]/div/div/ul/li/input")
        inputElement.click()
        inputElement.send_keys("OK")
        inputElement.send_keys(Keys.RETURN)

        notInButton = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[11]/div/label")
        if not notInButton.find_element_by_xpath("input").is_selected():
            notInButton.click()
        #end if

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[17]/button')))
        submit_button.click()

        # Check table generatedd
        sources_table = wait.until(EC.visibility_of_element_located((By.ID,"sources")))
        number_of_elements = len(sources_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(sources_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        driver.quit()
