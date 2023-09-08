import pandas as pd
from sqlalchemy import create_engine, text
import uuid
import requests
import json
from time import sleep
from scrapers import companyscraper, articlescraper, prospectscraper, hiringscraperrw
from ai import articleai, prospectai, hiringai, contextualiseai
from bs4 import BeautifulSoup

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
    company_data = pd.DataFrame(columns=['domain'])
    prospect_data = pd.DataFrame(columns=['linkedin_profile'])
    pass


def start_research(upload_data):
    # Organising the json from upload_data
    name_header = upload_data['full name']
    position_header = upload_data['position']
    domain_header = upload_data['website header']
    linkedin_profile_header = upload_data['linkedin profile header']
    csv_data = pd.DataFrame.from_dict(upload_data['csv'])
    companies_to_research = {}

    # Researching the company and prospect starts here
    for ind in csv_data.index:
        name = (csv_data[name_header][ind])
        position = (csv_data[position_header][ind])
        domain = (csv_data[domain_header][ind])
        linkedin_profile = (csv_data[linkedin_profile_header][ind])

        # Logic to determine if the company and prospect have been previously scraped.
        company_already_exists = (domain in companies_to_research or domain in company_data['domain'].values)
        prospect_already_exists = (linkedin_profile in prospect_data['linkedin_profile'].values)

        if company_already_exists is True and prospect_already_exists is True:
            pass

        elif company_already_exists is True and prospect_already_exists is False:
            focus = 0
            save_focus = 0
            unique_prospect_identifier = uuid.uuid4
            unique_company_identifier = company_data['company identifier'][ind]
            scrape_prospects = prospectscraper.prospect_scraping(name, position, linkedin_profile, unique_prospect_identifier, unique_company_identifier)
            scrape_company, scrape_articles, scrape_hiring = None, None, None

            if scrape_prospects['status'] == "success":
                saving = True
                while saving is True:
                    save_response = save_data(save_focus, scrape_company, scrape_articles, scrape_hiring, scrape_prospects, unique_company_identifier)
                    if save_response == "Saving complete":
                        saving = False
                ai_research_response, save_focus = ai_analysis_scraped_data(unique_company_identifier, focus)
            else:
                print("Scraping not successful")

        elif company_already_exists is False and prospect_already_exists is False:
            focus = 1
            save_focus = 1
            unique_company_identifier = uuid.uuid4()
            unique_prospect_identifier = uuid.uuid4()

            # Running the scraping functions. Need to extract the company LinkedIn URL to run the hiring scraper.
            scrape_company = companyscraper.company_scraping(domain, unique_company_identifier)
            scrape_articles = articlescraper.link_scraper(domain, unique_company_identifier)
            company_linkedin_url = scrape_company['socialNetworks']['linkedin']
            scrape_prospects = prospectscraper.prospect_scraping(name, position, linkedin_profile, unique_prospect_identifier, unique_company_identifier)
            scrape_hiring = hiringscraperrw.hiring_scraping(company_linkedin_url)

            status_checked = False
            while scrape_company and scrape_articles and scrape_prospects and scrape_hiring is not None and status_checked is False:
                scraped_company_status = scrape_company['status']
                scraped_articles_status = scrape_articles['status']
                scraped_prospects_status = scrape_prospects['status']
                if scraped_prospects_status and scraped_articles_status and scraped_company_status == "success":
                    print("success")
                    status_checked = True
                elif scraped_prospects_status and scraped_articles_status and scraped_company_status != "success":
                    print("not all successful")

            newly_researched_company = {domain: unique_company_identifier}
            companies_to_research.update(newly_researched_company)
            save_response = save_data(save_focus, scrape_company, scrape_articles, scrape_hiring, scrape_prospects, unique_company_identifier)
            ai_research_response = ai_analysis_scraped_data(unique_company_identifier, focus)


def save_data(save_focus, scrape_company, scrape_articles, scrape_hiring, scrape_prospects, unique_company_identifier):
    if save_focus == 0:
        upload = pd.DataFrame.from_dict(scrape_prospects)
        upload.to_sql(f'Prospect', con=engine, if_exists='append')
        return "Saving complete"
    elif save_focus == 1:
        prospect_upload = pd.DataFrame.from_dict(scrape_prospects)
        prospect_upload.to_sql(f'Prospect', con=engine, if_exists='append')

        company_upload = pd.DataFrame.from_dict(scrape_company)
        company_upload['Articles'], company_upload['Hiring Roles'], company_upload['Company ID'] = [scrape_articles, scrape_hiring, unique_company_identifier]
        return "Saving complete"
    elif save_focus == 2:
        # Save only prospect ai results.
    elif save_focus == 3:
        # Save company and prospect ai results.


def ai_analysis_scraped_data(unique_company_identifier, focus):
    if focus == 0:
        prospect_analysis = prospectai.start_prospect_ai(unique_company_identifier)
        save_focus = 2

        if prospect_analysis['status'] == 'success':
            contextualisation = contextualiseai.start_contextualisation_ai(unique_company_identifier)
            if contextualisation['status'] == "success":
                print("do whatever happens after the contextualisation ai has successfully finished executing")
                save_focus = 3
            else:
                print("contextualisation analysis failure")
        elif prospect_analysis['status'] != 'success':
            print("status failure")

    elif focus == 1:
        hiring_analysis = hiringai.start_hiring_ai(unique_company_identifier)
        article_analysis = articleai.start_article_ai(unique_company_identifier)
        prospect_analysis = prospectai.start_prospect_ai(unique_company_identifier)

        status_checked = False
        status_success = False
        while hiring_analysis and article_analysis and prospect_analysis is not None and status_checked is False:
            hiring_analysis_status = hiring_analysis['status']
            articles_analysis_status = article_analysis['status']
            prospects_analysis_status = prospect_analysis['status']
            if hiring_analysis_status and articles_analysis_status and prospects_analysis_status == 'success':
                status_checked = True
                status_success = True
            elif hiring_analysis_status and articles_analysis_status and prospects_analysis_status != 'success':
                print("not all successful")

        if status_success is True:
            contextualisation = contextualiseai.start_contextualisation_ai(unique_company_identifier)
            if contextualisation == "Summary complete":
                print("do whatever happens after the contextualisation ai has successfully finished executing")
                save_focus = 3
            else:
                pass


def ai_analysis_contextualisation():
    # Notes so that I do not forget what to do tomorrow morning.
    # Pass the unsaved AI analysis' into this function.
    # Figure out how to loop through the relevant data correctly and create prompts off the back of this.
    # Return the data to this function.
    # Return this data to the previous function, then back to the core function.
    # Pass the data into the save_data function and save the data.
    # This includes the hiring_analysis, article_analysis, prospect_analysis and contextualisation piece.

