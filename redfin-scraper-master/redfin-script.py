from selenium import webdriver  # install selenium
import sqlite3
import csv
from lxml import html  # pip install lxml
import json
import pickle
from datetime import datetime
import sys
import os
import pprint
import time
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
FIRST_PAGE_URL = "https://www.redfin.com/zipcode/46135"


# PATH TO BROWSER
path_to_browser = "./chromedriver"


TIME_PAUSE = 1.0  # pause


# xp is string, how_long_to_wait float - the number of seconds to wait
def wait_by_xpath(xp, how_long_to_wait):
    try:
        WebDriverWait(driver, how_long_to_wait).until(
            EC.presence_of_element_located((By.XPATH, xp)))
        time.sleep(TIME_PAUSE)
        return 1  # success
    except TimeoutException:
        print("Too much time has passed while waiting for", xp)
        return 0  # fail


def fix_string(entry_string):  # remove "\n", "\t" and double spaces
    exit_string = entry_string.replace("\n", "")
    exit_string = exit_string.replace("\t", "")
    exit_string = exit_string.replace("\r", "")
    while "  " in exit_string:
        exit_string = exit_string.replace("  ", " ")
    if len(exit_string) > 0:  # remove first space
        if exit_string[0] == ' ':
            exit_string = exit_string[1:len(exit_string)]
    if len(exit_string) > 0:  # remove last space
        if exit_string[len(exit_string)-1] == ' ':
            exit_string = exit_string[0:len(exit_string)-1]

    return exit_string


ser = Service(path_to_browser)
op = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=ser, options=op)
driver.maximize_window()


# in any case, get a list of listing URLs from first page url, and then for each of those links, visit them if they aren't in database
listing_links = []
current_page = 1
while 1:
    if current_page == 1:
        page_link_to_open = FIRST_PAGE_URL
    else:
        page_link_to_open = next_page_url

    try:
        driver.get(page_link_to_open)
        wait_for_listings = wait_by_xpath(
            "//div[@class='homecards']/div[contains(@id, 'MapHomeCard')]//div[@class='homecardv2']/following-sibling::a[@title and @href]", 30)
        if wait_for_listings == 0:
            print("Try again with page", current_page)
            continue
        innerHTML_listings = driver.execute_script(
            "return document.body.innerHTML")
        htmlElem_listings = html.document_fromstring(innerHTML_listings)

    except KeyboardInterrupt:
        print("Manual interrupt, quit!")
        driver.quit()
        sys.exit(0)
    except:
        print("An exception, try again with page", current_page)
        continue

    # if here, take urls
    listings_els = htmlElem_listings.xpath(
        "//div[@class='homecards']/div[contains(@id, 'MapHomeCard')]//div[@class='homecardv2']/following-sibling::a[@title and @href]")
    for listing_el in listings_els:
        listing_links.append("https://www.redfin.com" +
                             listing_el.attrib["href"])

    # try to find next page url, update counter if found. if not, go out
    next_page_el = htmlElem_listings.xpath(
        "//div[@class='PagingControls']/div/a[@href and contains(@class, 'selected')]/following-sibling::a[@href][1]")
    if len(next_page_el) == 0:
        break
    else:
        next_page_url = "https://www.redfin.com" + \
            next_page_el[0].attrib["href"]
        current_page = current_page + 1

print("Found", len(listing_links), "listings on", current_page, "pages.")


# create a database if it doesn't exist, load already scraped URLs. then, go scrape URLs and save scraped items into database, update already scraped links
# it creates a database if it doesn't exist
db_conn = sqlite3.connect("REDFIN_DB.db")
db_cursor = db_conn.cursor()
db_cursor.execute(
    "CREATE TABLE IF NOT EXISTS TableWithData(url TEXT, json_data TEXT)")

already_scraped_links = {}
for already_scraped_item in db_cursor.execute("SELECT url FROM TableWithData"):
    already_scraped_links[already_scraped_item[0]] = ''

