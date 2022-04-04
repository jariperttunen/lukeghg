from optparse import OptionParser as OP
from collections import Counter
import stat
import glob
import os

## @file
# Collect double UIDs. 
# CheckDoubleUID collects information about UIDs occuring more than once in GHG inventory.

## @defgroup UserInfo User Information
# Collect user information to a dictionary
# @{
def CreateUserInformation(file_name:str):
    """! Transfer content of file to dictionary for UIDs holding information file name, date modified and owner 
    @param file_name
    @return dictionary
    @sa dict
    """
##
    ## @var $dict
    # Dictionary holding file name and owner information for UIDs 
    dict={}
    f = open(file_name)
    #Split each data row to list of strings, delimeters are white space characters
    ls = [x.split() for x in f.readlines()]
    f.close()
    #Create dictionary based on uid indexing a pair (file name, user name) 
    for (uid,fname,modified,user) in ls:
        #print(uid,fname,modified,user)
        uid_new =  uid_new = uid.strip('{}')
        dict[uid_new] = (fname,modified,user)
    return dict
## @}

## @defgroup CheckDouble Check double UID
# Check and return list of UIDs occuring twice or more 
# @{
def CheckDoubleUID(dirfilels:list):
    """! Check and collect information about UIDs occuring in the GHG inventory
    @param dirfilels: List for inventory files
    @return 2-tuple (ls,dictionary): List of UIDs occuring more than once 
    and Dictionary associating UIDs to their files
    @sa ls 
    @sa dictionary
    """
##
    ## @var $c
    # Counter from `collections` package.
    # Count the UID occurings (frequencies).
    c = Counter()
    ## @var dictionary
    # Dictionary to associate UID to its files.
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
    #Sort UID occurences in descending order
    uidls = c.most_common()
    #print(uidls)
    #print(len(uidls))
    ## @var $ls
    # Collect all UIDs occurung more than once.
    ls = [item for item in uidls if item[1] > 1]
    return (ls,dictionary)
## @}
