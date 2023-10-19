import celery
import sys
sys.path.append('../')
from main.core_platform import research_main

app = celery.Celery('example')
app.conf.update(broker_url='rediss://:p10ad8c33e664c24f880e4e617de76589c86a9deb86bd1740b1fd523622ab4883@ec2-52-51-176-162.eu-west-1.compute.amazonaws.com:17730')

@app.task
def researchworker(upload_data):
    response = research_main.check_against_database(upload_data)
    return "Scraping complete"