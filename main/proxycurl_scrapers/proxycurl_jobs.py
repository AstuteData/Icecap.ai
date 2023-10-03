import requests
from sqlalchemy import create_engine
import json
import pandas as pd
import pprint as pp

conn = None
cur = None
engine = create_engine(
    'postgresql://xpdmcctztuueoj:5c6b0ce73d0e1d7a8b7ea13688df6b7268edd3e85ddc1ba488a8e233759731d2@ec2-34-241-82-91.'
    'eu-west-1.compute.amazonaws.com:5432/d6i1k6lrk3j39n')


def run_proxycurl(job_list, company_id):
    formatted_job_list = []
    job_counter = 0
    for job in job_list['job']:
        job_title = job['job_title']
        job_url = job['job_url']
        formatted_job_data = {'job_title': job_title, 'job_url': job_url}
        formatted_job_list.append(formatted_job_data)
        job_counter += 1

    job_data_list = []
    for job in formatted_job_list:
        url = job['job_url']

        api_key = 'Hnt8EpqHzgkG97GSkk7Krw'
        headers = {'Authorization': 'Bearer ' + api_key}
        api_endpoint = 'https://nubela.co/proxycurl/api/linkedin/job'
        params = {'url': url}
        response = requests.get(api_endpoint,
                                params=params,
                                headers=headers)
        r = response.json()
        job_data_list.append(r)
        pp.pprint(r)
        print("---------------------------------------------------")

    pp.pprint(job_data_list)
    completion = format_proxycurl_response(job_data_list, company_id)

    if completion is True:
        return {"Status": "Success"}
    else:
        return {"Status": "Failed"}


def format_proxycurl_response(job_data_list, company_id):
    keys = ['apply_url', 'employment_type', 'job_description', 'job_functions',
            'linkedin_internal_id', 'location', 'title']
    jobs_dataframe = pd.DataFrame(columns=keys)

    try:
        for job in job_data_list:
            formatted_job_response = {key: job[key] for key in keys}
            str_response = {}
            reduced_response = {}
            for key in formatted_job_response:
                if type(formatted_job_response[key]) == list or type(formatted_job_response[key]) == dict:
                    value = formatted_job_response[key]
                    list_reduced = json.dumps(value)
                    reduced_response.update({key: list_reduced})
                else:
                    str_response.update({key: formatted_job_response[key]})
            transformed_job_response = {**str_response, **reduced_response}
            temp_job_dataframe = pd.DataFrame(transformed_job_response, index=[0])
            temp_job_dataframe['company_id'] = company_id
            jobs_dataframe = pd.concat([jobs_dataframe, temp_job_dataframe], ignore_index=True)

        jobs_dataframe.to_sql(f'jobs', con=engine, if_exists='append')
        return True
    except Exception as e:
        print(e)
        return False
