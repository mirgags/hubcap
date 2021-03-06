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
import urlparse

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
        theParams = '?q=+%s' % urllib.quote_plus(userDict['params'])
        print 'pre-regex url: %s%s' % (theUrl, theParams)
#        theParams = re.sub('(?<!\?q)=',':',theParams)
        theUrl += theParams
        theParams = None
        print 'request url: %s%s' % (theUrl, theParams)
    response = getUrl(theUrl, theParams)
    responseList = json.loads(response.read())
    print 'search results: ' + str(responseList['total_count'])
    print response.info()
    for user in responseList['items']:
        print user['login']
        #print 'id: %s' % user['id']
        userDict['users'].append(user)
    linkTuples = response.info()['Link'].split(',')
    print json.dumps(linkTuples)
    for theTuple in linkTuples:
        print json.dumps(theTuple)
        if theTuple.count('next') > 0:
            print 'found next'
            userDict['nextUrl'] = theTuple[theTuple.find('<')+1:theTuple.find('>')]
        if theTuple.count('last') > 0:
            print 'found last'
            userDict['lastUrl'] = theTuple[theTuple.find('<')+1:theTuple.find('>')]
            linkParams = urlparse.urlsplit(userDict['lastUrl'])
            qStr = urlparse.parse_qs(linkParams[3])
            print qStr
            userDict['lastPage'] = int(qStr['page'][0])
            print 'Last Page: ' + str(userDict['lastPage'])
    print 'nextUrl: ' + userDict['nextUrl']
    pingsRemaining = int(response.info()['X-RateLimit-Remaining'])
    userDict['ratelimitReset'] =                                                                    int(response.info()['X-RateLimit-Reset'])
    userDict['ratelimitRemaining'] = pingsRemaining    
    print pingsRemaining
    print userDict['ratelimitReset']
    print userDict['nextUrl']
    linkParams = urlparse.urlsplit(theUrl)
    qStr = urlparse.parse_qs(linkParams[3])
    print qStr
    try:
        currentPage = int(qStr['page'][0])
        print 'Current Page: ' + str(currentPage)
    except KeyError:
        currentPage = 1
    if currentPage == userDict['lastPage']:
        return userDict
    else:
        if (userDict['ratelimitRemaining'] > 0):
            return githubUsers(userDict)
        else:
            while userDict['ratelimitReset'] - time.time() >= 0:
                print 'sleeping'
                time.sleep(30)
            userDict['ratelimitRemaining'] = 30
            return githubUsers(userDict)

def getSingleUser(userURL, userDict):
    if (userDict['ratelimitRemaining'] > 0):
        res = getUrl(userURL, None)
        return [json.loads(res.read()), userDict]
    else:
        while userDict['ratelimitReset'] - time.time() >= 0:
            print 'sleeping'
            time.sleep(30)
        userDict['ratelimitRemaining'] = 1
        getSingleUser(userURL, userDict)

if __name__ == '__main__':
    location = 'location:"san diego"'
    if os.path.isfile('gitDict.pkl'):
        f = open('gitDict.pkl', 'rb')
        userDict = pickle.load(f)
        userDict['lastUser'] = {'id': 0}
        f.close()
    else:
        userDict = {'nextUrl': None,                                                           'lastUser': None,                                                          'lastPage': None,                                                          'ratelimitReset': None,                                                    'ratelimitRemaining': 30,                                                'params': location,                                                      'users': []                                                               }
    userDict = githubUsers(userDict)
    f = open('gitDict.pkl', 'wb')
    pickle.dump(userDict, f)
    f.close()
    f = open('newCSV.csv', 'wb')
#    f.write(json.dumps(userDict['users']))
    with f:
        for user in userDict['users']:
            print user['url']
            userRes = getSingleUser(user['url'], userDict)
            print 'Writing *****\n' + json.dumps(userRes[0])
            lineToWrite = ''
            keyList = [
                'login',\
                'html_url',\
                'followers_url',\
                'name',\
                'company',\
                'blog',\
                'email',\
                'hireable',\
                'location',\
                'followers',\
                'public_repos'
            ]
            for key in keyList:
                try:
                    lineToWrite += userList[0][key]
                except TypeError:
                    pass
                lineToWrite += '^'
            lineToWrite += '\n'
            f.write(lineToWrite)
    f.close()

