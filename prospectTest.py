import pandas as pd
from sqlalchemy import create_engine, text
import uniqueIDfunc
import requests
import json
from time import sleep

conn = None
cur = None
engine = create_engine(
    'postgresql://xpdmcctztuueoj:5c6b0ce73d0e1d7a8b7ea13688df6b7268edd3e85ddc1ba488a8e233759731d2@ec2-34-241-82-91.eu-west-1.compute.amazonaws.com:5432/d6i1k6lrk3j39n')


def upload_prospects(importrequest):
    reff = pd.json_normalize(importrequest)
    df = pd.DataFrame(data=reff)

    for ind in df.index:
        linkedinLink = (df['LinkedIn Account Url'][ind])
        currentProspect = (df['Prospect Name'][ind])

        try:
            with engine.connect() as conn:
                select = text('SELECT * FROM "ProspectData"')
                postgresProspectDf = pd.read_sql_query(select, conn)
                postgresProspectDf = postgresProspectDf.drop(columns='index')
                conn.close()

            prospectCheck = currentProspect in postgresProspectDf['originalCompanyName'].values
        except:
            prospectCheck = False

        if prospectCheck:
            locateIndex = postgresProspectDf.loc[df.isin([currentProspect]).any(axis=1)].index.tolist()
            prospectID = postgresProspectDf.loc[locateIndex[0], 'ProspectID']
            prospect_search(linkedinLink, currentProspect, prospectCheck, prospectID)

        else:
            prospectID = uniqueIDfunc.uniqueProspectID()
            prospect_search(linkedinLink, currentProspect, prospectCheck, prospectID)

def prospect_search(linkedinLink, currentProspect, prospectCheck, prospectID):
    if prospectCheck:
            ''' this function is the response for if the prospect already exists in the db '''
    else:
        username = 'jackwhitehouse'
        apiKey = 'jagu6xaIGs2z3cWZSWniNjSBq'
        scraper = 'linkedinProfile'
        url = linkedinLink

        apiEndPoint = "http://api.scraping-bot.io/scrape/data-scraper"
        apiEndPointResponse = "http://api.scraping-bot.io/scrape/data-scraper-response?"

        payload = json.dumps({"url": url, "scraper": scraper})
        headers = {
            'Content-Type': "application/json"
        }

        response = requests.request("POST", apiEndPoint, data=payload, auth=(username, apiKey), headers=headers)
        if response.status_code == 200:
            print(response.json())
            print(response.json()["responseId"])
            responseId = response.json()["responseId"]

            pending = True
            while pending:
                sleep(5)
                finalResponse = requests.request("GET",
                                                 apiEndPointResponse + "scraper=" + scraper + "&responseId=" + responseId
                                                 , auth=(username, apiKey))
                result = finalResponse.json()
                if type(result) is list:
                    pending = False
                    r = finalResponse.json()
                elif type(result) is dict:
                    if "status" in result and result["status"] == "pending":
                        print(result["message"])
                        continue
                    elif result["error"] is not None:
                        pending = False
                        print(json.dumps(result, indent=4))
        else:
            print(response.text)

        rp = r
        keys = ['url', 'name', 'position', 'current_company', 'experience', 'city', 'about', 'recommendations',
                'recommendations_count', 'education_details', 'posts', 'certifications', 'publications', 'activities',
                'avatar', 'people_also_viewed']

        r_filtered = {x: rp[x] for x in keys}
        df = pd.DataFrame.from_dict([r_filtered])
        df['ProspectID'] = prospectID
        df['ResearchStatus'] = None
        df.to_sql(f'CompanyData', con=engine, if_exists='append')