for item_to_visit in listing_links:
    if item_to_visit in already_scraped_links:
        continue  # this was already scraped

    try:
        driver.get(item_to_visit)
        wait_for_info = wait_by_xpath(
            "//h2/span[text()='Property Details']/../following-sibling::div[@class='main-content']/div/div[@class='super-group-title']", 30)
        if wait_for_info == 0:
            print("Can't find property details - something maybe changed on the site.")
            continue
        innerHTML = driver.execute_script("return document.body.innerHTML")
        htmlElem = html.document_fromstring(innerHTML)

    except KeyboardInterrupt:
        print("Manual interrupt, quit!")
        driver.quit()
        db_cursor.close()
        db_conn.close()
        sys.exit(0)

    except:
        print("Some kind of exception, continue!")
        continue

    # if still here, scrape from htmlElem and add into database, but only if essential info was found
    data = {}  # will save this into db if everything goes fine
    data["Redfin URL"] = item_to_visit

    data["Street Address"] = ''
    str_adr_el = htmlElem.xpath(
        "//div[@class='top-stats']/h1//span[@class='adr']/span[@class='street-address']")
    if len(str_adr_el) != 0:
        data["Street Address"] = fix_string(str_adr_el[0].text_content())

    data["City"] = ''
    data["State"] = ''
    data["ZIP"] = ''
    city_el = htmlElem.xpath(
        "//div[@class='top-stats']/h1//span[@class='adr']/span[@class='citystatezip']/span[@class='locality']/text()[1]")
    if len(city_el) != 0:
        data["City"] = fix_string(city_el[0])
    state_el = htmlElem.xpath(
        "//div[@class='top-stats']/h1//span[@class='adr']/span[@class='citystatezip']/span[@class='region']")
    if len(state_el) != 0:
        data["State"] = fix_string(state_el[0].text_content())
    zip_el = htmlElem.xpath(
        "//div[@class='top-stats']/h1//span[@class='adr']/span[@class='citystatezip']/span[@class='postal-code']")
    if len(zip_el) != 0:
        data["ZIP"] = fix_string(zip_el[0].text_content())

    if data["City"] == '' or data["Street Address"] == '' or data["ZIP"] == '':  # can't find essential info
        print("Couldn't find some of the essential data: city or street address or zip code, continue without saving!")
        continue

    data["Price"] = ''
    price_el = htmlElem.xpath(
        "//div[@class='top-stats']//div[@class='info-block price']/div[@class='statsValue']")
    if len(price_el) != 0:
        data["Price"] = fix_string(price_el[0].text_content())

    data["Beds"] = ''
    beds_el = htmlElem.xpath(
        "//div[@class='top-stats']//div[@class='info-block']/span[@class='statsLabel' and text()='Beds']/preceding-sibling::div[@class='statsValue']")
    if len(beds_el) != 0:
        data["Beds"] = beds_el[0].text_content()

    data["Baths"] = ''
    baths_el = htmlElem.xpath(
        "//div[@class='top-stats']//div[@class='info-block']/span[@class='statsLabel' and text()='Baths']/preceding-sibling::div[@class='statsValue']")
    if len(baths_el) != 0:
        data["Baths"] = baths_el[0].text_content()

    data["Square Feet"] = ''
    sq_ft_el = htmlElem.xpath(
        "//div[@class='top-stats']//div[@class='info-block sqft']/span/span[@class='statsValue']")
    if len(sq_ft_el) != 0:
        data["Square Feet"] = sq_ft_el[0].text_content()

    data["Price per sqft"] = ''
    price_sqft_el = htmlElem.xpath(
        "//div[@class='top-stats']//div[@class='info-block sqft']/span/div[@class='statsLabel']")
    if len(price_sqft_el) != 0:
        data["Price per sqft"] = price_sqft_el[0].text_content()

    data["HOA Dues"] = ''
    hoadues_el = htmlElem.xpath(
        "//div[@class='sectionContainer']//div[@class='keyDetailsList']/div/span[text()='HOA Dues']/following-sibling::span")
    if len(hoadues_el) != 0:
        data["HOA Dues"] = hoadues_el[0].text_content()

    data["Style"] = ''
    style_el = htmlElem.xpath(
        "//div[@class='sectionContainer']//div[@class='keyDetailsList']/div/span[text()='Style']/following-sibling::span")
    if len(style_el) != 0:
        data["Style"] = style_el[0].text_content()

    data["County"] = ''
    county_el = htmlElem.xpath(
        "//div[@class='sectionContainer']//div[@class='keyDetailsList']/div/span[text()='County']/following-sibling::span/a[@href]")
    if len(county_el) != 0:
        data["County"] = county_el[0].text_content()

    data["Built"] = ''
    built_el = htmlElem.xpath(
        "//div[@class='sectionContainer']//div[@class='keyDetailsList']/div/span[text()='Built']/following-sibling::span")
    if len(built_el) != 0:
        data["Built"] = built_el[0].text_content()

    data["Type"] = ''
    type_el = htmlElem.xpath(
        "//div[@class='sectionContainer']//div[@class='keyDetailsList']/div/span[text()='Type']/following-sibling::span")
    if len(type_el) != 0:
        data["Type"] = type_el[0].text_content()

    data["Community"] = ''
    comm_el = htmlElem.xpath(
        "//div[@class='sectionContainer']//div[@class='keyDetailsList']/div/span[text()='Community']/following-sibling::span")
    if len(comm_el) != 0:
        data["Community"] = comm_el[0].text_content()

    data["MLS#"] = ''
    mls_no_el = htmlElem.xpath(
        "//div[@class='sectionContainer']//div[@class='keyDetailsList']/div/span[text()='MLS#']/following-sibling::span")
    if len(mls_no_el) != 0:
        data["MLS#"] = mls_no_el[0].text_content()

    # those ^^ are all fixed headers. now get variable ones!

    data["variable_headers"] = {}
    variable_section_els = htmlElem.xpath(
        "//h2/span[text()='Property Details']/../following-sibling::div[@class='main-content']/div/div[@class='super-group-title']/following-sibling::div[@class='super-group-content']/div[@class='amenity-group']")
    # variable_section_els are amenity_group elements
    for variable_section_el in variable_section_els:
        section_name_el = variable_section_el.xpath("./ul/div/h3")
        if len(section_name_el) == 0:
            continue

        section_name = section_name_el[0].text_content()
        data["variable_headers"][section_name] = {}

        for section_part_el in variable_section_el.xpath("./ul//li[contains(@class, 'entryItem')]/span[@class='entryItemContent']"):
            label_el = section_part_el.xpath("./text()[1]")
            value_el = section_part_el.xpath("./span")

            if len(label_el) != 0 and len(value_el) != 0:
                label_to_add = fix_string(label_el[0].replace(":", ""))
                if label_to_add == '':
                    continue

                # if here, should be good
                data["variable_headers"][section_name][label_to_add] = value_el[0].text_content()

    # finally, all data is parsed. save data and update urls
    db_cursor.execute("INSERT INTO TableWithData (url, json_data) VALUES (?,?)",
                      (item_to_visit, json.dumps(data)))  # not necessary to insert all columns!
    db_conn.commit()
    already_scraped_links[item_to_visit] = ''
    print("Successfully scraped item number", listing_links.index(
        item_to_visit)+1, "/", len(listing_links))


