#!python
import os
import pwd
from xml.etree.ElementTree import ElementTree as ET
from xml.etree.ElementTree import Element,SubElement
import datetime
import argparse
import glob
import pandas as pd
import xlsxwriter
from lukeghg.crf.uid340to500mapping import MapUID340to500, Create340to500UIDMapping
import lukeghg.crf.ghginventory as ghg
## @file
# Create ToDo list for GHG inventory. 
def GHGToDo(fprev:str,fcurrent:str,xml_file:str,outfile:str,uid_mapping_file:str,inventory_year:int):
    """! Compare two inventories.
    Compare two inventories, LU and KP files. Create two sets of inventories for previous and current respectively.
    Calculate set difference. Create Excel file sheets for time series not yet in current inventory, 
    time series in current inventory and for missing, erroneous UIDs.
     
    @param fprev: Previous inventory files (wild cards).
    @param fcurrent: Current inventory files (wild cards).
    @param xml_file: CRFReporter PartyProfyle xml file.
    @param outfile: Excel outoput file name.
    @param uid_mapping_file: CRFReporter `300_500_mappings_1.1.csv` file.
    @param inventory_year: Inventory year (last year in CRFReporter).
    @return None (write excel file).
    """
##
    #Inventory results from the previous year
    filels1 = glob.glob(fprev)
    filels1 = sorted(filels1)
    #Inventory results from the current year
    filels2= []
    if fcurrent != None:
        filels2 = glob.glob(fcurrent)
        filels2 = sorted(filels2)
    ## @var $t
    # xml.etree.ElementTree xml parser.
    t = ET()
    print("Number of files",inventory_year-1,len(filels1))
    print("Number of files",inventory_year,len(filels2))
    print("Parsing xml file", xml_file)
    t.parse(xml_file)
    it=t.iter('variable')
    variablels = [e for e in it if e.tag=='variable']
    #Create two sets of the UID identifiers
    ## @var set1
    # Previous year UIDs
    set1=set()
    ## @var set2
    # Current year UIDs
    set2=set()
    uid_file_dict1={}
    uid_file_dict2={}
    uid_missing_ls=[]
    #Read results
    print("Reading previous inventory",fprev)
    for fname in filels1:
        ls = ghg.ParseGHGInventoryFile(fname,uid_mapping_file)
        for x in ls:
            if len(x) == 0:
                print("Empty line found")
            else:
                uid1 = x.pop(0)
                #Get owner information
                ## @var $stat_info
                # python `os` library data structure for file information. 
                stat_info = os.stat(fname)
                ## @var $user
                # Owner of a file. \sa stat_info
                user = uid = stat_info.st_uid
                try:
                    user = pwd.getpwuid(uid)[0]
                except KeyError:
                    user=uid
                ## @var $varls
                # Find single `variable` from the xml that matches `uid1`.
                # @snippet{lineno} bin/ghg-todo.py FindVar
                # @internal
                # [FindVar]
                varls = [var for var in variablels if var.get('uid')==uid1]
                # [FindVar]
                # @endinternal
                if len(varls)==0:
                    #Missing UID
                    uid_missing_ls.append([uid1,fname]+x)
                else:
                    set1.add(uid1)
                    uid_file_dict1[uid1]=(fname,len(x),user,x)   
    print("Reading current inventory",fcurrent)
    for fname in filels2:
        ls = ghg.ParseGHGInventoryFile(fname,uid_mapping_file)
        for x in ls:
            if len(x) == 0:
                print("Empty line found")
            else:
                uid2 = x.pop(0)
                #get owner information
                stat_info = os.stat(fname)
                user = uid = stat_info.st_uid
                try:
                    user = pwd.getpwuid(uid)[0]
                except KeyError:
                    user=uid
                varls = [var for var in variablels if var.get('uid')==uid2]
                if len(varls)==0:
                    uid_missing_ls.append([uid2,fname]+x)
                else:
                    set2.add(uid2)
                    uid_file_dict2[uid2]=(fname,len(x),user)    
    ## @var set3
    # Take the set difference set1 and set2, i.e. missing records from the inventory. \sa set1 set2.
    set3 = set1.difference(set2)
    print("Number of inventory records:","Previous",len(set1),"Current",len(set2),"Set difference",len(set3))
    df_ls1=[]
    df_ls1.append(['Data in previous inventory '+fprev+' but not in current '+str(inventory_year)+' inventory'])
    df_ls1.append(['UID','File','Inventory Years','CRFReporter name','Owner','Data'])
    print("Creating Excel sheets for",outfile)
    if len(set3) == 0:
        print("Same set of inventory ")
    else:
        ls=list(set3)
        for uid in ls:
            varls = [var for var in variablels if var.get('uid')==uid]
            var=varls[0]
            name = var.get('name')
            fname=uid_file_dict1[uid][0]
            length=uid_file_dict1[uid][1]
            user = uid_file_dict1[uid][2]
            data = uid_file_dict1[uid][3]
            df_ls1.append([uid,fname,length,name,user]+data)
    df_ls1.append(['Date: '+str(datetime.datetime.now())])
    df1 = pd.DataFrame(df_ls1)
    df_ls2=[]
    df_ls2.append(['Current '+str(inventory_year)+' inventory'])
    df_ls2.append(['UID','File','Number of inventory years','CRFReporter name','Owner'])
    ls = list(set2)
    for uid in ls:
        varls = [var for var in variablels if var.get('uid')==uid]
        if len(varls) > 0:
            var=varls[0]
            name = var.get('name')
            fname=uid_file_dict2[uid][0]
            length=uid_file_dict2[uid][1]
            user=uid_file_dict2[uid][2]
            df_ls2.append([uid,fname,length,name,user])
    df_ls2.append(['Date: '+str(datetime.datetime.now())])
    df2 = pd.DataFrame(df_ls2)
    df_ls3=[]
    df_ls3.append(['Missing UID '+str(inventory_year)])
    df_ls3.append(['UID','File'])
    for data in uid_missing_ls:
        df_ls3.append(data)
    df_ls3.append(['Date: '+str(datetime.datetime.now())])
    df3 = pd.DataFrame(df_ls3)
    print("Creating Excel file",outfile)
    writer = pd.ExcelWriter(outfile,engine='xlsxwriter')
    df1.to_excel(writer,sheet_name='Data not in '+str(inventory_year))
    df2.to_excel(writer,sheet_name=str(inventory_year)+' inventory data')
    df3.to_excel(writer,sheet_name='Missing UID '+str(inventory_year))
    writer.save()
