from newspaper import Article
import pandas as pd
import requests
import json
from sqlalchemy import create_engine, text
import pprint as pp

conn = None
cur = None
engine = create_engine(
    'postgresql://xpdmcctztuueoj:5c6b0ce73d0e1d7a8b7ea13688df6b7268edd3e85ddc1ba488a8e233759731d2@ec2-34-241-82-91.eu-west-1.compute.amazonaws.com:5432/d6i1k6lrk3j39n')

# TESTED - PRODUCTION APPROVED.

def article_scraper(domain):
    print("Article search")
    params = {
        'api_key': '172D9AB76C6943D3ACD0BFACD1893705',
        'search_type': 'news',
        'q': {domain},
        'news_type': 'all',
        'google_domain': 'google.com',
        'gl': 'us',
        'lr': 'lang_en',
        'sort_by': 'date',
        'output': 'json',
        'num': '3'
    }

    # Returning links from Google News based on the company domain.

    r = requests.get('https://api.valueserp.com/search', params)
    rp = r.json()
    news_urls = []

    for result in rp['news_results']:
        news_url = result['link']
        news_urls.append(news_url)
    print(news_urls)
    articles = {}
    count = 0
    for url in news_urls:
        try:
            article = Article(url)
            article.download()
            article.parse()

            title = article.title
            article_text = article.text

            refined_title = title.replace('\n', ' ')
            refined_article_text = article_text.replace('\n', ' ')

            scraped_data = {'Article Title': refined_title, 'Article Text': refined_article_text}
            count += 1
            count_str = str(count)
            articles[count_str] = scraped_data
            print(scraped_data)
        except Exception as error:
            print(error)
            pass

    pp.pprint(articles)
    return articles

