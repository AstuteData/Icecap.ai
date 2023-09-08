import pandas as pd
from sqlalchemy import create_engine, text
import requests
import json
import openai

conn = None
cur = None
engine = create_engine(
    'postgresql://xpdmcctztuueoj:5c6b0ce73d0e1d7a8b7ea13688df6b7268edd3e85ddc1ba488a8e233759731d2@ec2-34-241-82-91.eu-west-1.compute.amazonaws.com:5432/d6i1k6lrk3j39n')
openai.api_key = "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"
modelEngine = "text-davinci-003"

def start_hiring_ai(unique_company_identifier):
    connect_attempt = 0
    connect_successful = False
    retries = 3
    while connect_successful is False or connect_attempt < retries:
        try:
            with engine.connect() as conn:
                company_select = text('SELECT * FROM "CompanyData"')
                company_data_table = pd.read_sql_query(company_select, conn)
                company_data_table.drop(columns='index')
                connect_successful = True
        except Exception as error:
            connect_attempt += 1
            print("An exception has occurred:", error)
            if connect_attempt == retries:
                return "Error:", error

    queried_company_data_table = company_data_table.query("company identifier == @unique_company_identifier")
    hiring_posts = json.loads(queried_company_data_table['hiring posts'])
    analysis_response = hiring_ai_analysis(hiring_posts)
    return analysis_response


def hiring_ai_analysis(hiring_posts):
    analysed_posts = {}
    for post in hiring_posts.values():
        title = post['title']
        link = post['link']
        general_information = post['p']
        specific_information = post ['ul']

        prompt = "Analyse this job role and then summarise it." \
                 "Important information includes why this job has been posted by the company," \
                 "Skills that they need to have and any technical requirements for the job." \
                 "" \
                 "The information about the role:" \
                 f"Job Title: {title}" \
                 f"Job post: {general_information}" \
                 f"{specific_information}"

        ai_response = openai.Completion.create(
            model=modelEngine,
            prompt=prompt,
            temperature=0.5,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.5,
        )

        post_dict = {"title": title, "link": link, "analysis": ai_response}
        analysed_posts.update(post_dict)

    return analysed_posts
