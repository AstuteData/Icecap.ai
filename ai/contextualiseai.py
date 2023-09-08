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




def start_contextualisation_ai(unique_company_identifier):
    # Connecting to Postgres and extracting the company data table into a dataframe.
    connect_attempt = 0
    retries = 3
    while connect_attempt < retries:
        try:
            with engine.connect() as conn:
                article_select = text('SELECT * FROM "ArticleSummariesData"')
                article_data_table = pd.read_sql_query(article_select, conn)
                article_data_table.drop(columns='index')
                retries = 0

            with engine.connect() as conn:
                prospect_select = text('SELECT * FROM "ProspectSummariesData"')
                prospect_data_table = pd.read_sql_query(prospect_select, conn)
                prospect_data_table.drop(columns='index')
                retries = 0

        except Exception as error:
            connect_attempt += 1
            print("An exception has occurred:", error)
            if connect_attempt == retries:
                return "Error:", error

    # Filter based on company id
    # Contextualise the articles to the persona + company.


