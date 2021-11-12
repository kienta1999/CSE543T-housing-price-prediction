# get specific housing information

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

# write header
data_file = open("./data/housing_data_raw.csv", "a")
data_file.write('beds, bath, area, stress_address, city, state, year_built, \
lot_size, county, walk_score, transit_score, bike_score, price\n')
data_file.close()

# all_href = pd.read_csv('./data/property_href.csv')['href']
# for href in all_href:

# test with only 2 href first
for href in ['https://www.redfin.com/CA/San-Francisco/401-Harrison-St-94105/unit-46B/home/144064341', \
            'https://www.redfin.com/NY/Fort-Plain/38-Clinton-Ave-13339/home/92339866']:
    data_file = open("./data/housing_data_raw.csv", "a")
    progress_file = open("progress2.txt", "a")
    driver.get(href)
    sleep(0.2)
    data = driver.find_elements(By.CSS_SELECTOR , ".statsValue")
    [price, beds, bath, area] = [c.text for c in data]
    price = price.replace(',', '')
    area = area.replace(',', '')
    stress_address = driver.find_elements(By.CSS_SELECTOR , ".street-address")[0].text[:-1]
    city_and_state = driver.find_elements(By.CSS_SELECTOR , ".dp-subtext")[0].text

    # home_facts = driver.find_elements(By.CSS_SELECTOR, ".keyDetailsList")[0] \
    #                    .find_elements(By.CSS_SELECTOR, "div.keyDetail")
    # home_fact_index = [fact.find_elements(By.CSS_SELECTOR , "span")[0].text for fact in home_facts]
    # home_fact_text = [fact.find_elements(By.CSS_SELECTOR, "span.text-right")[0].text for fact in home_facts]
    # year_built = home_fact_text[home_fact_index.index('Year Built')] if 'Year Built' in home_fact_index else None
    # lot_size = home_fact_text[home_fact_index.index('Lot Size')] if 'Lot Size' in home_fact_index else None

    basic_infor = driver.find_elements(By.ID, "basicInfo")[0]
    basic_infor_label = [e.text for e in basic_infor.find_elements(By.CSS_SELECTOR, "span.table-label")]
    basic_infor_value = [e.text for e in basic_infor.find_elements(By.CSS_SELECTOR, "div.table-value")]
    year_built = basic_infor_value[basic_infor_label.index('Year Built')] if 'Year Built' in basic_infor_label else None
    county = basic_infor_value[basic_infor_label.index('County')] if 'County' in basic_infor_label else None
    lot_size = basic_infor_value[basic_infor_label.index('Lot Size')] if 'Lot Size' in basic_infor_label else None
    lot_size = lot_size.replace(',', '')
    scores = driver.find_elements(By.CSS_SELECTOR , ".walk-score")
    if scores:
        scores = scores[0].find_elements(By.CSS_SELECTOR , ".score")
        trademark = [score.find_elements(By.CSS_SELECTOR , ".walkscore-trademark")[0].text[:-1] for score in scores]
        score_value = [score.find_elements(By.CSS_SELECTOR , "div.percentage > span.value")[0].text for score in scores]
        walk_score = score_value[trademark.index('Walk Score')] if 'Walk Score' in trademark else None
        transit_score = score_value[trademark.index('Transit Score')] if 'Transit Score' in trademark else None
        bike_score = score_value[trademark.index('Bike Score')] if 'Bike Score' in trademark else None
    data_file.write(f'{beds}, {bath}, {area}, {stress_address}, {city_and_state}, {year_built}, {lot_size}, {county}, {walk_score}, {transit_score}, {bike_score}, {price}\n')
    progress_file.write(f'crawling done for property {href}\n')
    data_file.close()