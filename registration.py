import pandas as pd
from sqlalchemy import create_engine, text
import uniqueIDfunc
import requests
import json

conn = None
cur = None
engine = create_engine(
    'postgresql://xpdmcctztuueoj:5c6b0ce73d0e1d7a8b7ea13688df6b7268edd3e85ddc1ba488a8e233759731d2@ec2-34-241-82-91.eu-west-1.compute.amazonaws.com:5432/d6i1k6lrk3j39n')


def registeruser(registeruserdata):
    NewUserDf = pd.json_normalize(registeruserdata, max_level=0)
    currentEmail = (NewUserDf['EmailAddress'][0])
    print(currentEmail)

    try:
        with engine.connect() as conn:
            select = text('SELECT * FROM "UserData"')
            PostgresUserDf = pd.read_sql_query(select, conn)
            PostgresUserDf = PostgresUserDf.drop(columns='index')

        ExistingEmailCheck = currentEmail in PostgresUserDf['Email Address'].values
        print(ExistingEmailCheck)
    except:
        ExistingEmailCheck = False
        print(ExistingEmailCheck)

    if ExistingEmailCheck:
        print("Error - email exists")
        return("ErrorExistingEmail")
    else:
        userID = uniqueIDfunc.uniqueID()
        companyID = uniqueIDfunc.uniqueCompanyID()
        print(userID)
        print(companyID)

        try:
            NewUserDf['UserID'] = userID
            NewUserDf['CompanyID'] = companyID
            NewUserDf.to_sql(f'UserData', con=engine, if_exists='append')
            conn.close()
            print("Registration success")
            return("RegistrationSuccessful")
        except:
            print("Registration Error")
            return("RegistrationError")
