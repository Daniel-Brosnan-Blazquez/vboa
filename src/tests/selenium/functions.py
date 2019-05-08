"""
Extra functions used to perform selenium tests

Written by DEIMOS Space S.L. (femd)

module vboa
"""
import os
import sys
import unittest
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import ActionChains,TouchActions
from selenium.webdriver.common.keys import Keys


def goToTab(driver,tab_name):
    tab = driver.find_element_by_link_text(tab_name)
    tab.click()

def value_comparer(tab, driver, wait, type, value_name, value_value, like_bool, value_operator):

    types = {"text":1,"timestamp":2,"boolean":3,"double":4,"geometry":6,"object":7}
    value_operators = {"==":1,">":2,">=":3,"<":4,"<=":5,"!=":6}
    tabs = {
        "annotations": "/html/body/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div/form",
        "events": "/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form"
    }

    # filter, will be erased when finding elements by ID
    if tab is "annotations":
        if type is not "ingestion_time":
            driver.find_element_by_xpath(tabs[tab] + "/div[4]/div[1]/select").click()
            driver.find_element_by_xpath(tabs[tab] + "/div[4]/div[1]/select/option["+ str(types[type]) +"]").click()

            inputElement = driver.find_element_by_xpath(tabs[tab] + "/div[4]/div[2]/div/input")
            inputElement.send_keys(value_name)

            inputElement = driver.find_element_by_xpath(tabs[tab] + "/div[4]/div[3]/div/input")
            inputElement.send_keys(value_value)

            if like_bool is False:
                driver.find_element_by_xpath(tabs[tab] + "/div[4]/div[2]/div/select").click()
                driver.find_element_by_xpath(tabs[tab] + "/div[4]/div[2]/div/select/option[2]").click()
            #end if

            driver.find_element_by_xpath(tabs[tab] + "/div[4]/div[3]/div/select").click()
            driver.find_element_by_xpath(tabs[tab] + "/div[4]/div[3]/div/select/option["+ str(value_operators[value_operator]) +"]").click()
        #end if
        else:
            driver.find_element_by_xpath(tabs[tab] + "/div[6]/div[1]/div/div/select").click()
            driver.find_element_by_xpath(tabs[tab] + "/div[6]/div[1]/div/div/select/option["+ str(value_operators[value_operator]) +"]").click()

            inputElement = driver.find_element_by_xpath(tabs[tab] + "/div[6]/div[1]/div/input")
            ActionChains(driver).double_click(inputElement).perform()
            inputElement.send_keys(value_name)
        #end else

        #Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,"/html/body/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div/form/div[9]/button")))
        submitButton.click()
    #end if

    elif tab is "events":
        if type is not "ingestion_time":
            driver.find_element_by_xpath(tabs[tab] + "/div[5]/div[1]/select").click()
            driver.find_element_by_xpath(tabs[tab] + "/div[5]/div[1]/select/option["+ str(types[type]) +"]").click()

            inputElement = driver.find_element_by_xpath(tabs[tab] + "/div[5]/div[2]/div/input")
            inputElement.send_keys(value_name)

            inputElement = driver.find_element_by_xpath(tabs[tab] + "/div[5]/div[3]/div/input")
            inputElement.send_keys(value_value)

            if like_bool is False:
                driver.find_element_by_xpath(tabs[tab] + "/div[5]/div[2]/div/select").click()
                driver.find_element_by_xpath(tabs[tab] + "/div[5]/div[2]/div/select/option[2]").click()
            #end if

            driver.find_element_by_xpath(tabs[tab] + "/div[5]/div[3]/div/select").click()
            driver.find_element_by_xpath(tabs[tab] + "/div[5]/div[3]/div/select/option["+ str(value_operators[value_operator]) +"]").click()
        #end if
        else:
            driver.find_element_by_xpath(tabs[tab] + "/div[9]/div[1]/div/div/select").click()
            driver.find_element_by_xpath(tabs[tab] + "/div[9]/div[1]/div/div/select/option["+ str(value_operators[value_operator]) +"]").click()

            inputElement = driver.find_element_by_xpath(tabs[tab] + "/div[9]/div[1]/div/input")
            ActionChains(driver).double_click(inputElement).perform()
            inputElement.send_keys(value_name)
        #end else
        #Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,"/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[12]/button")))
        submitButton.click()
    #end if

    #Check table generated
    annot_table = wait.until(EC.visibility_of_element_located((By.ID,tab)))
    number_of_elements = len(annot_table.find_elements_by_xpath("tbody/tr"))
    empty_element = len(annot_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

    return number_of_elements,empty_element

def two_values_comparer(tab,driver, wait, type, type_2, value_name, value_value, value_name_2, value_value_2, like_bool, like_bool_2, value_operator, value_operator_2):

    types = {"text":1,"timestamp":2,"boolean":3,"double":4,"geometry":6,"object":7}
    value_operators = {"==":1,">":2,">=":3,"<":4,"<=":5,"!=":6}
    tabs = {
        "annotations": "/html/body/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div/form",
        "events": "/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form"
    }

    if tab is "annotations":
        # type
        if type is not "ingestion_time":
            driver.find_element_by_xpath(tabs[tab] + "/div[4]/div[1]/select").click()
            driver.find_element_by_xpath(tabs[tab] + "/div[4]/div[1]/select/option["+ str(types[type]) +"]").click()

            inputElement = driver.find_element_by_xpath(tabs[tab] + "/div[4]/div[2]/div/input")
            inputElement.send_keys(value_name)

            inputElement = driver.find_element_by_xpath(tabs[tab] + "/div[4]/div[3]/div/input")
            inputElement.send_keys(value_value)

            if like_bool is False:
                driver.find_element_by_xpath(tabs[tab] + "/div[4]/div[2]/div/select").click()
                driver.find_element_by_xpath(tabs[tab] + "/div[4]/div[2]/div/select/option[2]").click()
            #end if

            driver.find_element_by_xpath(tabs[tab] + "/div[4]/div[3]/div/select").click()
            driver.find_element_by_xpath(tabs[tab] + "/div[4]/div[3]/div/select/option["+ str(value_operators[value_operator]) +"]").click()
        #end if
        else:
            driver.find_element_by_xpath(tabs[tab] + "/div[6]/div[1]/div/div/select").click()
            driver.find_element_by_xpath(tabs[tab] + "/div[6]/div[1]/div/div/select/option["+ str(value_operators[value_operator]) +"]").click()

            inputElement = driver.find_element_by_xpath(tabs[tab] + "/div[6]/div[1]/div/input")
            ActionChains(driver).double_click(inputElement).perform()
            inputElement.send_keys(value_name)
        #end else

        driver.find_element_by_xpath(tabs[tab] + "/div[4]/div[4]/span/span").click()

        if type_2 is not "ingestion_time":
            driver.find_element_by_xpath(tabs[tab] + "/div[5]/div[1]/div[1]/select").click()
            driver.find_element_by_xpath(tabs[tab] + "/div[5]/div[1]/div[1]/select/option["+ str(types[type_2]) +"]").click()

            inputElement = driver.find_element_by_xpath(tabs[tab] + "/div[5]/div[1]/div[2]/div/input")
            inputElement.send_keys(value_name_2)

            inputElement = driver.find_element_by_xpath(tabs[tab] + "/div[5]/div[1]/div[3]/div/input")
            inputElement.send_keys(value_value_2)

            if like_bool_2 is False:
                driver.find_element_by_xpath(tabs[tab] + "/div[5]/div[1]/div[2]/div/select").click()
                driver.find_element_by_xpath(tabs[tab] + "/div[5]/div[1]/div[2]/div/select/option[2]").click()
            #end if

            driver.find_element_by_xpath(tabs[tab] + "/div[5]/div[1]/div[3]/div/select").click()
            driver.find_element_by_xpath(tabs[tab] + "/div[5]/div[1]/div[3]/div/select/option["+ str(value_operators[value_operator_2]) +"]").click()
        #end if

        #Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,tabs[tab] + '/div[9]/button')))
        submitButton.click()
    #emd if

    elif tab is "events":
        # type
        if type is not "ingestion_time":
            driver.find_element_by_xpath(tabs[tab] + "/div[5]/div[1]/select").click()
            driver.find_element_by_xpath(tabs[tab] + "/div[5]/div[1]/select/option["+ str(types[type]) +"]").click()

            inputElement = driver.find_element_by_xpath(tabs[tab] + "/div[5]/div[2]/div/input")
            inputElement.send_keys(value_name)

            inputElement = driver.find_element_by_xpath(tabs[tab] + "/div[5]/div[3]/div/input")
            inputElement.send_keys(value_value)

            if like_bool is False:
                driver.find_element_by_xpath(tabs[tab] + "/div[5]/div[2]/div/select").click()
                driver.find_element_by_xpath(tabs[tab] + "/div[5]/div[2]/div/select/option[2]").click()
            #end if

            driver.find_element_by_xpath(tabs[tab] + "/div[5]/div[3]/div/select").click()
            driver.find_element_by_xpath(tabs[tab] + "/div[5]/div[3]/div/select/option["+ str(value_operators[value_operator]) +"]").click()
        #end if
        else:
            driver.find_element_by_xpath(tabs[tab] + "/div[7]/div[1]/div/div/select").click()
            driver.find_element_by_xpath(tabs[tab] + "/div[7]/div[1]/div/div/select/option["+ str(value_operators[value_operator]) +"]").click()

            inputElement = driver.find_element_by_xpath(tabs[tab] + "/div[7]/div[1]/div/input")
            ActionChains(driver).double_click(inputElement).perform()
            inputElement.send_keys(value_name)
        #end else

        driver.find_element_by_xpath(tabs[tab] + "/div[5]/div[4]/span/span").click()

        if type_2 is not "ingestion_time":
            driver.find_element_by_xpath(tabs[tab] + "/div[6]/div/div[1]/select").click()
            driver.find_element_by_xpath(tabs[tab] + "/div[6]/div/div[1]/select/option["+ str(types[type_2]) +"]").click()
            inputElement = driver.find_element_by_xpath(tabs[tab] + "/div[6]/div/div[2]/div/input")
            inputElement.send_keys(value_name_2)

            inputElement = driver.find_element_by_xpath(tabs[tab] + "/div[6]/div/div[3]/div/input")
            inputElement.send_keys(value_value_2)

            if like_bool_2 is False:
                driver.find_element_by_xpath(tabs[tab] + "/div[6]/div/div[2]/div/select").click()
                driver.find_element_by_xpath(tabs[tab] + "/div[6]/div/div[2]/div/select/option[2]").click()
            #end if

            driver.find_element_by_xpath(tabs[tab] + "/div[6]/div/div[3]/div/select").click()
            driver.find_element_by_xpath(tabs[tab] + "/div[6]/div/div[3]/div/select/option["+ str(value_operators[value_operator_2]) +"]").click()
        #end if
        #Click on query button
        submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,tabs[tab] + '/div[12]/button')))
        submitButton.click()
    #end elif

    #Check table generated
    annot_table = wait.until(EC.visibility_of_element_located((By.ID,tab)))
    number_of_elements = len(annot_table.find_elements_by_xpath("tbody/tr"))
    empty_element = len(annot_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

    return number_of_elements,empty_element

def period_comparer(driver, wait, start_value = None, start_operator = None, end_value = None, end_operator = None):

    value_operators = {"==":1,">":2,">=":3,"<":4,"<=":5,"!=":6}

    #start
    if(start_value is not None):
        driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[7]/div[1]/div/div/select").click()
        driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[7]/div[1]/div/div/select/option["+ str(value_operators[start_operator]) +"]").click()

        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[7]/div[1]/div/input")
        ActionChains(driver).double_click(inputElement).perform()
        inputElement.send_keys(start_value)
    #end if
    #end start

    #end
    if(end_value is not None):
        driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[7]/div[2]/div/div/select").click()
        driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[7]/div[2]/div/div/select/option["+ str(value_operators[end_operator]) +"]").click()

        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[7]/div[2]/div/input")
        ActionChains(driver).double_click(inputElement).perform()
        inputElement.send_keys(end_value)
    #end if
    #end end

    #Click on query button
    submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,"/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[12]/button")))
    submitButton.click()

    #Check table generated
    annot_table = wait.until(EC.visibility_of_element_located((By.ID,"events")))
    number_of_elements = len(annot_table.find_elements_by_xpath("tbody/tr"))
    empty_element = len(annot_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

    return number_of_elements,empty_element

def two_periods_comparer(driver, wait, start_value_1 = None, start_operator_1 = None, end_value_1 = None, end_operator_1 = None, start_value_2 = None, start_operator_2 = None, end_value_2 = None, end_operator_2 = None):

    value_operators = {"==":1,">":2,">=":3,"<":4,"<=":5,"!=":6}

    #start 1
    if(start_value_1 is not None):
        driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[7]/div[1]/div/div/select").click()
        driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[7]/div[1]/div/div/select/option["+ str(value_operators[start_operator_1]) +"]").click()

        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[7]/div[1]/div/input")
        ActionChains(driver).double_click(inputElement).perform()
        inputElement.send_keys(start_value_1)
    #end if
    #end start 1

    #end 1
    if(end_value_1 is not None):
        driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[7]/div[2]/div/div/select").click()
        driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[7]/div[2]/div/div/select/option["+ str(value_operators[end_operator_1]) +"]").click()

        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[7]/div[2]/div/input")
        ActionChains(driver).double_click(inputElement).perform()
        inputElement.send_keys(end_value_1)
    #end if
    #end end 1

    driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[7]/div[3]/span/span").click()

    #start 2
    if(start_value_2 is not None):
        driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[8]/div/div[1]/div/div/select").click()
        driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[8]/div/div[1]/div/div/select/option["+ str(value_operators[start_operator_2]) +"]").click()

        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[8]/div/div[1]/div/input")
        ActionChains(driver).double_click(inputElement).perform()
        inputElement.send_keys(start_value_2)
    #end if
    #end start 2

    #end 2
    if(end_value_2 is not None):
        driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[8]/div/div[2]/div/div/select").click()
        driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[8]/div/div[2]/div/div/select/option["+ str(value_operators[end_operator_2]) +"]").click()

        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[8]/div/div[2]/div/input")
        ActionChains(driver).double_click(inputElement).perform()
        inputElement.send_keys(end_value_2)
    #end if
    #end end 2

    #Click on query button
    submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,"/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[12]/button")))
    submitButton.click()

    #Check table generated
    annot_table = wait.until(EC.visibility_of_element_located((By.ID,"events")))
    number_of_elements = len(annot_table.find_elements_by_xpath("tbody/tr"))
    empty_element = len(annot_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

    return number_of_elements,empty_element
