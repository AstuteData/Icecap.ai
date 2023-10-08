from sqlalchemy import create_engine
import uuid
import pandas as pd
import sys

sys.path.append('../proxycurl_scrapers')
sys.path.append('../general_scrapers')
from main.proxycurl_scrapers import proxycurl_hiring, proxycurl_company, proxycurl_prospect
from main.general_scrapers import article_scraper
from main.ai import company_ai, prospect_ai

conn = None
cur = None
engine = create_engine('postgresql://xpdmcctztuueoj:5c6b0ce73d0e1d7a8b7ea13688df6b7268edd3e85ddc1ba488a8e233759731d2'
                       '@ec2-34-241-82-91.eu-west-1.compute.amazonaws.com:5432/d6i1k6lrk3j39n')


def run_mainframe(upload_data):
    domain_header = upload_data['website header']
    prospect_linkedin_profile_header = upload_data['linkedin profile header']
    company_linkedin_url_header = upload_data['company linkedin profile header']
    csv_data = pd.DataFrame.from_dict(upload_data['csv'])
    researched_companies = {}
    research_ids = []

    for ind in csv_data.index:
        domain = (csv_data[domain_header][ind])
        li_prospect_linkedin_url = (csv_data[prospect_linkedin_profile_header][ind])
        li_company_linkedin_url = (csv_data[company_linkedin_url_header][ind])

        print("Company and prospect do not exist.")
        li_company_profile_url = "https://www.linkedin.com/company/rivery/"
        li_prospect_profile_url = "https://www.linkedin.com/in/jackwhitehouse/"
        domain = "rivery.io"
        print("Company and prospect do not exist.")
        company_id = uuid.uuid4()
        prospect_id = uuid.uuid4()
        research_id = uuid.uuid4()

        company_scraping_complete = proxycurl_company.run_proxycurl(company_id, li_company_linkedin_url, research_id)
        cs_status = company_scraping_complete['Status']
        search_id = company_scraping_complete['Search ID']

        if cs_status == 'Success':
            article = article_scraper.url_search(domain, company_id, research_id)
            prospect = proxycurl_prospect.run_proxycurl(prospect_id, li_prospect_profile_url, company_id,
                                                        research_id)
            hiring = proxycurl_hiring.run_proxycurl(company_id, search_id, research_id)
        else:
            print("Something went wrong.")

        research_ids.append(research_id)
        prospect_ai.start_ai(research_id)
        company_ai.start_ai(research_id)

    return "Research complete"


def test():
    research_ids = []

    print("Company and prospect do not exist.")
    li_company_profile_url = "https://www.linkedin.com/company/rivery/"
    li_prospect_profile_url = "https://www.linkedin.com/in/jackwhitehouse/"
    domain = "rivery.io"
    print("Company and prospect do not exist.")
    company_id = uuid.uuid4()
    prospect_id = uuid.uuid4()
    research_id = uuid.uuid4()

    company_scraping_complete = proxycurl_company.run_proxycurl(company_id, li_company_profile_url, research_id)
    cs_status = company_scraping_complete['Status']
    search_id = company_scraping_complete['Search ID']

    if cs_status == 'Success':
        article = article_scraper.url_search(domain, company_id, research_id)
        prospect = proxycurl_prospect.run_proxycurl(prospect_id, li_prospect_profile_url, company_id,
                                                    research_id)
        hiring = proxycurl_hiring.run_proxycurl(company_id, search_id, research_id)
    else:
        print("Something went wrong.")

    research_ids.append(str(research_id))
    print(research_ids)
    prospect_ai.start_ai(str(research_id))
    company_ai.start_ai(str(research_id))


test()