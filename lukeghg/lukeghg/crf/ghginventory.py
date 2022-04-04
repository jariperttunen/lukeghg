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
## @file
# GHGInvnetory result files to CRFReporter.
# Functions ParseGHGInventoryFile and GHGToCRFReporter produce CRFReporter xml file from
# GHG inventoryt results. \sa ParseGHGInventoryFile() and GHGToCRFReporter()
def ParseGHGInventoryFile(data_file:str,uid_mapping_file:str,sep1:str=None):
    """! Parse GHG inventory file and return the list of time series.
    Split each data row to  list of strings. Delimeters are white space  characters by default. Comments will be filtered out. 
    Comments at the beginning of a file for the whole file start a line with `#`.
    A single line comment for a time series appears first in front the UID and starts and ends with `#`.  
    After that time series is split into a list of strings. The result is a list of lists 
    of data series including their UID's in order to locate times series positions in CRFReporter xml.

    @param data_file: GHG inventory result file.
    @param uid_mapping_file:  CRFeporter v3.0.0 to v5.0.0 UID mapping file.
    @param sep1: Time series separator value (Default is None, i.e. white space).
    @return list of lists of data series with UID.
    """
##
    ## @var $uid340set
    # Set of CRFReport v.3.0.0 UIDs
    ## @var $uiddict340to500
    # Dictionary to map CRFReporter v.3.0.0 UIDs to v.5.0.0 UIDs
    (uid340set,uiddict340to500) = Create340to500UIDMapping(uid_mapping_file)

    f = open(data_file)
    ## Parse data series, remove comments:
    # - Comments starting a line with  `#`
    # - Comment for  a time  series in  front of it before the UID starting and  ending with `#`
    #
    # Remove empty lines (result from readlines is [], empty list).
    # \sa ParseGHGInventoryFile().
    # @snippet{lineno} crf/ghginventory.py ParseGHGFile
    # @internal
    # [ParseGHGFile]
    datalss = [x.rpartition('#')[2].split(sep=sep1) for x in f.readlines() if x.count('#') != 1]
    datalss = [ x for x in datalss if x != []]
    # [ParseGHGFile]
    # @endinternal 
    for datals in datalss:
        uid=datals[0]
        uid = uid.replace(' ','')
        ## @var $uid_stripped
        # UID with curly braces removed.
        uid_stripped = uid.strip('{}')
        ## @var $uid_changed
        # Some UIDs have changed from CRFReporter version 3.4.0 to 5.0.0.
        uid_changed = MapUID340to500(uid_stripped,uid340set,uiddict340to500)
        datals[0]=uid_changed
    f.close()
    return datalss

def GHGToCRFReporter(file_ls:list,partyprofile_xml_file:str,crf_xml_file:str,uid_mapping_file:str,current_inventory_year:int,sep1:str=None,kp_1990:str=None):
    """! GHGInventory files (emissions and stocks) to CRFReporter PartyProfile xml file. 

    Parse GHG inventory files and insert time series to CRFReporter PartyProfile xml file. Write the xml to output file. 
    File names are assumed to begin with LU or KP.

    @param file_ls: List of GHG inventory csv files.
    @param partyprofile_xml_file: CRFReporter PartyProfile xml file.
    @param crf_xml_file: CRFReporter xml output file.
    @param uid_mapping_file: CRFeporter v3.0.0 to v5.0.0 UID mapping file.
    @param current_inventory_year: Inventory year.
    @param sep1: Time series separator value (Default is None).
    @param kp_1990: KP notation keys file for 1990 insertion (Default None) .
    @return None.
    """
    time_series_count=0
    t=ET()
    t.parse(partyprofile_xml_file)
    (uid340set,uiddict340to500) = Create340to500UIDMapping(uid_mapping_file)
    not_found_uid_ls=[]
