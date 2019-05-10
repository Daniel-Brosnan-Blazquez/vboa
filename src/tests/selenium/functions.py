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
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import ActionChains,TouchActions
from selenium.webdriver.common.keys import Keys


def goToTab(driver,tab_name):
    tab = driver.find_element_by_link_text(tab_name)
    tab.click()

def fill_value(driver, wait, tab, value_type, value_name, value_value, like_bool, value_operator, row):

    if row is 1:
        value_query_div = driver.find_element_by_id(tab + "_value_query_initial")
    else:
        value_query_div = driver.find_element_by_id("more-value-query-" + tab).find_element_by_xpath("div[" + str(row-1) + "]")
    type = Select(value_query_div.find_element_by_id(tab + "_value_type"))
    type.select_by_visible_text(value_type)

    name = value_query_div.find_element_by_id(tab + "_value_name_text")
    name.send_keys(value_name)

    name_like = Select(value_query_div.find_element_by_id(tab + "_value_name_option"))
    if like_bool is False:
        name_like.select_by_visible_text("notlike")

    operator = Select(value_query_div.find_element_by_id(tab + "_value_value_operator"))
    operator.select_by_visible_text(value_operator)

    value = value_query_div.find_element_by_id(tab + "_value_value_text")
    value.send_keys(value_value)

def fill_ingestion_time(driver, wait, tab, value_value, like_bool, value_operator, row):

    if row is 1:
        ingestion_time_div = driver.find_element_by_id(tab + "_ingestion_time_initial")
    else:
        ingestion_time_div = driver.find_element_by_id("more-ingestion-time-query-" + tab).find_element_by_xpath("div[" + str(row-1) + "]")

    operator = Select(ingestion_time_div.find_element_by_id("ingestion_duration_operator"))
    operator.select_by_visible_text(value_operator)

    value = ingestion_time_div.find_element_by_id("ingestion_duration_text")
    value.click()
    value.click()
    value.send_keys(value_value)

def fill_two_values(driver, wait, tab, type, type_2, value_name, value_value, value_name_2, value_value_2, like_bool, like_bool_2, value_operator, value_operator_2):

    fill_value(driver, wait, tab, type, value_name, value_value, like_bool, value_operator, 1)
    driver.find_element_by_id(tab + "_add_value").click()
    fill_value(driver, wait, tab, type_2, value_name_2, value_value_2, like_bool_2, value_operator_2, 2)

def fill_period(driver, wait, tab, row, start_value = None, start_operator = None, end_value = None, end_operator = None):

    if row is 1:
        period_div = driver.find_element_by_id(tab + "_start_stop_initial")
    else:
        period_div = driver.find_element_by_id("more-start-stop-query-" + tab).find_element_by_xpath("div[" + str(row-1) + "]")

    if start_value is not None:
        start = period_div.find_element_by_id("start_input")
        start.click()
        start.click()
        start.send_keys(start_value)

        start_op = Select(period_div.find_element_by_id("start_operator"))
        start_op.select_by_visible_text(start_operator)

    if end_value is not None:
        end = period_div.find_element_by_id("stop_input")
        end.click()
        end.click()
        end.send_keys(end_value)

        end_op = Select(period_div.find_element_by_id("stop_operator"))
        end_op.select_by_visible_text(end_operator)

def fill_two_periods(driver, wait, tab, start_value_1 = None, start_operator_1 = None, end_value_1 = None, end_operator_1 = None, start_value_2 = None, start_operator_2 = None, end_value_2 = None, end_operator_2 = None):

    fill_period(driver, wait, tab, 1, start_value_1, start_operator_1, end_value_1, end_operator_1,)
    driver.find_element_by_id("events_add_start_stop").click()
    fill_period(driver, wait, tab, 2, start_value_2, start_operator_2, end_value_2, end_operator_2)

def click_no_graphs(driver, tab):

    if tab is "Events":
        #Disable show timeline
        timeline_button = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/div/form/div[11]/label")
        if timeline_button.find_element_by_xpath('input').is_selected():
            timeline_button.click()
        #end if
    #end if

    if tab is "Annotations":
        #Disable show map
        map_button = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div/form/div[8]/label")
        if map_button.find_element_by_xpath('input').is_selected():
            map_button.click()
        #end if
    #end if

    if tab is "Sources":
        #Click on show map                                         /html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[14]/label
        validity_timeline_button = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[14]/label")
        driver.execute_script("arguments[0].scrollIntoView();", validity_timeline_button)
        if validity_timeline_button.find_element_by_xpath('input').is_selected():
            validity_timeline_button.click()
        #end if

        #Click on show map
        gen2ing_timeline_button = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[15]/label")
        if gen2ing_timeline_button.find_element_by_xpath('input').is_selected():
            gen2ing_timeline_button.click()
        #end if

        #Click on show map
        number_events_per_source_button = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[16]/label")
        if number_events_per_source_button.find_element_by_xpath('input').is_selected():
            number_events_per_source_button.click()
        #end if

        #Click on show map
        ingestion_duration_button = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[17]/label")
        if ingestion_duration_button.find_element_by_xpath('input').is_selected():
            ingestion_duration_button.click()
        #end if

        #Click on show map
        gen2ing_times_button = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[3]/div/div/div/div/div/form/div[18]/label")
        if gen2ing_times_button.find_element_by_xpath('input').is_selected():
            gen2ing_times_button.click()
        #end if
    #end if

    if tab is "Gauges":
        #Disable show map
        network_button = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/div[5]/div/div/div/div/div/form/div[3]/label")
        if network_button.find_element_by_xpath('input').is_selected():
            network_button.click()
        #end if
    #end if
