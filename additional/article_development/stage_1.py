import pandas as pd
from sqlalchemy import create_engine, text
import requests
import time

conn = None
cur = None
engine = create_engine(
    'postgresql://xpdmcctztuueoj:5c6b0ce73d0e1d7a8b7ea13688df6b7268edd3e85ddc1ba488a8e233759731d2@ec2-34-241-82-91.'
    'eu-west-1.compute.amazonaws.com:5432/d6i1k6lrk3j39n')


def load_postgres():
    with engine.connect() as conn:
        stage1_select = text('SELECT * FROM "stage1"')
        stage1_dataframe = pd.read_sql_query(stage1_select, conn)
        stage1_dataframe.drop(columns='index')
        stage1_dataframe = stage1_dataframe.drop_duplicates(subset='company url')
        existing_company_urls = stage1_dataframe['company url'].to_list()
        extract(existing_company_urls)


def extract(existing_company_urls):
    csv_dataframe = pd.read_csv('stage_1_data.csv', low_memory=False)
    csv_dataframe = csv_dataframe.drop_duplicates(subset='Company Website Domain')
    print(len(csv_dataframe))

    for url in existing_company_urls:
        csv_dataframe = csv_dataframe[csv_dataframe['Company Website Domain'] != url]
    csv_dataframe_length = len(csv_dataframe)
    print(f"Gathering data on {csv_dataframe_length} companies")

    next_iter_pause = 250
    iteration_total = 0

    for index, row in csv_dataframe.iterrows():
        print(f"Completed {iteration_total}/{csv_dataframe_length} iterations")
        company_url = row['Company Website Domain']
        print(f"Processing {company_url}")
        iteration_total += 1

        params = {'api_key': '172D9AB76C6943D3ACD0BFACD1893705',
                  'q': f'{company_url} news',
                  'search_type': 'news',
                  'location': 'United+States',
                  'max_page': 5}
        try:
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
                else:
                    pass
            elif valueserp_result.status_code == 429:
                print("API limit reached")
                print(f"{iteration_total} iterations complete")
                time.sleep(60)
            elif valueserp_result.status_code == 402:
                print("No credits left on ValueSERP")
                exit()
        except Exception as e:
            print(f"Error occurred: {e}")
            pass


load_postgres()
