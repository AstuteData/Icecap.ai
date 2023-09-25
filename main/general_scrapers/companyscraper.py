import pandas as pd
import requests
import pprint as pp


def company_scraping(company_linkedin_url):
    # Fetching data from TheCompaniesAPI API and storing it.
    try:
        company_data_response = requests.get(f"https://api.thecompaniesapi.com/v1/companies/by-social?linkedin={company_linkedin_url}",
                         headers={'Authorization': 'basic EvGVkI4x'})
        company_data_json = company_data_response.json()
        keys = ['name', 'domainName', 'domain', 'description', 'descriptionShort', 'industryMain', 'revenue',
                'totalEmployees', 'logo', 'technologies', 'technologyCategories', 'socialNetworks']
        company_data_with_keys = {data: company_data_json[data] for data in keys}
        pp.pprint(company_data_with_keys)

        return company_data_with_keys
    except Exception as error:
        print(f"There has been an error with this company scrape: {error}")
        return {"status": "failure", "response": error}
        pass
