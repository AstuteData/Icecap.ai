import pandas as pd
from sqlalchemy import create_engine, text
import uuid
import requests
import json
from time import sleep
from scrapers import articlescraper

conn = None
cur = None
engine = create_engine(
    'postgresql://xpdmcctztuueoj:5c6b0ce73d0e1d7a8b7ea13688df6b7268edd3e85ddc1ba488a8e233759731d2@ec2-34-241-82-91.eu-west-1.compute.amazonaws.com:5432/d6i1k6lrk3j39n')

try:
    with engine.connect() as conn:
        company_select = text('SELECT * FROM "CompanyData"')
        company_data = pd.read_sql_query(company_select, conn)
        company_data.drop(columns='index')

        prospect_select = text('SELECT * FROM "ProspectData"')
        prospect_data = pd.read_sql_query(prospect_select, conn)
        prospect_data.drop(columns='index')
except Exception as error:
    print("An exception has occurred:", error)
    company_data = pd.Dataframe(columns=['domain'])
    prospect_data = pd.Dataframe(columns=['linkedin_profile'])
    pass


def start_research(upload_data):
    # Organising the json from upload_data
    domain_header = upload_data['website header']
    linkedin_profile_header = upload_data['linkedin profile header']
    csv_data = pd.DataFrame.from_dict(upload_data['csv'])
    companies_to_research = []

    # Researching the company and prospect starts here
    for index in csv_data.index:
        domain = (csv_data[domain_header][index])
        linkedin_profile = (csv_data[linkedin_profile_header][index])

        if domain not in companies_to_research and domain not in company_data['domain'].values:
            companies_to_research.append(domain)
            unique_company_identifier = uuid.uuid4()
            company_scraping(domain, unique_company_identifier)
            articlescraper.link_scraper(domain, unique_company_identifier)

        else:
            if linkedin_profile not in prospect_data['linkedin_profile'].values:
                unique_prospect_identifier = uuid.uuid4
                prospect_scraping(linkedin_profile, unique_prospect_identifier)
            else:
                continue


def company_scraping(domain, unique_company_identifier):
    # Fetching data from TheCompaniesAPI API and storing it.
    try:
        company_data_response = requests.get(f"https://api.thecompaniesapi.com/v1/companies/{domain}",
                         headers={'Authorization': 'basic EvGVkI4x'})
        company_data_json = company_data_response.json()
        keys = ['name', 'domainName', 'domain', 'description', 'descriptionShort', 'industryMain', 'revenue',
                'totalEmployees', 'logo', 'technologies', 'technologyCategories']
        company_data_with_keys = {data: company_data_json[data] for data in keys}

        researched_company = pd.DataFrame.from_dict([company_data_with_keys])
        researched_company['unique_identifier'] = [unique_company_identifier]
        researched_company.to_sql(f'CompanyData', con=engine, if_exists='append')
    except:
        pass


def prospect_scraping(linkedin_profile, unique_prospect_identifier):
        # Scraping-bot API request to scrape the specified LinkedIn profile via their LinkedIn URL
        username = 'jackwhitehouse'
        apiKey = 'jagu6xaIGs2z3cWZSWniNjSBq'
        scraper = 'linkedinProfile'
        url = linkedin_profile

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

        prospect_data_json = r.json()
        keys = ['url', 'name', 'position', 'current_company', 'experience', 'city', 'about', 'recommendations',
                'recommendations_count', 'education_details', 'posts', 'certifications', 'publications', 'activities',
                'avatar', 'people_also_viewed']
        prospect_data_with_keys = {data: prospect_data_json[data] for data in keys}

        # Storing the scraped data
        researched_prospect = pd.DataFrame.from_dict([prospect_data_with_keys])
        researched_prospect['unique_identifier'] = [unique_prospect_identifier]
        researched_prospect.to_sql(f'ProspectData', con=engine, if_exists='append')

