import os
import urllib
import urllib2
import json
import datetime
import base64
import re
import pickle


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
def getUrl(theurl, data=None):
    auth = 'Basic ' + base64.urlsafe_b64encode('%s:' % getUser() )
    if data:
        data = urllib.urlencode(data)
        print data
    req = urllib2.Request('%s?%s' % (theurl, data))
    req.add_header('Authorization', auth)
    req.add_header('Content-Type', 'application/json')
    req.add_header('user-agent', getUser())

    pagehandle = urllib2.urlopen(req)
    return pagehandle

### POST request accepts the Teamwork-specific URL and a JSON object with      the necessary parameters for the action.
def postUrl(theurl, thePost):

    req = urllib2.Request(theurl)
    auth = 'Basic ' + base64.urlsafe_b64encode("%s:%s" % (getApiKey(), 'x'))
    req.add_header('Authorization', auth)
    req.add_header('Content-Type', 'application/json')
    req.add_header('user-agent', getUser())

    return urllib2.urlopen(req, json.dumps(thePost))

def githubUsers(pattern, userDict):
    if userDict['lastUser']:
        response = getUrl('https://api.github.com/users?since=%s' % userDict['lastUser'])
    else:
        response = getUrl('https://api.github.com/users')
    responseList = json.loads(response.read())
    count = 0
    
    for user in responseList:
        print user['login']
        print 'id: %s' % user['id']
        userResponse = getUrl('https://api.github.com/users/%s' % user['login'])
        thisUser = json.loads(userResponse.read())
        if 'location' in thisUser:
            if thisUser['location']:
                if pattern.match(thisUser['location']):
                    userDict['users'][str(user['login'])] = thisUser #json.loads(userResponse.read())
        userDict['nextUrl'] = response.info()['Link']
        pingsRemaining = int(response.info()['X-RateLimit-Remaining'])
        userDict['ratelimitReset'] = int(response.info()['X-RateLimit-Reset'])
        userDict['ratelimitRemaining'] = int(response.info()['X-RateLimit-Remaining'])

        userDict['lastUser'] = thisUser['id']
        count += 1
    userDict['nextUrl'] = userDict['nextUrl'][1:userDict['nextUrl'].find('>')]
    print pingsRemaining
    print userDict['ratelimitReset']
    print userDict['nextUrl']
    return githubUsers(pattern, userDict)

if os.path.isfile('gitDict.pkl'):
    f = open('gitDict.pkl', 'rb')
    userDict = pickle.load(f)
    f.close()
else:
    userDict = {'nextUrl': None, 'lastUser': None, 'ratelimitReset': None, 'ratelimitRemaining': 5000, 'users': {}}

pattern = re.compile('san francisco', re.I)
nextUrl = None

while userDict['ratelimitRemaining'] > 299:
    userDict = githubUsers(pattern, userDict)
   
print userDict
f = open('gitDict.pkl', 'wb')
pickle.dump(userDict, f)
f.close()
#print userDict['mojombo']
