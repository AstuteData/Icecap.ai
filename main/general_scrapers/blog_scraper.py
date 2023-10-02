import requests
from newspaper import Article
import pandas as pd
from sqlalchemy import create_engine
import pprint as pp
import json

conn = None
cur = None
engine = create_engine(
    'postgresql://xpdmcctztuueoj:5c6b0ce73d0e1d7a8b7ea13688df6b7268edd3e85ddc1ba488a8e233759731d2@ec2-34-241-82-91.'
    'eu-west-1.compute.amazonaws.com:5432/d6i1k6lrk3j39n')

company_url = 'Clari.com'
company_id = 1


def url_search(company_url, company_id):
    blog_serp_results = {}
    try:
        params = {'api_key': '172D9AB76C6943D3ACD0BFACD1893705',
                  'q': f'site:{company_url}/blog',
                  'search_type': 'news',
                  'location': 'United+States',
                  'time_period': 'custom',
                  'time_period_min': '05-01-2023',
                  'max_page': 2}
        valueserp_result = requests.get('https://api.valueserp.com/search', params)
        r = valueserp_result.json()
        blog_serp_results[company_url] = r
    except Exception as e:
        print(e)
        pass

    print(blog_serp_results)

    serp_results_filtered = blog_serp_results[company_url]['news_results']
    print(serp_results_filtered)
    for result in serp_results_filtered:
        url = result['link']
        title = result['title']
        date = result['date']
        serp_blog_data = {'SERP Url': url, 'SERP Title': title, 'SERP Date': date}
        researched_blog_data = scrape(url)
        blog_data = {**serp_blog_data, **researched_blog_data}
        blog_dataframe = pd.DataFrame([blog_data])
        print(blog_dataframe)
        blog_dataframe.to_sql(f'blogposts', con=engine, if_exists='append')


def scrape(url):
    retries = 0
    while retries <= 3:
        try:
            article = Article(url)
            article.download()
            article.parse()

            title = article.title
            article_text = article.text

            refined_title = title.replace('\n', ' ')
            refined_article_text = article_text.replace('\n', ' ')

            scraped_data = {'Blog Title': refined_title, 'Blog Text': refined_article_text}
            return scraped_data
        except Exception as error:
            print(error)
            retries += 1
            if retries == 3:
                return url


url_search(company_url, company_id)

#articles_dataframe = pd.DataFrame([scraped_data])
#print(articles_dataframe)
#articles_dataframe.to_sql(f'articles', con=engine, if_exists='append')