import os
import urllib
import urllib2
import json
import datetime
import base64
import re
import pickle
import time
import shelve


### Retrieve API key from local file user.txt
def getUser():
    curPath = os.getcwd()
    f = open('%s/user.txt' % curPath, 'rb')
    user = f.readline().strip()
    f.close()
    return user

### Using Basic auth no password needed
#def getPass():
#    curPath = os.getcwd()
#    f = open('%s/user.txt' % curPath, 'rb')
#    passwd = f.readline().strip()
#    f.close()
#    return passwd

### Create authorization handler for Github
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
        theurl += '?%s' % data
    req = urllib2.Request(theurl)
    req.add_header('Authorization', auth)
    req.add_header('Content-Type', 'application/json')
    req.add_header('user-agent', getUser())

    pagehandle = urllib2.urlopen(req)
    return pagehandle

### POST request accepts the Teamwork-specific URL and a JSON object with      the necessary parameters for the action.
def postUrl(theurl, thePost):

    req = urllib2.Request(theurl)
    auth = 'Basic '+base64.urlsafe_b64encode("%s:%s" % (getApiKey(), 'x'))
    req.add_header('Authorization', auth)
    req.add_header('Content-Type', 'application/json')
    req.add_header('user-agent', getUser())

    return urllib2.urlopen(req, json.dumps(thePost))

def githubUsers(userDict):
    theParams = ''
    if userDict['nextUrl'] is not None:
        theUrl = userDict['nextUrl']
    else:
        theUrl = 'https://api.github.com/search/users'
        theParams = urllib.urlencode(userDict['params'])
        theParams = 'q=' + theParams.replace('=', ':')
    print 'request url: ' + theUrl + '?%s' + theParams
    response = getUrl(theUrl, theParams)
    responseList = json.loads(response.read())
#    print response.info()
    for user in responseList['items']:
        print user['login']
        #print 'id: %s' % user['id']
        userDict['users'][str(user['login'])] = user
    linkTuples = response.info()['Link'].split(',')
    for theTuple in linkTuples:
        print json.dumps(theTuple)
        if theTuple.count('next') > 0:
            print 'found next'
            userDict['nextUrl'] = theTuple[theTuple.find('<')+1:theTuple.find('>')]
        if theTuple.count('last') > 0:
            print 'found last'
            userDict['lastUrl'] = theTuple[theTuple.find('<')+1:theTuple.find('>')]
        if theTuple.count('first') > 0:
            print 'found first'
            return userDict
    print 'nextUrl: ' + userDict['nextUrl']
    pingsRemaining = int(response.info()['X-RateLimit-Remaining'])
    userDict['ratelimitReset'] =                                                                    int(response.info()['X-RateLimit-Reset'])
    userDict['ratelimitRemaining'] = pingsRemaining    
    print pingsRemaining
    print userDict['ratelimitReset']
    print userDict['nextUrl']
    if (userDict['ratelimitRemaining'] > 0):
        return githubUsers(userDict)
    else:
        while userDict['ratelimitReset'] - time.time() >= 0:
            print 'sleeping'
            time.sleep(30)
        userDict['ratelimitRemaining'] = 30
        return githubUsers(userDict)

if __name__ == '__main__':
    parameters = {'location': 'san diego',\
                  'type': 'user'}
    if os.path.isfile('gitDict.pkl'):
        f = open('gitDict.pkl', 'rb')
        userDict = pickle.load(f)
        userDict['lastUser'] = {'id': 0}
        f.close()
    else:
        userDict = {'nextUrl': None,                                                           'lastUser': None,                                                          'ratelimitReset': None,                                                    'ratelimitRemaining': 30,                                                'params': parameters,                                                      'users': {}                                                               }
    userDict = githubUsers(userDict)
    f = open('gitDict.pkl', 'wb')
    pickle.dump(userDict, f)
    f.close()
    f = open('newCSV.csv', 'wb')
    with f:
        for user in userDict:
            f.write(user)
    f.close()

