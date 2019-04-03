import os
import sys
import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

# CHECK BROWSER PROCESS KILLED

def test_empty_events_table():
    options = Options()
    options.headless = True

    # Create a new instance of the Firefox driver
    driver = webdriver.Firefox(options=options)

    wait = WebDriverWait(driver,30);

    driver.get("http://localhost:5000/eboa_nav/")

    # the page is ajaxy so the title is originally this:
    print(driver.title)

    # find the element that's name attribute is source_like
    inputElement = driver.find_element_by_name("source_like")

    # type in the search
    inputElement.send_keys("XXX")

    # submit the form
    submitElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[12]/button")
    submitElement.click()

    events_table = wait.until(EC.visibility_of_element_located((By.XPATH,"/html/body/div[1]/div/div[2]/div/div/div[1]/div[2]/div[2]/div/div[3]/div[2]")))
    table_content = events_table.text

    driver.quit()
    assert table_content == "No data available in table"

#def test_empty_events_timeline():
    # options = Options()
    # options.headless = True
    #
    # # Create a new instance of the Firefox driver
    # driver = webdriver.Firefox(options=options)
    #
    # wait = WebDriverWait(driver,30);
    #
    # driver.get("http://localhost:5000/eboa_nav/")
    #
    # # the page is ajaxy so the title is originally this:
    # print(driver.title)
    #
    # # find the element that's name attribute is source_like
    # inputElement = driver.find_element_by_name("source_like")
    #
    # # type in the search
    # inputElement.send_keys("XXX")
    #
    # # submit the form
    # submitElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[12]/button")
    # submitElement.click()
    #
    # events_timeline = wait.until(EC.visibility_of_element_located((By.XPATH,"/html/body/div[1]/div/div[2]/div/div/div[1]/div[3]/div[2]")))
    # table_content = events_timeline.text
    #
    # driver.quit()
    # assert table_content == "No data available in table"

def test_element_exists():
    options = Options()
    options.headless = True

    # Create a new instance of the Firefox driver
    driver = webdriver.Firefox(options=options)

    wait = WebDriverWait(driver,30);

    driver.get("http://localhost:5000/eboa_nav/")

    # the page is ajaxy so the title is originally this:
    print(driver.title)

    # find the element that's name attribute is source_like
    inputElement = driver.find_element_by_name("source_like")

    # type in the search
    inputElement.send_keys("FILE_WITH_LINKS.EOF")

    # submit the form
    submitElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[12]/button")
    submitElement.click()

    events_table = wait.until(EC.visibility_of_element_located((By.XPATH,"/html/body/div[1]/div/div[2]/div/div/div[1]/div[2]/div[2]/div/div[3]/div[2]")))
    gauge_name = events_table.find_element_by_xpath("table/tbody/tr/td[2]").text
    events_table.find_element_by_xpath('//*[@id="events"]').screenshot("/vboa/src/tests/selenium/screen.png")

    driver.quit()
    assert gauge_name == "STATION_REPORT"
