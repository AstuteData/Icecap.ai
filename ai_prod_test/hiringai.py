import pandas as pd
from sqlalchemy import create_engine, text
import requests
import json
import openai
import pprint as pp
from types import NoneType

openai.api_key = "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"
modelEngine = "text-davinci-003"


def start_hiring_ai(hiring_data):
    print(hiring_data)
    analysed_posts = {}
    loop_number = 0
    if type(hiring_data) is NoneType:
        print("No hiring data")
        return "NoneType. No hiring data."
    else:
        for i in hiring_data.items():
            loop_number += 1
            loop_number_str = str(loop_number)
            title = i['Job Title']
            link = i['Job Link']
            ul_data = i['Ul Data']
            p_data = i['P Data']
            print(title, link)

            prompt = "Analyse this job role and then summarise it." \
                     "Important information includes why this job has been posted by the company," \
                     "Skills that they need to have and any technical requirements for the job." \
                     "" \
                     "The information about the role:" \
                     f"Job Title: {title}" \
                     f"Job post: {ul_data}" \
                     f"{p_data}"

            ai_response = openai.Completion.create(
                model=modelEngine,
                prompt=prompt,
                temperature=0.5,
                max_tokens=200,
                top_p=1,
                frequency_penalty=0.0,
                presence_penalty=0.5,
            )

            post_dict = {"Job Title": title, "Job Link": link, "Job Analysis": ai_response}
            analysed_posts[loop_number_str] = post_dict

        pp.pprint(analysed_posts)
        return analysed_posts
