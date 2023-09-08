import pandas as pd
from sqlalchemy import create_engine, text
import json
import requests
from time import sleep
from bs4 import BeautifulSoup

conn = None
cur = None
engine = create_engine(
    'postgresql://xpdmcctztuueoj:5c6b0ce73d0e1d7a8b7ea13688df6b7268edd3e85ddc1ba488a8e233759731d2@ec2-34-241-82-91.eu-west-1.compute.amazonaws.com:5432/d6i1k6lrk3j39n')

rivery_key_words = ["data", "data engineer", "analytics", "sql", "python", "etl", "data scientist", "data analyst",
                    "cto", "chief technology officer", "cdo", "chief data officer", "data science", "data engineering"
                    "architect", "technology"]


def hiring_scraping(company_linkedin_url):
    scrape_hiring = json.dumps(scrape_jobs_link(company_linkedin_url))
    return {"status": "success", "response": scrape_hiring}


def scrape_jobs_link(company_linkedin_url):
    linkedin_url = company_linkedin_url
    formatted_url = linkedin_url + "jobs/"

    # Async request through a proxy to scrape HTML data from LinkedIn profiles.
    # A 1-minute sleep timer initiates to give time for scraping the page.
    r = requests.post(url='https://async.scraperapi.com/jobs',
                      json={'apiKey': 'a084d8aff5227dce52232270ec7188d3',
                            'url': formatted_url})

    r_json = r.json()
    request_id1 = r_json['status']
    sleep(60)

    # After the 1-minute timer has finished, the application tries to get the scraped HTML data.
    # If there are 3 exceptions, it passes on to the next prospect.
    retries = 0
    retry_limit = 3
    while retries >= retry_limit:
        try:
            response = requests.get(url=request_id1)
            r = response.json()
            html_text = (r['response']['body'])
            fullHtml = BeautifulSoup(html_text, 'html.parser')

            jobs_section = fullHtml.find('div', class_='org-jobs-recently-posted-jobs-module__show-all-jobs-btn')
            all_jobs_html = jobs_section.find('a')
            all_jobs_link_end = all_jobs_html.text.strip()
            all_jobs_link = 'https://www.linkedin.com/' + all_jobs_link_end

            sjl_r = scrape_jobs_list(all_jobs_link)
            return sjl_r
        except Exception as e:
            print(e)
            retries += 1
            sleep(30)
            if retries == retry_limit:
                pass



def scrape_jobs_list(all_jobs_link):
    r = requests.post(url='https://async.scraperapi.com/jobs',
                      json={'apiKey': 'a084d8aff5227dce52232270ec7188d3',
                            'url': all_jobs_link})

    r_json = r.json()
    request_id2 = r_json['status']
    sleep(60)

    retries2 = 0
    retry_limit2 = 3
    job_list = {}
    while retries2 < retry_limit2:
        try:
            response = requests.get(url=request_id2)
            r = response.json()
            html_text = (r['response']['body'])

            fullHtml = BeautifulSoup(html_text, 'html.parser')
            job_containers = fullHtml.find_all('div', class_='full-width artdeco-entity-lockup__title ember-view')

            for job in job_containers:
                job_title = job.find('a',
                                     class_="disabled ember-view job-card-container__link job-card-list__title").text.strip()
                job_link_end = \
                job.find('a', class_="disabled ember-view job-card-container__link job-card-list__title")[
                    'href'].strip().split('/')
                job_link = 'https://www.linkedin.com/'+job_link_end

                search_key_words = True
                total_count = 0
                while search_key_words is True:
                    for key_word in rivery_key_words:
                        if key_word in job_title.lower():
                            job_dict = {'job title': job_title, 'link': job_link}
                            job_list.update(job_dict)
                            total_count += 1

                            if total_count == len(rivery_key_words):
                                search_key_words = False
                            else:
                                pass

                            # Writing a note so that I remember what to code.
                            # Code the scraper for individual job pages based on job_list.
                            # Write the individual AI component.
                            # Add to the contextualiseai.py document for job hiring.
                            # Bug test.

                        elif key_word not in job_title:
                            total_count += 1
                            if total_count == len(rivery_key_words):
                                search_key_words = False
                            else:
                                pass

                if search_key_words is False:
                    sjd_r = scrape_job_data(job_list, all_jobs_link)
                    return sjd_r
        except Exception as e:
            print(e)
            retries2 += 1
            sleep(30)
            if retries2 == retry_limit2:
                pass


def scrape_job_data(job_list, all_jobs_link):
    scraped_jobs = {}
    run_count = 0
    for job_title, job_link in job_list.items():
        formatted_url = job_link
        r = requests.post(url='https://async.scraperapi.com/jobs',
                          json={'apiKey': 'a084d8aff5227dce52232270ec7188d3',
                                'url': formatted_url})
        r_json = r.json()
        request_id3 = r_json['status']
        sleep(60)

        retries3 = 0
        retry_limit3 = 3
        ul_dict = {}
        p_dict = {}
        while retries3 < retry_limit3:
            try:
                response = requests.get(url=request_id3)
                r = response.json()
                html_text = (r['response']['body'])
                fullHtml = BeautifulSoup(html_text, 'html.parser')
                job_post_section = fullHtml.find('div', id_="job-details")

                # <ul> </ul> tags typically contain:
                # Responsibilities, Qualifications, Perks & Benefits
                job_post_ul = job_post_section.find_all('ul')
                # <p> </p> tags typically contain:
                # Company information, general position information, responsibilities
                job_post_p = job_post_section.find_all('p')

                ul_count = 0
                for ul in job_post_ul:
                    ul_count += 1
                    hot_ul = ul.text.strip()
                    hot_ul_dict = {f"ul {ul_count}": hot_ul}
                    ul_dict.update(hot_ul_dict)

                p_count = 0
                for p in job_post_p:
                    p_count += 1
                    hot_p = p.text.strip()
                    hot_p_dict = {f"p {p_count}": hot_p}
                    p_dict.update(hot_p_dict)

                scraped_job = {"Job Title": job_title, "Job Link": job_link,
                               "Ul Data": ul_dict, "P Data": p_dict, "LinkedIn Jobs Page": all_jobs_link}
                scraped_jobs.update(scraped_job)
                run_count += 1
                if run_count is len(job_list):
                    retries3 = 3
            except Exception as e:
                print(e)
                retries3 += 1
                sleep(30)
                if retries3 == retry_limit3:
                    pass
    return scraped_jobs

