from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager import chrome
import json
import pandas as pd
from dotenv import *

TESTCASE_PATH = 'equivalent_class/testcase.csv'
testcase_cnt = {'success': 0, 'failed': 0}

def getCurrentTestDay(driver, interval):
    driver.get(f"http://localhost/calendar/view.php?view=day&time={interval}")
    
def getNextDay(driver):
    next_click = driver.find_element("xpath", "//a[@class='arrow_link next']")
    next_day = next_click.get_attribute('data-day')
    next_year = next_click.get_attribute('data-year')
    next_month = next_click.get_attribute('data-month')
    
    return f"{next_year}/{next_month.zfill(2)}/{next_day.zfill(2)}"

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

    driver.find_element("xpath", "//a[@href='http://localhost/my/']").click()

    driver.find_element("xpath", "//*[@id='inst8']/div/div/div[2]/div/span[1]").click()
 
    driver.find_element("xpath", "//button[@id='calendarviewdropdown']").click()
    
    day_filter = driver.find_element("xpath", "//ul[@class='dropdown-menu show']/li[2]/a")
    
    driver.execute_script("arguments[0].click();", day_filter)
    

def run(driver, tc, interval):
    getCurrentTestDay(driver, interval)
    next_day = getNextDay(driver)
    global testcase_cnt
    try:
        assert tc['output'] == next_day
        print(f"PASSED. Expected: {tc['output']}. Output: {next_day}")
        testcase_cnt['success'] += 1
    except:
        print(f"FAILED. Expected: {tc['output']}. Output: {next_day}")
        testcase_cnt['failed'] += 1

def main():
    options = Options()
    options.add_experimental_option("detach", True)
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--disable-notifications")
    
    driver = webdriver.Chrome(service=Service(chrome.ChromeDriverManager().install()), options=options)
    setup(driver)
    df = pd.read_csv(TESTCASE_PATH, sep=',')
    

    for _, row in df.iterrows():
        print('----------------------------------------')
        print('Testcase {}:'.format(row['testname']))
        curr_day = row['currentDay']
        curr_dt = datetime.strptime(curr_day, "%Y/%m/%d")
        time_epoch = int(curr_dt.timestamp())
        try:
            run(driver, row, time_epoch)
        except:
            run(driver, row, time_epoch)
        print('----------------------------------\n')

    print(f"Total result: {testcase_cnt['success']}/{testcase_cnt['failed'] + testcase_cnt['success']} testcases")
    driver.quit()
    
if __name__ == '__main__':
    main()