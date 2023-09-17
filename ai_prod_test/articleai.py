import pandas as pd
from sqlalchemy import create_engine, text
import uuid
import requests
import json
import openai
import pprint as pp

openai.api_key = "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"
modelEngine = "text-davinci-003"


def start_article_ai(article_data):
    analysed_articles = {}
    loop_number = 0
    for i in article_data.values():
        loop_number += 1
        loop_number_str = str(loop_number)
        article_title = i['Article Title']
        article_text = i['Article Text']

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

        summary_response = {'Article Title': article_title, 'Article Analysis': ai_response}
        analysed_articles[loop_number_str] = summary_response
        print(summary_response)

    pp.pprint(analysed_articles)
    return analysed_articles
