import pandas as pd
from sqlalchemy import create_engine
import uuid
import json
from scrapers_prod_test import prospectscraper, hiringscraperrw
from main.general_scrapers import companyscraper, articlescraperrw
from ai_prod_test import articleai, prospectai, hiringai, contextualiseai
import pprint as pp

conn = None
cur = None
engine = create_engine(
    'postgresql://xpdmcctztuueoj:5c6b0ce73d0e1d7a8b7ea13688df6b7268edd3e85ddc1ba488a8e233759731d2@ec2-34-241-82-91.eu-west-1.compute.amazonaws.com:5432/d6i1k6lrk3j39n')


def start_research(upload_data):
    # Organising the json from upload_data
    # name_header = upload_data['full name']
    # position_header = upload_data['position']
    # domain_header = upload_data['website header']
    # prospect_linkedin_profile_header = upload_data['linkedin profile header']
    # company_linkedin_url_header = upload_data['company linkedin profile header']
    # csv_data = pd.DataFrame.from_dict(upload_data['csv'])
    companies_to_research = []

    # Researching the company and prospect starts here
    # for ind in csv_data.index:
    # name = (csv_data[name_header][ind])
    # position = (csv_data[position_header][ind])
    # domain = (csv_data[domain_header][ind])
    # prospect_linkedin_profile = (csv_data[prospect_linkedin_profile_header][ind])
    # company_linkedin_profile = (csv_data[company_linkedin_url_header][ind])

    # Logic to determine if the company and prospect have been previously scraped.
    # company_already_exists = (domain in companies_to_research or domain in company_data['domain'].values)
    # prospect_already_exists = (prospect_linkedin_profile in prospect_data['linkedin_profile'].values)

    name = "Jack Whitehouse"
    position = "SDR"
    domain = "Rivery.io"
    prospect_linkedin_profile = "https://www.linkedin.com/in/jackwhitehouse/"
    company_linkedin_profile = "https://www.linkedin.com/company/rivery/"

    for i in range(1):
        company_already_exists = False
        prospect_already_exists = False

        if company_already_exists is True and prospect_already_exists is True:
            pass

        elif company_already_exists is True and prospect_already_exists is False:
            pass
            # focus = 0
            # save_focus = 0
            # unique_prospect_identifier = uuid.uuid4
            # unique_company_identifier = company_data['company identifier'][ind]
            # scrape_prospects = prospectscraper.prospect_scraping(name, position, prospect_linkedin_profile, unique_prospect_identifier, unique_company_identifier)
            # scrape_company, scrape_articles, scrape_hiring = None, None, None

            # if scrape_prospects['status'] == "success":
            # saving = True
            # while saving is True:
            # save_response = save_data(save_focus, scrape_company, scrape_articles, scrape_hiring, scrape_prospects, unique_company_identifier)
            # if save_response == "Saving complete":
            # saving:
            # print("Scraping not successful")

        elif company_already_exists is False and prospect_already_exists is False:
            focus = 1
            save_focus = 1
            unique_company_identifier = uuid.uuid4()
            unique_prospect_identifier = uuid.uuid4()
            print(f"Company ID: {unique_company_identifier}")
            print(f"Prospect ID: {unique_prospect_identifier}")
            # Running the scraping functions. Need to extract the company LinkedIn URL to run the hiring scraper.
            scrape_company = companyscraper.company_scraping(company_linkedin_profile)
            scrape_articles = articlescraperrw.article_scraper(domain)
            company_linkedin_url = scrape_company['socialNetworks']['linkedin']
            scrape_prospects = prospectscraper.prospect_scraping(name, position, prospect_linkedin_profile, unique_prospect_identifier, unique_company_identifier)
            scrape_hiring = hiringscraperrw.hiring_scraping(company_linkedin_url)

            pp.pprint(f"Company data: \n {scrape_company}")
            pp.pprint(f"Articles data: \n {scrape_articles}")
            pp.pprint(f"Prospects data: \n {scrape_prospects}")
            pp.pprint(f"Hiring data: \n {scrape_hiring}")

            companies_to_research.append(domain)

            scraped_data = {"Company": scrape_company, "Articles": scrape_articles, "Prospect": scrape_prospects,
                            "Hiring": scrape_hiring}
            pp.pprint(scraped_data)

            start_ai(scraped_data, unique_prospect_identifier, unique_company_identifier)


