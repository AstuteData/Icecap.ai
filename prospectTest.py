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


def prospect_search():
    username = 'jackwhitehouse'
    apiKey = 'jagu6xaIGs2z3cWZSWniNjSBq'
    scraper = 'linkedinProfile'
    url = 'https://www.linkedin.com/in/jackwhitehouse/'

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
                print(r)
                print(result)
                print(finalResponse)
            elif type(result) is dict:
                if "status" in result and result["status"] == "pending":
                    print(result["message"])
                    continue
                elif result["error"] is not None:
                    pending = False
                    print(json.dumps(result, indent=4))
    else:
        print(response.text)

prospect_search()