#!python
import os
from xml.etree.ElementTree import ElementTree as ET
from xml.etree.ElementTree import Element,SubElement,dump
from optparse import OptionParser as OP
import sys,glob
from lukeghg.crf.uid340to500mapping import MapUID340to500, Create340to500UIDMapping
from lukeghg.crf.ppxml import PrettyPrint
from lukeghg.crf.crfxmlconstants import *
from lukeghg.crf.crfxmlfunctions import *

def InsertNIR3TableInventoryData(uid,t,datals,file,not_found_uid_ls,start_year,inventory_year):
    """
    Insert time series to CRFReporter Party Profile xml file
    uid: The CRFReporter unique identifier for the time series
    t:   The ElementTree representation of the Party Profile xml file
    not_found_uid_ls: Collect UIDs not found to this list
    start_year: Inventory start year (LULUCF 1990, KPLULUCF 2013
    inventory_year: Current inventory year, i.e. the last year in CRFReporter.
    """
    print(file,uid)
    it = t.iter('variable')
    variablels = [e for e in it if e.tag=='variable']
    #Find the time series that match the UID
    varls = [var for var in variablels if var.get('uid')==uid]
    if len(varls) == 0:
        print("UID:", uid, "not found, doing nothing",file=sys.stderr)
        not_found_uid_ls.append(uid)
    elif len(varls)> 1:
        print("UID:", uid, "not unique, found",len(uidls),"time series, doing nothing",file=sys.stderr)
    else:
        #Now start populating xml with time series data
        variable=varls[0]
        #This element is a list of length two: a) the time series and b) the comment
        yearscommentls = list(variable)
        #Time series is the first one
        years = yearscommentls[0]
        #The time series is now in a list 
        yearls = list(years)
        #Sort the list
        yearls.sort(key=SortYearList)
        #print("UID:",uid,)
        if len(yearls) == 0:
            print('NO RECORD',uid, len(yearls), len(datals))
        if start_year == kp_start_year:
            print("Inventory start 2013, assuming KPLULUCF")
            #Reverse both year records in XML and the inventory data list 
            yearls.reverse()
            #Now, for KP LULUCF the inventory xml seems to be in constant change.
            #At the moment, fall 2015 Reporter version 5.10.x, the years 1990->2013 are present
            #But that will change back to previous, i.e years start from 2013. Another possible
            #change is that Kai Skoglund will kindly insert years up to 2020 as before.
            #The only stable solution is that at this point all years outside the inventory
            #will be filtered out.
            yearls=[x for x in yearls if int(x.get('name')) >= kp_start_year and int(x.get('name')) <= inventory_year]
        for year_record in yearls:
            #A year_record has name and uid attributes, a single value and comment subtrees
            recordls = list(year_record)
            #dump(year_record)
            #Take the record itsels that has the single value and the comment
            record = recordls[0]
            #dump(record)
            #Take the value and the comment
            valuecommentls = list(record)
            #Time series value is the first
            value = valuecommentls[0]
            #dump(value)
            #value.text = str(datals[0])
            data = None
            if len(datals) > 1:
                data = str(datals[1])
                print(year_record.get('name'),value.text,"<----",str(datals[1]))
            else:
                data = str(datals[0])
                print(year_record.get('name'),value.text,"<----",str(datals[0]))
            value.text = str(data)
            #The  EU 529  Submission  requires the  (base)  year 1990  for
        #Cropland  management  KP.B.2   and  Grazing  land  management
        #KP.B.3. This is denoted in the file name.
        basename=os.path.basename(file)
        if "EU529" in basename:
            yearls=list(years)
            yearls.sort(key=SortYearList)
            #1990 is now the first, 2014 last in datals
            #Only 1990 is needed
            datals=datals[:1]
            print("EU 529 submission, adding the base year 1990") 
            for year_record,data in zip(yearls,datals):
                recordls= list(year_record)
                record=recordls[0]
                valuecommentls=list(record)
                value=valuecommentls[0]
                try:
                    #round to six decimals
                    data_round = float(format(float(data),crf_precision))
                    if data_round == 0.0:
                        #if the value is zero after rounding use with original accuracy
                        print(year_record.get('name'),value.text,"<----",str(data))
                        if (float(data)== 0.0):
                            print(file,uid,"Zero value",year_record.get('name'),file=sys.stderr)
                        value.text = str(data)
                    else:
                        #otherwise use the rounded value
                        print(year_record.get('name'),value.text,"<----",str(data_round))
                        value.text = str(data_round)
                #Notation key if not successfull conversion to floating point
                except ValueError:
                    print(year_record.get('name'),value.text,"<----",str(data))
                    value.text = str(data)

#---------------------------------The main program begins--------------------------------------------------
#Command line generator
parser = OP()
parser.add_option("-c","--csv",dest="f1",help="Read GHG inventory NIR3 tablefiles")
parser.add_option("-p","--pxml",dest="f2",help="Read CRFReporter Party Profile xml file")
parser.add_option("-x","--xml",dest="f3",help="Write new Party profile populated with Notation Key comments")
parser.add_option("-m","--map",dest="f4",help="CRFReporter 3.0.0 --> 5.0.0 UID mapping file")
parser.add_option("-y","--year",dest="f5",help="GHG Inventory year (last year in CRFReporter)")
(options,args) = parser.parse_args()
 
if options.f1 is None:
    print("No input NIR3 table files")
    quit()
if options.f2 is None:
    print("No input Party Profile xml file")
    quit()
if options.f3 is None:
    print("No output Party Profile xml file")
    quit()
if options.f4 is None:
    print("No output Party Profile xml file")
    quit()
if options.f5 is None:
    print("No GHG inventory year")
    quit()
    
#List the inventory files to be imported 
dirfilels = glob.glob(options.f1)
print("Parsing  Party Profile xml from:",options.f2)
t=ET()
t.parse(options.f2)
print("Creating UID mapping from", options.f4)
(uid340set,uiddict340to500) = Create340to500UIDMapping(options.f4)
not_found_uid_ls=[]
for file in dirfilels:
    f=open(file)
    print("Reading file",file)
    #datals = f.readlines()
    #datals = [x.strip('\n') for x in datals]
    #Split comments using ';' separator
    datals = [x.rpartition('#')[2].split(';') for x in f.readlines() if x.count('#') != 1]
    f.close()
    #datals = [x.split(';') for x in datals]
    counter=1
    for  nir3table_ls in datals:
        if len(nir3table_ls) == 0:
            print("Found empty line")
        else:
            #The first string in the list is the uid
            uid = nir3table_ls.pop(0)
            nir3table_ls = [x.strip('\n') for x in nir3table_ls]
            #print(nkcomments_ls)
            #The old reporter wrapped uid in {}, the new one does not
            uid1 = uid.strip(' ')
            uid_new = uid1.strip('{}')
            #Some UIDs have changed from CRFReporter version 3.4.0 to 5.0.0
            uid_changed = MapUID340to500(uid_new,uid340set,uiddict340to500)
            if uid_changed != uid_new:
                print("UID changed:",uid_new,"-->",uid_changed)
                uid_new = uid_changed
            InsertNIR3TableInventoryData(uid_new,t,nir3table_ls,file,not_found_uid_ls,kp_start_year,int(options.f5))
            counter = counter+1
print("Pretty printing xml to human readable form")
PrettyPrint(t.getroot(),0,"   ")
print("Writing xml file to",options.f3)
t.write(options.f3)
