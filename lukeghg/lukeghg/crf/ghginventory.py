import os
import sys
import glob
from xml.etree.ElementTree import ElementTree as ET
from xml.etree.ElementTree import Element,SubElement,dump
from optparse import OptionParser as OP
from lukeghg.crf.uid340to500mapping import MapUID340to500, Create340to500UIDMapping
import lukeghg.crf.ppxml as ppxml
import lukeghg.crf.crfxmlconstants as crfxmlconstants 
import lukeghg.crf.crfreporter as crfreporter

def ParseGHGInventoryFile(file,uidmapping_file,sep1=None):
    """
    Split each data row to  list of strings, delimeters are white
    space  characters by default. The  data  file  can  contain  
    A) comment starting with  '#' for the  whole file spanning  over several
    lines  and B)  comment for  the time  series in  front of  it
    starting and  ending with '#'.  The following line (so called
    list comprehension)  reads the  data file, filters  out lines
    with single  '#', then  separates the  times series  from the
    data comment and  finally splits the time series  into a list
    of strings (datals).
    """
    (uid340set,uiddict340to500) = Create340to500UIDMapping(uid_mapping_file)
    f = open(file)
    datals = [x.rpartition('#')[2].split(sep=sep1) for x in f.readlines() if x.count('#') != 1]
    uid=datals[0]
    uid = uid.replace(' ','')
    uid_stripped = uid.strip('{}')
    #Some UIDs have changed from CRFReporter version 3.4.0 to 5.0.0
    uid_changed = MapUID340to500(uid_stripped,uid340set,uiddict340to500)
    datals[0]=uid_changed
    f.close()
    return datals

def GHGToCRFReporter(file_ls,partyprofile_xml_file,crf_xml_file,uid_mapping_file,current_inventory_year,sep1=None):
    time_series_count=0
    t=ET()
    t.parse(partyprofile_xml_file)
    (uid340set,uiddict340to500) = Create340to500UIDMapping(uid_mapping_file)
    not_found_uid_ls=[]
    #Find all varibles once
    it = t.iter('variable')
    variablels = [e for e in it if e.tag=='variable']
    for file_name in file_ls:
        f=open(file_name)
        start_year = crfxmlconstants.lulu_start_year
        #Important!: all LULU files shall start with 'LU' and KPLULU files with 'KP'
        if os.path.basename(file_name).startswith('KP'):
            start_year = crfxmlconstants.kp_start_year
        elif os.path.basename(file_name).startswith('LU'):
            start_year = crfxmlconstants.lulu_start_year
        else:
            print("Cannot decide if KP LULUCF or LULUCF file", file_name,file=sys.stderr)
        #Split each data row to  list of strings, delimeters are white
        #space  characters  The  data  file  can  contain  A)  comment
        #starting with  '#' for the  whole file spanning  over several
        #lines  and B)  comment for  the time  series in  front of  it
        #starting and  ending with '#'.  The following line (so called
        #list comprehension)  reads the  data file, filters  out lines
        #with single  '#', then  separates the  times series  from the
        #data comment and  finally splits the time series  into a list
        #of strings (datals).
        datals = [x.rpartition('#')[2].split(sep=sep1) for x in f.readlines() if x.count('#') != 1]
        f.close()
        if len(datals) == 0:
            print("Empty file",file_name,file=sys.stderr)
            continue
        ##Retrieve user based on the first time series uid
        print(file_name)
        time_series=datals[0]
        #The first string in the list is the uid
        uid = time_series[0]
        uid=uid.replace(' ','')
        uid_new = uid.strip('{}')
        not_found_uid_ls=[]
        print("--------------------------------------------------------------------------")
        print("File:",file_name)
        print("--------------------------------------------------------------------------")
        for time_series in datals:
            if len(time_series) == 0:
                print(file_name,"Found empty line")
            else:
                #The first string in the list is the uid
                uid = time_series.pop(0)
                uid = uid.replace(' ','')
                uid_new = uid.strip('{}')
                time_series_count += 1
                #Some UIDs have changed from CRFReporter version 3.4.0 to 5.0.0
                uid_changed = MapUID340to500(uid_new,uid340set,uiddict340to500)
                if uid_changed != uid_new:
                    print("UID changed:",uid_new,"-->",uid_changed)
                    uid_new = uid_changed
                else:
                    print("UID:",uid_new)
                crfreporter.InsertInventoryData(uid_new,variablels,time_series,file_name,not_found_uid_ls,start_year,current_inventory_year)
                print("--------------------------------------------------------------------------")
        print("Done, total of",time_series_count,"time series")
        if len(not_found_uid_ls)==0:
            print("Found all UIDs")
        else:
            print("REMEMBER TO UPDATE PARTY PROFILE XML AFTER NEW NODES IN THE INVENTORY!",file=sys.stderr)
            print("------------------------------------------------------",file=sys.stderr)
            print("The following",len(not_found_uid_ls),"UIDs not found in current invetory:",file=sys.stderr)
            print("UID",file=sys.stderr)
            for uid in not_found_uid_ls:
                print(uid,file_name,file=sys.stderr)
            print("------------------------------------------------------",file=sys.stderr)
    print("Pretty print xml")
    ppxml.PrettyPrint(t.getroot(),0,"   ")
    print("Writing xml to:",crf_xml_file)
    t.write(crf_xml_file)
    print("Done")
    
if __name__ == "__main__":
    parser = OP()
    parser.add_option("-c","--csv",dest="f1",help="Read GHG inventory csv files")
    parser.add_option("-p","--pxml",dest="f2",help="Read CRFReporter Party Profile xml file")
    parser.add_option("-x","--xml",dest="f3",help="Write new Party profile populated with inventory results")
    parser.add_option("-m","--map",dest="f4",help="CRFReporter 3.0.0 --> 5.0.0 UID mapping file")
    parser.add_option("-y","--year",dest="f5",help="Inventory year (the last year in CRFReporter)")
    (options,arg)=parser.parse_args()
    if opions.f1 is None:
        print("No inventory GHG csv files")
        quit()
    if options.f2 is None:
        print("No CRFReporter Party Profile XML file")
        quit()
    if options.f3 is None:
        print("No CRFReporter XML output file name")
        quit()
    if options.f4 is None:
        print("No CRFReporter v3.0.0 to CRFReporter v5.0.0 UID mapping file")
        quit()
    if options.f5 is None:
        print("No last inventory year")
        quit()

    file_ls=glob.glob(options.f1)
    print("Filling",options.f2,"with GHG inventory data from",options.f1)
    print("REMEMBER TO UPDATE PARTY PROFILE XML FROM CRFREPORTER AFTER NEW NODES IN THE INVENTORY!")
    GHGToCRFReporter(file_ls,options.f2,options.f3,options.f4,int(options.f5))
