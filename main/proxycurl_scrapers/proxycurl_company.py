# Tested and works. 24.09.2023

import sys
import requests
from sqlalchemy import create_engine
import json
import pandas as pd
sys.path.append('../')
from main.general_scrapers.companyscraper import company_scraping

conn = None
cur = None
engine = create_engine(
    'postgresql://xpdmcctztuueoj:5c6b0ce73d0e1d7a8b7ea13688df6b7268edd3e85ddc1ba488a8e233759731d2@ec2-34-241-82-91.'
    'eu-west-1.compute.amazonaws.com:5432/d6i1k6lrk3j39n')


def run_proxycurl(company_id, li_company_linkedin_url):
    api_key = 'Hnt8EpqHzgkG97GSkk7Krw'
    headers = {'Authorization': 'Bearer ' + api_key}
    api_endpoint = 'https://nubela.co/proxycurl/api/linkedin/company'
    params = {
        'url': li_company_linkedin_url,
        'resolve_numeric_id': 'false',
        'categories': 'exclude',
        'funding_data': 'include',
        'extra': 'include',
        'exit_data': 'include',
        'acquisitions': 'include',
        'use_cache': 'if-present',
    }
    response = requests.get(api_endpoint,
                            params=params,
                            headers=headers)
    r = response.json()
    general_company_completion = company_scraping(company_id, li_company_linkedin_url)
    if general_company_completion['Status'] == 'Success':
        general_cc_data = general_company_completion['Data']
        proxycurl_company_completion = format_proxycurl_response(r, general_cc_data, company_id)
        print(proxycurl_company_completion)
        proxycurl_status = proxycurl_company_completion
    else:
        print("-------------------------------------")
        print("proxycurl_company ---- Process failed")
        print("failed to fetch general company data")
        print("-------------------------------------")
        return {'Status': 'Failed', 'Search ID': "None"}

    if proxycurl_status['Status'] == 'Success':
        print("---------------------------------------")
        print("proxycurl_company ---- Process complete")
        print("---------------------------------------")
        return {'Status': 'Success', 'Search ID': proxycurl_company_completion}
    else:
        print("-------------------------------------")
        print("proxycurl_company ---- Process failed")
        print("-------------------------------------")
        return {'Status': 'Failed', 'Search ID': "None"}


def format_proxycurl_response(r, general_company_completion, company_id):
    keys = ['acquisitions', 'background_cover_image_url', 'company_size_on_linkedin', 'company_type', 'description',
            'exit_data', 'extra', 'follower_count', 'founded_year', 'funding_data', 'hq', 'industry',
            'linkedin_internal_id', 'locations', 'name', 'profile_pic_url', 'search_id', 'similar_companies',
            'specialities', 'tagline', 'universal_name_id', 'website']

    formatted_response = {key: r[key] for key in keys}
    str_response = {}
    reduced_response = {}

    for key in formatted_response:
        if type(formatted_response[key]) == list or type(formatted_response[key]) == dict:
            value = formatted_response[key]
            list_reduced = json.dumps(value)
            reduced_response.update({key: list_reduced})
        else:
            str_response.update({key: formatted_response[key]})
    str_response.update({'company_id': company_id})

    transformed_response = {**str_response, **reduced_response, **general_company_completion}
    response_dataframe = pd.DataFrame(transformed_response, index=[0])
    print(response_dataframe)
    response_dataframe.to_sql(f'company', con=engine, if_exists='append')

    return str_response['search_id']
