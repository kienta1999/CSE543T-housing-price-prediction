import pandas as pd
import requests
import json
import os

zip_code = pd.read_excel('uszips.xlsx')
api_key = 'c26df8e66267985116815eacb3b109f4'
curpath = os.path.abspath(os.curdir)
# property_infor = []
progress_file = open("progress.txt", "a")
progress_file.write("Getting started\n")
count = 0

for code in zip_code['zip']:
    progress_file.write(f'Crawling data for zip code {code} ...  \n')
    response = requests.get('https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/snapshot',
                            params={'postalcode': code},
                            headers={'apikey': api_key}
                            )
    if response.status_code == 200:
        data = response.json()['property']
        # property_infor.extend(data)
        progress_file.write('Success!! \n')
        data_file = open(os.path.join(
            curpath, f"property_infor/{code}.json"), "w")
        json.dump(data, data_file, ensure_ascii=False, indent=4)
    else:
        progress_file.write(
            f'Error for zip code {code} with status {response.status_code} \n')
    progress_file.write('\n')

# print('Writing json to file')
# with open('property_infor.json', 'w', encoding='utf-8') as f:
#     json.dump(property_infor, f, ensure_ascii=False, indent=4)
