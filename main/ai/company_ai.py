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


def start_ai(research_id):
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

    print('matched')
    print(research_id)
    try:
        str_research_id = str(research_id)
        matched_company = company_data[company_data['research_id'] == str_research_id]
        matched_hiring = hiring_data.loc[hiring_data['research_id'] == str_research_id]
        matched_articles = articles_data.loc[articles_data['research_id'] == str_research_id]

        print(matched_company)

        company_name = matched_company['name'].values[0]
        company_description = matched_company['tagline'].values[0]
        company_domain = matched_company['domain'].values[0]
        company_id = matched_company['company_id'].values[0]

        job_response = job(matched_hiring)
        articles_response = articles(matched_articles, company_domain)

        jobs_response_json = json.dumps(job_response)
        articles_response_json = json.dumps(articles_response)

        company_data = {'Company Name': company_name, 'Company Description': company_description,
                        'Jobs Analysis': jobs_response_json, 'Articles Analysis': articles_response_json,
                        'Research ID': research_id, 'Company ID': company_id}

        company_analysis_df = pd.DataFrame.from_dict(company_data, orient='index').transpose()
        company_analysis_df.to_sql('company_analysis', con=engine, if_exists='append', index=False)
        return 'Complete'
    except Exception as e:
        print(e)
        print('Error in Company AI occurred')
        exit()


def job(matched_hiring):
    job_dict = {}
    for index, row in matched_hiring.iterrows():
        job_title = row['title']
        job_description = row['job_description']

        prompt = (
                "Highlight the top 8 key requirements of the following job description. No more than 10 words for each highlighted point. "
                "You must not mention information about the company or the job benefits. "
                "Store the output in a dictionary with each key being a number and the value being the key point. Do not assign the dictionary to a variable or add text outside of the dictionary. Always close the dictionary bracket "
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


def articles(matched_articles, company_domain):
    article_dict = {}
    count = 0
    for index, row in matched_articles.iterrows():
        try:
            article_title = row['Article Title']
            article_text = row['Article Text']

            prompt = (
                    "Highlight the top 8 key points of the following article. No more than 10 words for each highlighted point. "
                    f"The highlights should also be contextualised to {company_domain}."
                    "Store the output in a dictionary with each key being a number and the value being the key point. Do not assign the dictionary to a variable or add text outside of the dictionary. Always close the dictionary bracket."
                    "This is the article that you will summarise: " + article_text + "")

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
            article_dict[count] = {'Article Title': article_title, 'Article Highlights': response}
            count += 1
        except Exception as e:
            print(e)

        return article_dict

