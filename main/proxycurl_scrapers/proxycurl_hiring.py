import requests
import pprint as pp

api_key = 'Hnt8EpqHzgkG97GSkk7Krw'
headers = {'Authorization': 'Bearer ' + api_key}
api_endpoint = 'https://nubela.co/proxycurl/api/v2/linkedin/company/job'
params = {
    'job_type': 'anything',
    'when': 'past-month',
    'flexibility': 'remote',
    'search_id': '10688010',
}
response = requests.get(api_endpoint,
                        params=params,
                        headers=headers)

r = response.json()
pp.pprint(r)