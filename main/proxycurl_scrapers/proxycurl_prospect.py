import requests
import pprint as pp

api_key = 'Hnt8EpqHzgkG97GSkk7Krw'
headers = {'Authorization': 'Bearer ' + api_key}
api_endpoint = 'https://nubela.co/proxycurl/api/v2/linkedin'
linkedin_profile_url = 'https://www.linkedin.com/in/jackwhitehouse/'

response = requests.get(api_endpoint,
                        params={'url': linkedin_profile_url},
                        headers=headers)

r = response.json()
pp.pprint(r)
