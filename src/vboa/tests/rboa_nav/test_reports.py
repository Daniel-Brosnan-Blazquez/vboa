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

class TestReportsTab(unittest.TestCase):

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

    def test_reports_no_data(self):
        
        wait = WebDriverWait(self.driver,5)

        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'reports-submit-button')))
        functions.click(submitButton)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"reports-nav-no-data")))

        assert no_data

    def test_reports_query_no_filter_with_graphs(self):

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
                            "generator_version":"1.0"
                        }
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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"reports-submit-button")))
        functions.click(submit_button)

        # Check table generated
        reports_table = wait.until(EC.visibility_of_element_located((By.ID,"reports-table")))
        number_of_elements = len(reports_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

        # Check whether the timeline is displayed
        timeline_section = self.driver.find_element_by_id("reports-nav-validity-timeline")

        condition = timeline_section.is_displayed()
        assert condition is True

        # Check whether the generation duration xy is displayed
        generation_duration_xy_section = self.driver.find_element_by_id("reports-nav-generation-duration-xy")

        condition = generation_duration_xy_section.is_displayed()
        assert condition is True

        # Check generated content for widgets
        kwargs ={}
        kwargs["order_by"] = {"field": "validity_start", "descending": False}
        reports = self.query_eboa.get_reports(**kwargs)

        assert len(reports) == 1

        var_reports = [
            {
                "compressed": "True",
                "generated": "True",
                "generation_error": "False",
                "generation_mode": "MANUAL",
                "generation_start": "2018-07-05 02:07:10",
                "generation_stop": "2018-07-05 02:15:10",
                "generator": "report_generator",
                "id": str(reports[0].report_uuid),
                "metadata_ingestion_duration": str(reports[0].metadata_ingestion_duration),
                "name": "report.html",
                "report_group": "report_group",
                "triggering_time": "2018-07-05 02:07:03",
                "validity_start": "2018-06-05 02:07:03",
                "validity_stop": "2018-06-05 08:07:36",
                "version": "1.0"
            }
        ]

        returned_alerts = self.driver.execute_script('return reports;')
        functions.assert_equal_list_dictionaries(returned_alerts, var_reports)

        # Check report alerts table
        reports_table = self.driver.find_element_by_id("reports-table")

        # Row 1
        name = reports_table.find_element_by_xpath("tbody/tr[1]/td[2]")

        assert name.text == "report.html"

        generation_mode = reports_table.find_element_by_xpath("tbody/tr[1]/td[3]")

        assert generation_mode.text == "MANUAL"

        validity_start = reports_table.find_element_by_xpath("tbody/tr[1]/td[4]")

        assert validity_start.text == "2018-06-05T02:07:03"

        validity_stop = reports_table.find_element_by_xpath("tbody/tr[1]/td[5]")

        assert validity_stop.text == "2018-06-05T08:07:36"

        validity_duration = reports_table.find_element_by_xpath("tbody/tr[1]/td[6]")

        assert validity_duration.text == "360.55"

        generation_start = reports_table.find_element_by_xpath("tbody/tr[1]/td[7]")

        assert generation_start.text == "2018-07-05T02:07:10"

        generation_stop = reports_table.find_element_by_xpath("tbody/tr[1]/td[8]")

        assert generation_stop.text == "2018-07-05T02:15:10"

        generation_duration = reports_table.find_element_by_xpath("tbody/tr[1]/td[9]")

        assert generation_duration.text == "8.0"

        report_group = reports_table.find_element_by_xpath("tbody/tr[1]/td[10]")

        assert report_group.text == "report_group"

        generator = reports_table.find_element_by_xpath("tbody/tr[1]/td[11]")

        assert generator.text == "report_generator"

        version = reports_table.find_element_by_xpath("tbody/tr[1]/td[12]")

        assert version.text == "1.0"

        report_uuid = reports_table.find_element_by_xpath("tbody/tr[1]/td[14]")

        assert report_uuid.text == str(reports[0].report_uuid)


    def test_reports_query_report_filter(self):

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
                            "generator_version":"1.0"
                        }
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
                        }
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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"reports-submit-button")))
        functions.click(submit_button)

        ## Like ##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")

        # Fill the explicit_ref_like input
        input_element = self.driver.find_element_by_id("reports-report-name-text")
        input_element.send_keys("report.html")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"reports-submit-button")))
        functions.click(submit_button)

        # Check table generated
        reports_table = wait.until(EC.visibility_of_element_located((By.ID,"reports-table")))
        number_of_elements = len(reports_table.find_elements_by_xpath("tbody/tr"))

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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"reports-submit-button")))
        functions.click(submit_button)

        # Check table generated
        reports_table = wait.until(EC.visibility_of_element_located((By.ID,"reports-table")))
        number_of_elements = len(reports_table.find_elements_by_xpath("tbody/tr"))

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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"reports-submit-button")))
        functions.click(submit_button)

        # Check table generated
        reports_table = wait.until(EC.visibility_of_element_located((By.ID,"reports-table")))
        number_of_elements = len(reports_table.find_elements_by_xpath("tbody/tr"))

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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"reports-submit-button")))
        functions.click(submit_button)

        # Check table generate
        reports_table = wait.until(EC.visibility_of_element_located((By.ID,"reports-table")))
        number_of_elements = len(reports_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

    def test_reports_query_generator_filter(self):

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
                        }
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
                            "generator_version":"1.0"
                        }
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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"reports-submit-button")))
        functions.click(submit_button)

        ## Like ##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")

        # Fill the explicit_ref_like input
        input_element = self.driver.find_element_by_id("reports-generator-text")
        input_element.send_keys("report_generator")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"reports-submit-button")))
        functions.click(submit_button)

        # Check table generated
        reports_table = wait.until(EC.visibility_of_element_located((By.ID,"reports-table")))
        number_of_elements = len(reports_table.find_elements_by_xpath("tbody/tr"))

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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"reports-submit-button")))
        functions.click(submit_button)

        # Check table generated
        reports_table = wait.until(EC.visibility_of_element_located((By.ID,"reports-table")))
        number_of_elements = len(reports_table.find_elements_by_xpath("tbody/tr"))

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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"reports-submit-button")))
        functions.click(submit_button)

        # Check table generated
        reports_table = wait.until(EC.visibility_of_element_located((By.ID,"reports-table")))
        number_of_elements = len(reports_table.find_elements_by_xpath("tbody/tr"))

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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"reports-submit-button")))
        functions.click(submit_button)

        # Check table generate
        reports_table = wait.until(EC.visibility_of_element_located((By.ID,"reports-table")))
        number_of_elements = len(reports_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

    def test_reports_query_groups_filter(self):

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
                        }
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
                        }
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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"reports-submit-button")))
        functions.click(submit_button)

        ## Like ##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")

        # Fill the explicit_ref_like input
        input_element = self.driver.find_element_by_id("reports-report-group-text")
        input_element.send_keys("report_group")

        # Click on query button
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"reports-submit-button")))
        functions.click(submit_button)

        # Check table generated
        reports_table = wait.until(EC.visibility_of_element_located((By.ID,"reports-table")))
        number_of_elements = len(reports_table.find_elements_by_xpath("tbody/tr"))

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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"reports-submit-button")))
        functions.click(submit_button)

        # Check table generated
        reports_table = wait.until(EC.visibility_of_element_located((By.ID,"reports-table")))
        number_of_elements = len(reports_table.find_elements_by_xpath("tbody/tr"))

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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"reports-submit-button")))
        functions.click(submit_button)

        # Check table generated
        reports_table = wait.until(EC.visibility_of_element_located((By.ID,"reports-table")))
        number_of_elements = len(reports_table.find_elements_by_xpath("tbody/tr"))

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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,"reports-submit-button")))
        functions.click(submit_button)

        # Check table generate
        reports_table = wait.until(EC.visibility_of_element_located((By.ID,"reports-table")))
        number_of_elements = len(reports_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 1

    def test_reports_query_validity_period(self):

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
                        }
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
                        }
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
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'reports-submit-button')))
        functions.click(submitButton)

        # Check table generated
        reports_table = wait.until(EC.visibility_of_element_located((By.ID,"reports-table")))
        number_of_elements = len(reports_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(reports_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## >= ## Only Start##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")

        functions.fill_validity_period(self.driver, wait, "reports", 1,  start_value = "2018-06-05T02:00:00", start_operator = ">=")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'reports-submit-button')))
        functions.click(submitButton)

        # Check table generated
        reports_table = wait.until(EC.visibility_of_element_located((By.ID,"reports-table")))
        number_of_elements = len(reports_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(reports_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        ## != ## Only End##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")

        functions.fill_validity_period(self.driver, wait, "reports", 1,  end_value = "2018-06-05T04:00:00", end_operator = "!=")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'reports-submit-button')))
        functions.click(submitButton)

        # Check table generated
        reports_table = wait.until(EC.visibility_of_element_located((By.ID,"reports-table")))
        number_of_elements = len(reports_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(reports_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

        ## > ## Only Start## < ## Only Start##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")
        
        functions.fill_validity_period(self.driver, wait, "reports", 1, start_value = "2018-06-05T01:00:00", start_operator = ">")
        functions.click(self.driver.find_element_by_id("reports-add-validity-start-validity-stop"))
        functions.fill_validity_period(self.driver, wait, "reports", 2, start_value = "2018-06-05T03:00:00", start_operator = "<")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'reports-submit-button')))
        functions.click(submitButton)

        # Check table generated
        reports_table = wait.until(EC.visibility_of_element_located((By.ID,"reports-table")))
        number_of_elements = len(reports_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(reports_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## <= ## Start## > ## End## != ## Start## >= ## End##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")

        functions.fill_validity_period(self.driver, wait, "reports", 1, start_value = "2018-06-05T03:00:00", start_operator = "<=", end_value = "2018-06-05T02:30:00", end_operator = ">")
        functions.click(self.driver.find_element_by_id("reports-add-validity-start-validity-stop"))
        functions.fill_validity_period(self.driver, wait, "reports", 2, start_value = "2018-06-05T04:00:00", start_operator = "!=", end_value = "2018-06-05T03:00:00", end_operator = ">=")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'reports-submit-button')))
        functions.click(submitButton)

        # Check table generated
        reports_table = wait.until(EC.visibility_of_element_located((By.ID,"reports-table")))
        number_of_elements = len(reports_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(reports_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1

    def test_reports_query_report_validity_duration(self):

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
                        }
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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'reports-submit-button')))

        functions.fill_any_duration(self.driver, wait, "reports", "report-validity", validity_duration_in_days, "==", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        reports_table = wait.until(EC.visibility_of_element_located((By.ID,"reports-table")))
        number_of_elements = len(reports_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(reports_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## > ##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'reports-submit-button')))

        functions.fill_any_duration(self.driver, wait, "reports", "report-validity", validity_duration_in_days, ">", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"reports-nav-no-data")))

        assert no_data

        ## >= ##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'reports-submit-button')))
    
        functions.fill_any_duration(self.driver, wait, "reports", "report-validity", validity_duration_in_days, ">=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        reports_table = wait.until(EC.visibility_of_element_located((By.ID,"reports-table")))
        number_of_elements = len(reports_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(reports_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## < ##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'reports-submit-button')))

        functions.fill_any_duration(self.driver, wait, "reports", "report-validity", validity_duration_in_days, "<", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"reports-nav-no-data")))

        assert no_data

        ## <= ##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'reports-submit-button')))

        functions.fill_any_duration(self.driver, wait, "reports", "report-validity", validity_duration_in_days, "<=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        reports_table = wait.until(EC.visibility_of_element_located((By.ID,"reports-table")))
        number_of_elements = len(reports_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(reports_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'reports-submit-button')))

        functions.fill_any_duration(self.driver, wait, "reports", "report-validity", validity_duration_in_days, "!=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"reports-nav-no-data")))

        assert no_data

    def test_reports_query_triggering_time(self):

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
                        }
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
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'reports-submit-button')))

        functions.fill_any_time(self.driver, wait, "reports", "triggering", triggering_time, "==", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        reports_table = wait.until(EC.visibility_of_element_located((By.ID,"reports-table")))
        number_of_elements = len(reports_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(reports_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## > ##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'reports-submit-button')))

        functions.fill_any_time(self.driver, wait, "reports", "triggering", triggering_time, ">", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"reports-nav-no-data")))

        assert no_data

        ## >= ##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'reports-submit-button')))
    
        functions.fill_any_time(self.driver, wait, "reports", "triggering", triggering_time, ">=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        reports_table = wait.until(EC.visibility_of_element_located((By.ID,"reports-table")))
        number_of_elements = len(reports_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(reports_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## < ##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'reports-submit-button')))

        functions.fill_any_time(self.driver, wait, "reports", "triggering", triggering_time, "<", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"reports-nav-no-data")))

        assert no_data

        ## <= ##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'reports-submit-button')))

        functions.fill_any_time(self.driver, wait, "reports", "triggering", triggering_time, "<=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        reports_table = wait.until(EC.visibility_of_element_located((By.ID,"reports-table")))
        number_of_elements = len(reports_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(reports_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        self.driver.get("http://localhost:5000/rboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Reports")
        submit_button = wait.until(EC.visibility_of_element_located((By.ID,'reports-submit-button')))

        functions.fill_any_time(self.driver, wait, "reports", "triggering", triggering_time, "!=", 1)

        # Click on query button
        functions.click(submit_button)

        # Check table generated
        no_data = wait.until(EC.visibility_of_element_located((By.ID,"reports-nav-no-data")))

        assert no_data
