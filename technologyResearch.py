import pandas as pd
from sqlalchemy import create_engine, text
import requests
import openai

conn = None
cur = None
engine = create_engine(
    'postgresql://xpdmcctztuueoj:5c6b0ce73d0e1d7a8b7ea13688df6b7268edd3e85ddc1ba488a8e233759731d2@ec2-34-241-82-91.eu-west-1.compute.amazonaws.com:5432/d6i1k6lrk3j39n')
openai.api_key = "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"
modelEngine = "text-davinci-003"



def retrieve_techstack_research(companyid):
    select = text('SELECT * FROM "CompanyData"')
    TechstackResearchDf = pd.read_sql_query(select, conn)
    TechstackResearchDf = TechstackResearchDf.drop(columns='index')

    Name = []
    Summaries = []
    Focuses = []
    Positioning = []

    for id in companyid:
        for ind in TechstackResearchDf.index:
            if TechstackResearchDf['UniqueID'][ind] == id:
                currentCompany = (TechstackResearchDf['name'][ind])
                techstackList = (TechstackResearchDf['technologies'][ind])
                summary, key_focuses, positioning = auto_techstack_research(currentCompany, techstackList)
                Name.append(currentCompany)
                Summaries.append(summary)
                Focuses.append(key_focuses)
                Positioning.append(Positioning)
            else:
                pass

    TechAiResearchDf = pd.DataFrame()
    TechAiResearchDf['name'] = Name
    TechAiResearchDf['Tech Summary'] = Summaries
    TechAiResearchDf['Tech Focuses'] = Focuses
    TechAiResearchDf['Tech Positioning'] = Positioning
    TechstackResearchDf.to_sql(f'TechsAiResearch', con=engine, if_exists='append')
    return "Complete"


def auto_techstack_research(currentCompany, techstackList):
    select = text('SELECT * FROM "Technologies"')
    TechnologiesDf = pd.read_sql_query(select, conn)
    TechnologiesDf = TechnologiesDf.drop(columns='index')

    uncleanedTechstackList = techstackList

    for tech in uncleanedTechstackList:
        tech.capitalize()
        tech.replace("-", " ")

    cleanTechstackList = uncleanedTechstackList
    newTechnologyUnsummarised = []
    newTechnologySummarised = {}

    for tech in cleanTechstackList:
        if TechnologiesDf[TechnologiesDf['Technology Name'].astype(str).str.contains(tech)]:
            pass
        else:
            newTechnologyUnsummarised.append(tech)

    for tech in newTechnologyUnsummarised:
        prompt = f"You will analyse what a specific piece of technology is. " \
                 f"You will then outline three things: 1. What the technolgy does. 2) Which business function the technology helps. " \
                 f"3. Benefits and limiations of the technology." \
                 f"The technology you will analyse and outline is: {tech}"
        newTechnology_completion = openai.Completion.create(
            model=modelEngine,
            prompt=prompt,
            temperature=0,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.5,
        )
        newTechnologySummarised[tech] = newTechnology_completion

    newTechnologiesDf = pd.DataFrame.from_dict(newTechnologySummarised)
    newTechnologiesDf.to_sql(f'Technologies', con=engine, if_exists='replace')
    techstack_summary(currentCompany, techstackList)


def techstack_summary(currentCompany, techstackList):
    select = text('SELECT * FROM "Technologies"')
    TechnologiesDf = pd.read_sql_query(select, conn)
    TechnologiesDf = TechnologiesDf.drop(columns='index')

    uncleanedTechstackList = techstackList

    for tech in uncleanedTechstackList:
        tech.capitalize()
        tech.replace("-", " ")

    cleanTechstackList = uncleanedTechstackList
    techstackInfo = {}

    for tech in cleanTechstackList:
        technologyInfo = TechnologiesDf.iloc[0][tech]
        techstackInfo[tech] = technologyInfo

    techCounter = 0
    techSummaryPromptStr = ""
    for tech in techstackInfo.items():
        technologyName = tech[0]
        technologyDesc = tech[1]
        techCounter = techCounter + 1
        techPromptStr = techSummaryPromptStr + f"{techCounter}. \n Technology {techCounter} Name: {technologyName} \n " \
                                               f"Technology {techCounter} Description: {technologyDesc} \n \n"


    prompt = f"You are a Sales Development Representative at Rivery.io, which sells cloud ETL solutions. Based on " \
                 f"the description of the numbered technology below, summarise the most relevant pieces of " \
                 f"technology. If the technology is not relevant, do not mention it. The technologies that you need " \
                 f"to summarise are: {techSummaryPromptStr}"

    techstack_summary_completion = openai.Completion.create(
        model=modelEngine,
        prompt=prompt,
        temperature=0.5,
        max_tokens=200,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.5,
    )

    techstack_key_focuses(techSummaryPromptStr, currentCompany)


def techstack_key_focuses(techSummaryPromptStr, currentCompany, techstack_summary_completion):
    prompt = f"You are a Sales Development Representative at Rivery.io, which sells cloud ETL solutions. Based on " \
                 f"the description of the numbered technology below, summarise the top key focuses that you would " \
             f"highlight that can be used to make a convincing pitch. This is a list of all of the technologies " \
             f"used by {currentCompany} you need to analyse: {techSummaryPromptStr}"

    techstack_key_focuses_completion = openai.Completion.create(
        model=modelEngine,
        prompt=prompt,
        temperature=0.5,
        max_tokens=200,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.5,
    )

    techstack_product_positioning(techSummaryPromptStr, currentCompany, techstack_key_focuses_completion, techstack_summary_completion)

def techstack_product_positioning(techSummaryPromptStr, currentCompany, techstack_key_focuses_completion, techstack_summary_completion):
    prompt = f"You are a Sales Development Representative at Rivery.io, which sells cloud ETL solutions. Based on " \
                 f"the key focuses and summary, identify the best way to position Rivery.io to {currentCompany}. Here " \
             f"are the key focuses:  {techstack_key_focuses_completion}, and here's the summary: {techstack_summary_completion}. Now tell me the best way to position Rivery.io for {currentCompany}"

    techstack_product_positioning_completion = openai.Completion.create(
        model=modelEngine,
        prompt=prompt,
        temperature=0.5,
        max_tokens=200,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.5,
    )

    return techstack_summary_completion, techstack_key_focuses_completion, techstack_product_positioning_completion