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

TESTCASE_PATH = 'use_case_1/testcase.json'

testcase_cnt = {'success': 0, 'failed': 0}

def compare_list(lst_1, lst_2):
    idx = 0
    for i in range(len(lst_1)):
        if lst_1[idx] != lst_2[idx]:
            return False
    return True

def precondition(driver, testcase):
    driver.find_element("xpath", "//a[@href='http://localhost/my/courses.php']").click()
    
    if len(testcase['last_accessed']) != 0:
        last_access_lst = testcase['last_accessed'][::-1]
        for item in last_access_lst:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//a[@class='aalink coursename']")))
            
            get_courses = driver.find_elements('xpath', "//ul[@class='list-group']//li")
            for i in get_courses:
                name = i.find_element('xpath', ".//a[@class='aalink coursename']")
                if name.text.split('\n')[-1] == item:
                    # print("course name:",name.text.split('\n')[-1])
                    name.click()
                    break
            time.sleep(1)
            driver.find_element("xpath", "//a[@href='http://localhost/my/courses.php']").click()
    
    if len(testcase['starred']) != 0:
        driver.find_element("xpath", "//*[@id='groupingdropdown']").click()
        filter_ = driver.find_element("xpath", f"//a[@data-value='all']")
        driver.execute_script("arguments[0].click();", filter_)
             
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//a[@class='aalink coursename']")))
        get_courses = driver.find_elements('xpath', "//ul[@class='list-group']//li")
        
        for item in get_courses:
            name = item.find_element('xpath', ".//a[@class='aalink coursename']")
            if name.text.split('\n')[-1] in testcase['starred']:
                item.find_element("xpath", ".//div[@class='ml-auto dropdown']/button").click()
                starred = item.find_element("xpath", ".//a[@data-action='add-favourite']")
                driver.execute_script("arguments[0].click();", starred)
                
    if len(testcase['inprogress']) != 0:
        driver.find_element("xpath", "//div[@class='btn-group']/a").click()
        driver.find_element("xpath", "//div[@class='dropdown-menu dropdown-menu-right show']/a[2]").click()
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//a[@class='float-left coursename aalink']")))
        get_courses = driver.find_elements('xpath', "//ul[@class='ml course-list yui3-dd-drop']//li")
        for i in range(len(get_courses)):
            name = driver.find_element('xpath', f"//ul[@class='ml course-list yui3-dd-drop']/li[{i+1}]/div/a[@class='float-left coursename aalink']")
            if name.text.split('\n')[-1] in testcase['inprogress']:
                driver.find_element('xpath', f"//ul[@class='ml course-list yui3-dd-drop']/li[{i+1}]/div/div[3]/span[2]/a[@class='action-edit']").click()
                dt_now = datetime.now().strftime("%Y-%m-%d")
                month = int(dt_now.split('-')[1])
                year = int(dt_now.split('-')[0])
                
                if month == 12:
                    start_month = month - 1
                    start_year = year
                    end_month = 1
                    end_year = year + 1
                elif month == 1:
                    start_month = 12
                    start_year = year - 1
                    end_month = month + 1
                    end_year = year
                else:
                    start_month = month - 1
                    start_year = year
                    end_month = month + 1
                    end_year = year
                    
                Select(driver.find_element('xpath', "//*[@id='id_startdate_month']")).select_by_value(str(start_month))
                Select(driver.find_element('xpath', "//*[@id='id_startdate_year']")).select_by_value(str(start_year))
                Select(driver.find_element('xpath', "//*[@id='id_enddate_month']")).select_by_value(str(end_month))
                Select(driver.find_element('xpath', "//*[@id='id_enddate_year']")).select_by_value(str(end_year))

                driver.find_element("xpath", "//*[@id='id_saveandreturn']").click()
                
        driver.find_element("xpath", "//a[@href='http://localhost/my/courses.php']").click()
    
    
    if len(testcase['future']) != 0:
        driver.find_element("xpath", "//div[@class='btn-group']/a").click()
        driver.find_element("xpath", "//div[@class='dropdown-menu dropdown-menu-right show']/a[2]").click()
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//a[@class='float-left coursename aalink']")))
        get_courses = driver.find_elements('xpath', "//ul[@class='ml course-list yui3-dd-drop']//li")
        for i in range(len(get_courses)):
            name = driver.find_element('xpath', f"//ul[@class='ml course-list yui3-dd-drop']/li[{i+1}]/div/a[@class='float-left coursename aalink']")
            if name.text.split('\n')[-1] in testcase['future']:
                driver.find_element('xpath', f"//ul[@class='ml course-list yui3-dd-drop']/li[{i+1}]/div/div[3]/span[2]/a[@class='action-edit']").click()
                dt_now = datetime.now().strftime("%Y-%m-%d")
                month = int(dt_now.split('-')[1])
                year = int(dt_now.split('-')[0])
                
                if month == 12:
                    start_month = 1
                    start_year = year + 1
                    end_month = 3
                    end_year = year + 1

                else:
                    start_month = month + 1
                    start_year = year
                    end_month = month + 4
                    end_year = year
                    
                Select(driver.find_element('xpath', "//*[@id='id_startdate_month']")).select_by_value(str(start_month))
                Select(driver.find_element('xpath', "//*[@id='id_startdate_year']")).select_by_value(str(start_year))
                Select(driver.find_element('xpath', "//*[@id='id_enddate_month']")).select_by_value(str(end_month))
                Select(driver.find_element('xpath', "//*[@id='id_enddate_year']")).select_by_value(str(end_year))

                driver.find_element("xpath", "//*[@id='id_saveandreturn']").click()
                
        driver.find_element("xpath", "//a[@href='http://localhost/my/courses.php']").click()        

    if len(testcase['past']) != 0:
        driver.find_element("xpath", "//div[@class='btn-group']/a").click()
        driver.find_element("xpath", "//div[@class='dropdown-menu dropdown-menu-right show']/a[2]").click()
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//a[@class='float-left coursename aalink']")))
        get_courses = driver.find_elements('xpath', "//ul[@class='ml course-list yui3-dd-drop']//li")
        for i in range(len(get_courses)):
            name = driver.find_element('xpath', f"//ul[@class='ml course-list yui3-dd-drop']/li[{i+1}]/div/a[@class='float-left coursename aalink']")
            if name.text.split('\n')[-1] in testcase['past']:
                driver.find_element('xpath', f"//ul[@class='ml course-list yui3-dd-drop']/li[{i+1}]/div/div[3]/span[2]/a[@class='action-edit']").click()
                dt_now = datetime.now().strftime("%Y-%m-%d")
                month = int(dt_now.split('-')[1])
                year = int(dt_now.split('-')[0])
                
                if month == 12:
                    start_month = month - 4
                    start_year = year
                    end_month = month - 1
                    end_year = year 
                elif month == 1 or month == 2 or month == 3:
                    start_month = 10
                    start_year = year - 1
                    end_month = 12
                    end_year = year - 1
                else:
                    start_month = month - 3
                    start_year = year
                    end_month = month - 1
                    end_year = year
                    
                Select(driver.find_element('xpath', "//*[@id='id_startdate_month']")).select_by_value(str(start_month))
                Select(driver.find_element('xpath', "//*[@id='id_startdate_year']")).select_by_value(str(start_year))
                Select(driver.find_element('xpath', "//*[@id='id_enddate_month']")).select_by_value(str(end_month))
                Select(driver.find_element('xpath', "//*[@id='id_enddate_year']")).select_by_value(str(end_year))

                driver.find_element("xpath", "//*[@id='id_saveandreturn']").click()
                
        driver.find_element("xpath", "//a[@href='http://localhost/my/courses.php']").click()
        
    if len(testcase['removed']) != 0:
        driver.find_element("xpath", "//*[@id='groupingdropdown']").click()
        filter_ = driver.find_element("xpath", f"//a[@data-value='all']")
        driver.execute_script("arguments[0].click();", filter_)
        
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//a[@class='aalink coursename']")))
        get_courses = driver.find_elements('xpath', "//ul[@class='list-group']//li")
        
        for item in get_courses:
            name = item.find_element('xpath', ".//a[@class='aalink coursename']")
            if name.text.split('\n')[-1] in testcase['removed']:
                hide_btn = item.find_element("xpath", ".//div[@class='ml-auto dropdown']/button")
                driver.execute_script("arguments[0].click();", hide_btn)

                removed = item.find_element("xpath", ".//a[@data-action='hide-course']")
                driver.execute_script("arguments[0].click();", removed)
                


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
    with open(TESTCASE_PATH, 'r', encoding="utf8") as f:
        test_cases = json.load(f)
    global testcase_cnt
    
    for tc in test_cases:
        step_success = 0
        step_2 = []
        step_3 = []        
        
        precondition(driver, tc['input'])
        
        print('Testcase {}:'.format(tc['input']['name']))
        driver.find_element("xpath", "//a[@href='http://localhost/my/courses.php']").click()
        print('\t - Step 1: Load My Course page successful')
        step_success += 1
        ##################### DEFAULT CASE #########################################
       
         # Filter select
        driver.find_element("xpath", "//*[@id='groupingdropdown']").click()
        filter_ = driver.find_element("xpath", f"//a[@data-value='{tc['input']['filter']}']")
        driver.execute_script("arguments[0].click();", filter_)
        time.sleep(3)
        
        # Sort select
        driver.find_element("xpath", "//*[@id='sortingdropdown']").click()
        if tc['input']['sort'] == 'Sort by last accessed':
            sorting = driver.find_element("xpath", "//a[@data-value='ul.timeaccess desc']")
        else:
            sorting = driver.find_element("xpath", "//a[@data-value='fullname']")
        driver.execute_script("arguments[0].click();", sorting)
        time.sleep(3)
       

        # View select
        driver.find_element("xpath", "//*[@id='displaydropdown']").click()
        view = driver.find_element("xpath", "//a[@data-value='list']")
        driver.execute_script("arguments[0].click();", view)
        time.sleep(3)
        
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//a[@class='aalink coursename']")))

            get_courses_1 = driver.find_elements('xpath', "//ul[@class='list-group']//li")
            
        except Exception:
            get_courses_1 = []
        
        for item in get_courses_1:
            name_1 = item.find_element('xpath', ".//a[@class='aalink coursename']").text
            step_2.append(name_1.split('\n')[-1])
       
        if compare_list(step_2, tc['output']['default']):
            print('\t - Step 2: Load course with default filter successful. Expected: {}. Output: {}'.format(tc['output']['default'], step_2))
            step_success += 1
        else:
            print('\t - Step 2: Load course with default filter failed. Expected: {}. Output: {}'.format(tc['output']['default'], step_2))
            
        #################################################################################
        
        ######################### TEST FILTER ###########################################
         # Search input
        if len(tc['input']['searchbar']) != 0:
            driver.find_element("xpath", "//*[@id='searchinput']").send_keys(tc['input']['searchbar'])
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//button[@class='btn btn-clear']")))
            time.sleep(5)
        
        # Sort test
        if len(tc['input']['sortTest']) != 0:
            driver.find_element("xpath", "//*[@id='sortingdropdown']").click()
            if tc['input']['sortTest'] == 'Sort by last accessed':
                sortingTest = driver.find_element("xpath", "//a[@data-value='ul.timeaccess desc']")
            else:
                sortingTest = driver.find_element("xpath", "//a[@data-value='fullname']") 
            driver.execute_script("arguments[0].click();", sortingTest)
            time.sleep(3)
            
        # Filter test
        if len(tc['input']['filterTest']) != 0:
            driver.find_element("xpath", "//*[@id='groupingdropdown']").click()
            filter = driver.find_element("xpath", f"//a[@data-value='{tc['input']['filterTest']}']")
            driver.execute_script("arguments[0].click();", filter)
            time.sleep(3)
            
        if len(tc['input']['filterTest']) == 0 and len(tc['input']['sortTest']) == 0:
            if step_success == 2:
                testcase_cnt['success'] += 1
            else:
                testcase_cnt['failed'] += 1
            print('Result: {}/{}'.format(step_success, 2))
            print('--------------------------------------------------------\n')
            continue
        else:   
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//a[@class='aalink coursename']")))
                        
            get_courses_2 = driver.find_elements('xpath', "//ul[@class='list-group']//li")

            for item in get_courses_2:
                name_2 = item.find_element('xpath', ".//a[@class='aalink coursename']").text
                step_3.append(name_2.split('\n')[-1])
            if compare_list(step_3, tc['output']['test']):
                print('\t - Step 3: Load course with test filter succesful. Expected: {}. Output: {}'.format(tc['output']['test'], step_3))
                step_success += 1
            else:
                print('\t - Step 3: Load course with test filter failed. Expected: {}. Output: {}'.format(tc['output']['test'], step_3))
            
            if step_success == 3:
                testcase_cnt['success'] += 1
            else:
                testcase_cnt['failed'] += 1 
        
        print('Result: {}/{}'.format(step_success, 3))
        print('--------------------------------------------------------\n')
        time.sleep(5)

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