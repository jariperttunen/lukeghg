from optparse import OptionParser as OP
from collections import Counter
import stat
import glob
import os

def CreateUserInformation(file):
    dictionary={}
    f = open(file)
    #Split each data row to list of strings, delimeters are white space characters
    ls = [x.split() for x in f.readlines()]
    f.close()
    #Create dictionary based on uid indexing a pair (file name, user name) 
    for (uid,fname,modified,user) in ls:
        #print(uid,fname,modified,user)
        uid_new =  uid_new = uid.strip('{}')
        dictionary[uid_new] = (fname,modified,user)
    return dictionary

def CheckDoubleUID(dirfilels):
    c = Counter()
    dictionary={}
    for file in dirfilels:
        f = open(file)
        #print(file)
        #Split each data row to list of strings, delimeters are white space characters
        datals=[x.rpartition('#')[2].split() for x in f.readlines() if x.count('#') != 1]
        #print(datals)
        f.close()
        ##Retrieve user based on the first time series uid
        for time_series in datals:
            if len(time_series) > 0:
                #print(time_series)
                #The first string in the list is the uid
                uid = time_series[0]
                uid_new = uid.strip('{}')
                #Collect the files where the uid occured
                if uid_new in dictionary:
                    dictionary[uid_new].append(file)
                else:
                    dictionary[uid_new]=[file]
                c[uid_new]+=1
    uidls = c.most_common()
    #print(uidls)
    #print(len(uidls))
    ls = [item for item in uidls if item[1] > 1]
    return (ls,dictionary)

