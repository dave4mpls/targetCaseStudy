#  
#   Simple implementation of just enough aspects of the requests
#   module for nextbus to run without changes under Brython in the web.
#

import json
import urllib.parse
import browser.ajax

class BrythonAjaxResultClass:
    def __init__(self, pResultCode, pText):
        self.resultCode = pResultCode
        self.text = pText
        if (self.resultCode >= 200 and self.resultCode < 300):
            self.ok = True
        else:
            self.ok = False
    
    def json(self):
        return json.loads(self.text)

def get(url, params):
    # implementation of requests.get for use in Brython
    fullUrl = url
    # first handle params
    if params is None:
        pass
    else:
        fullUrl += "?"
        firstFlag = True
        for thisParam in params:
            if not firstFlag:
                fullUrl += "&"
            firstFlag = False
            fullUrl += urllib.parse.quote_plus(thisParam)
            fullUrl += "="
            fullUrl += urllib.parse.quote_plus(params[thisParam])
    # now use Brython ajax module, synchronously, to get result
    a = browser.ajax.ajax()
    a.open("GET",fullUrl,False)
    a.send()
    resultCode = a.status
    if a.readyState != 4: resultCode = 500
    resultObject = BrythonAjaxResultClass(resultCode, a.text)
    return resultObject
