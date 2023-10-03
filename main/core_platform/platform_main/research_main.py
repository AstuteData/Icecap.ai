from sqlalchemy import create_engine, text
import uuid
import json
import multiprocessing
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


def run_mainframe(upload_data):
    domain_header = upload_data['website header']
    prospect_linkedin_profile_header = upload_data['linkedin profile header']
    company_linkedin_url_header = upload_data['company linkedin profile header']
    csv_data = pd.DataFrame.from_dict(upload_data['csv'])
    companies_to_research = {}

    for ind in csv_data.index:
        domain = (csv_data[domain_header][ind])
        li_prospect_linkedin_url = (csv_data[prospect_linkedin_profile_header][ind])
        li_company_linkedin_url = (csv_data[company_linkedin_url_header][ind])

        # Logic to determine if the company and prospect have been previously scraped.
        company_already_exists = (domain in companies_to_research or domain in company_data['domain'].values)
        prospect_already_exists = (li_prospect_linkedin_url in prospect_data['linkedin_profile'].values)

        if company_already_exists is True and prospect_already_exists is True:
            print("Company and prospect already exist.")
            pass

        elif company_already_exists is True and prospect_already_exists is False:


            prospect_id = uuid.uuid4()
            prospect = proxycurl_prospect.run_proxycurl(company_id, prospect_id, li_prospect_linkedin_url)
            print("Company already exists, prospect does not.")

        else:
            print("Company and prospect do not exist.")
            company_id = uuid.uuid4()
            prospect_id = uuid.uuid4()

            company_scraping_complete = proxycurl_company.run_proxycurl(company_id, li_company_linkedin_url)
            cs_status = company_scraping_complete['Status']
            search_id = company_scraping_complete['Search ID']

            if cs_status == 'Success':
                articles = multiprocessing.Process(target=article_scraper.url_search, args=(domain, company_id))
                prospect = multiprocessing.Process(target=proxycurl_prospect.run_proxycurl, args=(prospect_id, li_prospect_linkedin_url, company_id))

                if __name__ == '__main__':
                    articles.start()
                    prospect.start()

                    articles.join()
                    prospect.join()

                hiring = proxycurl_hiring.run_proxycurl(company_id, search_id)
                job_list = hiring['Job List']
                job_scraping_complete = proxycurl_jobs.run_proxycurl(job_list, company_id)
                if job_scraping_complete['Status'] == 'Success':
                    print("Next part of the app.")
            else:
                print("Something went wrong.")
