import pandas as pd
import requests


def company_scraping(domain, unique_company_identifier):
    # Fetching data from TheCompaniesAPI API and storing it.
    try:
        company_data_response = requests.get(f"https://api.thecompaniesapi.com/v1/companies/{domain}",
                         headers={'Authorization': 'basic EvGVkI4x'})
        company_data_json = company_data_response.json()
        keys = ['name', 'domainName', 'domain', 'description', 'descriptionShort', 'industryMain', 'revenue',
                'totalEmployees', 'logo', 'technologies', 'technologyCategories', 'socialNetworks']
        company_data_with_keys = {data: company_data_json[data] for data in keys}

        return {"status": "success", "response": company_data_with_keys}
    except Exception as error:
        print(f"There has been an error with this company scrape: {error}")
        return {"status": "failure", "response": error}
        pass
