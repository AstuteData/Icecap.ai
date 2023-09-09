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


def start_contextualisation_ai(focus, hiring_analysis_response, article_analysis_response, prospect_analysis_response):
    if focus == 0:
        article_summary_string = article_analysis_response
        hiring_summary_string = hiring_analysis_response
        prospect_post_summary_string = None
        prospect_position_summary_string = None

        prospect_post_summary_complete = False
        prospect_position_summary_complete = False

        prospect_post_count = 0
        for prospect_posts_summary in prospect_analysis_response:
            prospect_posts_data = prospect_analysis_response[prospect_posts_summary]
            prospect_posts_summary = prospect_posts_data['summary']
            prospect_post_count += 1
            prospect_post_summary_string += f"Post number: {prospect_post_count}" \
                                            f"Post summary: {prospect_posts_summary}" \
                                            f""
            if prospect_post_count == len(prospect_analysis_response):
                prospect_post_summary_complete = True
            else:
                pass

        prospect_position_count = 0
        for prospect_position_summary in prospect_analysis_response:
            prospect_position_data = prospect_analysis_response[prospect_position_summary]
            prospect_position_title = prospect_position_data['title']
            prospect_position_summary = prospect_position_data['summary']
            prospect_position_count += 1
            prospect_position_summary_string += f"Prospect position number: {prospect_position_count}" \
                                                f"Prospect position: {prospect_position_title}" \
                                                f"Prospect position summary: {prospect_position_summary}"\
                                                f""
            if prospect_position_count == len(prospect_analysis_response):
                prospect_position_summary_complete = True
            else:
                pass

        if prospect_post_summary_complete and prospect_position_summary_complete is True:
            prompt = ""

            ai_response = openai.Completion.create(
                model=modelEngine,
                prompt=prompt,
                temperature=0.5,
                max_tokens=200,
                top_p=1,
                frequency_penalty=0.0,
                presence_penalty=0.5,
            )

            return {"status": "success", "response": ai_response}

    elif focus == 1:
        article_summary_string = None
        prospect_post_summary_string = None
        prospect_position_summary_string = None
        hiring_summary_string = None

        article_summary_complete = False
        prospect_post_summary_complete = False
        prospect_position_summary_complete = False
        hiring_summary_complete = False

        article_count = 0
        for article_summary in article_analysis_response:
            article_data = article_analysis_response[article_summary]
            article_title = article_data['title']
            article_summary = article_data['text']
            article_count += 1
            article_summary_string += f"Article number: {article_count}" \
                                      f"Article title: {article_title}" \
                                      f"Article summary: {article_summary}" \
                                      f""
            if article_count == len(article_analysis_response):
                article_summary_complete = True
            else:
                pass

        prospect_post_count = 0
        for prospect_posts_summary in prospect_analysis_response:
            prospect_posts_data = prospect_analysis_response[prospect_posts_summary]
            prospect_posts_summary = prospect_posts_data['summary']
            prospect_post_count += 1
            prospect_post_summary_string += f"Post number: {prospect_post_count}" \
                                            f"Post summary: {prospect_posts_summary}" \
                                            f""
            if prospect_post_count == len(prospect_analysis_response):
                prospect_post_summary_complete = True
            else:
                pass

        prospect_position_count = 0
        for prospect_position_summary in prospect_analysis_response:
            prospect_position_data = prospect_analysis_response[prospect_position_summary]
            prospect_position_title = prospect_position_data['title']
            prospect_position_summary = prospect_position_data['summary']
            prospect_position_count += 1
            prospect_position_summary_string += f"Prospect position number: {prospect_position_count}" \
                                                f"Prospect position: {prospect_position_title}" \
                                                f"Prospect position summary: {prospect_position_summary}" \
                                                f""
            if prospect_position_count == len(prospect_analysis_response):
                prospect_position_summary_complete = True
            else:
                pass

        hiring_job_count = 0
        for hiring_job_summary in hiring_analysis_response:
            hiring_job_title = hiring_analysis_response[hiring_job_summary]['title']
            hiring_job_summary = hiring_analysis_response[hiring_job_summary]['summary']
            hiring_job_count += 1
            hiring_summary_string += f"Job number: {hiring_job_count}" \
                                     f"Job title: {hiring_job_title}" \
                                     f"Job summary: {hiring_job_summary}" \
                                     f""
            if hiring_job_count == len(hiring_analysis_response):
                hiring_summary_complete = True
            else:
                pass

        if article_summary_complete and prospect_post_summary_complete and prospect_position_summary_complete and hiring_summary_complete is True:
            prompt = ""

            ai_response = openai.Completion.create(
                model=modelEngine,
                prompt=prompt,
                temperature=0.5,
                max_tokens=200,
                top_p=1,
                frequency_penalty=0.0,
                presence_penalty=0.5,
            )

            return {"status": "success", "response": ai_response}
