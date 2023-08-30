import requests
import pandas as pd
import openai
from sqlalchemy import create_engine, text

conn = None
cur = None
engine = create_engine(
    'postgresql://xpdmcctztuueoj:5c6b0ce73d0e1d7a8b7ea13688df6b7268edd3e85ddc1ba488a8e233759731d2@ec2-34-241-82-91.eu-west-1.compute.amazonaws.com:5432/d6i1k6lrk3j39n')
openai.api_key = "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"
modelEngine = "text-davinci-003"


def news_summary(companyid):
    with engine.connect() as conn:
        select = text('SELECT * FROM "ArticleData"')
        postgresArticleDf = pd.read_sql_query(select, conn)
        postgresArticleDf = postgresArticleDf.drop(columns='index')

        company = []
        ids = []
        summary = []
        focuses = []
        positioning = []

        for id in companyid:
            postgresArticleDf_Filtered = postgresArticleDf.query("UniqueID == @id")
            currentCompany = postgresArticleDf_Filtered['name']
            for i in range(len(postgresArticleDf_Filtered)):
                articleCount = 0
                articles = ""
                for article in postgresArticleDf_Filtered["AiSummary"]:
                    articleCount = articleCount + 1
                    articleCount_str = str(articleCount)
                    current_article = article
                    articles = articles + f"Article {articleCount_str}: \n{current_article}\n"

                prompt = f"x: {articles}"

                news_summary_completion = openai.Completion.create(
                    model=modelEngine,
                    prompt=prompt,
                    temperature=0.5,
                    max_tokens=200,
                    top_p=1,
                    frequency_penalty=0.0,
                    presence_penalty=0.5,
                )

                key_focuses, product_positioning = news_key_focuses(articles)
                company.append(currentCompany)
                ids.append(id)
                summary.append(news_summary_completion)
                focuses.append(key_focuses)
                positioning.append(product_positioning)

    newsResearchDf = pd.DataFrame()
    newsResearchDf["Company Name"] = company
    newsResearchDf["UniqueID"] = ids
    newsResearchDf["Summary"] = summary
    newsResearchDf["Key Focuses"] = focuses
    newsResearchDf["Product Positioning"] = positioning

    newsResearchDf.to_sql(f'NewsAiResearch', con=engine, if_exists='append')
    conn.close()

    return "Complete"


def news_key_focuses(articles):
    prompt = f"x: {articles}"

    news_key_focuses_completion = openai.Completion.create(
        model=modelEngine,
        prompt=prompt,
        temperature=0.5,
        max_tokens=200,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.5,
    )

    news_product_positioning(articles, news_key_focuses_completion)


def news_product_positioning(articles, news_key_focuses_completion):
    prompt = f"x: {articles} \n y: {news_key_focuses_completion} \n z: do abc"

    news_product_positioning_completion = openai.Completion.create(
        model=modelEngine,
        prompt=prompt,
        temperature=0.5,
        max_tokens=200,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.5,
    )

    return news_key_focuses_completion, news_product_positioning_completion