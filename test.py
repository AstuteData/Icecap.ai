import pandas as pd
import json

a = [{"Company Name":"4Com","LinkedIn URL":"https://www.linkedin.com/company/785333"},
     {"Company Name":"Aardman","LinkedIn URL":"https://www.linkedin.com/company/aardman"},
     {"Company Name":"Airwave","LinkedIn URL":"https://www.linkedin.com/company/2016"}]

reff = pd.json_normalize(a)
df = pd.DataFrame(data=reff)

df1 = df.to_json()
parseddf = json.loads(df1)

print(parseddf)