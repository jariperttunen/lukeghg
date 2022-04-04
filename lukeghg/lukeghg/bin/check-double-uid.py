#!python
from optparse import OptionParser as OP
from collections import Counter
import stat
import glob
import os
import sys
import pwd
import datetime
import pandas as pd
import xlsxwriter
import lukeghg.check.checkdoubleuid as check
## @file
# Create Excel file for double UIDs.
# Create Excel file for UIDs occuring twice or more in the GHG inventory.
# @sa CheckDoubleUID

#-------------------------Main program begins---------------------------------------
if __name__ == "__main__":
    parser = OP()
    parser.add_option("-c","--csv",dest="f1",help="Read GHG inventory csv files")
    parser.add_option("-o","--excel",dest="f2",help="Excel file")
    (options,args) = parser.parse_args()
    dirfilels = []
    if options.f1 is None:
        print("No input")
        quit()
    if options.f2 is None:
        print("No Excel file")
        quit()
    #List the inventory files to be imported
    ## @var  $dirfilels
    # GHG inventory files.
    dirfilels = glob.glob(options.f1)
    print(len(dirfilels),"files")
    #Generate UID file for those who make inventory
    #user_information_file = "file-owners-dict.txt"
    #dictionary = CreateUserInformation(user_information_file)
    (ls,dict1) = check.CheckDoubleUID(dirfilels)
    ## @var df_ls
    # List for the data found by CheckDoubleUID.
    # Eventually turned to data frame  
    # @sa  CheckDoubleUID
    # @sa df 
    df_ls = []
    if len(ls) > 0:
        print("Found duplicate UID:",len(ls),file=sys.stderr)
        df_ls.append(["Found duplicate UID:",len(ls)])
        print("UID",'\tTimes','\tFiles','\tOwners',file=sys.stderr)
        df_ls.append(['UID','Times','Files','Owners'])
        for item in ls:
            duplicate_ls=[]
            uid = item[0]
            filels = dict1[uid]
            #Print the uid and number of times it occured 
            print(uid,item[1],end=" ",file=sys.stderr)
            #Print the files where the uid occured
            duplicate_ls.append(uid)
            duplicate_ls.append(item[1])
            for file in filels:
                duplicate_ls.append(file)
                print(file,end=" ",file=sys.stderr)
            #Print the file owners
            for file in filels:
                stat_info = os.stat(file)
                user = uid = stat_info.st_uid
                try:
                    user = pwd.getpwuid(uid)[0]
                    duplicate_ls.append(user)
                except KeyError:
                    user=uid
                    duplicate_ls.append(user)
                print(user,end= " ",file=sys.stderr)
            print("",file=sys.stderr)
            df_ls.append(duplicate_ls)
        df_ls.append(['Date: '+str(datetime.datetime.now())])
        ## @var $df
        # Data frame for Excel sheet
        # @sa $df_ls
        df = pd.DataFrame(df_ls)
        writer = pd.ExcelWriter(options.f2,engine='xlsxwriter')
        df.to_excel(writer,sheet_name='Duplicate UID')
        writer.save()
        sys.exit(1)
    else:
        print("No duplicate UID")
        sys.exit(0)

