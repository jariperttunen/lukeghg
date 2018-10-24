from xml.etree.ElementTree import ElementTree as ET
from xml.etree.ElementTree import Element,SubElement
import datetime
import argparse
import glob
import pandas as pd
import xlsxwriter
from lukeghg.crf.uid340to500mapping import MapUID340to500, Create340to500UIDMapping
import lukeghg.crf.ghginventory as ghg

def GHGToDo(fprev,fcurrent,xml_file,outfile,uid_mapping_file):
    #Inventory results from the previous year
    filels1 = glob.glob(fprev)
    filels1 = sorted(filels1)
    #Inventory results from the current year
    filels2 = glob.glob(fcurrent)
    filels2 = sorted(filels2)
    t = ET()
    t.parse(xml_file)
    it=t.iter('variable')
    variablels = [e for e in it if e.tag=='variable']
    #Create two sets of the UID identifiers
    #Previous year
    set1=set()
    #Current year
    set2=set()
    uid_file_dict={}
    uid_missing_ls=[]
    #Read results
    for fname in filels1:
        ls = ghg.ParseGHGInventoryFile(fname,uid_mapping_file)
        for x in ls:
            if len(x) == 0:
                print("Empty line found")
            else:
                uid1 = x.pop(0)
                set1.add(uid1)
                uid_file_dict[uid1]=(fname,len(x))
    for fname in filels2:
        ls = ghg.ParseGHGInventoryFile(fname,uid_mapping_file)
        for x in ls:
            if len(x) == 0:
                print("Empty line found")
            else:
                uid2 = x.pop(0)
                set2.add(uid2)
                uid_file_dict[uid2]=(fname,len(x))
                varls = [var for var in variablels if var.get('uid')==uid2]
                if len(varls)==0:
                    print('UID2',uid2,fname)
                    uid_missing_ls.append([uid2,fname])
    #Take the set difference, i.e. missing records from the inventory
    set3 = set1.difference(set2)
    df_ls1=[]
    df_ls1.append(['Data in 2016 but not in 2017'])
    df_ls1.append(['UID','File','Number of inventory years','CRFReporter name'])
    print("Number of inventory records",len(set1),len(set2),len(set3))
    if len(set3) == 0:
        print("Same set of inventory ")
    else:
        ls=list(set3)
        for uid in ls:
            varls = [var for var in variablels if var.get('uid')==uid]
            var=varls[0]
            name = var.get('name')
            fname=uid_file_dict[uid][0]
            length=uid_file_dict[uid][1]
            df_ls1.append([uid,fname,length,name])
    df_ls1.append(['Date: '+str(datetime.datetime.now())])
    df1 = pd.DataFrame(df_ls1)
    df_ls2=[]
    df_ls2.append(['Current '+str(datetime.datetime.now().year-1)+' inventory'])
    df_ls2.append(['UID','File','Number of inventory years','CRFReporter name'])
    ls = list(set2)
    for uid in ls:
        varls = [var for var in variablels if var.get('uid')==uid]
        if len(varls) > 0:
            var=varls[0]
            name = var.get('name')
            fname=uid_file_dict[uid][0]
            length=uid_file_dict[uid][1]
            df_ls2.append([uid,fname,length,name])
    df_ls2.append(['Date: '+str(datetime.datetime.now())])
    df2 = pd.DataFrame(df_ls2)
    df_ls3=[]
    df_ls3.append(['Missing UID 2017'])
    df_ls3.append(['UID','File'])
    for data in uid_missing_ls:
        df_ls3.append(data)
    df_ls3.append(['Date: '+str(datetime.datetime.now())])
    df3 = pd.DataFrame(df_ls3)
    writer = pd.ExcelWriter(outfile,engine='xlsxwriter')
    df1.to_excel(writer,sheet_name='Missing from 2017')
    df2.to_excel(writer,sheet_name='2017 inventory')
    df3.to_excel(writer,sheet_name='Missing UID 2017')
    writer.save()
#---------------------------------The main program begins--------------------------------------------------
#Command line generator   
parser = argparse.ArgumentParser()
parser.add_argument("-f1",type=str,dest="f1",help="Read input ghg result files (wild card search),previous year")
parser.add_argument("-f2",type=str,dest="f2",help="Read input ghg result files (wild card search), current year")
parser.add_argument("-x",type=str,dest="x",help="CRFReporter Simple XML file for current year")
parser.add_argument("-o",type=str,dest="o",help="Output Excel file for missing inventory categories")
parser.add_argument("-m",type=str,dest="m",help="CRFReporter 3.0.0 --> 5.0.0 UID mapping file")
#parser.add_argument("-u",type=str,dest="f5",help="File for dictionary of (UID,file name, date modified, file owner) from previous year")

args = parser.parse_args()

if args.f1 is None:
    print("No input ghg inventory results files, previous year")
    quit()
if args.f2 is None:
    print("No input ghg inventory results files, current year")
    quit()
if args.x is None:
    print("No input CRFReporter Simple XML file to generate human readable output")
    quit()
if args.o is None:
    print("No output file for missing inventory categories")
    quit()
if args.m is None:
    print("No output file for missing inventory categories")
    quit()

GHGToDo(args.f1,args.f2,args.x,args.o,args.m)


