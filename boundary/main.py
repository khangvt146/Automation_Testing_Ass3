from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager import chrome
from selenium.webdriver.common.by import By
import json
from dotenv import *
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

FILE_PATH = dir_path.replace("\\", "/") + '/file/'
TESTCASE_PATH = 'boundary/testcase.csv'
DATA_PATH = 'boundary/data.csv'

all_quiz_name = []
testcase_cnt = {'success': 0, 'failed': 0}


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
    
def find_by_xpath_script(xpath):
    return f'return document.evaluate("{xpath}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue'


def find_by_xpath(driver, xpath):
    script = find_by_xpath_script(xpath)
    elem = driver.execute_script(script)
    return elem

def drop_files(element, files, js_drop_files, offsetX=0, offsetY=0):
    driver = element.parent
    isLocal = not driver._is_remote or '127.0.0.1' in driver.command_executor._url
    paths = []
    
    # ensure files are present, and upload to the remote server if session is remote
    for file in (files if isinstance(files, list) else [files]) :
        if not os.path.isfile(file) :
            raise FileNotFoundError(file)
        paths.append(file if isLocal else element._upload(file))
    
    value = '\n'.join(paths)
    elm_input = driver.execute_script(js_drop_files, element, offsetX, offsetY)
    elm_input._execute('sendKeysToElement', {'value': [value], 'text': value})


def run(driver):
    df = pd.read_csv(TESTCASE_PATH, sep=',')
    for _, row in df.iterrows():
        step_cnt = 0
        print('------------------------------------------------')
        print('Testcase {}:'.format(row['testname']))
        driver.get("http://localhost/my/courses.php")
        print('Step 1: Load Moodle homepage successful')
        step_cnt += 1
        # filter all to access courses
        driver.find_element("xpath", "//*[@id='groupingdropdown']").click()
        filter_ = driver.find_element("xpath", f"//a[@data-value='all']")
        driver.execute_script("arguments[0].click();", filter_)
             
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[@class='aalink coursename']")))
        get_courses = driver.find_elements('xpath', "//ul[@class='list-group']//li")
        
        for item in get_courses:
            name = item.find_element('xpath', ".//a[@class='aalink coursename']")
            if name.text.split('\n')[-1] == row['subject']:
                
                name.click()
                
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='activity-item ']")))
                
                driver.find_element('xpath', "//div[@data-activityname='{}']/div/div/div/div/div[2]/div[2]/a".format(row['quizName'])).click()
                driver.find_element('xpath', "//button[@type='submit']".format(row['quizName'])).click()
                
                break
        print("Step 2: Load detail quiz site successful")
        step_cnt += 1

        WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[@title='Thêm...']")))
        
        open_subwindow = driver.find_element('xpath', "//a[@title='Thêm...']")
        
        driver.execute_script("arguments[0].click();", open_subwindow)
        time.sleep(3)
        
        WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@name='repo_upload_file']")))
        
        input_btn = driver.find_element("xpath","//input[@name='repo_upload_file']")
        
        input_btn.send_keys(FILE_PATH + row['fileName'] )
        
        WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@class='fp-upload-btn btn-primary btn']")))
        driver.find_element("xpath","//button[@class='fp-upload-btn btn-primary btn']").click()
        time.sleep(2)
    
        try:
            driver.find_element("xpath","//input[@name='submitbutton']").click()
            msg = "successful"
        except Exception:
            msg =  driver.find_element("xpath","//div[@class='moodle-exception-message']").text
        
        if msg == row['output']:
            print("Step 3: Upload file successful! Expected: {} Output: {}".format(row["output"], msg))
            step_cnt += 1
            testcase_cnt["success"] += 1
        else:
            print("Step 3: Upload file failed! Expected: {} Output: {}".format(row["output"], msg))
            testcase_cnt["failed"] += 1
        
        print('Result: {}/{}\n'.format(step_cnt, 3))
        print('------------------------------------------------\n')
        time.sleep(3)
        
def main():
    options = Options()
    options.add_experimental_option("detach", True)
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--disable-notifications")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument("disable-logging")
    
    driver = webdriver.Chrome(service=Service(chrome.ChromeDriverManager().install()), options=options)
    setup(driver)
    run(driver)
    print("--------------------------------------------------------------------------------------------")
    print(f"Total result: {testcase_cnt['success']}/{testcase_cnt['failed'] + testcase_cnt['success']} testcases")
    driver.quit()
    
if __name__ == '__main__':
    main()
    