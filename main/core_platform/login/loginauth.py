import pandas as pd
from sqlalchemy import create_engine, text
import json

conn = None
cur = None
engine = create_engine(
    'postgresql://xpdmcctztuueoj:5c6b0ce73d0e1d7a8b7ea13688df6b7268edd3e85ddc1ba488a8e233759731d2@ec2-34-241-82-91.'
    'eu-west-1.compute.amazonaws.com:5432/d6i1k6lrk3j39n')


def login(login_data):
    try:
        with engine.connect() as conn:
            user = text('SELECT * FROM "user"')
            user_data = pd.read_sql_query(user, conn)
            user_data.drop(columns='index')
    except Exception as e:
        print(e)
        user_data = pd.DataFrame()

    email = login_data['EmailAddress']
    email_formatted = email.lower()
    password = login_data['password']
    user_data_len = len(user_data)

    try:
        count = 0
        for row, index in user_data.iterrows():
            count = count + 1
            if email_formatted == index['email']:
                if password == index['password']:
                    return {'Status': 'Successful login', 'User ID': index['user_id']}
                else:
                    return {'Status': 'Incorrect password', 'User ID': 'None'}
            else:
                if count == user_data_len:
                    return {'Status': 'Account does not exist', 'User ID': 'None'}
                else:
                    pass
    except Exception as e:
        print(e)
        return {'Status': f'Error: {e}', 'User ID': 'None'}
