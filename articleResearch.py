import requests
from newspaper import Article
import pandas as pd
import openai
from sqlalchemy import create_engine, text
import psycopg2

conn = None
cur = None
engine = create_engine(
    'postgresql://xpdmcctztuueoj:5c6b0ce73d0e1d7a8b7ea13688df6b7268edd3e85ddc1ba488a8e233759731d2@ec2-34-241-82-91.eu-west-1.compute.amazonaws.com:5432/d6i1k6lrk3j39n')


def prep_article_data(jsonstring):
    df = pd.json_normalize(jsonstring, max_level=0)
    print(df)

    for ind in df.index:
        currentCompany = (df['originalCompanyName'][ind])
        currentCompanyDomain = (df['domain'][ind])
        uniqueID = (df['UniqueID'][ind])

        article_search(currentCompany, currentCompanyDomain, uniqueID)


def article_search(currentCompany, currentCompanyDomain, uniqueID):

    print("Article search")
    params = {
    'api_key': '172D9AB76C6943D3ACD0BFACD1893705',
      'search_type': 'news',
      'q': {currentCompanyDomain},
      'news_type': 'all',
      'google_domain': 'google.com',
      'sort_by': 'date',
      'show_duplicates': 'false',
      'gl': 'us',
      'hl': 'en',
      'time_period': 'custom',
      'time_period_min': '01-01-2020',
      'time_period_max': '05-21-2023',
      'output': 'json',
      'num': '10'
    }

    # Returning links from Google News based on the company domain.

    r = requests.get('https://api.valueserp.com/search', params)
    rp = r.json()
    df = pd.json_normalize(rp, record_path=['news_results'])

    allArticleLinks = []
    goodArticleLinks = []
    titles = []
    summaries = []
    texts = []
    authors = []
    keywords = []

    for row in df.itertuples():
        allArticleLinks.append(row.link)

    for url in allArticleLinks:
        try:
            article = Article(url)
            article.download()
            article.parse()
            article.nlp()

            goodArticleLinks.append(url)

            title = article.title
            title = title.replace('\n',' ')
            titles.append(title)

            summary = article.summary
            summary = summary.replace('\n',' ')
            summaries.append(summary)

            text = article.text
            text = text.replace('\n',' ')
            texts.append(text)

            author = article.authors
            author = author.replace('\n', ' ')
            authors = authors.append(author)

            keyword = article.keywords
            keyword = keyword.replace('\n', ' ')
            keywords = keywords.append(keyword)
        except:
            pass

    data = {'Title': titles,
            'Article': goodArticleLinks,
            'Summary': summaries,
            'Text': texts,
            }

    df1 = pd.DataFrame.from_dict(data, orient='index')
    df1 = df1.transpose()
    df1['CompanyName'] = currentCompany
    df1['UniqueID'] = uniqueID

    articlePrompt = "Summarize this article in 5 bullet points: "
    articleCount = 0
    summarizedArticles = []

    print(f"Summarising {currentCompany}'s articles")

    for ind in df1.index:
        currentArticleText = (df1['Text'][ind])
        articleCount = articleCount + 1
        print("------")
        print("summarising")
        print(articleCount)
        print("------")

        openai.api_key = "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"
        modelEngine = "text-davinci-003"
        activePrompt = (f"{articlePrompt} {currentArticleText}")

        completion = openai.Completion.create(
            model=modelEngine,
            prompt=activePrompt,
            temperature=0.5,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.5,
        )

        response = completion.choices[0].text
        summarizedArticles.append(response)

        if (articleCount == df1.index.size):
            df1['AiSummary'] = summarizedArticles
            df1.to_sql(f'ArticleData', con=engine, if_exists='append')
            print("Process finished")

        elif (articleCount != df1.index.size):
            print("next article")
            continue