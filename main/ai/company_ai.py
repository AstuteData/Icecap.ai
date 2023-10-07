import pandas as pd
from sqlalchemy import create_engine, text
import ast
import uuid
import requests
import json
import openai
import pprint as pp

engine = create_engine('postgresql://xpdmcctztuueoj:5c6b0ce73d0e1d7a8b7ea13688df6b7268edd3e85ddc1ba488a8e233759731d2'
                       '@ec2-34-241-82-91.eu-west-1.compute.amazonaws.com:5432/d6i1k6lrk3j39n')
openai.api_key = "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"
modelEngine = "text-davinci-003"

list_of_ids = ['fdf7c99f-556e-4f11-9d33-32d33f2e04aa']


def start_ai(list_of_ids):
    with engine.connect() as conn:
        company_select = text('SELECT * FROM "company"')
        company_data = pd.read_sql_query(company_select, conn)
        company_data.drop(columns='index')

        hiring_select = text('SELECT * FROM "jobs"')
        hiring_data = pd.read_sql_query(hiring_select, conn)
        hiring_data.drop(columns='index')

        articles_select = text('SELECT * FROM "articles"')
        articles_data = pd.read_sql_query(articles_select, conn)
        articles_data.drop(columns='index')

    for research_id in list_of_ids:
        # Change company id to research id when implemented
        matched_company = company_data[company_data['research_id'] == research_id]
        matched_hiring = hiring_data.loc[hiring_data['research_id'] == research_id]
        matched_articles = articles_data.loc[articles_data['research_id'] == research_id]

        company_name = matched_company['name'].values[0]
        company_description = matched_company['tagline'].values[0]

        job(matched_hiring)
        articles(matched_articles)


def job(matched_hiring):
    job_dict = {}
    for job, row in matched_hiring.iterrows():
        job_title = matched_hiring['title'].values[0]
        job_description = matched_hiring['job_description'].values[0]

        prompt = (
                    "Highlight the top 8 key requirements of the following job description. No more than 10 words for each highlighted point. "
                    "You must not mention information about the company or the job benefits. "
                    "Store the output in a dictionary with each key being a number and the value being the key point. "
                    "This is the job description that you will summarise: " + job_description + "")

        ai_response = openai.Completion.create(
            model=modelEngine,
            prompt=prompt,
            temperature=0.2,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.5,
        )

        print(ai_response['choices'][0]['text'])
        response = ast.literal_eval(ai_response['choices'][0]['text'])
        job_dict[job_title] = response

    return job_dict


def articles(matched_articles):
    article_dict = {}
    for article, row in matched_articles.iterrows():
        article_title = matched_articles['Article Title'].values[0]
        article_description = matched_articles['Article Text'].values[0]

        prompt = (
                    "Highlight the top 8 key points of the following article. No more than 10 words for each highlighted point. "
                    "The highlights should also be contextualised to Rivery.io. "
                    "Store the output in a dictionary with each key being a number and the value being the key point. "
                    "This is the article that you will summarise: " + article_description + "")

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
        article_dict[article_title] = response


start_ai(list_of_ids)
