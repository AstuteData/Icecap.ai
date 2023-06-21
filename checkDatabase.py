import pandas as pd
from sqlalchemy import create_engine, text
import uniqueIDfunc
import requests

conn = None
cur = None
engine = create_engine(
    'postgresql://xpdmcctztuueoj:5c6b0ce73d0e1d7a8b7ea13688df6b7268edd3e85ddc1ba488a8e233759731d2@ec2-34-241-82-91.eu-west-1.compute.amazonaws.com:5432/d6i1k6lrk3j39n')


def check_database():

    try:
        with engine.connect() as conn:
            select = text('SELECT * FROM "CompanyData"')
            df = pd.read_sql_query(select, conn)
            df = df.drop(columns='index')
            conn.close()
            print(df)

            for index, row in df.iterrows():
                if row['UniquePersonID'] == '1234':
                    companycheck = True
                    return companycheck

                if row['UniquePersonID'] != '1234':
                    continue
    except:
        companycheck = False
        return companycheck


check_database()
