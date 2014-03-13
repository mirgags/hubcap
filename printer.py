#!/usr/bin/python
# -*- coding: utf-8 -*-
import pickle, os, re

count = 0
pattern = re.compile(r'\s+')

f = open('gitDict.pkl', 'rb')
r = pickle.load(f)
f.close()

if os.path.isfile('gitContact.csv') == True:
    f = open('gitContact.csv', 'wb')
else:
    f = open('gitContact.csv', 'wb')
    for key in r['users']['ctran']:
        f.write('%s^' % key)
    f.write('\n')

for key in r['users']:
    if r['users'][key]['hireable'] == True:
        print r['users'][key]
        for attr in r['users'][key]:
            if r['users'][key][attr]:
                if r['users'][key][attr] == True:
                    f.write('True')
                else:
                    try:
                        theString = str(r['users'][key][attr])
                        theString = re.sub(pattern, '  ', theString)
                        theString = theString.replace("^", "CARAT")
                        f.write(theString)
                    except UnicodeError:
                        f.write('Unicode Error')
                f.write('^')
            else:
                f.write("None^")
        f.write("\n")
#        f.write(key + "|" +                                                                r['users'][key]['url'] + "|" +                                             str(r['users'][key]['id']) + "|" +                                              r['users'][key]['blog'] + "|" +                                            r['users'][key]['location'] + "|" +                                        r['users'][key]['email'] + "|" +                                           r['users'][key]['company'] + "|" +                                         r['users'][key]['updated_at'] + "|" +                                      str(r['users'][key]['public_repos']) +                                     str(r['users'][key]['followers']) + "\n"                                     )
        count += 1

print "Count: ", count
f.close()
