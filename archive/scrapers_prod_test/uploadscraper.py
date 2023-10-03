import pandas as pd
from sqlalchemy import create_engine, text
import uuid
from archive.scrapers_prod_test import prospectscraper, hiringscraperrw
from main.general_scrapers import companyscraper
from archive import articlescraperrw
from ai_prod_test import articleai, prospectai, hiringai, contextualiseai

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
    prospect_linkedin_profile_header = upload_data['linkedin profile header']
    company_linkedin_url_header = upload_data['company linkedin profile header']
    csv_data = pd.DataFrame.from_dict(upload_data['csv'])
    companies_to_research = {}

    # Researching the company and prospect starts here
    for ind in csv_data.index:
        name = (csv_data[name_header][ind])
        position = (csv_data[position_header][ind])
        domain = (csv_data[domain_header][ind])
        prospect_linkedin_profile = (csv_data[prospect_linkedin_profile_header][ind])
        company_linkedin_profile = (csv_data[company_linkedin_url_header][ind])

        # Logic to determine if the company and prospect have been previously scraped.
        company_already_exists = (domain in companies_to_research or domain in company_data['domain'].values)
        prospect_already_exists = (prospect_linkedin_profile in prospect_data['linkedin_profile'].values)

        if company_already_exists is True and prospect_already_exists is True:
            pass

        elif company_already_exists is True and prospect_already_exists is False:
            prospect_id = uuid.uuid4
            filtered_cd_index = company_data[company_data.domain == domain].index[0]
            company_id = company_data['company identifier'][filtered_cd_index]

        elif company_already_exists is False and prospect_already_exists is False:
            unique_company_identifier = uuid.uuid4()
            unique_prospect_identifier = uuid.uuid4()


def ai_analysis_scraped_data(unique_company_identifier, focus):
    if focus == 0:
        save_focus = 0
        hiring_analysis, article_analysis = None, None
        prospect_analysis = prospectai.start_prospect_ai(unique_company_identifier)

        if prospect_analysis['status'] == 'success':
            contextualisation = contextualiseai.start_contextualisation_ai(focus, hiring_analysis, article_analysis, prospect_analysis)
            if contextualisation['status'] == "success":
                print("do whatever happens after the contextualisation ai has successfully finished executing")

            else:
                print("contextualisation analysis failure")
        elif prospect_analysis['status'] != 'success':
            print("status failure")

    elif focus == 1:
        hiring_analysis = hiringai.start_hiring_ai(unique_company_identifier)
        article_analysis = articleai.start_article_ai(unique_company_identifier)
        prospect_analysis = prospectai.start_prospect_ai(unique_company_identifier)
        save_focus = 1

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
            contextualisation = ai_analysis_contextualisation(focus, hiring_analysis, article_analysis, prospect_analysis)


def ai_analysis_contextualisation(focus, hiring_analysis, article_analysis, prospect_analysis):
    if focus == 0:
        save_focus = 2
        query_company_data = company_data.query("company_identifier == @unique_company_identifier")

        hiring_analysis_response = query_company_data['Hiring Analysis']
        article_analysis_response = query_company_data['Articles Analysis']
        prospect_analysis_response = prospect_analysis['response']

        contextualisation = contextualiseai.start_contextualisation_ai(focus, prospect_analysis_response, article_analysis_response, hiring_analysis_response)
    elif focus == 1:
        save_focus = 3
        hiring_analysis_response = hiring_analysis['response']
        article_analysis_response = article_analysis['response']
        prospect_analysis_response = prospect_analysis['response']

        contextualisation = contextualiseai.start_contextualisation_ai(focus, hiring_analysis_response, article_analysis_response, prospect_analysis_response)



def save_scraped_data(save_focus, scrape_company, scrape_articles, scrape_hiring, scrape_prospects, unique_company_identifier):
    if save_focus == 0:
        upload = pd.DataFrame.from_dict(scrape_prospects)
        upload.to_sql(f'Prospect', con=engine, if_exists='append')
        return "Saving complete"
    elif save_focus == 1:
        prospect_upload = pd.DataFrame.from_dict(scrape_prospects)
        prospect_upload.to_sql(f'Prospect', con=engine, if_exists='append')

        company_upload = pd.DataFrame.from_dict(scrape_company)
        company_upload['Articles'], company_upload['Hiring'], company_upload['Company ID'] = scrape_articles, scrape_hiring, unique_company_identifier
        company_upload['Hiring Analysis'], company_upload['Article Analysis'] = None, None
        return "Saving complete"


def save_ai_analysis(save_focus, hiring_analysis, article_analysis, prospect_analysis):
    if save_focus == 0:
        upload = pd.DataFrame.from_dict(scrape_prospects)
        upload.to_sql(f'Prospect', con=engine, if_exists='append')
        return "Saving complete"
    elif save_focus == 1:
        prospect_upload = pd.DataFrame.from_dict(scrape_prospects)
        prospect_upload.to_sql(f'Prospect', con=engine, if_exists='append')

        company_upload = pd.DataFrame.from_dict(scrape_company)
        company_upload['Articles'], company_upload['Hiring Roles'], company_upload['Company ID'] = scrape_articles, scrape_hiring, unique_company_identifier
        company_upload['Hiring Analysis'], company_upload['Article Analysis'] = None, None
        return "Saving complete"