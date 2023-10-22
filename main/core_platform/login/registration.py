import uuid
import pandas as pd
from sqlalchemy import create_engine, text
import json

conn = None
cur = None
engine = create_engine(
    'postgresql://xpdmcctztuueoj:5c6b0ce73d0e1d7a8b7ea13688df6b7268edd3e85ddc1ba488a8e233759731d2@ec2-34-241-82-91.'
    'eu-west-1.compute.amazonaws.com:5432/d6i1k6lrk3j39n')


def register(registration_data):
    try:
        user = text('SELECT * FROM "user"')
        user_data = pd.read_sql_query(user, conn)
        user_data.drop(columns='index')
    except Exception as e:
        print(e)
        user_data = pd.DataFrame()
    user_data_len = len(user_data)

    email = registration_data['EmailAddress']
    email_formatted = email.lower()
    password = registration_data['Password']

    try:
        count = -1
        for row, index in user_data.iterrows():
            count = count + 1
            if email_formatted == index['email']:
                return {'Status': 'Email already registered', 'User ID': 'None'}
            else:
                if count == user_data_len:
                    user_id = uuid.uuid4()
                    new_user_data = pd.DataFrame()
                    new_user_data['company_name'] = [registration_data['CompanyName']]
                    new_user_data['first_name'] = [registration_data['FirstName']]
                    new_user_data['last_name'] = [registration_data['LastName']]
                    new_user_data['email'] = [email_formatted]
                    new_user_data['password'] = [password]
                    new_user_data['user_id'] = [user_id]

                    new_user_data.to_sql(f'user', con=engine, if_exists='append')
                    return {'Status': 'Successful registration', 'User ID': user_id}
                elif count < user_data_len:
                    pass
    except Exception as e:
        print(e)
        return {'Status': f'Error: {e}', 'User ID': 'None'}


def registration_table():
    new_user_data = pd.DataFrame()
    new_user_data['first_name'] = ['Terry']
    new_user_data['last_name'] = ['Tester']
    new_user_data['email'] = ['terry@tester.com']
    new_user_data['password'] = ['password']
    new_user_data['user_id'] = ['1']
    print(new_user_data)
    new_user_data.to_sql(f'user', con=engine, if_exists='append')
