from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import string
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

from selenium.common.exceptions import TimeoutException

import sys
import os
from datetime import datetime
import csv


url = 'https://warrants-hk.credit-suisse.com/en/cbbc/outstanding-chart'

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

def bot_dirver():
    # driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    driver.maximize_window()
    time.sleep(2)

    return driver

def write_to_record(rows, col_date):
    for row in range(len(rows)):
        all_cols = rows[row].findAll('td')

        call_level_lower = all_cols[0].text.strip().split(' - ')[0]
        call_level_upper = all_cols[0].text.strip().split(' - ')[1]
        try:
            span_value = all_cols[1].find_all('span')
            if len(span_value) >= 1:
                for span in all_cols[1].find_all('span'):
                    # future_contract_num = span.get_text().split(' ')[1][1:-1]
                    future_contract_num = span.get_text()
        except:
            # future_contract_num = all_cols[1].text.strip().split(' ')[1][1:-1]
            future_contract_num = all_cols[1].text.strip()

        record = {}
        record['date'] = col_date
        record['call_level_lower'] = call_level_lower
        record['call_level_upper'] = call_level_upper
        record['future_contract_num'] = future_contract_num

        records.append(record)

def get_table_data(driver, col_date):
    content = driver.page_source
    soup = BeautifulSoup(content, 'lxml')
    table = soup.find('table', attrs = {'id': 'index_os_map'})
    tbody = table.findAll('tbody')

    all_rows = tbody[1].findAll('tr')

    boundary_rows = int((len(all_rows) - 3) / 2)
    
    # bear
    write_to_record(all_rows[:boundary_rows], col_date)
    
    # bull
    write_to_record(all_rows[boundary_rows + 2:len(all_rows) - 1], col_date)        

def scrape_data(driver):
    # Historical Chart - Options
    # sDate = driver.find_element_by_xpath("/html/body/div[1]/section/div[2]/div[5]/div[4]/div[3]/div/div")
    # sDate = driver.find_element_by_xpath("/html/body/div[1]/section/div[2]/div[5]/div[4]/div[3]/div/div/div/div[1]")
    sDate = driver.find_element(By.XPATH, '/html/body/div[1]/section/div[2]/div[5]/div[4]/div[3]/div/div/div/div[1]')
    sDate.click()
    time.sleep(2)

    sDate_options = driver.find_elements_by_xpath("/html/body/div[1]/section/div[2]/div[5]/div[4]/div[3]/div/div/div/div[2]/div/div")

    for index in range(len(sDate_options)):
        col_date = sDate_options[index].text.strip()
        sDate_options[index].click()
        time.sleep(3)

        get_table_data(driver, col_date)

        # sDate - Back
        sDate.click()
        time.sleep(2)



if __name__ == "__main__":
    # Load driver
    driver = bot_dirver()

    # Start scraping
    scrape_data(driver)

    # write to csv
    with open('hk.csv', mode='w') as csv_file:
        fieldnames= ['date', 'call_level_lower', 'call_level_upper', 'future_contract_num']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for entry in records:
            writer.writerow({
                'date': entry['date'],
                'call_level_lower': entry['call_level_lower'],
                'call_level_upper': entry['call_level_upper'],
                'future_contract_num': entry['future_contract_num']
            })

    # End driver
    driver.quit()