driver.quit()


# make csv files, only with links in listing_links!
# gather headers first
# fixed are in proper ordering for columns later
fixed_headers = ['Street Address', 'City', 'State', 'ZIP', 'Price', 'Beds', 'Baths', 'Square Feet',
                 'Price per sqft', 'Redfin URL', 'HOA Dues', 'Style', 'County', 'Built', 'Type', 'Community', 'MLS#']
variable_headers_dict = {}

for url_to_find in listing_links:
    for found_item in db_cursor.execute("SELECT * FROM TableWithData WHERE url=?", (url_to_find,)):
        # gather variable headers
        found_data = json.loads(found_item[1])
        for variable_primary_key in found_data["variable_headers"]:
            for variable_secondary_key in found_data["variable_headers"][variable_primary_key]:
                if variable_primary_key not in variable_headers_dict:
                    variable_headers_dict[variable_primary_key] = []

                if variable_secondary_key not in variable_headers_dict[variable_primary_key]:
                    variable_headers_dict[variable_primary_key].append(
                        variable_secondary_key)

        break

variable_headers_list = []
for variable_first_key in sorted(variable_headers_dict.keys()):
    for variable_second_key in sorted(variable_headers_dict[variable_first_key]):
        variable_headers_list.append([variable_first_key, variable_second_key])

# use this when writing, select based on type!
ALL_HEADERS = fixed_headers + variable_headers_list

output_basename = datetime.now().strftime("%m-%d-%Y %H_%M_%S")

with open(output_basename + ".csv", "w", newline="", encoding="utf-8") as csv_fil:
    writer = csv.writer(csv_fil, delimiter=";", quoting=csv.QUOTE_MINIMAL)
    headers_to_write = []
    for head_item in ALL_HEADERS:
        if type(head_item) == str:
            headers_to_write.append(head_item)
        elif type(head_item) == list:
            headers_to_write.append(head_item[0] + " - " + head_item[1])

    csv_wr = writer.writerow(headers_to_write)

    # load to write
    for url_to_find in listing_links:
        for found_item in db_cursor.execute("SELECT * FROM TableWithData WHERE url=?", (url_to_find,)):
            # gather variable headers
            found_data = json.loads(found_item[1])

            this_row_to_write = []  # append either empty strings or values to write
            for head_item in ALL_HEADERS:
                if type(head_item) == str:
                    # these are fixed keys which are always inside
                    this_row_to_write.append(found_data[head_item])
                elif type(head_item) == list:
                    # search for primary and secondary key
                    try:
                        this_row_to_write.append(
                            found_data["variable_headers"][head_item[0]][head_item[1]])
                    except KeyError:
                        this_row_to_write.append("")

            csv_wr = writer.writerow(this_row_to_write)
            break


# write a txt file for headers
with open(output_basename + " headers.txt", "w") as write_txt_headers:
    txt_wr = write_txt_headers.write("FIXED HEADERS:\n")
    var_head_txt_written = False

    for head_item in ALL_HEADERS:
        if type(head_item) == str:
            txt_wr = write_txt_headers.write(head_item + "\n")
        elif type(head_item) == list:
            if not var_head_txt_written:
                txt_wr = write_txt_headers.write("\n\n\nVARIABLE HEADERS:\n")
                var_head_txt_written = True
            txt_wr = write_txt_headers.write(
                head_item[0] + " - " + head_item[1] + "\n")


print("Output files are:", output_basename + ".csv", "for data and",
      output_basename + " headers.txt", "for headers")
db_cursor.close()
db_conn.close()
