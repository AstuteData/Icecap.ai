import pandas as pd
from sqlalchemy import create_engine, text
import uuid
import requests
import json
import openai


conn = None
cur = None
engine = create_engine(
    'postgresql://xpdmcctztuueoj:5c6b0ce73d0e1d7a8b7ea13688df6b7268edd3e85ddc1ba488a8e233759731d2@ec2-34-241-82-91.eu-west-1.compute.amazonaws.com:5432/d6i1k6lrk3j39n')
openai.api_key = "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"
modelEngine = "text-davinci-003"


def start_article_ai(unique_company_identifier):

    # Connecting to Postgres and extracting the prospect's data into a dataframe.
    connect_attempt = 0
    retries = 3
    while connect_attempt < retries:
        try:
            with engine.connect() as conn:
                article_select = text('SELECT * FROM "ArticleData"')
                article_data_table = pd.read_sql_query(article_select, conn)
                article_data_table.drop(columns='index')
                retries = 0

        except Exception as error:
            connect_attempt += 1
            print("An exception has occurred:", error)
            if connect_attempt == retries:
                return "Error:", error

    article_data = article_data_table.query("company_identifier == @unique_company_identifier")

    summaries = {}

    for ind in article_data.index:
        article_title = article_data['title'][ind]
        article_text = article_data['text'][ind]
        article_url = article_data['url'][ind]

        prompt = f"Summarise the following article, titled '{article_title}' around what the business " \
                 f"is focusing on based on the article content. This is the article that you will " \
                 f"summarise {article_text}"
        ai_response = openai.Completion.create(
            model=modelEngine,
            prompt=prompt,
            temperature=0.5,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.5,
        )
        summary_response = {'title': article_title, 'summary': ai_response,
                            'url': article_url, 'company_identifier': unique_company_identifier}
        summaries.update(summary_response)

    return "Summaries complete"
