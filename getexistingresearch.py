import pandas as pd
from sqlalchemy import create_engine, text
import json

conn = None
cur = None
engine = create_engine(
    'postgresql://xpdmcctztuueoj:5c6b0ce73d0e1d7a8b7ea13688df6b7268edd3e85ddc1ba488a8e233759731d2@ec2-34-241-82-91.eu-west-1.compute.amazonaws.com:5432/d6i1k6lrk3j39n')

def getresearch(companyid):
    with engine.connect() as conn:
        select = text('SELECT * FROM "ArticleData"')
        postgresArticleDf = pd.read_sql_query(select, conn)
        conn.close()

    print(postgresArticleDf)
    print(companyid)

    return companyid

    '''postgresArticleDf_Filtered = postgresArticleDf.query("UniqueID == @companyid")
    print(postgresArticleDf_Filtered)

    postgresArticleDf_Json = postgresArticleDf_Filtered.to_json(orient='records')
    print(postgresArticleDf_Json)'''


