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
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException

def goToTab(driver,tab_name):
    tab = driver.find_element_by_link_text(tab_name)
    click(tab)

def fill_value(driver, wait, tab, value_type, value_name, value_value, value_name_operator, value_value_operator, row):

    if row is 1:
        value_query_div = driver.find_element_by_id(tab + "-value-query-initial")
    else:
        done = False
        retries = 0
        while not done:
            try:
                value_query_div = driver.find_element_by_id("more-value-query-" + tab).find_element_by_xpath("div[" + str(row-1) + "]")
                done = True
            except NoSuchElementException as e:
                time.sleep(0.1)
                if retries < 10:
                    print("Retry")
                    retries += 1
                    pass
                else:
                    raise e
                # end if
            # end try
        # end while
    # end if

    type_name = Select(value_query_div.find_element_by_id("value-type"))
    type_name.select_by_visible_text(value_type)

    name = value_query_div.find_element_by_id("value-name-text")
    name.send_keys(value_name)

    operator = Select(value_query_div.find_element_by_id("value-name-option"))
    operator.select_by_visible_text(value_name_operator)

    operator = Select(value_query_div.find_element_by_id("value-value-operator"))
    operator.select_by_visible_text(value_value_operator)

    value = value_query_div.find_element_by_id("value-value-text")
    value.send_keys(value_value)

def fill_text_operator_with_more_option(driver, wait, tab, field_name, value_value, value_operator, row):

    if row is 1:
        any_time_or_duration = driver.find_element_by_id(tab + "-" + field_name + "-initial")
    else:
        any_time_or_duration = driver.find_element_by_id("more-" + field_name + "-query-" + tab).find_element_by_xpath("div[" + str(row-1) + "]")

    operator = Select(any_time_or_duration.find_element_by_id(field_name + "-operator"))
    operator.select_by_visible_text(value_operator)

    value = any_time_or_duration.find_element_by_id(field_name + "-text")
    click(value)
    click(value)
    value.send_keys(value_value)

def fill_ingestion_time(driver, wait, tab, value_value, value_operator, row):

    if row is 1:
        ingestion_time_div = driver.find_element_by_id(tab + "-ingestion-time-initial")
    else:
        ingestion_time_div = driver.find_element_by_id("more-ingestion-time-query-" + tab).find_element_by_xpath("div[" + str(row-1) + "]")

    operator = Select(ingestion_time_div.find_element_by_id("ingestion-time-operator"))
    operator.select_by_visible_text(value_operator)

    value = ingestion_time_div.find_element_by_id("ingestion-time-text")
    click(value)
    click(value)
    value.send_keys(value_value)

def fill_generation_time(driver, wait, tab, value_value, value_operator, row):

    if row is 1:
        generation_time_div = driver.find_element_by_id(tab + "-generation-time-initial")
    else:
        generation_time_div = driver.find_element_by_id("more-generation-time-query-" + tab).find_element_by_xpath("div[" + str(row-1) + "]")

    operator = Select(generation_time_div.find_element_by_id("generation-duration-operator"))
    operator.select_by_visible_text(value_operator)

    value = generation_time_div.find_element_by_id("generation-duration-text")
    click(value)
    click(value)
    value.send_keys(value_value)

def fill_ingestion_duration(driver, wait, tab, value_value, value_operator, row):

    if row is 1:
        generation_time_div = driver.find_element_by_id(tab + "-ingestion-duration-initial")
    else:
        generation_time_div = driver.find_element_by_id("more-ingestion-duration-query-" + tab).find_element_by_xpath("div[" + str(row-1) + "]")

    operator = Select(generation_time_div.find_element_by_id("ingestion-duration-operator"))
    operator.select_by_visible_text(value_operator)

    value = generation_time_div.find_element_by_id("ingestion-duration-text")
    click(value)
    click(value)
    value.send_keys(value_value)

def fill_period(driver, wait, tab, row, start_value = None, start_operator = None, end_value = None, end_operator = None):

    if row is 1:
        period_div = driver.find_element_by_id(tab + "-start-stop-initial")
    else:
        period_div = driver.find_element_by_id("more-start-stop-query-" + tab).find_element_by_xpath("div[" + str(row-1) + "]")
    if start_value is not None:
        start = period_div.find_element_by_id("start-input")
        click(start)
        click(start)
        start.send_keys(start_value)

        start_op = Select(period_div.find_element_by_id("start-operator"))
        start_op.select_by_visible_text(start_operator)

    if end_value is not None:
        end = period_div.find_element_by_id("stop-input")
        click(end)
        click(end)
        end.send_keys(end_value)

        end_op = Select(period_div.find_element_by_id("stop-operator"))
        end_op.select_by_visible_text(end_operator)

