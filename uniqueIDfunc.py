import datetime
import random
import string

def uniqueID():
    randomStringGen = str(random.random())
    randomString = randomStringGen.replace(".", "")
    uniqueIdGen = str(datetime.datetime.now())
    uniqueId = uniqueIdGen.replace("-", "")
    uniqueId = uniqueId.replace(" ", "")
    uniqueId = uniqueId.replace(":", "")
    uniqueId = uniqueId.replace(".", "")
    uniqueId = uniqueId+randomString
    return(uniqueId)

def uniqueCompanyID():
    randomStringGen = str(random.random())
    randomString = randomStringGen.replace(".", "")
    uniqueIdGen = str(datetime.datetime.now())
    uniqueId = uniqueIdGen.replace("-", "")
    uniqueId = uniqueId.replace(" ", "")
    uniqueId = uniqueId.replace(":", "")
    uniqueNumber = uniqueId.replace(".", "")
    uniqueChar = ""
    for i in range(8):
        CharGen = str(random.choice(string.ascii_letters))
        uniqueChar = uniqueChar + CharGen
        print(uniqueChar)
    companyID = uniqueChar +uniqueNumber
    print(companyID)

uniqueCompanyID()
