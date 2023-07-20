import pandas
import pandas as pd
from sqlalchemy import create_engine, text
import uniqueIDfunc
import requests
import json

conn = None
cur = None
engine = create_engine(
    'postgresql://xpdmcctztuueoj:5c6b0ce73d0e1d7a8b7ea13688df6b7268edd3e85ddc1ba488a8e233759731d2@ec2-34-241-82-91.eu-west-1.compute.amazonaws.com:5432/d6i1k6lrk3j39n')

email = "jack@whitehouse.co.uk"
password = "password1234!"
company = "Rivery"

userDataJson = {"email": "jack@whitehouse.co.uk",
                "password": "password1234!",
                "company": "Rivery"}

def register():
    userID = uniqueIDfunc.uniqueID()

    response_df = pandas.DataFrame.from_dict([userDataJson])

    print(response_df)












register()