def start_ai(scraped_data, unique_prospect_identifier, unique_company_identifier):
    # Running the AI analysis' on the scraped data
    article_data = scraped_data['Articles']
    prospect_data = scraped_data['Prospect']
    hiring_data = scraped_data['Hiring']
    company_data = scraped_data['Company']
    all_jobs_link = ""

    article_analysis = articleai.start_article_ai(article_data)
    prospect_analysis = prospectai.start_prospect_ai(prospect_data)
    hiring_analysis = hiringai.start_hiring_ai(hiring_data)
    print(hiring_analysis)
    holistic_analysis = contextualiseai.start_contextualisation_ai(article_analysis, prospect_analysis, hiring_analysis)

    data_to_save = {"Company Data": company_data, "Raw Article Data": article_data,
                    "Raw Prospect Data": prospect_data, "Raw Hiring Data": hiring_data,
                    "Articles Analysis": article_analysis, "Prospect Analysis": prospect_analysis,
                    "Hiring Analysis": hiring_analysis, "Holistic Analysis": holistic_analysis,
                    "Hiring Jobs Link": all_jobs_link}
    save_data(data_to_save, unique_prospect_identifier, unique_company_identifier)

    return "AI analysis complete"


def save_data(data_to_save, unique_prospect_identifier, unique_company_identifier):
    # Saving the scraped data to the database

    # Saving the company data
    company_data = data_to_save['Company Data']
    article_data = data_to_save['Raw Article Data']
    hiring_data = data_to_save['Raw Hiring Data']
    all_jobs_link = data_to_save['Hiring Jobs Link']
    article_analysis = data_to_save['Articles Analysis']
    hiring_analysis = data_to_save['Hiring Analysis']
    holistic_analysis = data_to_save['Holistic Analysis']

    json_keys = ['description', 'descriptionShort', 'domain', 'domainName', 'industryMain',
                 'logo', 'name', 'revenue', 'totalEmployees']
    non_json_keys = ['socialNetworks', 'technologies', 'technologiesCategories']
    json_company_data = {}
    non_json_company_data = {}

    for key, value in company_data.items():
        if company_data[key] in json_keys:
            jsonified_data = json.loads(company_data[value])
            json_company_data[key] = jsonified_data
        elif company_data[key] in non_json_keys:
            non_json_company_data[key] = company_data[value]

    prepared_article_data = {"Articles": json.dumps(article_data)}
    prepared_hiring_data = {"Hiring": json.dumps(hiring_data)}
    prepared_company_data = {**non_json_company_data, **json_company_data,
                             **prepared_article_data, **prepared_hiring_data,
                             **{"Article Analysis": article_analysis},
                             **{"Hiring Analysis": hiring_analysis},
                             **{"Holistic Analysis": holistic_analysis},  # Split output of AI into company / prospect.
                             **{'Company Li Hiring Page': all_jobs_link},
                             **{"Company ID": unique_company_identifier}
                             }
    company_data_for_postgres = pd.DataFrame.from_dict(prepared_company_data)
    company_data_for_postgres.to_sql(f'Company', con=engine, if_exists='append')

    # Saving the prospect data
    prospect_data = data_to_save['Prospect']['response']
    prospect_analysis = data_to_save['Prospect Analysis']
    prepped_prospect_data = {**prospect_data,
                             **{"Prospect Analysis": prospect_analysis},
                             **{"Holistic Analysis": holistic_analysis},  # Split output of AI into company / prospect.
                             **{"Prospect ID": unique_prospect_identifier},
                             **{"Company ID": unique_company_identifier}
                             }

    prospect_data_for_postgres = pd.DataFrame.from_dict(prepped_prospect_data)
    prospect_data_for_postgres.to_sql(f'Prospect', con=engine, if_exists='append')

    return "Saving complete"


start_research(upload_data="test")
