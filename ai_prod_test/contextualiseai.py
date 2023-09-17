import pandas as pd
from sqlalchemy import create_engine, text
import uuid
import requests
import json
import openai
from types import NoneType

openai.api_key = "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"
modelEngine = "text-davinci-003"


def start_contextualisation_ai(article_analysis, prospect_analysis, hiring_analysis):
    article_analysis_string = ""
    hiring_analysis_string = ""

    article_count = 0
    for i in article_analysis.values():
        article_title = i['Article Title']
        article_summary = i['Article Analysis']
        article_count += 1
        article_analysis_string += f"Article number: {article_count}" \
                                   f"Article title: {article_title}" \
                                   f"Article analysis: {article_summary}" \
                                   f""

    # Shouldn't be run if there's no hiring data.
    hiring_job_count = 0
    for i in hiring_analysis.values():
        hiring_job_title = i['Article Title']
        hiring_job_analysis = i['Article Analysis']
        hiring_job_count += 1
        hiring_job_count_str = str(hiring_job_count)
        hiring_analysis_string += f"Job number: {hiring_job_count_str}" \
                                  f"Job title: {hiring_job_title}" \
                                  f"Job analysis: {hiring_job_analysis}" \
                                  f""

    prompt = F"The overview:" \
             F"" \
             F"You are a veteran salesman. You must complete the task of reading through analysed company" \
             F"  data to find information about the company, and create a convincing strategy and " \
             F"pitch to get them to buy your product. " \
             F"" \
             F"The following information is critical. You need to analyse every element of the analysed data" \
             F" and highlight the most important information. The information will be used to understand how to " \
             F"1. Make your product relevant in to their company and explain why they have to buy this product now instead of later. " \
             F"2. Personalise the interaction with the prospect so that you can a) catch their attention, and b) build rapport. It is mission critical that you do this " \
             F" extremely well. Otherwise you will be fired from your job. " \
             F" " \
             F"The task:" \
             F"Task 1: You must read through the following summaries and do as overview instructs. " \
             F"" \
             F"Here is the article analysis to help analyse the company holistically:" \
             F"{article_analysis_string}" \
             F"" \
             F"Here is the hiring analysis to help analyse company holistically:" \
             F"{hiring_analysis_string}" \
             F"" \
             F"Now analyse how to make the pitch relevant to the prospect:" \
             F"" \
             F"Task 2: You must analyse these summaries from the prospect's LinkedIn profile." \
             F"" \
             F"Here is the prospect's LinkedIn profile summary to help analyse the prospect." \
             F"{prospect_analysis} " \

    ai_response = openai.Completion.create(
        model=modelEngine,
        prompt=prompt,
        temperature=0.5,
        max_tokens=400,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.4,
    )

    print(ai_response)
    return {"Holistic Analysis": ai_response}
