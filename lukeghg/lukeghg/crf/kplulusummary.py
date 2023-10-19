import os
import sys
import glob
from optparse import OptionParser as OP
from xml.etree.ElementTree import ElementTree as ET
from xml.etree.ElementTree import Element,SubElement
from lukeghg.crf.crfxmlconstants import *
from lukeghg.crf.crfxmlfunctions import *
from lukeghg.crf.ppxml import PrettyPrint
from lukeghg.crf.uid340to500mapping import MapUID340to500, Create340to500UIDMapping
kp_start_year=2013
lulu_start_year=1990
start_year=kp_start_year
def CreateGHGDictionary(dirfilels):
    """
    For each file in the list:
    Read the file content, i.e. inventory results, to a list
    Then insert each inventory result to a dictionary based on the UID
    2015 inventory calls for two same uid's to be taken care of (from agriculture
    and forestry)
    """
    dictionary = {}
    for file_name in dirfilels:
        ls = ReadGHGInventoryFile(file_name)
        for item in ls:
            #print(item)
            if len(item) > 0: 
               uid = item[0]
               uid_new = uid.strip('{}')
               #2015 inventory calls for two same uid's (from agriculture
               #and forestry)-->for one uid list of several time series  
               if uid_new in dictionary:
                   #list of time series
                   #print("A",uid_new)
                   time_series = dictionary[uid_new]
                   #print("A",time_series)
                   time_series.append(item)
                   #append new time series
                   #print("A",time_series)
                   dictionary[uid_new]=time_series
               else:
                   #first time series found
                   ls_tmp=[item]
                   dictionary[uid_new]=ls_tmp
                   ls_tmp1 = dictionary[uid_new]
                   #print("B",uid_new)
                   #print("B",ls_tmp1)
                   #print("")
            else:
               print("kplulusummary.py",file_name,"Found empty line",file=sys.stderr)
    return dictionary 

def CheckActivityFile(activity_file,uid_dict):
    ls = ReadGHGInventoryFile(activity_file)
    for line in ls:
        #The first is the UID to find place in CRFReporter
        uid_to = line.pop(0)
        for uid in line:
            uid_new = uid.strip('{}')
            if not uid_new in uid_dict:
                print("kplulusummary.py",activity_file,"UID not found", uid_new,file=sys.stderr)

def KPRegionSum(activity_file,uid_dict,inventory_year):
    """
    Region sums (Region 1 and Region 2) for each activity.
    activity_file: each line has the same following format: First_UID Other_UID1 Other_UID2 ... Other_UIDN
                 First_UID: where the sum of the time series goes in CRFREporter
                 Other_UID: time series UID to be summed
    uid_dict: dictionary to find the time series themselves
    return the list of the sums with UID where to put them in CRFReporter:
    [[UID1,year1,year2...,inv_year],...,[UIDN,year1,year2,...,inv_year]]
    """
    ls = ReadGHGInventoryFile(activity_file)
    #print('Activity file',ls)
    sum_ls=[]
    reporter_sum_ls=[]
    for line in ls:
        #The first is the UID to find place in CRFReporter
        uid_to = line.pop(0)
        uid_new_to = uid_to.strip('{}')
        #Create the first list of zeros ("inital sum") from 1990 to inventory_year
        #print("SumLS",sum_ls)
        #print("UID_to",uid_new_to)
        for uid_from in line:
            #Find the time series for the UID
            uid_from_new = uid_from.strip('{}')
            #print("UIDfrom",uid_from_new)
            #One or more time series in a list
            try:
                time_series_lss = uid_dict[uid_from_new]
                #print("Time series",time_series_lss)
                first_sum_ls = time_series_lss.pop(0)
                #Remove UID
                first_sum_ls.pop(0)
                #Time series in KP differ in length: some have calculated 1990->
                #and some 2013->. Create paading list of zeros to make time series of equal length
                #We should not get problem with padding zeros, because only years 2013-> in KP
                #are imported to reporter
                padding_ls = PaddingList(inventory_year,first_sum_ls)
                first_sum_ls=padding_ls+first_sum_ls
                if len(time_series_lss) > 2:
                    print("kplulusummary.py",uid_new, "More than two with the same UID!", file=sys.stderr)
                for time_series_ls in time_series_lss:
                    #Remove the UID, not needed
                    time_series_ls.pop(0)
                    #KPLULUCF: Some have calculated  from 1990 to inventory to
                    #year, some from 2013 to inventory yesr. Fill with zeroes so that
                    #all time series are of equal length. 
                    padding_ls = PaddingList(inventory_year,time_series_ls)
                    time_series_ls = padding_ls+time_series_ls
                    sum_ls = [SumTwoValues(ConvertFloat(x),ConvertFloat(y)) for (x,y) in zip(first_sum_ls,
                                                                                         time_series_ls)]
                    #print('Series',uid_new,time_series_ls)
                    #print('Sum series',uid_new_first,sum_ls)
                    #print("")
            except KeyError:
                print("kplulusummary.py: UID",uid_from_new,"NOT IN INVENTORY",file=sys.stderr)
        #The sum for the aggregate uid_to is done 
        reporter_sum_ls.append([uid_new_to]+sum_ls)
    return reporter_sum_ls
            