#---------------------------------The main program begins--------------------------------------------------
#Command line generator
if __name__ == "__main__":
    ## @var $parser
    # Command line parser
    parser = argparse.ArgumentParser()
    ## @var $required
    # Command line parser required arguments
    ## @var $dest
    # Command line parser argument
    ## @var $int
    # Command line parser argument data type. \sa type.
    ## @var type
    # Command line parser argument types.
    ## @var $str
    # Command line parser argument data type. \sa type.
    ## @var $help
    # Command line parser `help` argument
    ## @var $True
    ## Command line parser argments are required. \sa required. 
    parser.add_argument("-f1",type=str,dest="f1",required = True,help="Read input ghg result files (wild card search),previous year")
    parser.add_argument("-f2",type=str,dest="f2",required = True,help="Read input ghg result files (wild card search), current year")
    parser.add_argument("-x",type=str,dest="x",required = True,help="CRFReporter Simple XML file for current year")
    parser.add_argument("-o",type=str,dest="o",required = True,help="Output Excel file for missing inventory categories")
    parser.add_argument("-m",type=str,dest="m",required = True,help="CRFReporter 3.0.0 --> 5.0.0 UID mapping file")
    parser.add_argument("-y",type=int,dest="y",required=True,help="Inventory year")
    ## @var $args
    # Command line arguments
    args = parser.parse_args()
    GHGToDo(args.f1,args.f2,args.x,args.o,args.m,args.y)
    print("Done")

