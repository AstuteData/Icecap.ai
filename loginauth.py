import pandas as pd
from sqlalchemy import create_engine, text
import json

conn = None
cur = None
engine = create_engine(
    'postgresql://xpdmcctztuueoj:5c6b0ce73d0e1d7a8b7ea13688df6b7268edd3e85ddc1ba488a8e233759731d2@ec2-34-241-82-91.eu-west-1.compute.amazonaws.com:5432/d6i1k6lrk3j39n')


def loginauth(loginuserdata):
    existingUserDf = pd.json_normalize(loginuserdata, max_level=0)
    currentEmail = (existingUserDf['EmailAddress'][0])
    currentPassword = (existingUserDf['Password'][0])

    try:
        with engine.connect() as conn:
            select = text('SELECT * FROM "UserData"')
            PostgresUserDf = pd.read_sql_query(select, conn)
            PostgresUserDf = PostgresUserDf.drop(columns='index')
            conn.close()

        ExistingEmailCheck = currentEmail in PostgresUserDf['EmailAddress'].values
    except:
        ExistingEmailCheck = False

    if ExistingEmailCheck:
        emailPosition = PostgresUserDf.loc[PostgresUserDf.isin([currentEmail]).any(axis=1)].index.tolist()
        emailPosition = emailPosition[0]
        existingEmail = (PostgresUserDf['EmailAddress'][emailPosition])
        existingPassword = (PostgresUserDf['Password'][emailPosition])

        if currentEmail == existingEmail and currentPassword == existingPassword:
            print("Successful Login")
            return("LoginSuccessful")
        else:
            print("Unsuccessful login")
            return("LoginUnsuccessful")
    else:
        return("ErrorNoExistingEmail")