##
    ## @var $it
    # Iterator to all variables in the xml tree.
    # Each `variable` node is a CRFReporter xml subtree containing place for the time series
    # including its comments. \sa variablels.
    # @snippet{lineno} crf/ghginventory.py Variables
    # @internal
    # [Variables]
    it = t.iter('variable')
    ##  @var $variablels
    # List of all variables from the iterator `it`. \sa it.
    variablels = [e for e in it if e.tag=='variable']
    # [Variables]
    # @endinternal
    # Single GHG Inventory result file to process 
    for file_name in file_ls:
        ## @var $file_name
        # GHG inventory file. Important: LULUCF file names shall start with *LU* and KPLULUCF file names with *KP*.
        ## @var $f
        # Open GHG inventory file. \sa file_name
        f=open(file_name)
        start_year = crfxmlconstants.lulu_start_year
        if os.path.basename(file_name).startswith('KP'):
            start_year = crfxmlconstants.kp_start_year
        elif os.path.basename(file_name).startswith('LU'):
            start_year = crfxmlconstants.lulu_start_year
        else:
            print("Cannot decide if KP LULUCF or LULUCF file", file_name,file=sys.stderr)
        ## Split each data row to  list of strings, delimeters are white space  characters by default.
        # The  GHG inventory  file  can  contain  comments:
        #  +  Comments starting a line with  `#` spanning  over several lines at the beginning of the file
        #     before the time series.
        #     + This section can be used to describe the content of the file.
        #  +  Comment for  a time  series in  front of it before the UID starting and  ending with `#`.
        #
        # The so called list comprehension reads the  data file, filters  out lines with single  `#`- or
        # separates the  times series  from the its comment and
        # finally splits the time series  into a list of strings in `datals`.
        # \sa GHGToCRFReporter().
        # @snippet{lineno} crf/ghginventory.py ParseLine
        # @internal
        # [ParseLine]
        datals = [x.rpartition('#')[2].split(sep=sep1) for x in f.readlines() if x.count('#') != 1]
        # [ParseLine]
        # @endinternal
        f.close()
        if len(datals) == 0:
            print("Empty file",file_name,file=sys.stderr)
            continue
        ## Collect missing UID's to a list.
        not_found_uid_ls=[]
        print("--------------------------------------------------------------------------")
        print("File:",file_name)
        print("--------------------------------------------------------------------------")
        for time_series in datals:
            if len(time_series) == 0:
                print(file_name,"Found empty line")
            else:
                ## @var  $uid
                # UID of the time series
                uid = time_series.pop(0)
                uid = uid.replace(' ','')
                ## @var $uid_new
                # UID after stripping '{}'
                uid_new = uid.strip('{}')
                time_series_count += 1
                #Some UIDs have changed from CRFReporter version 3.4.0 to 5.0.0
                ## @var $uid_changed
                # UID after mapping to new v5.0.0 UID
                uid_changed = MapUID340to500(uid_new,uid340set,uiddict340to500)
                if uid_changed != uid_new:
                    print("UID changed:",uid_new,"-->",uid_changed)
                    uid_new = uid_changed
                else:
                    print("UID:",uid_new)
                crfreporter.InsertInventoryData(uid_new,variablels,time_series,file_name,not_found_uid_ls,start_year,current_inventory_year,
                                                kp_1990)
                print("--------------------------------------------------------------------------")
        print("Done, total of",time_series_count,"time series")
        if len(not_found_uid_ls)==0:
            print("Found all UIDs")
        else:
            ## @var $file
            # Named parameter for print statement.
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
    ## @var $parser
    # Command line parser
    parser = OP()
    ## @var  $dest 
    # Command line parser's named parameter
    parser.add_option("-c","--csv",dest="f1",help="Read GHG inventory csv files")
    parser.add_option("-p","--pxml",dest="f2",help="Read CRFReporter Party Profile xml file")
    parser.add_option("-x","--xml",dest="f3",help="Write new Party profile populated with inventory results")
    parser.add_option("-m","--map",dest="f4",help="CRFReporter 3.0.0 --> 5.0.0 UID mapping file")
    parser.add_option("-y","--year",dest="f5",help="Inventory year (the last year in CRFReporter)")
    parser.add_option("-kp","--kp1990",dest="f6",help="KP notation keys file for 1990 insertion, see lukeghg/KP1990 directory")
    ## @var $options
    # Command line arguments
    ## @var arg
    # Command line arguments
    (options,arg)=parser.parse_args()## 
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
    ## @var  $kp1990_file_name
    # KP notation key file (command line option -kp1990)
    kp1990_file_name=None
    if options.f5 is None:
        print("No file for KP 1990 insertion given")
    else:
        kp1990_file_name=options.f5
    ## @var  $file_ls
    # List of GHG inventory files from command line
    file_ls=glob.glob(options.f1)
    print("Filling",options.f2,"with GHG inventory data from",options.f1)
    print("REMEMBER TO UPDATE PARTY PROFILE XML FROM CRFREPORTER AFTER NEW NODES IN THE INVENTORY!")
    GHGToCRFReporter(file_ls,options.f2,options.f3,options.f4,int(options.f5),kp1990_file_name=kp1990_file_name)
