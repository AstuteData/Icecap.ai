import pandas as pd
from sqlalchemy import create_engine, text
import json
import requests
from time import sleep
from bs4 import BeautifulSoup
import pprint as pp

conn = None
cur = None
engine = create_engine(
    'postgresql://xpdmcctztuueoj:5c6b0ce73d0e1d7a8b7ea13688df6b7268edd3e85ddc1ba488a8e233759731d2@ec2-34-241-82-91.eu-west-1.compute.amazonaws.com:5432/d6i1k6lrk3j39n')


def prospect_scraping(name, position, linkedin_profile, unique_prospect_identifier, unique_company_identifier):
    linkedin_page = prospect_profile_scraping(name, position, linkedin_profile, unique_prospect_identifier, unique_company_identifier)

    prospect_data = {"Name": name, "Position": position, "LinkedIn Profile": linkedin_page,
                     "linkedin URL": linkedin_profile, "Prospect ID": unique_prospect_identifier,
                     "Company ID": unique_company_identifier}

    pp.pprint(prospect_data)
    return prospect_data


def prospect_profile_scraping(name, position, linkedin_profile, unique_prospect_identifier, unique_company_identifier):
    # Async request through a proxy to scrape HTML data from LinkedIn profiles.
    # A 1-minute sleep timer initiates to give time for scraping the page.
    r = requests.post(url='https://async.scraperapi.com/jobs', json={'apiKey': "a084d8aff5227dce52232270ec7188d3",
                                                                     "apiParams": {
                                                                         'ultra-premium': True},
                                                                     'url': linkedin_profile})

    r_json = r.json()
    request_id = r_json['statusUrl']
    print(request_id)

    seconds = 0
    for i in range(10):
        response = requests.get(url=request_id)
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

    try:
        response = requests.get(url=request_id)
        r = response.json()
        print(r)
        html_text = (r['response']['body'])
        fullHtml = BeautifulSoup(html_text, 'html.parser')

        header = fullHtml.find('h2', class_='top-card-layout__headline').text.strip()
        about = fullHtml.find('div', class_='core-section-container__content break-words').text.strip()

        experience_section = fullHtml.find('ul', class_="experience__list")
        job_titles = experience_section.find_all('h3', class_="profile-section-card__title")
        job_companies = experience_section.find_all('a', class_="profile-section-card__subtitle-link")
        job_locations = experience_section.find_all('p',
                                                    class_="experience-item__location experience-item__meta-item")
        job_descriptions = experience_section.find_all('p', class_="show-more-less-text__text--less")

        job_experience = []
        for title, company, location, description in zip(job_titles, job_companies, job_locations,
                                                         job_descriptions):
            dict = {"Title": title.text.strip(), "Company": company.text.strip(), "Location": location.text.strip(),
                    "Description": description.text.strip()}
            job_experience.append(dict)

        prospect_profile_data = {"Position": position.replace("\n", ""), "Header": header.replace("\n", ""),
                                 "About": about.replace("\n", ""), "Experience": job_experience}

        pp.pprint(prospect_profile_data)
        return prospect_profile_data
    except Exception as e:
        print(e)


def prospect_posts_scraping(linkedin_profile):
    activity_url = linkedin_profile + "recent-activity/all/"
    r = requests.post(url='https://async.scraperapi.com/jobs', json={'apiKey': "a084d8aff5227dce52232270ec7188d3",
                                                                     "apiParams": {
                                                                         'ultra-premium': True,
                                                                         'render': True,
                                                                         'country_code': "us"},
                                                                     'url': activity_url})

    sleep(3)
    r_json = r.json()
    request_id = r_json['statusUrl']
    print(request_id)
    seconds = 0
    for i in range(10):
        response = requests.get(url=request_id)
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

    all_posts = {}
    try:
        response = requests.get(url=f'https://async.scraperapi.com/jobs/{request_id}')
        r = response.json()
        html_text = (r['response']['body'])
        fullHtml = BeautifulSoup(html_text, 'html.parser')

        activity_section = fullHtml.find('section', class_="artdeco-card ember-view pb3")
        posts = activity_section.find_all('div', class_="update-components-text relative feed-shared-update-v2__commentary ")

        post_counter = 0
        for post in posts:
            post_text = post.text.strip()
            post_counter += 1
            all_posts[post_counter] = post_text
        return all_posts
    except Exception as e:
        print(e)


def prospect_comment_scraping(linkedin_profile):
    activity_url = linkedin_profile + "recent-activity/comments/"
    r = requests.post(url='https://async.scraperapi.com/jobs', json={'apiKey': 'a084d8aff5227dce52232270ec7188d3',
                                                                     'url': activity_url})
    r_json = r.json()
    request_id = r_json['statusUrl']
    sleep(60)

    all_posts = {}
    retries = 0
    retry_limit = 3
    while retries > retry_limit:
        try:
            response = requests.get(url=f'https://async.scraperapi.com/jobs/{request_id}')
            r = response.json()
            html_text = (r['response']['body'])
            fullHtml = BeautifulSoup(html_text, 'html.parser')

            activity_section = fullHtml.find('section', class_="artdeco-card ember-view pb3")
            posts = activity_section.find_all('div', class_="update-components-text relative feed-shared-update-v2__commentary ")
            comments = activity_section.find_all('div', class_="update-components-text relative")

            post_counter = 0
            for post, comment in zip(posts, comments):
                post_text = post.text.strip()
                comment_text = comment.text.strip()
                post_counter += 1
                post_dict = {f"post number {post_counter}": post_text, f"prospect comment {post_counter}": comment_text}
                all_posts.update(post_dict)
            return all_posts
        except Exception as e:
            print(e)
            retries += 1
            sleep(30)
            if retries == retry_limit:
                pass
