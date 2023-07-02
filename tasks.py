import celery
import articleResearch
import time

app = celery.Celery('example')
app.conf.update(broker_url='rediss://:p10ad8c33e664c24f880e4e617de76589c86a9deb86bd1740b1fd523622ab4883@ec2-3-248-126-144.eu-west-1.compute.amazonaws.com:16830')

@app.task
def researchworker(jsonstring):
    start_time = time.time()
    articleResearch.prep_article_data(jsonstring)
    fin_time = time.time() - start_time
    return fin_time

