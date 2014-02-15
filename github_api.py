import os
import urllib
import urllib2
import json
import datetime
import base64


### Retrieve API key from local file ./teamworkpm_api_key.txt
def getUser():
    curPath = os.getcwd()
    f = open('%s/user.txt' % curPath, 'rb')
    user = f.readline().strip()
    f.close()
    return user

def getPass():
    curPath = os.getcwd()
    f = open('%s/user.txt' % curPath, 'rb')
    passwd = f.readline().strip()
    f.close()
    return passwd

### Create authorization handler for TeamworkPM
def authUrl(theurl):
    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(realm='GitHub.com',                                                        uri=theurl,                                                                user=getUser(),                                                            passwd=getPass())
    
    authhandler = urllib2.HTTPBasicAuthHandler(passman)

    opener = urllib2.build_opener(authhandler)
    
    urllib2.install_opener(opener)
    return

### GET request to establish parameters
def getUrl(theurl):
    
    auth = 'Basic ' + base64.urlsafe_b64encode('%s:' % getUser() )
    req = urllib2.Request(theurl)
    req.add_header('Authorization', auth)
    req.add_header('Content-Type', 'application/json')
    req.add_header('user-agent', getUser())

    pagehandle = urllib2.urlopen(req)
#    return pagehandle.read()
    return pagehandle

### POST request accepts the Teamwork-specific URL and a JSON object with      the necessary parameters for the action.
def postUrl(theurl, thePost):

    req = urllib2.Request(theurl)
    auth = 'Basic ' + base64.urlsafe_b64encode("%s:%s" % (getApiKey(), 'x'))
    req.add_header('Authorization', auth)
    req.add_header('Content-Type', 'application/json')
    req.add_header('user-agent', getUser())

    return urllib2.urlopen(req, json.dumps(thePost))

response = getUrl('https://api.github.com/users')
print response.info()
