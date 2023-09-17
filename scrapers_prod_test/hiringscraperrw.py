import pandas as pd
from sqlalchemy import create_engine, text
import json
import requests
from time import sleep
from bs4 import BeautifulSoup
import pprint as pp
from types import NoneType

rivery_key_words = ["data", "analytics", "sql", "python", "etl", "cto", "cdo",
                    "architect", "technology", "developer"]


def hiring_scraping(company_linkedin_url):
    print("Hiring Scraping Started")

    scrape_hiring = scrape_jobs_link(company_linkedin_url)
    pp.pprint(scrape_hiring)
    return scrape_hiring


def scrape_jobs_link(company_linkedin_url):
    print("Scrape Job Link Started")

    linkedin_url = company_linkedin_url
    formatted_url = linkedin_url + "jobs/"

    # Async request through a proxy to scrape HTML data from LinkedIn profiles.
    # A 1-minute sleep timer initiates to give time for scraping the page.
    r = requests.post(url='https://async.scraperapi.com/jobs', json={'apiKey': 'a084d8aff5227dce52232270ec7188d3',
                                                                     "apiParams": {
                                                                         'ultra-premium': True,
                                                                         'render': True,
                                                                         'country_code': "us"},
                                                                     'url': formatted_url})

    r_json = r.json()
    request_id1 = r_json['statusUrl']
    print(request_id1)

    seconds = 0
    for i in range(4):
        response = requests.get(url=request_id1)
        print(response)
        print(response.json)
        r2 = response.json()
        if r2['status'] == 'finished':
            print(f"It took {seconds} seconds to receive a positive response from ScraperAPI")
            break
        else:
            sleep(30)
            seconds += 30
            print(f"Waiting for ScraperAPI to finish, it has been {seconds} seconds")
    print("Exited loop.")

    # After the 1-minute timer has finished, the application tries to get the scraped HTML data.
    # If there are 3 exceptions, it passes on to the next prospect.

    try:
        response = requests.get(url=request_id1)
        r = response.json()
        html_text = (r['response']['body'])
        fullHtml = BeautifulSoup(html_text, 'html.parser')
        jobs_section = fullHtml.find('a',
                                     class_='top-card-layout__cta mt-2 ml-1.5 h-auto babybear:flex-auto top-card-layout__cta--primary btn-md btn-primary')
        href = jobs_section.get('href')
        all_jobs_link = href
        scraped_jobs_list_response = scrape_jobs_list(all_jobs_link)

        print("Returning scraped jobs list")
        return scraped_jobs_list_response
    except Exception as e:
        print(e)
        sleep(15)
        print("Need longer to scrape. Waiting another 15 seconds...")


def scrape_jobs_list(all_jobs_link):
    print("Scrape Job List Started")

    r = requests.post(url='https://async.scraperapi.com/jobs', json={'apiKey': 'a084d8aff5227dce52232270ec7188d3',
                                                                     "apiParams": {
                                                                         'ultra-premium': True,
                                                                         'render': True,
                                                                         'country_code': "us"},
                                                                     'url': all_jobs_link})

    r_json = r.json()
    request_id2 = r_json['statusUrl']
    print(request_id2)
    print("Sleeping for 30 seconds...")
    sleep(30)
    print("2. Now awake")

    print("Started")
    response = requests.get(url=request_id2)
    r2 = response.json()
    html_text = (r2['response']['body'])
    fullHtml = BeautifulSoup(html_text, 'html.parser')

    job_list = fullHtml.find('main', class_="two-pane-serp-page__results")
    job_containers = job_list.find_all('li')

    job_list = {}

    for job in job_containers:
        job_title = job.find('h3', class_="base-search-card__title").text.strip()
        job_link_html = job.find('a',
                                 class_="base-card__full-link absolute top-0 right-0 bottom-0 left-0 p-0 z-[2]")
        job_link = job_link_html.get('href')

        search_key_words = True
        total_count = 0
        while search_key_words is True:
            for key_word in rivery_key_words:
                if key_word in job_title.lower() and job_link:
                    job_dict = {'job title': job_title, 'link': job_link}
                    total_count += 1
                    job_list[total_count] = job_dict
                    if total_count == len(rivery_key_words):
                        search_key_words = False
                    else:
                        pass
                elif key_word not in job_title:
                    total_count += 1
                    if total_count == len(rivery_key_words):
                        search_key_words = False
                    else:
                        pass
    scraped_job_data_response = scrape_job_data(job_list, all_jobs_link)

    print("Returning scraped job data")
    return scraped_job_data_response


def scrape_job_data(job_list, all_jobs_link):
    print("Scrape Job Data Started")

    scraped_jobs = {}
    run_count = 0
    for i in job_list:
        job_title = job_list[i]['job title']
        job_link = job_list[i]['link']

        r = requests.post(url='https://async.scraperapi.com/jobs',
                          json={'apiKey': 'a084d8aff5227dce52232270ec7188d3',
                                "apiParams": {
                                    'ultra-premium': True,
                                    'render': True,
                                    'country_code': "us"},
                                'url': job_link})
        r_json = r.json()
        request_id3 = r_json['statusUrl']
        print(request_id3)
        print("Sleeping for 30 seconds...")
        sleep(30)
        print("3. Now awake")

        try:
            response = requests.get(url=request_id3)
            r = response.json()
            html_text = (r['response']['body'])
            fullHtml = BeautifulSoup(html_text, 'html.parser')
            job_post_section = fullHtml.find('div', class_="core-section-container__content break-words")

            job_description_section = job_post_section.find('div', class_="description__text description__text--rich")
            job_description_data_p = job_description_section.find_all('p')
            job_description_data_ul = job_description_section.find_all('ul')

            paragraph = ""
            unordered_list = ""

            for p in job_description_data_p:
                paragraph = p.text.strip()
                paragraph += "" \
                             ""

            for ul in job_description_data_ul:
                unordered_list += ul.text.strip()
                unordered_list += "" \
                                  ""

            scraped_job = {"Job Title": job_title, "Job Link": job_link,
                           "Ul Data": unordered_list, "P Data": paragraph}

            run_count += 1
            run_count_str = str(run_count)
            scraped_jobs[run_count_str] = scraped_job
        except Exception as e:
            print(e)
            sleep(30)

    print("Returning scraped jobs")
    return scraped_jobs
