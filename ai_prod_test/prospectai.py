import pandas as pd
from sqlalchemy import create_engine, text
import uuid
import requests
import json
import openai

conn = None
cur = None
openai.api_key = "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"
modelEngine = "text-davinci-003"


def start_prospect_ai(prospect_data):
    current_company = None
    current_title = None
    linkedin_profile_header = prospect_data['LinkedIn Profile']['Header']
    linkedin_profile_about = prospect_data['LinkedIn Profile']['About']
    linkedin_profile_experience = prospect_data['LinkedIn Profile']['Experience']
    linkedin_profile_experience_str = ""

    loop_count = 0
    for i in linkedin_profile_experience:
        scraped_position = i['Title']
        scraped_company = i['Company']
        scraped_description = i['Description']
        scraped_location = i['Location']
        loop_count += 1
        loop_count_str = str(loop_count)

        if loop_count == 1:
            current_company = i['Title']
            current_title = i['Company']

        linkedin_profile_experience_str += f" Job Experience {loop_count_str}. {scraped_position} at {scraped_company} in {scraped_location}." \
                                           f" This is the description: {scraped_description} "

    prompt = f"This is a prospect. They are a {current_title} at {current_company}. Analyse their LinkedIn profile:" \
             f"Header: {linkedin_profile_header}" \
             f"About: {linkedin_profile_about} " \
             f"Experience: {linkedin_profile_experience_str} " \

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
