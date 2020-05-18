# Python Library
import json
import os
import time

# Selenium library
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


CurrentDirectory = os.path.dirname(__file__)

with open(os.path.join(CurrentDirectory, "myAccount.json"), "r") as fp:
    UserNameAndPassword = json.load(fp)

url = "https://weixine.ustc.edu.cn/2020/caslogin"

driver = webdriver.PhantomJS()

driver.get(url)

UserName = driver.find_element_by_id("username")
Password = driver.find_element_by_id("password")
LoginButton = driver.find_element_by_id("login")

UserName.send_keys(UserNameAndPassword["username"])
Password.send_keys(UserNameAndPassword["password"])
LoginButton.click()

time.sleep(5)

SubmitButton = driver.find_element_by_id("report-submit-btn")
SubmitButton.click()


