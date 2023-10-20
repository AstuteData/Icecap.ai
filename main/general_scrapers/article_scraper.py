import requests
from newspaper import Article
import pandas as pd
from sqlalchemy import create_engine
import pprint as pp

conn = None
cur = None
engine = create_engine(
    'postgresql://xpdmcctztuueoj:5c6b0ce73d0e1d7a8b7ea13688df6b7268edd3e85ddc1ba488a8e233759731d2@ec2-34-241-82-91.'
    'eu-west-1.compute.amazonaws.com:5432/d6i1k6lrk3j39n')


def url_search(company_url, company_id, research_id, user_id):
    news_domains = ['businesswire.com', 'prnewswire.com', 'globenewswire.com']
    news_search_results = {}
    for news_domain in news_domains:
        try:
            params = {'api_key': '172D9AB76C6943D3ACD0BFACD1893705',
                      'q': f'site:{news_domain} "{company_url}" data',
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
                                   'source': result['source'], 'company_id': company_id, 'company_url': company_url,
                                   'research_id': research_id}
                    result_dataframe = pd.DataFrame(result_dict, index=[0])
                    result_dataframe.to_sql(f'serpdata', con=engine, if_exists='append')
                    valueserp_dict[source_count] = result_dict
            else:
                pass
            news_search_results[news_domain] = valueserp_dict
        except Exception as e:
            print(e)
            continue

    try:
        scraped_articles = {}
        for result in news_search_results:
            scraped_articles_with_origin = {}
            count = 0
            for obj in news_search_results[result]:
                link = news_search_results[result][obj]['link']
                source = news_search_results[result][obj]['source']
                count += 1
                url = news_search_results[result][obj]['link']
                scraped_data = scrape(url)
                scraped_data['Source'] = source
                scraped_data['Link'] = link
                articles_dataframe = pd.DataFrame([scraped_data])
                articles_dataframe['company_id'] = company_id
                articles_dataframe['research_id'] = research_id
                articles_dataframe['user_id'] = user_id
                articles_dataframe.to_sql(f'articles', con=engine, if_exists='append')
    except Exception as e:
        print(e)
        return {'Status': 'Failed'}


def scrape(url):
    retries = 0
    while retries <= 3:
        try:
            username = "geonode_aeYJlDbG0k-country-GB"
            password = "2c209d3a-1bbe-4122-a2e4-2c8a49b45489"
            GEONODE_DNS = "premium-residential.geonode.com:9000"
            urlToGet = url
            proxy = {"http": "http://{}:{}@{}".format(username, password, GEONODE_DNS)}
            r = requests.get(urlToGet, proxies=proxy)

            article = Article(urlToGet)
            article.download(input_html=r.text)
            article.parse()
            article_title = article.title
            article_text = article.text

            scraped_data = {'Article Title': article_title, 'Article Text': article_text}
            return scraped_data
        except Exception as error:
            print(error)
            retries += 1
            if retries == 3:
                pass