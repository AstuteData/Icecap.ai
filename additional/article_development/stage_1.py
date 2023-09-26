import pandas as pd
from sqlalchemy import create_engine
import requests
import time

conn = None
cur = None
engine = create_engine(
    'postgresql://xpdmcctztuueoj:5c6b0ce73d0e1d7a8b7ea13688df6b7268edd3e85ddc1ba488a8e233759731d2@ec2-34-241-82-91.'
    'eu-west-1.compute.amazonaws.com:5432/d6i1k6lrk3j39n')


def extract():
    csv_dataframe = pd.read_csv('stage_1_data.csv', low_memory=False)
    csv_dataframe = csv_dataframe.drop_duplicates(subset='Company Website Domain')

    valueserp_dataframe = pd.DataFrame(columns=['company url', 'domain', 'link', 'snippet', 'title', 'date', 'source'])
    next_iter_pause = 250
    iteration_total = 0
    for index, row in csv_dataframe.iterrows():
        company_url = row['Company Website Domain']
        iteration_total += 1

        params = {'api_key': '172D9AB76C6943D3ACD0BFACD1893705',
                  'q': f'{company_url} news',
                  'search_type': 'news',
                  'location': 'United+States',
                  'max_page': 5}

        valueserp_result = requests.get('https://api.valueserp.com/search', params)
        r = valueserp_result.json()

        if valueserp_result.status_code == 200:
            for result in r['news_results']:
                result_dict = {'company url': company_url, 'domain': result['domain'], 'link': result['link'],
                               'snippet': result['snippet'], 'title': result['title'], 'date': result['date'],
                               'source': result['source']}
                result_dataframe = pd.DataFrame(result_dict, index=[0])
                result_dataframe.to_sql(f'stage1', con=engine, if_exists='append')
            if iteration_total == next_iter_pause:
                print(f"{iteration_total} iterations complete")
                next_iter_pause += 250
                valueserp_dataframe.to_csv(f'stage_1_data_{iteration_total}.csv', index=False)
            else:
                pass
        elif valueserp_result.status_code == 429:
            print("API limit reached")
            print(f"{iteration_total} iterations complete")
            time.sleep(60)
        elif valueserp_result.status_code == 402:
            print("No credits left on ValueSERP")
            exit()


extract()
