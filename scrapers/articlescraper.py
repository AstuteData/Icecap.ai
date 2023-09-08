from newsplease import NewsPlease
import pandas as pd
import requests
import json
from sqlalchemy import create_engine, text

conn = None
cur = None
engine = create_engine(
    'postgresql://xpdmcctztuueoj:5c6b0ce73d0e1d7a8b7ea13688df6b7268edd3e85ddc1ba488a8e233759731d2@ec2-34-241-82-91.eu-west-1.compute.amazonaws.com:5432/d6i1k6lrk3j39n')


def link_scraper(domain, unique_company_identifier):
    #Scrapes the links relating to the search query.
    article_link_scraper_params = {
        'api_key': '172D9AB76C6943D3ACD0BFACD1893705',
        'search_type': 'news',
        'q': domain,
        'news_type': 'all',
        'google_domain': 'google.com',
        'sort_by': 'date',
        'output': 'json',
        'hl': 'en',
        'num': '5'
    }

    article_link_request = requests.get('https://api.valueserp.com/search', article_link_scraper_params)
    article_link_json = article_link_request.json()
    article_link_list = []

    # Loops through the response and appends only the links to article_link_list
    for i in article_link_json['news_results']:
        article_link = i['link']
        article_link_list.append(article_link)

    article_scraper_response = json.dumps(article_scraper(article_link_list, unique_company_identifier))
    return {"status": "success", "response": article_scraper_response}


def article_scraper(article_link_list, unique_company_identifier):
    # Loops through the article_link_list url's and scrapes the articles. It will skip url's that return 'None'
    count = 0
    articles = {}
    for article in range(len(article_link_list)):
        scraped_article = NewsPlease.from_url(article_link_list[article])
        if scraped_article.title is None:
            pass
        else:
            article_data = {'title': scraped_article.title, 'text': scraped_article.maintext,
                            'published': scraped_article.date_publish, 'url': scraped_article.url,
                            'language': scraped_article.language, 'company_identifier': unique_company_identifier}
            articles.update(article_data)
            count += 1
            if count == range(len(article_link_list)):
                return articles
            else:
                continue
