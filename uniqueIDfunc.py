import datetime
import random

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