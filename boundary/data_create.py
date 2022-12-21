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
import collections
import pandas as pd 

TEST_PATH = 'boundary/data.csv'

def time_handler(driver, start_time, end_time):
    s_dt_split = start_time.split(' ')
    s_date = s_dt_split[0]
    s_time = s_dt_split[1]
    
    e_dt_split = end_time.split(' ')
    e_date = e_dt_split[0]
    e_time = e_dt_split[1]
    
    Select(driver.find_element('xpath', "//*[@id='id_allowsubmissionsfromdate_day']")).select_by_value(str(int(s_date.split('/')[0])))
    Select(driver.find_element('xpath', "//*[@id='id_allowsubmissionsfromdate_month']")).select_by_value(str(int(s_date.split('/')[1])))
    Select(driver.find_element('xpath', "//*[@id='id_allowsubmissionsfromdate_year']")).select_by_value(str(int(s_date.split('/')[2])))
    Select(driver.find_element('xpath', "//*[@id='id_allowsubmissionsfromdate_hour']")).select_by_value(str(int(s_time.split(':')[0])))
    Select(driver.find_element('xpath', "//*[@id='id_allowsubmissionsfromdate_minute']")).select_by_value(str(int(s_time.split(':')[1])))
    
    Select(driver.find_element('xpath', "//*[@id='id_duedate_day']")).select_by_value(str(int(e_date.split('/')[0])))
    Select(driver.find_element('xpath', "//*[@id='id_duedate_month']")).select_by_value(str(int(e_date.split('/')[1])))
    Select(driver.find_element('xpath', "//*[@id='id_duedate_year']")).select_by_value(str(int(e_date.split('/')[2])))
    Select(driver.find_element('xpath', "//*[@id='id_duedate_hour']")).select_by_value(str(int(e_time.split(':')[0])))
    Select(driver.find_element('xpath', "//*[@id='id_duedate_minute']")).select_by_value(str(int(e_time.split(':')[1])))


def prepare_dataset(driver):  
    df = pd.read_csv(TEST_PATH, sep=',')


    # Create course data
    for _, row in df.iterrows():
        driver.get("http://localhost/my/courses.php")
        
        # filter all to access courses
        driver.find_element("xpath", "//*[@id='groupingdropdown']").click()
        filter_ = driver.find_element("xpath", f"//a[@data-value='all']")
        driver.execute_script("arguments[0].click();", filter_)
             
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//a[@class='aalink coursename']")))
        get_courses = driver.find_elements('xpath', "//ul[@class='list-group']//li")
        
        for item in get_courses:
            name = item.find_element('xpath', ".//a[@class='aalink coursename']")
            if name.text.split('\n')[-1] == row['Môn học']:
                name.click()
                driver.find_element("xpath", "//button[@data-action='open-chooser'][1]").click()
                WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "(//a[@title='Thêm mới một Bài tập'])[1]"))).click()
                
                driver.find_element("xpath", "//div[@class='collapsible-actions']/a").click()
                driver.find_element("xpath", "//*[@id='id_name']").send_keys(row['Tên bài tập'])

                time_handler(driver, row["Ngày bắt đầu"], row["Ngày kết thúc"])
                driver.find_element("xpath", "//*[@id='id_gradingduedate_enabled']").click()
                driver.find_element("xpath", "//*[@id='id_submitbutton2']").click()
                time.sleep(3)
                break        
            
                
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
    turn_on_config = driver.find_element("xpath", "//input[@class='custom-control-input']")
    driver.execute_script("arguments[0].click();", turn_on_config)

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
    driver.quit()
    
if __name__ == '__main__':
    main()
