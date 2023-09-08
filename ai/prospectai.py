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


def start_prospect_ai(company_identifier):
    # Connecting to Postgres and extracting the prospect's data into a dataframe.
    connect_attempt = 0
    connect_success = False
    retries = 3
    while connect_success is False or connect_attempt < retries:
        try:
            with engine.connect() as conn:
                prospect_select = text('SELECT * FROM "ProspectData"')
                prospect_data_table = pd.read_sql_query(prospect_select, conn)
                prospect_data_table.drop(columns='index')
                connect_success = True
        except Exception as error:
            connect_attempt += 1
            print("An exception has occurred:", error)
            if connect_attempt == retries:
                return "Error:", error

    # Extracting the relevant prospect.
    prospect_data_table_index = prospect_data_table.index[
        prospect_data_table['company_identifier'] == company_identifier]
    prospect_data = prospect_data_table.query("company_identifier == @unique_company_identifier")

    summaries = {}
    for ind in prospect_data.index:
        name = prospect_data['name'][ind]
        position = prospect_data['position'][ind]
        company = prospect_data['company'][ind]
        experience = prospect_data['experience'][ind]
        recent_posts = prospect_data['recent posts'][ind]
        recent_likes = prospect_data['recent likes'][ind]
        recent_comments = prospect_data['recent comments'][ind]
        prospect_identifier = prospect_data['prospect identifier'][ind]

        summary_loop = {"experience": experience, "recent posts": recent_posts,
                        "recent comments": recent_comments, "recent likes": recent_likes}

        for key, value in summary_loop.items():
            analysis_response = {key: prospect_element_ai(key, value)}
            summaries.update(analysis_response)

    return {"status": "success", "response": summaries}


def prospect_element_ai(key, value):
    # This processes the prospect's job experiences. Not finished - to do: create the system that un-lists and puts these back into lists.
    if key == "experience":
        prompt = "Summarise this work experience description:", value
        ai_response = openai.Completion.create(
            model=modelEngine,
            prompt=prompt,
            temperature=0.5,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.5,
        )
        return ai_response

    # This processes the prospect's recent posts, likes and shares. Not finished - to do: create the system that un-lists and puts these back into lists.
    elif key == "recent posts":
        prompt_input = ""
        for number, content in value.items():
            posts_str = f"{number} " \
                        f"Prospect post: {content}"
            prompt_input = prompt_input + posts_str

        prompt = "You will receive a list of posts made by a prospect on a business networking site. Analyse the posts and summarise " \
                 "the key findings for each post, and then rank the key findings in the categories you consider important for sales " \
                 "prospecting. When you generate the output based on the analysis give each category a consistent header and " \
                 "footer that makes the output easy to extract into strings in Python." \
                 "Here is the list of posts made by the prospect that you need to analyse: " \
                 f"{prompt_input}"

        ai_response = openai.Completion.create(
            model=modelEngine,
            prompt=prompt,
            temperature=0.5,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.5,
        )
        return ai_response