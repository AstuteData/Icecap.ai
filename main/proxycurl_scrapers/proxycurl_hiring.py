import requests
from sqlalchemy import create_engine
import json
import pandas as pd
import proxycurl_jobs

conn = None
cur = None
engine = create_engine(
    'postgresql://xpdmcctztuueoj:5c6b0ce73d0e1d7a8b7ea13688df6b7268edd3e85ddc1ba488a8e233759731d2@ec2-34-241-82-91.'
    'eu-west-1.compute.amazonaws.com:5432/d6i1k6lrk3j39n')


def run_proxycurl(company_id, search_id, research_id, user_id):
    api_key = 'Hnt8EpqHzgkG97GSkk7Krw'
    headers = {'Authorization': 'Bearer ' + api_key}
    api_endpoint = 'https://nubela.co/proxycurl/api/v2/linkedin/company/job'
    params = {
        'job_type': 'anything',
        'when': 'past-month',
        'flexibility': 'remote',
        'search_id': search_id,
        'keyword': 'data',
    }
    response = requests.get(api_endpoint,
                            params=params,
                            headers=headers)
    r = response.json()
    formatting_completion = format_proxycurl_response(r, company_id, research_id, user_id)

    if formatting_completion['Status'] == 'Success':
        print("---------------------------------------")
        print("proxycurl_hiring ---- Process complete")
        print("---------------------------------------")
        formatted_response = formatting_completion['Data']
        job_list = formatted_response['job']
        job_completion = proxycurl_jobs.run_proxycurl(job_list, company_id, research_id, user_id)
        if job_completion['Status'] == 'Success':
            print("---------------------------------------")
            print("proxycurl_jobs ---- Process complete")
            print("---------------------------------------")
            return {'Status': 'Success', 'Data': 'None'}
        else:
            print("---------------------------------------")
            print("proxycurl_jobs ---- Process failed")
            print("---------------------------------------")
            return {'Status': 'Failed', 'Data': 'None'}

    else:
        print("-------------------------------------")
        print("proxycurl_hiring ---- Process failed")
        print("-------------------------------------")
        return False


def format_proxycurl_response(r, company_id, research_id, user_id):
    keys = ['job']

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

    transformed_response = {**str_response, **reduced_response}
    response_dataframe = pd.DataFrame(transformed_response, index=[0])
    response_dataframe['company_id'] = company_id
    response_dataframe['research_id'] = research_id
    response_dataframe['user_id'] = user_id
    print(response_dataframe)
    response_dataframe.to_sql(f'hiring', con=engine, if_exists='append')

    return {'Status': 'Success', 'Data': formatted_response}
