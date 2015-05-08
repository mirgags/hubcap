import pickle

f = open('gitDict.pkl', 'rb')
r = pickle.load(f)
f.close()
for key in r:
    print key
print r['lastUser']['id']
