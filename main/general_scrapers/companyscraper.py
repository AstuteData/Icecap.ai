import requests
import json
import pprint as pp


def company_scraping(company_id, li_company_linkedin_url):
    # Fetching data from TheCompaniesAPI API and storing it.
    try:
        company_data_response = requests.get(f"https://api.thecompaniesapi.com/v1/companies/by-social?linkedin={li_company_linkedin_url}",
                                             headers={'Authorization': 'basic EvGVkI4x'})
        r = company_data_response.json()
        completion = formatted_company_scraping(r, company_id)
        pp.pprint(completion)
        return {'Status': 'Success', 'Data': completion}

    except Exception as error:
        print(f"There has been an error with this company scrape: {error}")
        return {'Status': 'Failed', 'Data': error}
        pass


def formatted_company_scraping(r, company_id):
    keys = ['domainName', 'domain', 'industryMain', 'revenue', 'technologies', 'technologyCategories', 'socialNetworks']

    formatted_response = {key: r[key] for key in keys}
    str_response = {}
    reduced_response = {}

    for key in formatted_response:
        if type(formatted_response[key]) == list or type(formatted_response[key]) == dict:
            value = formatted_response[key]
            list_reduced = json.dumps(value)
            reduced_response.update({key: list_reduced})
        else:
            str_response.update({key: formatted_response[key]})
    str_response.update({'company_id': company_id})
    transformed_general_response = {**str_response, **reduced_response}
    return transformed_general_response