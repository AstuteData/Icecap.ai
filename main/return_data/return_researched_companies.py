import requests
from sqlalchemy import create_engine, text
import json
import pandas as pd

conn = None
cur = None
engine = create_engine(
    'postgresql://xpdmcctztuueoj:5c6b0ce73d0e1d7a8b7ea13688df6b7268edd3e85ddc1ba488a8e233759731d2@ec2-34-241-82-91.'
    'eu-west-1.compute.amazonaws.com:5432/d6i1k6lrk3j39n')


def return_research_list():
    try:
        with engine.connect() as conn:
            company = text('SELECT * FROM "company"')
            company_data = pd.read_sql_query(company, conn)
            company_data.drop(columns='index')
    except Exception as e:
        print(e)

    researched_company_list = {}
    count = 0
    for index, row in company_data.iterrows():
        count = count + 1
        company_name = row['name']
        company_id = row['company_id']
        researched_company_list[count] = {'CompanyName': company_name,
                                          'CompanyID': company_id}

    return json.dumps(researched_company_list)
