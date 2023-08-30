import requests
from newspaper import Article
import pandas as pd
import openai
from sqlalchemy import create_engine, text

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
    openai.api_key = "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"
    modelEngine = "text-davinci-003"
    print("Article search")
    articleQ = (f"{currentCompany} {currentCompanyDomain} business articles")
    params = {
    'api_key': '172D9AB76C6943D3ACD0BFACD1893705',
      'search_type': 'news',
      'q': {articleQ},
      'news_type': 'all',
      'google_domain': 'google.com',
      'sort_by': 'date',
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
    businessArticleConfirmation = []

    for row in df.itertuples():
        allArticleLinks.append(row.link)
        print(allArticleLinks)

    for url in allArticleLinks:
        try:
            article = Article(url)
            article.download()
            article.parse()

            goodArticleLinks.append(url)

            title = article.title
            title = title.replace('\n',' ')
            titles.append(title)

            summary = article.summary
            summary = summary.replace('\n',' ')
            summaries.append(summary)

            arttext = article.text
            arttext = arttext.replace('\n',' ')
            texts.append(arttext)

            author = article.authors
            author = author.replace('\n', ' ')
            authors = authors.append(author)

            keyword = article.keywords
            keyword = keyword.replace('\n', ' ')
            keywords = keywords.append(keyword)
        except:
            pass

    '''businessOrNotPrompt = "You will classify articles as 'business related' or 'not business related' after analysing " \
                          "this text. 'Business related' articles will have information that can be used to position " \
                          "a product to somebody, if there is no information that can be used to position a product, " \
                          "then you will classify the article as 'not business related'. You do not need to give the " \
                          "reasoning behind this, answer only 'business related' or 'not business related'. Analyse " \
                          "and classify the following article:"

    for i in texts:
        articleCheckingPrompt = (f"{businessOrNotPrompt} + {i}")
        completion = openai.Completion.create(
            model=modelEngine,
            prompt=articleCheckingPrompt,
            temperature=0.5,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.5,
        )
        businessOrNot = completion.choices[0].text
        businessArticleConfirmation.append(businessOrNot)'''

    data = {'Title': titles,
            'Article': goodArticleLinks,
            'Summary': summaries,
            'Text': texts,
            }

    print(data)

    df1 = pd.DataFrame.from_dict(data, orient='index')
    df1 = df1.transpose()
    df1['CompanyName'] = currentCompany
    df1['UniqueID'] = uniqueID

    print(df1)

    '''df1 = df1.loc[df1['Confirmation'].str.contains('Business related', regex=False)]
    df1 = df1.drop('Confirmation', axis=1)'''

    articlePrompt = "You will summarize this article in 5 bullet points. You will only use bullet points and not dashes: "
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

        if articleCount == df1.index.size:
            with engine.connect() as conn:
                select = text('SELECT * FROM "CompanyData"')
                PostgresCompanyDf = pd.read_sql_query(select, conn)
                PostgresCompanyDf = PostgresCompanyDf.drop(columns='index')
            currentIndex = PostgresCompanyDf.loc[PostgresCompanyDf.isin([currentCompany]).any(axis=1)].index.tolist()
            print(currentCompany)
            print(currentIndex)
            PostgresCompanyDf.at[currentIndex[0], 'ResearchStatus'] = 'ResearchComplete'
            df1['AiSummary'] = summarizedArticles
            df1.to_sql(f'ArticleData', con=engine, if_exists='append')
            PostgresCompanyDf.to_sql(f'CompanyData', con=engine, if_exists='replace')
            conn.close()
            print("Process finished")
        elif articleCount != df1.index.size:
            print("next article")
            continue
