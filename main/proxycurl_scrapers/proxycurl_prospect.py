import requests
from sqlalchemy import create_engine
import json
import pandas as pd

conn = None
cur = None
engine = create_engine(
    'postgresql://xpdmcctztuueoj:5c6b0ce73d0e1d7a8b7ea13688df6b7268edd3e85ddc1ba488a8e233759731d2@ec2-34-241-82-91.'
    'eu-west-1.compute.amazonaws.com:5432/d6i1k6lrk3j39n')


def run_proxycurl(prospect_id, li_prospect_profile_url, company_id, research_id, user_id):
    api_key = 'Hnt8EpqHzgkG97GSkk7Krw'
    headers = {'Authorization': 'Bearer ' + api_key}
    api_endpoint = 'https://nubela.co/proxycurl/api/v2/linkedin'
    linkedin_profile_url = li_prospect_profile_url

    response = requests.get(api_endpoint,
                            params={'url': linkedin_profile_url},
                            headers=headers)

    r = response.json()
    completion = format_proxycurl_response(r, prospect_id, company_id, research_id, user_id)

    if completion is True:
        print("---------------------------------------")
        print("proxycurl_prospect ---- Process complete")
        print("---------------------------------------")
        return {'Status': 'Success'}
    else:
        print("-------------------------------------")
        print("proxycurl_prospect ---- Process failed")
        print("-------------------------------------")
        return {'Status': 'Failed'}


def format_proxycurl_response(r, prospect_id, company_id, research_id, user_id):
    keys = ['accomplishment_courses', 'accomplishment_honors_awards', 'accomplishment_organisations',
            'accomplishment_publications', 'accomplishment_projects', 'accomplishment_test_scores',
            'activities', 'articles', 'certifications', 'city', 'country', 'country_full_name',
            'education', 'experiences', 'extra', 'first_name', 'full_name', 'headline', 'industry',
            'inferred_salary', 'interests', 'languages', 'last_name', 'occupation', 'profile_pic_url',
            'public_identifier', 'recommendations', 'skills', 'state', 'summary', 'volunteer_work']

    formatted_response = {key: r[key] for key in keys}
    str_response = {}
    reduced_response = {}

    try:
        for key in formatted_response:
            if type(formatted_response[key]) == list or type(formatted_response[key]) == dict:
                value = formatted_response[key]
                list_reduced = json.dumps(value)
                reduced_response.update({key: list_reduced})
            else:
                str_response.update({key: formatted_response[key]})

        transformed_response = {**str_response, **reduced_response}
        response_dataframe = pd.DataFrame(transformed_response, index=[0])
        response_dataframe['prospect_id'] = prospect_id
        response_dataframe['company_id'] = company_id
        response_dataframe['research_id'] = research_id
        response_dataframe['user_id'] = user_id
        response_dataframe.to_sql(f'prospect', con=engine, if_exists='append')
        return True
    except Exception as e:
        print(e)
        return False
