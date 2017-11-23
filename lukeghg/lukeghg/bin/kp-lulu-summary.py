#!python
import os
import sys
import glob
from optparse import OptionParser as OP
from xml.etree.ElementTree import ElementTree as ET
from xml.etree.ElementTree import Element,SubElement
from lukeghg.crf.crfxmlconstants import *
import lukeghg.crf.crfreporter as crfreporter
from lukeghg.crf.ppxml import PrettyPrint
from lukeghg.crf.uid340to500mapping import MapUID340to500, Create340to500UIDMapping
from lukeghg.crf.kplulusummary import CheckActivityFile,CreateGHGDictionary,KPRegionSum,kp_start_year,lulu_start_year
#---------------------------------The main program begins--------------------------------------------------
if __name__ == "__main__":
    #Command line generator   
    parser = OP()
    parser.add_option("-c","--csv",dest="f2",help="Read GHG KP Inventory csv file")
    parser.add_option("-p","--pxml",dest="f1",help="Read CRFReporter Party Profile xml file")
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
    start_year=lulu_start_year
    if os.path.basename(activity_file).startswith('KP'):
        start_year = kp_start_year
    elif os.path.basename(activity_file).startswith('LU'):
        start_year = lulu_start_year
    else:
        print("Cannot decide if KP LULUCF or LULUCF file", activity_file,file=sys.stderr)
        quit()

    print("Summary for", activity_file,"begins")
    (uid340set,uiddict340to500) = Create340to500UIDMapping(options.f6)
 
    #Parse xml tree
    print("Parsing Party Profile xml from:",options.f1)
    t=ET()
    t.parse(options.f1)
    #Find all varibles once
    it = t.iter('variable')
    variablels = [e for e in it if e.tag=='variable']
    print("Reading GHG Inventory files")
    dirfilels = glob.glob(options.f2)
    print("Inserting GHG files into a dictionary")
    ghg_dict=CreateGHGDictionary(dirfilels)
    print("Reading UID files for Activities and Regions:",options.f5)

    #Check data available
    print("Checking UID exists")
    CheckActivityFile(activity_file,ghg_dict)
    print("Done")
    kp_region_sum_ls = KPRegionSum(activity_file,ghg_dict,int(options.f4))

    #This data comes from KP4A2_D_mineraalisationcl_gl_sl.csv
    if options.f7 is True:
        print("KP4A2_D_mineraalisationcl_gl_sl.csv conversion N2O->C:",n2o_min_c)
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
            print("UID changed:",uid,"-->",uid_changed)
        uid = uid_changed
        print(uid)
        #crfreporter.InsertInventoryData assumes data series are strings
        time_series_ls = [str(x) for x in time_series_ls]
        crfreporter.InsertInventoryData(uid,variablels,time_series_ls,options.f5,not_found_uid_ls,start_year,int(options.f4))
    
    if len(not_found_uid_ls) != 0:
        print("The following", len(not_found_uid_ls), "UID not found",file=sys.stderr)
        for item in not_found_uid_ls:
            print(item,file=sys.stderr)
        
    print("Pretty print xml for humans")
    PrettyPrint(t.getroot(),0,"   ")
    print("Writing xml to:",options.f3)
    if not options.f3 is None:
        t.write(options.f3)
        print("Done")
    print("Exit program")
