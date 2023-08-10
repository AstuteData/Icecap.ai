import pandas as pd
from sqlalchemy import create_engine, text
import requests

conn = None
cur = None
engine = create_engine(
    'postgresql://xpdmcctztuueoj:5c6b0ce73d0e1d7a8b7ea13688df6b7268edd3e85ddc1ba488a8e233759731d2@ec2-34-241-82-91.eu-west-1.compute.amazonaws.com:5432/d6i1k6lrk3j39n')


def techstack_research(rp, uniqueID):
    keys = ["technologies"]
    r_filtered = {x: rp[x] for x in keys}
    techstackDf = pd.DataFrame.from_dict(r_filtered)


