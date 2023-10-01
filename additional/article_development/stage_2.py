from rake_nltk import Rake
import pandas as pd
from sqlalchemy import create_engine, text

conn = None
cur = None
engine = create_engine(
    'postgresql://xpdmcctztuueoj:5c6b0ce73d0e1d7a8b7ea13688df6b7268edd3e85ddc1ba488a8e233759731d2@ec2-34-241-82-91.'
    'eu-west-1.compute.amazonaws.com:5432/d6i1k6lrk3j39n')


def load_postgres():
    with engine.connect() as conn:
        stage1_select = text('SELECT * FROM "stage1"')
        stage1_dataframe = pd.read_sql_query(stage1_select, conn)
        stage1_dataframe.drop(columns='index')
        print(len(stage1_dataframe))

    stage2_prep = stage1_dataframe.drop_duplicates(subset='domain')
    unique_company_domains = []
    for index, row in stage2_prep.iterrows():
        domain = row['domain']
        unique_company_domains.append(domain)

    print(unique_company_domains)

    unique_url_dict = {}
    for domain in unique_company_domains:
        current_domain = domain
        url_count = stage1_dataframe['domain'].value_counts()[domain]
        unique_url_dict[current_domain] = url_count

    sorted_url_list = sorted(unique_url_dict.items(), key=lambda x: x[1], reverse=True)
    sorted_url_dict = dict(sorted_url_list)
    transformed_url_dataframe = pd.DataFrame.from_dict(sorted_url_dict, orient='index')
    transformed_url_dataframe.to_sql(f'stage2', con=engine, if_exists='append')


load_postgres()
