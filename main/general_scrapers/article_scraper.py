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

company_url = 'Rivery.io'
company_id = 1


def url_search(company_url, company_id):
    news_domains = ['businesswire.com', 'finance.yahoo.com', 'prnewswire.com', 'globenewswire.com']
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
                    result_dict = {'domain': result['domain'], 'link': result['link'],
                                   'snippet': result['snippet'], 'title': result['title'], 'date': result['date'],
                                   'source': result['source'], 'company_id': company_id, 'company_url': company_url}
                    result_dataframe = pd.DataFrame(result_dict, index=[0])
                    result_dataframe.to_sql(f'serpdata', con=engine, if_exists='append')
                    valueserp_dict[count] = result_dict
            else:
                pass
            news_search_results[news_domain] = valueserp_dict
        except Exception as e:
            print(e)
            continue
    pp.pprint(news_search_results)

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
                print(url)
                scraped_data = scrape(url)
                scraped_data['Source'] = source
                scraped_data['Link'] = link
                pp.pprint(scraped_data)
                articles_dataframe = pd.DataFrame([scraped_data])
                print(articles_dataframe)
                articles_dataframe.to_sql(f'articles', con=engine, if_exists='append')
                return {'Status': 'Success'}
    except Exception as e:
        print(e)
        return {'Status': 'Failed'}




    print("Finished... exiting.")


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

            scraped_data = {'Article Title': refined_title, 'Article Text': refined_article_text}
            return scraped_data
        except Exception as error:
            print(error)
            retries += 1
            if retries == 3:
                return url


url_search(company_url, company_id)
