import pandas as pd
from sqlalchemy import create_engine, text
import uniqueIDfunc
import requests

conn = None
cur = None
engine = create_engine(
    'postgresql://xpdmcctztuueoj:5c6b0ce73d0e1d7a8b7ea13688df6b7268edd3e85ddc1ba488a8e233759731d2@ec2-34-241-82-91.eu-west-1.compute.amazonaws.com:5432/d6i1k6lrk3j39n')


def upload_list(testone, testtwo):
    t1 = pd.read_json(testone)
    t2 = pd.read_json(testtwo)
    df = pd.concat([t1, t2], axis=1, join='inner')

    for ind in df.index:
        linkedinLink = (df['LinkedIn URL'][ind])
        currentCompany = (df['Company Name'][ind])

        try:
            with engine.connect() as conn:
                select = text('SELECT * FROM "CompanyData"')
                df1 = pd.read_sql_query(select, conn)
                df1 = df1.drop(columns='index')
                conn.close()

            companyCheck = currentCompany in df1['originalCompanyName'].values
        except:
            companyCheck = False

        if companyCheck:
            locateIndex = df1.loc[df.isin([currentCompany]).any(axis=1)].index.tolist()
            uniqueID = df1.loc[locateIndex[0], 'UniqueID']
            company_search(linkedinLink, currentCompany, companyCheck, uniqueID)

        else:
            uniqueID = uniqueIDfunc.uniqueID()
            company_search(linkedinLink, currentCompany, companyCheck, uniqueID)


def company_search(linkedinLink, currentCompany, companyCheck, uniqueID):
    print("Company search")
    if companyCheck:
        with engine.connect() as conn:
            select = text('SELECT * FROM "CompanyData"')
            df = pd.read_sql_query(select, conn)
            df = df.drop(columns='index')
            locateIndex = df.loc[df.isin([currentCompany]).any(axis=1)].index.tolist()
            df = df.loc[[locateIndex[0]]]
            conn.close()

    else:
        r = requests.get(f"https://api.thecompaniesapi.com/v1/companies/by-social?linkedin={linkedinLink}",
                                headers={'Authorization': 'basic EvGVkI4x'})
        rp = r.json()
        keys = ['domainName', 'domain', 'domainTld', 'description', 'industryMain', 'monthlyVisitors', 'revenue', 'totalEmployees', 'yearFounded']
        r_filtered = {x: rp[x] for x in keys}
        df = pd.DataFrame.from_dict([r_filtered])
        df['UniqueID'] = uniqueID
        df['originalCompanyName'] = currentCompany
        df.to_sql(f'CompanyData', con=engine, if_exists='append')
