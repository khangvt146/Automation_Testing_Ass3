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

TESTCASE_PATH = 'decision_table/testcase.csv'
DATA_PATH = 'decision_table/data.csv'
LOG_PATH = 'decision_table/log.txt'

all_quiz_name = []
testcase_cnt = {'success': 0, 'failed': 0}

def get_all_quiz_name():
    df = pd.read_csv(DATA_PATH, sep=',')
    return df['Tên bài tập'].to_list()

def compare_list(lst_1, lst_2):
    if len(lst_1) != len(lst_2):
        return False
    
    idx = 0
    
    for i in range(len(lst_1)):
        if lst_1[idx] != lst_2[idx]:
            return False
    return True

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
    
def run(driver):
    df = pd.read_csv(TESTCASE_PATH, sep=',')

    for _, row in df.iterrows():
        step_success = 0
        step_2 = []
        global all_quiz_name
        

        print('Testcase {}:'.format(row['testname']))
        driver.find_element("xpath", "//a[@href='http://localhost/my/']").click()
        print('\t - Step 1: Load Timeline page successful')
        step_success += 1
        
        ##################### DEFAULT CASE #########################################
         # Filter select
        filter_btn = driver.find_element("xpath", "//button[@title='Filter timeline by date']")
        driver.execute_script("arguments[0].click();", filter_btn)
        filter_ = driver.find_element("xpath", f"//a[@data-filtername='{row['filtering']}']")
        driver.execute_script("arguments[0].click();", filter_)
        time.sleep(3)
        
        # Sort select
        sort_btn = driver.find_element("xpath", "//button[@title='Sort timeline items']")
        driver.execute_script("arguments[0].click();", sort_btn)
        if row['sort'] == 'Sort by dates':               
            sorting = driver.find_element("xpath", "//a[@data-filtername='sortbydates']")  
            driver.execute_script("arguments[0].click();", sorting)
            time.sleep(2)
            
            try:    
                WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//button[@data-action='more-events']")))
                more_events = driver.find_element("xpath", "//button[@data-action='more-events']")
                driver.execute_script("arguments[0].click();", more_events)
                
            except Exception:
                pass
   
        else:
            sorting = driver.find_element("xpath", "//a[@data-filtername='sortbycourses']")
            driver.execute_script("arguments[0].click();", sorting)
            time.sleep(2)
            
             # Get more event
            try:    
                WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//button[@data-action='more-courses']")))
                more_courses = driver.find_element("xpath", "//button[@data-action='more-courses']")
                driver.execute_script("arguments[0].click();", more_courses)
                
            except Exception:
                pass
             
        time.sleep(3)
        
                
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h6[@class='event-name mb-0 pb-1 text-truncate']")))

            all_text_step2 = driver.find_element("xpath", "//div[@class='block-timeline']").text
                        
            for item in all_text_step2.split('\n'):
                if item in all_quiz_name:
                    step_2.append(item)
        
        except Exception:
            pass
        output = row['output'].split(',')
        if compare_list(step_2, output):
            print('\t - Step 2: Load quiz with default filter successful.\n\t Expected: {}.\n\t Output: {}'.format(output, step_2))
            step_success += 1
        else:
            print('\t - Step 2: Load quiz with default filter failed.\n\t Expected: {}.\n\t Output: {}'.format(output, step_2))
        
        if step_success == 2:
            testcase_cnt['success'] += 1
        else:
            testcase_cnt['failed'] += 1
        print('Result: {}/{}\n'.format(step_success, 2))
        print('--------------------------------------------------------\n')
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
    all_quiz_name = get_all_quiz_name()
    main()
    