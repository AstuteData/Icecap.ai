import requests
import pprint as pp

api_key = 'Hnt8EpqHzgkG97GSkk7Krw'
headers = {'Authorization': 'Bearer ' + api_key}
api_endpoint = 'https://nubela.co/proxycurl/api/linkedin/company'
params = {
    'url': 'https://www.linkedin.com/company/rivery/',
    'resolve_numeric_id': 'false',
    'categories': 'exclude',
    'funding_data': 'exclude',
    'extra': 'exclude',
    'exit_data': 'exclude',
    'acquisitions': 'exclude',
    'use_cache': 'if-present',
}
response = requests.get(api_endpoint,
                        params=params,
                        headers=headers)

r = response.json()
pp.pprint(r)
