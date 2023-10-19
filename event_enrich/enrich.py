import sys

from newspaper import Article
import requests
from sqlalchemy import create_engine
import json
import time
import pandas as pd
import pprint as pp

email = "jack@rivery.io"


def assign_vars(upload_data):
    name_header = upload_data['name header']
    email_header = upload_data['email header']
    company_header = upload_data['company header']
    title_header = upload_data['title header']
    csv_data = pd.DataFrame.from_dict(upload_data['csv'])

    for ind in csv_data.index:
        name = (csv_data[name_header][ind])
        email = (csv_data[email_header][ind])
        company = (csv_data[company_header][ind])
        title = (csv_data[title_header][ind])


def find_company(email):
    company_url = None
    email_length = len(email)

    current_e_index = -1
    at_e_index = None
    for element in email:
        current_e_index += 1
        if element == "@":
            at_e_index = current_e_index
            break
    domain = email[at_e_index + 1:]

    if domain == "gmail.com":
        return "Skip"
    else:
        company_data_response = requests.get(
            f"https://api.thecompaniesapi.com/v1/companies/{domain}",
            headers={'Authorization': 'basic EvGVkI4x'})
        company_r = company_data_response.json()

        linkedin_url = company_r['socialNetworks']['linkedin']
        linkedin_id = company_r['socialNetworks']['linkedinIdNumeric']

        print(linkedin_url, linkedin_id)
        serp_search(domain)


def serp_search(domain):
    news_domains = ['businesswire.com', 'finance.yahoo.com', 'prnewswire.com', 'globenewswire.com']
    news_search_results = {}
    for news_domain in news_domains:
        try:
            params = {'api_key': '172D9AB76C6943D3ACD0BFACD1893705',
                      'q': f'site:{news_domain} "{domain}" data',
                      'search_type': 'news',
                      'location': 'United+States',
                      'max_page': 2}
            valueserp_result = requests.get('https://api.valueserp.com/search', params)
            r = valueserp_result.json()

            valueserp_dict = {}
            count = 0
            if valueserp_result.status_code == 200:
                for result in r['news_results']:
                    count += 1
                    source = result['source']
                    source_count = "source" + str(count)
                    result_dict = {'domain': result['domain'], 'link': result['link'],
                                   'snippet': result['snippet'], 'title': result['title'], 'date': result['date'],
                                   'source': result['source']}
                    valueserp_dict[source_count] = result_dict
            news_search_results[news_domain] = valueserp_dict
        except Exception as e:
            print(e)
            continue
        article_scraping(news_search_results)


def article_scraping(news_search_results):
    scraped_articles = {}
    for result in news_search_results:
        scraped_articles_with_origin = {}
        count = 0
        for obj in news_search_results[result]:
            try:
                link = news_search_results[result][obj]['link']

                username = "geonode_aeYJlDbG0k-country-GB"
                password = "2c209d3a-1bbe-4122-a2e4-2c8a49b45489"
                GEONODE_DNS = "premium-residential.geonode.com:9000"
                urlToGet = link
                proxy = {"http": "http://{}:{}@{}".format(username, password, GEONODE_DNS)}
                r = requests.get(urlToGet, proxies=proxy)

                article = Article(urlToGet)
                article.download(input_html=r.text)
                article.parse()
                title = article.title
                text = article.text
                print(text)
                time.sleep(5)
                print(title)
                print(text)
            except Exception as e:
                print(e)





find_company(email)

