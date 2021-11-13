# get all href to properties

from selenium import webdriver  # install selenium
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

import pandas as pd
from time import sleep

path_to_browser = "./chromedriver.exe"
ser = Service(path_to_browser)
op = webdriver.ChromeOptions()
op.add_argument('headless')
driver = webdriver.Chrome(service=ser, options=op)
driver.maximize_window()
data_file = open("./data/property_href.csv", "a")
data_file.write('zipcode,href\n')
data_file.close()

zip_code = pd.read_excel('data/uszips.xlsx')
# curr_zip  = 63744
# for code in zip_code[zip_code['zip'] > curr_zip]['zip']:

for code in zip_code['zip']:
    code = str(code).zfill(5)
    progress_file = open("progress.txt", "a")
    page_link_to_open = f"https://www.redfin.com/zipcode/{code}"
    driver.get(page_link_to_open)
    sleep(0.1)
    homeCard = driver.find_elements(By.CSS_SELECTOR , "a.slider-item")
    data_file = open("./data/property_href.csv", "a")
    for href in [c.get_attribute('href') for c in homeCard]:
        data_file.write(f'{code}, {href}\n')
    data_file.close()
    progress_file.write(f'crawling done for zipcode {code}\n')
    progress_file.close()

# import random 
# def partition (list_in, n):
#     random.shuffle(list_in)
#     return [list_in[i::n] for i in range(n)]

# href = pd.read_csv('data\property_href.csv')
# set_href = list(set(href[' href']))
# lists = partition(set_href, 10)