#---------------------------------The main program begins--------------------------------------------------
if __name__ == "__main__":
    #Command line generator   
    parser = OP()
    parser.add_option("-p","--pxml",dest="f1",help="Read CRFReporter Party Profile xml file")
    parser.add_option("-c","--csv",dest="f2",help="Read GHG KP Inventory csv file")
    parser.add_option("-x","--xml",dest="f3",help="Write new Party profile populated with inventory results")
    parser.add_option("-y","--year",dest="f4",help="Current inventory year in CRFReporter")
    parser.add_option("-u","--uid",dest="f5",help="Read the UID files for Activities and Regions that are to be summed")
    parser.add_option("-m","--map",dest="f6",help="CRFReporter 3.0.0 --> 5.0.0 UID mapping file")
    parser.add_option("-n","--n2o",action="store_true",dest="f7",help="Data from KP4A2_D_mineraalisationcl_gl_sl.csv")

    (options,args) = parser.parse_args()

    if options.f1 is None:
        print("No input Reporter Party Profile XML data file")
        quit()
    if options.f2 is None:
        print("No input GHG inventory csv files")
        quit()
    if options.f3 is None:
        print("No output PartyProfile XML file")
        quit()
    if options.f4 is None:
        print("No inventory year given")
        quit()
    if options.f5 is None:
        print("No Activity file given")
        quit()
    if options.f6 is None:
        print("No CRFReporter 340 to 500 UID mapping file")
        quit()
    activity_file=options.f5
    if os.path.basename(activity_file).startswith('KP'):
        start_year = kp_start_year
    elif os.path.basename(activity_file).startswith('LU'):
        start_year = lulu_start_year
    else:
        print("kplulusummary.py Cannot decide if KP LULUCF or LULUCF file", activity_file,file=sys.stderr)
        quit()

    print("kplulusummary.py Summary for", activity_file,"begins")
    (uid340set,uiddict340to500) = Create340to500UIDMapping(options.f6)
    print("HELLO from kplulucf.py") 
    #Parse xml tree
    print("kplulusummary.py Parsing Party Profile xml from:",options.f1)
    t=ET()
    t.parse(options.f1)
    print("kplulusummary.py Reading GHG KP Inventory files")
    dirfilels = glob.glob(options.f2)
    print("kplulusummary.py Inserting GHG files into a dictionary")
    ghg_dict=CreateGHGDictionary(dirfilels)
    print("kplulusummary.py Reading UID files for Activities and Regions:",options.f5)

    #Check data available
    print("kplulusummary.py Checking UID exists")
    CheckActivityFile(activity_file,ghg_dict)
    print("kplulusummary.py Done")
    kp_region_sum_ls = KPRegionSum(activity_file,ghg_dict,int(options.f4))

    #This data comes from KP4A2_D_mineraalisationcl_gl_sl.csv
    if options.f7 is True:
        print("4A2_D_mineraalisationcl_gl_sl.csv conversion N2O->C:",n2o_min_c)
        kp_mineralization_ls = []
        #The conversion 
        for time_series in  kp_region_sum_ls:
            time_series = [time_series[0]]+[n2o_min_c*float(x) for x in time_series[1:]]
            kp_mineralization_ls.append(time_series)
        #Replace with converted data
        kp_region_sum_ls=kp_mineralization_ls
    not_found_uid_ls=[]
    for time_series_ls in kp_region_sum_ls:
        uid=time_series_ls.pop(0)
        uid_changed = MapUID340to500(uid,uid340set,uiddict340to500)
        if uid_changed != uid:
            print("kplulusummary.py UID changed:",uid,"-->",uid_changed)
        uid = uid_changed
        #print(uid) 
        InsertInventoryData(uid,t,time_series_ls,options.f5,not_found_uid_ls,start_year,int(options.f4))
    
    if len(not_found_uid_ls) != 0:
        print("kplulusummary.py the following", len(not_found_uid_ls), "UID not found",file=sys.stderr)
        for item in not_found_uid_ls:
            print(item,file=sys.stderr)
        
    print("kplulusummary.py Pretty print xml for humans")
    PrettyPrint(t.getroot(),0,"   ")
    print("kplulusummary.py Writing xml to:",options.f3)
    if not options.f3 is None:
        t.write(options.f3)
        print("kplulusummary.py Done")
    print("kplulusummary.py Exit program")
