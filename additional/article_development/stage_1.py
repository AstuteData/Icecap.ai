import pandas as pd
import requests
import json
import time
import pprint as pp


def extract():
    csv_dataframe = pd.read_csv('stage_1_data.csv', low_memory=False)
    csv_dataframe = csv_dataframe.drop_duplicates(subset='Company Website Domain')

    next_iter_pause = 250
    iteration_total = 0
    for index, row in csv_dataframe.iterrows():
        company_url = row['Company Website Domain']
        print(company_url)
        iteration_total += 1

        params = {'api_key': '172D9AB76C6943D3ACD0BFACD1893705',
                  'q': f'{company_url} news',
                  'search_type': 'news',
                  'location': 'United+States',
                  'max_page': '5'}

        valueserp_result = requests.get('https://api.valueserp.com/search', params)
        r = valueserp_result.json()
        pp.pprint(r)

        if iteration_total == next_iter_pause:
            print(f"{iteration_total} iterations complete")
            next_iter_pause += 250
            time.sleep(65)
        else:
            pass


extract()
