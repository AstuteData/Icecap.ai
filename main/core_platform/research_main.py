from sqlalchemy import create_engine, text
import uuid
import pandas as pd
import sys
import json

sys.path.append('../proxycurl_scrapers')
sys.path.append('../general_scrapers')
from main.proxycurl_scrapers import proxycurl_hiring, proxycurl_company, proxycurl_prospect
from main.general_scrapers import article_scraper
from main.ai import company_ai, prospect_ai

conn = None
cur = None
engine = create_engine('postgresql://xpdmcctztuueoj:5c6b0ce73d0e1d7a8b7ea13688df6b7268edd3e85ddc1ba488a8e233759731d2'
                       '@ec2-34-241-82-91.eu-west-1.compute.amazonaws.com:5432/d6i1k6lrk3j39n')

user_id = 1
# 1. Save user ID

# 2. Check for date of last research attempt. If within a week, don't research the company.
#   If not, research the company and save the date of the research attempt.

# 3. Check for date of last prospect research attempt. If within a week, don't research the prospect.
#   If not, research the prospect and save the date of the research attempt.

# 4. Create login and register backend. Save user ID to database.
try:
    with engine.connect() as conn:
        company = text('SELECT * FROM "company"')
        company_data = pd.read_sql_query(company, conn)
        company_data.drop(columns='index')

        prospect = text('SELECT * FROM "prospect"')
        prospect_data = pd.read_sql_query(prospect, conn)
        prospect_data.drop(columns='index')
except Exception as e:
    print(e)
    print("Error in research_main.py. Could not connect to database")
    company_data = pd.DataFrame()
    prospect_data = pd.DataFrame()
    prospect_data['li_prospect_profile_url'] = None


def check_against_database(upload_data):
    # user_id = upload_data['user id']
    domain_header = upload_data['domain header']
    prospect_linkedin_profile_header = upload_data['prospect linkedin profile header'] # Change on front end to prospect linkedin profile header
    company_linkedin_url_header = upload_data['company linkedin profile header']
    csv_data = pd.DataFrame.from_dict(upload_data['csv'])
    researched_prospects = []
    researched_companies = []
    print(domain_header)
    print(prospect_linkedin_profile_header)
    print(company_linkedin_url_header)

    for ind in csv_data.index:
        domain = csv_data[domain_header].values[ind]
        li_prospect_profile_url = csv_data[prospect_linkedin_profile_header].values[ind]
        li_company_profile_url = csv_data[company_linkedin_url_header].values[ind]

        print(domain)
        print(li_prospect_profile_url)
        print(li_company_profile_url)

        # prospect_already_researched = (li_prospect_profile_url in prospect_data['li_prospect_profile_url']
                                       #or li_prospect_profile_url in researched_prospects)
        #company_already_researched = (company_data[company_data['domain'] == domain]
                                      #or domain in researched_companies)

        prospect_already_researched = False
        company_already_researched = False

        research_r = research(li_prospect_profile_url, li_company_profile_url, domain,
                 prospect_already_researched, company_already_researched, user_id)

        if research_r == "Company and Prospect Research Successful":
            researched_prospects.append(li_prospect_profile_url)
            researched_companies.append(domain)
        elif research_r == "Prospect Research Successful":
            researched_prospects.append(li_prospect_profile_url)
        else:
            print("Research Failed")
            print(research_r)
            return "Research Failed"

    return "Research Complete"


def research(li_prospect_profile_url, li_company_profile_url, domain,
             prospect_already_researched, company_already_researched, user_id):

    if prospect_already_researched is False and company_already_researched is False:
        print("Company and prospect do not exist.")
        company_id = uuid.uuid4()
        prospect_id = uuid.uuid4()
        research_id = uuid.uuid4()

        company_scraping_complete = proxycurl_company.run_proxycurl(company_id, li_company_profile_url, research_id, user_id)
        cs_status = company_scraping_complete['Status']
        search_id = company_scraping_complete['Search ID']

        if cs_status == 'Success':
            attempts = 0
            while attempts < 3:
                try:
                    article = article_scraper.url_search(domain, company_id, research_id, user_id)
                    prospect = proxycurl_prospect.run_proxycurl(prospect_id, li_prospect_profile_url, company_id, research_id, user_id)
                    hiring = proxycurl_hiring.run_proxycurl(company_id, search_id, research_id, user_id)

                    prospect_ai.start_ai(research_id)
                    company_ai.start_ai(research_id)
                    break
                except Exception as error:
                    print(error)
                    attempts += 1

            if attempts != 3:
                print("Company and Prospect Research Successful")
                return "Company and Prospect Research Successful"
            else:
                print("Company and Prospect research failed. Too many research attempts")
                return "Company and Prospect Research Failed"
        else:
            print("Company research unsuccessful. Could not research prospect.")

    elif prospect_already_researched is False and company_already_researched is True:
        company_row = company_data[company_data['domain'] == domain]
        company_id = company_row['company_id'].values[0]
        prospect_id = uuid.uuid4()
        research_id = uuid.uuid4()

        attempts = 0
        while attempts < 3:
            try:
                prospect_r = proxycurl_prospect.run_proxycurl(prospect_id, li_prospect_profile_url, company_id, research_id, user_id)
                prospect_ai_r = prospect_ai.start_ai(research_id)
                print("Prospect research and ai successful")
                break
            except Exception as error:
                print(f"Error in prospect only research: \n {error}")
                attempts += 1

        if attempts != 3:
            print("Prospect Research Successful")
            return "Prospect Research Successful"
        else:
            print("Prospect research failed. Too many prospect research attempts")
            return "Prospect Research Failed"
