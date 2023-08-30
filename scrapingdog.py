import requests
import json
from time import sleep
import pandas as pd
from sqlalchemy import create_engine, text

def research_prospect():
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
            finalResponse = requests.request("GET", apiEndPointResponse + "scraper=" + scraper + "&responseId=" + responseId
                                             , auth=(username, apiKey))
            result = finalResponse.json()
            if type(result) is list:
                pending = False
                print(finalResponse.text)
                a = result
                b = a[0]
                print(a)
                print(b)
            elif type(result) is dict:
                if "status" in result and result["status"] == "pending":
                    print(result["message"])
                    continue
                elif result["error"] is not None:
                    pending = False
                    print(json.dumps(result, indent=4))

    else:
        print(response.text)

research_prospect()