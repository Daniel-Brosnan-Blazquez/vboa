"""
Automated tests for the annotations tab

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

from vboa.eboa_nav import eboa_nav


class TestAnnotationsTab(unittest.TestCase):

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

    def test_annotations_query_no_filter_no_map(self):

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
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        # Check annotation_name
        annotation_name = annotations_table.find_elements_by_xpath("tbody/tr[1]/td[2]")

        assert annotation_name[0].text == "NAME_1"

        # Check annotation_system
        gauge_system = annotations_table.find_elements_by_xpath("tbody/tr[1]/td[3]")

        assert gauge_system[0].text == "SYSTEM"

        # Check ingestion_time
        ingestion_time = annotations_table.find_elements_by_xpath("tbody/tr[1]/td[4]")

        assert re.match("....-..-.. ..:..:...*", ingestion_time[0].text)

        # Check source
        source = annotations_table.find_elements_by_xpath("tbody/tr[1]/td[5]")

        assert source[0].text == "source.xml"

        # Check explicit_ref
        explicit_ref = annotations_table.find_elements_by_xpath("tbody/tr[1]/td[6]")

        assert explicit_ref[0].text == "EXPLICIT_REFERENCE"

        # Check uuid
        uuid = annotations_table.find_elements_by_xpath("tbody/tr[1]/td[7]")

        assert re.match("........-....-....-....-............", uuid[0].text)

    def test_annotations_query_no_filter_with_map(self):

        screenshot_path = os.path.dirname(os.path.abspath(__file__)) + "/screenshots/annotations/"

        if not os.path.exists(screenshot_path):
            os.makedirs(screenshot_path)

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
                         {"type": "geometry",
                          "name": "GEOMETRY",
                          "value": "27.5923694065675 28.6897912912051 27.8617502445779 28.6464983273278 27.7690524083984 28.2803979779816 27.4991925556512 28.322475522552 27.5923694065675 28.6897912912051"}]
                    }]
                }]
            }]}


        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5);

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        # Click on show map
        mapButton = self.driver.find_element_by_id("annotations-show-map")
        if not mapButton.find_element_by_xpath('input').is_selected():
            functions.click(mapButton)
        #end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        map = self.driver.find_element_by_id("annotations-nav-map")

        map.screenshot(screenshot_path + "map_screenshot.png")

        condition = map.is_displayed()

        annotation = self.session.query(Annotation).all()[0]

        assert self.driver.execute_script('return annotations_geometries;') == [{
            "id": str(annotation.annotation_uuid),
            "annotation_cnf":{
                    "name": "NAME_1",
                    "system": "SYSTEM"
            },
            "explicit_reference": str(annotation.explicitRef.explicit_ref),
            "ingestion_time": annotation.ingestion_time.isoformat().replace("T"," "),
            "source": "source_1.xml",
            "geometries": [
                {
                    "value": "POLYGON ((27.5923694065675 28.6897912912051, 27.8617502445779 28.6464983273278, 27.7690524083984 28.2803979779816, 27.4991925556512 28.322475522552, 27.5923694065675 28.6897912912051))",
                    "name": "GEOMETRY"
                }
            ]
        }]

        assert condition is True

    def test_annotations_query_source(self):

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
                "explicit_reference" : "EXPLICIT_REFERENCE",
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
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        # Fill the source_like input
        inputElement = self.driver.find_element_by_id("annotations-sources-like-text")
        inputElement.send_keys("source_1.xml")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        # Fill the source_like input
        inputElement = self.driver.find_element_by_id("annotations-sources-like-text")
        inputElement.send_keys("source_1.xml")

        notLikeButton = self.driver.find_element_by_id("annotations-sources-like-checkbox")
        if not notLikeButton.find_element_by_xpath("input").is_selected():
            functions.click(notLikeButton)
        #end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        # Fill the source_in input
        inputElement = self.driver.find_element_by_id("annotations-sources-in-text").find_element_by_xpath("../div/ul/li/input")
        functions.click(inputElement)

        assert len(self.driver.find_element_by_id("annotations-sources-in-text").find_elements_by_xpath("option")) == 2

        inputElement.send_keys("source_2.xml")
        inputElement.send_keys(Keys.RETURN)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        # Fill the source_in input
        inputElement = self.driver.find_element_by_id("annotations-sources-in-text").find_element_by_xpath("../div/ul/li/input")
        functions.click(inputElement)

        assert len(self.driver.find_element_by_id("annotations-sources-in-text").find_elements_by_xpath("option")) == 2

        inputElement.send_keys("source_1.xml")
        inputElement.send_keys(Keys.RETURN)

        notInButton = self.driver.find_element_by_id("annotations-sources-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.click(notInButton)
        #end if

        # Click on query butto
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

    def test_annotations_query_explicit_refs(self):

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
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        # Fill the explicit_ref_like input
        inputElement = self.driver.find_element_by_id("annotations-explicit-refs-like-text")
        inputElement.send_keys("EXPLICIT_REFERENCE")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        # Fill the explicit_ref_like input
        inputElement = self.driver.find_element_by_id("annotations-explicit-refs-like-text")
        inputElement.send_keys("EXPLICIT_REFERENCE")

        notLikeButton = self.driver.find_element_by_id("annotations-explicit-refs-like-checkbox")
        if not notLikeButton.find_element_by_xpath("input").is_selected():
            functions.click(notLikeButton)
        #end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        # Fill the explicit_ref_in input
        inputElement = self.driver.find_element_by_id("annotations-explicit-refs-in-text").find_element_by_xpath("../div/ul/li/input")
        functions.click(inputElement)

        assert len(self.driver.find_element_by_id("annotations-explicit-refs-in-text").find_elements_by_xpath("option")) == 2

        inputElement.send_keys("EXPLICIT_REFERENCE_2")
        inputElement.send_keys(Keys.RETURN)
        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        notInButton = self.driver.find_element_by_id("annotations-explicit-refs-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.click(notInButton)
        #end if

        # Fill the explicit_ref_in input
        inputElement = self.driver.find_element_by_id("annotations-explicit-refs-in-text").find_element_by_xpath("../div/ul/li/input")
        functions.click(inputElement)

        assert len(self.driver.find_element_by_id("annotations-explicit-refs-in-text").find_elements_by_xpath("option")) == 2

        inputElement.send_keys("EXPLICIT_REFERENCE")
        inputElement.send_keys(Keys.RETURN)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

    def test_annotations_query_annotation_names(self):

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
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        # Fill the annotation_name_like input
        inputElement = self.driver.find_element_by_id("annotations-annotation-names-like-text")
        inputElement.send_keys("NAME_2")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        # Fill the annotation_name_like input
        inputElement = self.driver.find_element_by_id("annotations-annotation-names-like-text")
        inputElement.send_keys("NAME_2")

        notLikeButton = self.driver.find_element_by_id("annotations-annotation-names-like-checkbox")
        if not notLikeButton.find_element_by_xpath("input").is_selected():
            functions.click(notLikeButton)
        #end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        # Fill the annotation_name_in input
        inputElement = self.driver.find_element_by_id("annotations-annotation-names-in-text").find_element_by_xpath("../div/ul/li/input")
        functions.click(inputElement)

        assert len(self.driver.find_element_by_id("annotations-annotation-names-in-text").find_elements_by_xpath("option")) == 2

        inputElement.send_keys("NAME_1")
        inputElement.send_keys(Keys.RETURN)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        # Fill the annotation_name_in input
        inputElement = self.driver.find_element_by_id("annotations-annotation-names-in-text").find_element_by_xpath("../div/ul/li/input")
        functions.click(inputElement)

        assert len(self.driver.find_element_by_id("annotations-annotation-names-in-text").find_elements_by_xpath("option")) == 2

        inputElement.send_keys("NAME_2")
        inputElement.send_keys(Keys.RETURN)

        notInButton = self.driver.find_element_by_id("annotations-annotation-names-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.click(notInButton)
        #end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

    def test_annotations_query_annotation_system(self):

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
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        # Fill the annotation_system_like input
        inputElement = self.driver.find_element_by_id("annotations-annotation-system-like-text")
        inputElement.send_keys("SYSTEM_2")

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        # Fill the annotation_system_like input
        inputElement = self.driver.find_element_by_id("annotations-annotation-system-like-text")
        inputElement.send_keys("SYSTEM_2")

        notLikeButton = self.driver.find_element_by_id("annotations-annotation-system-like-checkbox")
        if not notLikeButton.find_element_by_xpath("input").is_selected():
            functions.click(notLikeButton)
        #end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## In ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        # Fill the annotation_system_in input
        inputElement = self.driver.find_element_by_id("annotations-annotation-system-in-text").find_element_by_xpath("../div/ul/li/input")
        functions.click(inputElement)

        assert len(self.driver.find_element_by_id("annotations-annotation-system-in-text").find_elements_by_xpath("option")) == 2

        inputElement.send_keys("SYSTEM_1")
        inputElement.send_keys(Keys.RETURN)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))

        assert number_of_elements == 2

        ## Not in ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        # # Fill the annotation_system_in input
        inputElement = self.driver.find_element_by_id("annotations-annotation-system-in-text").find_element_by_xpath("../div/ul/li/input")
        functions.click(inputElement)

        assert len(self.driver.find_element_by_id("annotations-annotation-system-in-text").find_elements_by_xpath("option")) == 2

        inputElement.send_keys("SYSTEM_2")
        inputElement.send_keys(Keys.RETURN)

        notInButton = self.driver.find_element_by_id("annotations-annotation-system-in-checkbox")
        if not notInButton.find_element_by_xpath("input").is_selected():
            functions.click(notInButton)
        #end if

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 2

    def test_annotations_query_value_text(self):

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
                        {"name": "textname_1",
                         "type": "text",
                         "value": "textvalue_1"
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
                "explicit_reference" : "EXPLICIT_REFERENCE",
                "annotation_cnf": {
                    "name": "NAME_1",
                    "system": "SYSTEM"
                    },
                "values": [{
                    "name": "details",
                    "type": "object",
                    "values":  [
                    {"name": "textname_2",
                     "type": "text",
                     "value": "textvalue_2"
                        }]
                    }]
                },{
                "explicit_reference" : "EXPLICIT_REFERENCE",
                "annotation_cnf": {
                    "name": "NAME_2",
                    "system": "SYSTEM"
                    },
                "values": [{
                    "name": "details",
                    "type": "object",
                    "values": [
                        {"name": "textname_3",
                         "type": "text",
                         "value": "textvalue_2"
                        }]
                    }]
                }]
            }]
        }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5);

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "text", "textname_1", "textvalue_1", True, "==", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## Not like ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "text", "textname_1", "textvalue_2", False, "==", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert  number_of_elements == 2

    def test_annotations_query_value_timestamp(self):

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

        wait = WebDriverWait(self.driver,5);

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", True, "==", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", True, "==", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element is True

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", True, ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element is True

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", True, ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", True, ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element == True

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", True, ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", True, ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", True, ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element == True

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", True, "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element is True

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", True, "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element is True

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", True, "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", True, "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", True, "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element is True

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", True, "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:14", True, "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element is True

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:10", True, "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "timestamp", "timestamp_name_1", "2019-04-26T14:14:20", True, "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

    def test_annotations_query_value_double(self):

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

        wait = WebDriverWait(self.driver,5);

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "double", "double_name_1", "3.5", True, "==", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "double", "double_name_1", "3.5", False, "==", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element is True

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "double", "double_name_1", "3.5", True, ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element is True

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "double", "double_name_1", "3.25", True, ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "double", "double_name_1", "3.75", True, ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element == True

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "double", "double_name_1", "3.5", True, ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "double", "double_name_1", "3.25", True, ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "double", "double_name_1", "3.75", True, ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element == True

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "double", "double_name_1", "3.5", True, "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element is True

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "double", "double_name_1", "3.25", True, "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element is True

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "double", "double_name_1", "3.75", True, "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "double", "double_name_1", "3.5", True, "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "double", "double_name_1", "3.25", True, "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element is True

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "double", "double_name_1", "3.75", True, "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "double", "double_name_1", "3.5", True, "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element is True

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "double", "double_name_1", "3.25", True, "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait,"annotations", "double", "double_name_1", "3.75", True, "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

    def test_annotations_query_ingestion_time(self):

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
            }]
        }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        ingestion_time = self.session.query(Annotation).all()[0].ingestion_time.isoformat()

        wait = WebDriverWait(self.driver,5);

        ## == ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_ingestion_time(self.driver, wait, "annotations", ingestion_time, "==", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## > ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_ingestion_time(self.driver, wait,"annotations", ingestion_time, ">", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element is True

        ## >= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_ingestion_time(self.driver, wait,"annotations", ingestion_time, ">=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## < ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_ingestion_time(self.driver, wait,"annotations", ingestion_time, "<", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element is True

        ## <= ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_ingestion_time(self.driver, wait,"annotations", ingestion_time, "<=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        ## != ##
        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_ingestion_time(self.driver, wait,"annotations", ingestion_time, "!=", 1)

        # Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert empty_element is True

    def test_annotations_query_two_values(self):

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
                        {"name": "textname_1",
                         "type": "text",
                         "value": "textvalue_1"
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
                "explicit_reference" : "EXPLICIT_REFERENCE",
                "annotation_cnf": {
                    "name": "NAME_1",
                    "system": "SYSTEM"
                    },
                "values": [{
                    "name": "details",
                    "type": "object",
                    "values":  [
                    {"name": "textname_1",
                     "type": "text",
                     "value": "textvalue_1"
                        },
                    {"name": "double_name_1",
                     "type": "double",
                     "value": "1.4"
                        }]
                    }]
                },{
                "explicit_reference" : "EXPLICIT_REFERENCE",
                "annotation_cnf": {
                    "name": "NAME_2",
                    "system": "SYSTEM"
                    },
                "values": [{
                    "name": "details",
                    "type": "object",
                    "values": [
                        {"name": "textname_3",
                         "type": "text",
                         "value": "textvalue_2"
                        }]
                    }]
                }]
            }]
        }

        # Check data is correctly inserted
        self.engine_eboa.data = data
        assert eboa_engine.exit_codes["OK"]["status"] == self.engine_eboa.treat_data()[0]["status"]

        wait = WebDriverWait(self.driver,5);

        self.driver.get("http://localhost:5000/eboa_nav/")

        # Go to tab
        functions.goToTab(self.driver,"Annotations")
        functions.click_no_graphs_annotations(self.driver)

        functions.fill_value(self.driver, wait, "annotations", "text", "textname_1", "textvalue_1", True, "==", 1)
        functions.click(self.driver.find_element_by_id("annotations-add-value"))
        functions.fill_value(self.driver, wait, "annotations", "double", "double_name_1", "1.4", True, "==", 2)

        # Click on query butto
        submitButton = wait.until(EC.visibility_of_element_located((By.ID,'annotations-submit-button')))
        functions.click(submitButton)

        # Check table generated
        annotations_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations-table")))
        number_of_elements = len(annotations_table.find_elements_by_xpath("tbody/tr"))
        empty_element = len(annotations_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

        assert number_of_elements == 1 and empty_element is False

        assert True
