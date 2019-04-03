import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

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
#/html/body/div[1]/div/div[2]/div/div/div[1]/div[3]/div[2]/div/div/div[5]/div[1]/div/div[2]/div
events_timeline = wait.until(EC.visibility_of_element_located((By.XPATH,"/html/body/div[1]/div/div[2]/div/div/div[1]/div[3]/div[2]/div/div")))
events_timeline.find_element_by_xpath("div[4]/div[1]/div/div[2]/div[2]/div[1]").screenshot("/vboa/src/tests/selenium/screen.png")
table_content = events_timeline.find_element_by_xpath("div[4]/div[1]/div/div[2]/div[2]/div[1]").tag_name
print(table_content)
driver.quit()
