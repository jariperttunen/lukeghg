#!python
from optparse import OptionParser as OP
from collections import Counter
import stat
import glob
import os
import sys
import pwd
import lukeghg.check.checkdoubleuid as check

#-------------------------Main program begins---------------------------------------
if __name__ == "__main__":
    parser = OP()
    parser.add_option("-c","--csv",dest="f1",help="Read GHG inventory csv files")

    (options,args) = parser.parse_args()
    dirfilels = []
    if options.f1 is None:
        print("No input")
        quit()
    #List the inventory files to be imported 
    dirfilels = glob.glob(options.f1)
    print(len(dirfilels),"files")
    #Generate UID file for those who make inventory
    #user_information_file = "file-owners-dict.txt"
    #dictionary = CreateUserInformation(user_information_file)
    (ls,dict1) = check.CheckDoubleUID(dirfilels)
    if len(ls) > 0:
        print("Found duplicate UID:",len(ls),file=sys.stderr)
        print("UID",'\tTimes','\tFiles','\tOwners',file=sys.stderr)
        for item in ls:
            uid = item[0]
            filels = dict1[uid]
            #Print the uid and number of times it occured 
            print(uid,item[1],end=" ",file=sys.stderr)
            #Print the files where the uid occured
            for file in filels:
                print(file,end=" ",file=sys.stderr)
            #Print the file owners
            for file in filels:
                stat_info = os.stat(file)
                user = uid = stat_info.st_uid
                try:
                    user = pwd.getpwuid(uid)[0]
                except KeyError:
                    user=uid
                print(user,end= " ",file=sys.stderr)
            print("",file=sys.stderr)
        sys.exit(1)
    else:
        print("No duplicate UID")
        sys.exit(0)

