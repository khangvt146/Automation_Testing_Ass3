from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from webdriver_manager import chrome
from selenium.webdriver.common.by import By
import json
from dotenv import *
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

DATA_PATH = 'use_case_1/data.csv'

def create_course(driver, data):
    driver.find_element("xpath", "//input[@id='id_fullname']").send_keys(data['fullName'])
    driver.find_element("xpath", "//input[@id='id_shortname']").send_keys(data['shortName'])
    driver.find_element("xpath", "//input[@id='id_idnumber']").send_keys(data['courseId'])
    driver.find_element("xpath", "//*[@id='id_saveanddisplay']").click()

def prepare_dataset(driver):
    df = pd.read_csv(DATA_PATH, sep=',')
        
    # Create course data
    for _,row in df.iterrows():
        driver.find_element("xpath", "//a[@href='http://localhost/my/courses.php']").click()
        driver.find_element("xpath", "//div[@class='btn-group']/a").click()
        driver.find_element("xpath", "//div[@class='dropdown-menu dropdown-menu-right show']/a[1]").click()
        create_course(driver, row)

def clean_data(driver):
    driver.find_element("xpath", "//a[@href='http://localhost/my/courses.php']").click()
    driver.find_element("xpath", "//div[@class='btn-group']/a").click()
    driver.find_element("xpath", "//div[@class='dropdown-menu dropdown-menu-right show']/a[2]").click()
    config_btn = driver.find_element("xpath", "//*[@id='action-menu-toggle-1']")
    driver.execute_script("arguments[0].click();", config_btn)
    driver.find_element("xpath", "//a[@data-action='delete']").click()
    driver.find_element("xpath", "//*[@id='id_submitbutton']").click()
    time.sleep(10)

def setup(driver):

    driver.get("https://localhost")
    driver.maximize_window()

    link = driver.find_element("xpath", "//a[@href='http://localhost/login/index.php']")
    link.click()

    username = driver.find_elements("xpath", "//*[@id='username']")
    password = driver.find_elements("xpath", "//*[@id='password']")
    env = dotenv_values(".env")
    
    username_login = env["username"] 
    password_login = env["password"]
    
    username[0].send_keys(username_login)
    password[0].send_keys(password_login)

    driver.find_element("xpath", "//*[@id='loginbtn']").click()

def main():
    options = Options()
    options.add_experimental_option("detach", True)
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--disable-notifications")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument("disable-logging")
    
    driver = webdriver.Chrome(service=Service(chrome.ChromeDriverManager().install()), options=options)
    setup(driver)
    prepare_dataset(driver)
    print("Auto create database successful!")
    
if __name__ == '__main__':
    main()