import pandas as pd
from sqlalchemy import create_engine, text
import ast
import uuid
import requests
import json
import openai
from time import sleep
import pprint as pp

engine = create_engine('postgresql://xpdmcctztuueoj:5c6b0ce73d0e1d7a8b7ea13688df6b7268edd3e85ddc1ba488a8e233759731d2'
                       '@ec2-34-241-82-91.eu-west-1.compute.amazonaws.com:5432/d6i1k6lrk3j39n')
openai.api_key = "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"
modelEngine = "text-davinci-003"

list_of_ids = ['fdf7c99f-556e-4f11-9d33-32d33f2e04aa']
research_id = 1
prospect_id = 2
company_id = 3


def start_ai(list_of_ids, research_id, prospect_id, company_id):
    with engine.connect() as conn:
        prospect_select = text('SELECT * FROM "prospect"')
        prospect_data = pd.read_sql_query(prospect_select, conn)
        prospect_data.drop(columns='index')

    for research_id in list_of_ids:
        # Change company id to research id when implemented
        matched_prospect = prospect_data[prospect_data['research_id'] == research_id]

        prospect_const_unchecked = {'Full name': matched_prospect['full_name'].values[0],
                                    'Prospect ID': matched_prospect['prospect_id'].values[0],
                                    'Occupation': matched_prospect['occupation'].values[0],
                                    'Headline': matched_prospect['headline'].values[0],
                                    'Summary': matched_prospect['summary'].values[0],
                                    'Experiences': matched_prospect['experiences'].values[0],
                                    'Skills': matched_prospect['skills'].values[0],
                                    'Interests': matched_prospect['interests'].values[0]}
        prospect(prospect_const_unchecked, research_id, prospect_id, company_id)


def prospect(prospect_const_unchecked, research_id, prospect_id, company_id):
    unwrapped_const = unwrap_const(prospect_const_unchecked)

    analysed_experiences = {}
    kv_count = 0
    for key, value in unwrapped_const['Experience'].items():
        for k, v in value.items():
            str = (f"{k}"
                   f""
                   f"{v}")
            prompt = (
                    "Your job is to analyse the following job data from a LinkedIn profile and summarise it into key points no longer than 6 words."
                    "The key points will be used in prospecting to build a relationship with the prospect."
                    "Your response must be a Python dictionary with each key being a number and the value being the key point. You must always close the dictionary with a closing bracket."
                    ""
                    "This is the job data that you will summarise: " + str + "")
            analysis = analyse(prompt)
            analysed_experiences[kv_count] = analysis
            kv_count += 1

    summary_prompt = (
            f"Your job is to analyse the following Linkedin data from a LinkedIn profile and summarise it into key points no longer than 6 words."
            "The key points will be used in prospecting to build a relationship with the prospect."
            "Your response must be a Python dictionary with each key being a number and the value being the key point. You must always close the dictionary with a closing bracket."
            ""
            "This is the Linkedin data that you will summarise: " + unwrapped_const['Summary'] + "")

    analysed_summary = analyse(prompt=summary_prompt)
    analysed_experiences_transformed = json.dumps(analysed_experiences)
    analysed_summary_transformed = json.dumps(analysed_summary)

    prospect_data = {'Analysed Experiences': analysed_experiences_transformed,
                     'Analysed Summary': analysed_summary_transformed,
                     'Research ID': research_id,
                     'Prospect ID': prospect_id,
                     'Company ID': company_id}

    prospect_analysis_df = pd.DataFrame.from_dict(prospect_data, orient='index').transpose()
    print(prospect_analysis_df)
    prospect_analysis_df.to_sql('prospect_analysis', con=engine, if_exists='append', index=False)


def unwrap_const(prospect_const):
    experiences_str = prospect_const['Experiences']
    experiences_dict = json.loads(experiences_str)

    unwrapped_experience = {}
    loop_count = 0
    for experience in experiences_dict:
        title = experience['title']
        company = experience['company']
        location = experience['location']
        description = experience['description']

        started_month = experience['starts_at']['month']
        started_year = experience['starts_at']['year']

        if experience['ends_at'] is None:
            experience_overview = (f"Prospect's current company: {company}. \n"
                                   f"Prospect's current job title: {title}. \n"
                                   f"Description of prospect's job: {description} \n"
                                   f"The prospect current works at this company. \n"
                                   f"The prospect's current role is based in:. {location} \n")
            unwrapped_experience[loop_count] = {f'Current job': experience_overview}
        else:
            end_month = experience['ends_at']['month']
            end_year = experience['ends_at']['year']
            time = f"{started_month}/{started_year} - {end_month}/{end_year}"
            experience_overview = (f"Prospect's former company: {company}. \n"
                                   f"Prospect's former job title: {title}. \n"
                                   f"Description of prospect's former job: {description} \n"
                                   f"The prospect worked at this company from {time}. \n"
                                   f"The prospect's current role is based in: {location}. \n")
            unwrapped_experience[loop_count] = {f'Former job {loop_count}': experience_overview}

        loop_count += 1

    unwrapped_prospect = {'Full name': prospect_const['Full name'],
                          'Headline': prospect_const['Headline'],
                          'Summary': prospect_const['Summary'],
                          'Experience': unwrapped_experience}
    return unwrapped_prospect


def analyse(prompt):
    ai_response = openai.Completion.create(
        model=modelEngine,
        prompt=prompt,
        temperature=0.2,
        max_tokens=200,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.5,
    )
    response = ast.literal_eval(ai_response['choices'][0]['text'])
    return response


start_ai(list_of_ids, research_id, prospect_id, company_id)
