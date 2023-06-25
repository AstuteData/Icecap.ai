import pandas as pd
import json

jsonstring = [
    {
        "UniqueID": "2023062321534052842108428684599956294",
        "description": "Established in 1981 Poundstretcher is the UK's leading variety discount retailer for quality food, toiletries, garden essentials and home-ware brands. Offering over 5000 products at some of the lowest prices on the high street, Poundstretcher stores provide shoppers with an incredible selection of value for money items, ranging from 49p up to £150. With over 400 stores nationwide, Poundstretcher stocks a huge selection of great value products at competitive prices, including kitchenware, bedding, bathroom products, furniture, electric goods, children's toys and even pet care products within the brands \"Pet Hut\" section. For money-conscious grocery shoppers, Poundstretcher also offer great value prices on everyday big brand items such as food, toiletries and household goods, along with great range of fantastic seasonal goods. With Poundstretcher, you can be confident that you are getting the best deals, making your budget go further without sacrificing on quality or style. Employing over 6000 people nationwide across the brands chain of outlets, Poundstretcher aim to offer great customer service and a quality selection of products at all of our stores across the UK. Follow us on Facebook for more daily updates, competitions and promotions.",
        "domain": "poundstretcher.co.uk",
        "domainName": "poundstretcher",
        "domainTld": "co.uk",
        "industryMain": "retail",
        "monthlyVisitors": "under-10k",
        "originalCompanyName": "Poundstretcher Ltd.",
        "revenue": "200m-1b",
        "totalEmployees": "200-500",
        "yearFounded": 1981
    },
    {
        "UniqueID": "202306232153409545170811083367292699",
        "description": "Established in 1997, Mountain Warehouse has grown rapidly to become the largest Outdoor Retailer in the UK, with 270+ stores worldwide and strong online sales both in the UK and Internationally. Unlike other outdoor retailers, we don't carry lots of different brands. In fact, almost all the products we sell through our stores and website are exclusive to Mountain Warehouse - you won't find them anywhere else. To keep us on the cutting edge of the outdoor world we are always on the lookout for young, talented, enthusiastic people who love to be part of a fast paced team. If you embrace hard work, love change and strive to always make things bigger and better then come join us. We have a vibrant, busy office full of great people. There are loads of opportunities to get involved in projects away from your day to day and plenty of opportunity for growth across all departments. If you think you have what it takes to join the Mountain Warehouse adventure check out our Current Vacancies.",
        "domain": "mountainwarehouse.com",
        "domainName": "mountainwarehouse",
        "domainTld": "com",
        "industryMain": "retail",
        "monthlyVisitors": "1m-10m",
        "originalCompanyName": "Mountain Warehouse",
        "revenue": "200m-1b",
        "totalEmployees": "200-500",
        "yearFounded": 1997
    },
    {
        "UniqueID": "20230623215341208560004449956933373811",
        "description": "City Plumbing Supplies has built on its reputation of selling quality products and providing expert service to the Plumbing and Heating trade for more than 25 years. They began trading in 1981 from a single site in Salisbury, Wiltshire and have rapidly grown the business and now have a nationwide network of over 180 branches in the UK. In 2002 City Plumbing Supplies was acquired by Travis Perkins plc and has since gone from strength to strength with the added support of being part of the Travis Perkins Group.",
        "domain": "cityplumbing.co.uk",
        "domainName": "cityplumbing",
        "domainTld": "co.uk",
        "industryMain": "building-materials",
        "monthlyVisitors": "under-10k",
        "originalCompanyName": "City Plumbing Supplies",
        "revenue": "200m-1b",
        "totalEmployees": "500-1k",
        "yearFounded": 1981
    }
]

df = pd.json_normalize(jsonstring, max_level=0)
print(df)

for ind in df.index:
    currentCompany = (df['originalCompanyName'][ind])
    currentDomain = (df['domain'][ind])
    print(currentCompany)
    print(currentDomain)