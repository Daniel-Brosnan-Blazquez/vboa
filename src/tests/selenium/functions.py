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
    print(tab)
    tab.click()

def annotations_value_comparer(driver, wait, type, value_name, value_value, like_bool, value_operator):

    types = {"text":1,"timestamp":2,"boolean":3,"double":4,"geometry":6,"object":7}
    value_operators = {"==":1,">":2,">=":3,"<":4,"<=":5,"!=":6}

    # type
    if type is not "ingestion_time":
        driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div/form/div[4]/div[1]/select").click()
        driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div/form/div[4]/div[1]/select/option["+ str(types[type]) +"]").click()

        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div/form/div[4]/div[2]/div/input")
        inputElement.send_keys(value_name)

        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div/form/div[4]/div[3]/div/input")
        inputElement.send_keys(value_value)

        if like_bool is False:
            driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div/form/div[4]/div[2]/div/select").click()
            driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div/form/div[4]/div[2]/div/select/option[2]").click()

        driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div/form/div[4]/div[3]/div/select").click()
        driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div/form/div[4]/div[3]/div/select/option["+ str(value_operators[value_operator]) +"]").click()
    else:
        driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div/form/div[6]/div[1]/div/div/select").click()
        driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div/form/div[6]/div[1]/div/div/select/option["+ str(value_operators[value_operator]) +"]").click()

        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div/form/div[6]/div[1]/div/input")
        ActionChains(driver).double_click(inputElement).perform()
        inputElement.send_keys(value_name)

    #Click on query button
    submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div/form/div[9]/button')))
    submitButton.click()

    #Check table generated
    annot_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations")))
    number_of_elements = len(annot_table.find_elements_by_xpath("tbody/tr"))
    empty_element = len(annot_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

    return number_of_elements,empty_element

def annotations_two_values_comparer(driver, wait, type, type_2, value_name, value_value, value_name_2, value_value_2, like_bool, like_bool_2, value_operator, value_operator_2):

    types = {"text":1,"timestamp":2,"boolean":3,"double":4,"geometry":6,"object":7}
    value_operators = {"==":1,">":2,">=":3,"<":4,"<=":5,"!=":6}


    # type
    if type is not "ingestion_time":
        driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div/form/div[4]/div[1]/select").click()
        driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div/form/div[4]/div[1]/select/option["+ str(types[type]) +"]").click()

        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div/form/div[4]/div[2]/div/input")
        inputElement.send_keys(value_name)

        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div/form/div[4]/div[3]/div/input")
        inputElement.send_keys(value_value)

        if like_bool is False:
            driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div/form/div[4]/div[2]/div/select").click()
            driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div/form/div[4]/div[2]/div/select/option[2]").click()

        driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div/form/div[4]/div[3]/div/select").click()
        driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div/form/div[4]/div[3]/div/select/option["+ str(value_operators[value_operator]) +"]").click()
    else:
        driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div/form/div[6]/div[1]/div/div/select").click()
        driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div/form/div[6]/div[1]/div/div/select/option["+ str(value_operators[value_operator]) +"]").click()

        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div/form/div[6]/div[1]/div/input")
        ActionChains(driver).double_click(inputElement).perform()
        inputElement.send_keys(value_name)

    driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div/form/div[4]/div[4]/span/span").click()

    if type_2 is not "ingestion_time":
        driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div/form/div[5]/div[1]/div[1]/select").click()
        driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div/form/div[5]/div[1]/div[1]/select/option["+ str(types[type_2]) +"]").click()

        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div/form/div[5]/div[1]/div[2]/div/input")
        inputElement.send_keys(value_name_2)

        inputElement = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div/form/div[5]/div[1]/div[3]/div/input")
        inputElement.send_keys(value_value_2)

        if like_bool_2 is False:
            driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div/form/div[5]/div[1]/div[2]/div/select").click()
            driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div/form/div[5]/div[1]/div[2]/div/select/option[2]").click()

        driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div/form/div[5]/div[1]/div[3]/div/select").click()
        driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div/form/div[5]/div[1]/div[3]/div/select/option["+ str(value_operators[value_operator_2]) +"]").click()

    #Click on query button
    submitButton = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div/form/div[9]/button')))
    submitButton.click()

    #Check table generated
    annot_table = wait.until(EC.visibility_of_element_located((By.ID,"annotations")))
    number_of_elements = len(annot_table.find_elements_by_xpath("tbody/tr"))
    empty_element = len(annot_table.find_elements_by_xpath("tbody/tr/td[contains(@class,'dataTables_empty')]")) > 0

    return number_of_elements,empty_element
