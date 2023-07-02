import celery
import os
import articleResearch

app = celery.Celery('example')
app.conf.update(BROKER_URL=os.environ['rediss://:p10ad8c33e664c24f880e4e617de76589c86a9deb86bd1740b1fd523622ab4883@ec2-3-248-126-144.eu-west-1.compute.amazonaws.com:16830'])

@app.task
def researchworker(jsonstring):
    articleResearch.prep_article_data(jsonstring)
    return "complete"
