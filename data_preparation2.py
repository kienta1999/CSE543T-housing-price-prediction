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
op.add_argument("headless")
driver = webdriver.Chrome(service=ser, options=op)
driver.maximize_window()

index = 0

# write header
# data_file = open(f"./data/housing_data_raw/{index}.csv", "a")
# data_file.write('href,stress_address,city,state_and_zip,county,img_href,beds,bath,area,year_built,\
# lot_size,walk_score,transit_score,bike_score,lot_size,\
# cooling,heating,has_pool,parking_size,price\n')
# data_file.close()

all_href = pd.read_csv(f"data/property_href/{index}.csv")["href"]
for i, href in enumerate(all_href):
    # for href in ['https://www.redfin.com/CA/San-Francisco/401-Harrison-St-94105/unit-46B/home/144064341', \
    #             'https://www.redfin.com/NY/Fort-Plain/38-Clinton-Ave-13339/home/92339866']:
    if i <= 16425:
        continue
    data_file = open(f"./data/housing_data_raw/{index}.csv", "a")
    progress_file = open("progress2.txt", "a")
    driver.get(href)
    # sleep(0.1)
    data = driver.find_elements(By.CSS_SELECTOR, ".statsValue")
    if not data:
        continue
    [price, beds, bath, area] = [c.text for c in data]
    price = price.replace(",", "")
    area = area.replace(",", "")
    stress_address = driver.find_elements(By.CSS_SELECTOR, ".street-address")[0].text[
        :-1
    ]
    city_and_state = driver.find_elements(By.CSS_SELECTOR, ".dp-subtext")[0].text

    # home_facts = driver.find_elements(By.CSS_SELECTOR, ".keyDetailsList")[0] \
    #                    .find_elements(By.CSS_SELECTOR, "div.keyDetail")
    # home_fact_index = [fact.find_elements(By.CSS_SELECTOR , "span")[0].text for fact in home_facts]
    # home_fact_text = [fact.find_elements(By.CSS_SELECTOR, "span.text-right")[0].text for fact in home_facts]
    # year_built = home_fact_text[home_fact_index.index('Year Built')] if 'Year Built' in home_fact_index else None
    # lot_size = home_fact_text[home_fact_index.index('Lot Size')] if 'Lot Size' in home_fact_index else None

    basic_infor = driver.find_elements(By.ID, "basicInfo")
    year_built = county = None
    if basic_infor:
        basic_infor = basic_infor[0]
        basic_infor_label = [
            e.text
            for e in basic_infor.find_elements(By.CSS_SELECTOR, "span.table-label")
        ]
        basic_infor_value = [
            e.text
            for e in basic_infor.find_elements(By.CSS_SELECTOR, "div.table-value")
        ]
        year_built = (
            basic_infor_value[basic_infor_label.index("Year Built")]
            if "Year Built" in basic_infor_label
            else None
        )
        county = (
            basic_infor_value[basic_infor_label.index("County")]
            if "County" in basic_infor_label
            else None
        )
    # lot_size = basic_infor_value[basic_infor_label.index('Lot Size')] if 'Lot Size' in basic_infor_label else None
    # lot_size = lot_size.replace(',', '')
    scores = driver.find_elements(By.CSS_SELECTOR, ".walk-score")
    walk_score = transit_score = bike_score = None
    if scores:
        scores = scores[0].find_elements(By.CSS_SELECTOR, ".score")
        trademark = [
            score.find_elements(By.CSS_SELECTOR, ".walkscore-trademark")[0].text[:-1]
            for score in scores
        ]
        score_value = [
            score.find_elements(By.CSS_SELECTOR, "div.percentage > span.value")[0].text
            for score in scores
        ]
        walk_score = (
            score_value[trademark.index("Walk Score")]
            if "Walk Score" in trademark
            else None
        )
        transit_score = (
            score_value[trademark.index("Transit Score")]
            if "Transit Score" in trademark
            else None
        )
        bike_score = (
            score_value[trademark.index("Bike Score")]
            if "Bike Score" in trademark
            else None
        )

    property_details_container = (
        driver.find_elements(
            By.CSS_SELECTOR, "div.super-group-content > div.amenity-group"
        )
        or []
    )
    pool_text = heating_cooling_text = parking_garage_text = lot_text = []
    for pc in property_details_container:
        header = pc.find_elements(By.TAG_NAME, "h3")[0].text
        if header == "Pool Information":
            pool_text = [e.text for e in pc.find_elements(By.TAG_NAME, "li")]
        if header == "Heating & Cooling":
            heating_cooling_text = [e.text for e in pc.find_elements(By.TAG_NAME, "li")]
        if header == "Parking & Garage Information":
            parking_garage_text = [e.text for e in pc.find_elements(By.TAG_NAME, "li")]
        if header == "Lot Information":
            lot_text = [e.text for e in pc.find_elements(By.TAG_NAME, "li")]

    lot_size = cooling = heating = has_pool = parking_size = None
    for lt in lot_text:
        if lt.startswith("Lot Size Acres: "):
            lot_size = lt.split("Lot Size Acres: ")[1].replace(",", "|")
    for hc in heating_cooling_text:
        if hc.startswith("Cooling: "):
            cooling = hc.split("Cooling: ")[1].replace(",", "|")
        if hc.startswith("Heating: "):
            heating = hc.split("Heating: ")[1].replace(",", "|")
    for p in pool_text:
        if p.startswith("Has Private Pool: "):
            has_pool = p.split("Has Private Pool: ")[1].replace(",", "|")
    for pg in parking_garage_text:
        if pg.startswith("Parking Total: "):
            parking_size = pg.split("Parking Total: ")[1].replace(",", "|")

    photo_elements = driver.find_elements(By.CSS_SELECTOR, "div.InlinePhotoPreview")
    photo_elements = photo_elements[0] if photo_elements else []
    img_href = " ".join(
        [
            img.get_attribute("src")
            for img in photo_elements.find_elements(By.TAG_NAME, "img")
        ]
    )

    # lot_size, cooling, heating, has_pool, parking_size
    data_file.write(
        f"{href},{stress_address},{city_and_state},{county},{img_href},{beds},{bath},{area},{year_built},{lot_size},{walk_score},{transit_score},{bike_score},{lot_size},{cooling},{heating},{has_pool},{parking_size},{price}\n"
    )
    progress_file.write(f"crawling done for property {i} - {href}\n")
    data_file.close()
print(f"index {index} done!")
print(f"index {index} done!")
print(f"index {index} done!")