def fill_validity_period(driver, wait, tab, row, start_value = None, start_operator = None, end_value = None, end_operator = None):

    if row is 1:
        period_div = driver.find_element_by_id(tab + "-validity-start-validity-stop-initial")
    else:
        period_div = driver.find_element_by_id("more-validity-start-validity-stop-query-" + tab).find_element_by_xpath("div[" + str(row-1) + "]")

    if start_value is not None:
        start = period_div.find_element_by_id("start-input")
        click(start)
        click(start)
        start.send_keys(start_value)

        start_op = Select(period_div.find_element_by_id("start-operator"))
        start_op.select_by_visible_text(start_operator)

    if end_value is not None:
        end = period_div.find_element_by_id("stop-input")
        click(end)
        click(end)
        end.send_keys(end_value)

        end_op = Select(period_div.find_element_by_id("stop-operator"))
        end_op.select_by_visible_text(end_operator)

def fill_any_period(driver, wait, tab, field_name, row, start_value = None, start_operator = None, end_value = None, end_operator = None):

    if row is 1:
        any_period_div = driver.find_element_by_id(tab + "-" + field_name + "-initial")
    else:
        any_period_div = driver.find_element_by_id("more-" + field_name + "-query-" + tab).find_element_by_xpath("div[" + str(row-1) + "]")
    if start_value is not None:
        start = any_period_div.find_element_by_id("start-input")
        click(start)
        click(start)
        start.send_keys(start_value)

        start_op = Select(any_period_div.find_element_by_id("start-operator"))
        start_op.select_by_visible_text(start_operator)

    if end_value is not None:
        end = any_period_div.find_element_by_id("stop-input")
        click(end)
        click(end)
        end.send_keys(end_value)

        end_op = Select(any_period_div.find_element_by_id("stop-operator"))
        end_op.select_by_visible_text(end_operator)

def click_no_graphs_events(driver):

    #Disable show timeline
    timeline_button = driver.find_element_by_id("events-show-timeline")
    if timeline_button.find_element_by_xpath('input').is_selected():
        click(timeline_button)
    #end if

def click_no_graphs_annotations(driver):

    #Disable show map
    map_button = driver.find_element_by_id("annotations-show-map")
    if map_button.find_element_by_xpath('input').is_selected():
        click(map_button)
    #end if

def click_no_graphs_sources(driver):

    #Click on show map
    validity_timeline_button = driver.find_element_by_id("sources-show-validity-timeline")
    #driver.execute_script("arguments[0].scrollIntoView();", validity_timeline_button)
    if validity_timeline_button.find_element_by_xpath('input').is_selected():
        click(validity_timeline_button)
    #end if

    #Click on show map
    gen2ing_timeline_button = driver.find_element_by_id("sources-show-generation-to-ingestion-timeline")
    if gen2ing_timeline_button.find_element_by_xpath('input').is_selected():
        click(gen2ing_timeline_button)
    #end if

    #Click on show map
    number_events_per_source_button = driver.find_element_by_id("sources-show-number-events-xy")
    if number_events_per_source_button.find_element_by_xpath('input').is_selected():
        click(number_events_per_source_button)
    #end if

    #Click on show map
    ingestion_duration_button = driver.find_element_by_id("sources-show-ingestion-duration-xy")
    if ingestion_duration_button.find_element_by_xpath('input').is_selected():
        click(ingestion_duration_button)
    #end if

    #Click on show map
    gen2ing_times_button = driver.find_element_by_id("sources-show-generation-time-to-ingestion-time-xy")
    if gen2ing_times_button.find_element_by_xpath('input').is_selected():
        click(gen2ing_times_button)
    #end if

def click_no_graphs_gauges(driver):

    #Disable show map
    network_button = driver.find_element_by_id("gauges-show-network")
    if network_button.find_element_by_xpath('input').is_selected():
        click(network_button)
    #end if

def click(element):

    done = False
    retries = 0
    while not done:
        try:
            element.click()
            done = True
        except ElementClickInterceptedException as e:
            if retries < 5:
                retries += 1
                pass
            else:
                raise e
            # end if
        # end try
    # end while

def select_checkbox(element):
    input = element.find_element_by_xpath("input")
    state = input.is_selected()
    retries = 0
    while state is False:
        click(element)
        state = input.is_selected()
        retries += 1
        if retries > 5:
            print("Too many retries on " + element.get_attribute("id"))
            break
        #end if
    #end while

def verify_js_var(items, expected_items):
    for expected_item in expected_items:
        matched_item = [item for item in items if item["id"] == expected_item["id"]]
        assert len(matched_item) > 0
        assert matched_item[0] == expected_item
    # end for