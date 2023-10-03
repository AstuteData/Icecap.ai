
from sqlalchemy import create_engine, text
import uuid
import json
import pandas as pd
import sys
sys.path.append('../')
from main.proxycurl_scrapers import proxycurl_company, proxycurl_jobs, proxycurl_hiring, proxycurl_prospect
from main.general_scrapers import article_scraper

conn = None
cur = None
engine = create_engine('postgresql://xpdmcctztuueoj:5c6b0ce73d0e1d7a8b7ea13688df6b7268edd3e85ddc1ba488a8e233759731d2'
                       '@ec2-34-241-82-91.eu-west-1.compute.amazonaws.com:5432/d6i1k6lrk3j39n')

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
    company_data = pd.DataFrame(columns=['domain'])
    prospect_data = pd.DataFrame(columns=['linkedin_profile'])
    pass


def format_csv(upload_data):
    name_header = upload_data['full name']
    position_header = upload_data['position']
    domain_header = upload_data['website header']
    prospect_linkedin_profile_header = upload_data['linkedin profile header']
    company_linkedin_url_header = upload_data['company linkedin profile header']
    csv_data = pd.DataFrame.from_dict(upload_data['csv'])
    companies_to_research = {}

    for ind in csv_data.index:
        name = (csv_data[name_header][ind])
        position = (csv_data[position_header][ind])
        domain = (csv_data[domain_header][ind])
        li_prospect_linkedin_url = (csv_data[prospect_linkedin_profile_header][ind])
        li_company_linkedin_url = (csv_data[company_linkedin_url_header][ind])

        # Logic to determine if the company and prospect have been previously scraped.
        company_already_exists = (domain in companies_to_research or domain in company_data['domain'].values)
        prospect_already_exists = (li_prospect_linkedin_url in prospect_data['linkedin_profile'].values)

        if company_already_exists is True and prospect_already_exists is True:
            pass

        elif company_already_exists is True and prospect_already_exists is False:


def scrape_data(li_company_linkedin_url, company_id, company_url):
    company_scraping_complete = proxycurl_company.run_proxycurl(company_id, li_company_linkedin_url)
    cs_status = company_scraping_complete['Status']
    search_id = company_scraping_complete['Search ID']

    hiring_scraping_complete = proxycurl_hiring.run_proxycurl(company_id, search_id)
    hs_status = hiring_scraping_complete['Status']
    job_list = hiring_scraping_complete['Job List']

    job_scraping_complete = proxycurl_jobs.run_proxycurl(job_list, company_id)
    js_status = job_scraping_complete['Status']

    article_scraping_complete = article_scraper.url_search(company_url, company_id)
    as_status = article_scraping_complete['Status']

    prospect_scraping_complete = proxycurl_prospect.run_proxycurl(prospect_id, li_prospect_profile_url, search_id)
    ps_status = prospect_scraping_complete['Status']

    if cs_status == 'Success' and hs_status == 'Success' and js_status == 'Success' and as_status == 'Success' and ps_status == 'Success':
        print("Next part of the app.")
    else:
        print("Something went wrong.")
        print("CS Status: " + cs_status)
        print("HS Status: " + hs_status)
        print("JS Status: " + js_status)
        print("AS Status: " + as_status)
        print("PS Status: " + ps_status)



