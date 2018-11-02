import os
import sys
import glob
from xml.etree.ElementTree import ElementTree as ET
from xml.etree.ElementTree import Element,SubElement,dump
from optparse import OptionParser as OP
from lukeghg.crf.uid340to500mapping import MapUID340to500, Create340to500UIDMapping
from lukeghg.crf.ppxml import PrettyPrint
from lukeghg.crf.crfxmlconstants import lulu_hwp_start_year,lulu_start_year,kp_start_year,crf_precision

#filter KPLULUCF and LULUCF sectors
keywordls = ['4(KP)','NIR-1','NIR-2','NIR-3','HWP','Cropland',
             'Forest Land','Forest land','Grassland','Settlements','Wetlands',
             'Other Land','wood products','Wood','Sawnwood','Wood panels','Woodpanels',
             'Paper','Harvested Wood','Land Transition Matrix',
             'Land Use','LULUCF']

#LULUCF HWP start year is 1961
#LULUCF and KPLULUCF start years 1990 and 2013 respectively
user_information_file = "file-owners-dict.txt"
#Current inventory year is mandatory information from command line
current_inventory_year=0
#Precision to use when when impoting data to CRFREporter
#crf_precision='.6f'

class WrongTypeError(ValueError):
    def __init__(self,arg):
        self.args=arg

def CreateScenarioExcel(file_out,t,dirls,uid340set,uiddict340to500):
    """Paula's scenario to excel
       file_out: output file
       t: xml tree
       dirls: list of inventory file names
       uid340set: set of uid that have changed
       uiddict340to500: mapping of changed uid from CrfReporter 3.4.0 to 5.0.0
    """
    fout = open(file_out,'w')
    for file in dirls:
        fin = open(file)
        datals = [x.split() for x in fin.readlines()]
        fin.close()
        for time_series in datals:
            print(time_series)
            uid = time_series.pop(0)
            uid_new = uid.strip('{}')
            uid_changed = MapUID340to500(uid_new,uid340set,uiddict340to500)
            it = t.iter('variable')
            variablels=[e for e in it if e.tag == 'variable']
            variablels.sort(key=SortKey)
            print(uid_changed)
            varls = [var for var in variablels if var.get('uid') == uid_changed]
            print(len(varls))
            var = varls[0]
            name = var.get('name')
            name = name.replace('[','#[')
            fout.write(uid_changed)
            fout.write(name+"#")
            for val in time_series:
                fout.write(val+'#')
            fout.write('\n')
    fout.close()
    
def CreateUserInformation(file):
    dictionary={}
    f = open(file)
    #Split each data row to list of strings, delimeters are white space characters
    ls = [x.split() for x in f.readlines()]
    f.close()
    #Create dictionary based on uid indexing a pair (file name, user name)
    for (uid,fname,modified,user) in ls:
        #print(uid,fname,modified,user)
        uid_new = uid.strip('{}')
        dictionary[uid_new] = (fname,modified,user)
    return dictionary

#Go through the list of keywords and return true if any of the
#keywords are part of the name  
def HasKeyword(keywordls,name):
    for keyword in keywordls:
        if keyword in name:
            return True
    return False

def SortKey(x):
    return x.get('name')

def SortYearList(year):
    y = year.get('name')
    return int(y)

def WriteHeader(f,begin,end):
    f.write('UID'+"#")
    f.write('Name'+"########Gas#Unit#")
    yearls = [x for x in range(begin,end+1)]
    for year in yearls:
        f.write(str(year)+"#")
    f.write("\n")

def WriteFalseInput(f,variable):
    yearcommentls = list(variable)
    years = yearcommentls[0]
    yearls = list(years)
    yearls.sort(key=SortYearList)
    uid = variable.get('uid')
    name = variable.get('name')
    name = name.replace('[','#[')
    s = "#######################"
    write_time_series = False
    #Don'tcheck other sectors than LULUCF and KPLULUCF
    if not HasKeyword(keywordls,name):
        return
    else:
        if yearls[0].get('name') == '2013':
            year = yearls[0]
            rls = list(year)
            r = rls[0]
            valuels = list(r)
            value = valuels[0]
            if value.text == None:
                return
             #Check the keywords
            keyset=set(value.text.split(','))
            sdiff = keyset.difference(nkset) 
            if len(sdiff)==0:
                return
            #Next try to convert to float
            try:
                d = float(value.text.replace(',',''))
                #If a number then return (OK)
                return
            except ValueError:
                write_time_series = True
            #Write the time series
            if write_time_series == True:
                f.write(uid)
                f.write(name+"#")
                f.write(s+value.text+"#\n")
            return
        else:
            #LULUCF
            #Check the values for the time series
             for year in yearls:
                rls = list(year)
                r = rls[0]
                valuels = list(r)
                value = valuels[0]
                if value.text == None:
                    return
                #If a notation key then no need to write
                keyset = set(value.text.split(','))
                sdiff = keyset.difference(nkset) 
                if len(sdiff) == 0:
                    return
                #Check if a number
                try:
                    d = float(value.text.replace(',',''))
                    #if success return
                    return
                except ValueError:
                    write_time_series = True
                #If any value is wrong kind or does not exist write the whole time series
                if write_time_series == True:
                    f.write(uid)
                    f.write(name+"#")
                    for year in yearls:
                        rls = list(year)
                        r = rls[0]
                        valuels = list(r)
                        value = valuels[0]
                        f.write(value.text+"#")
                    f.write('\n')
        return
        
def WriteEmptyAndFalseVariables(f,variable):
    yearcommentls = list(variable)
    years = yearcommentls[0]
    yearls = list(years)
    yearls.sort(key=SortYearList)
    uid = variable.get('uid')
    name = variable.get('name')
    name = name.replace('[','#[')
    s = "#######################"
    write_time_series = False
    #Don'tcheck other sectors than LULUCF and KPLULUCF
    if not HasKeyword(keywordls,name):
        return
    else:
        if yearls[0].get('name') == '2013':
            year = yearls[0]
            rls = list(year)
            r = rls[0]
            valuels = list(r)
            value = valuels[0]
            if value.text == None:
                value.text = 'None'
            #For KPLULUCF check for NA
            #if 'NA' in value.text:
            #    write_time_series = True
            #Check the keywords
            keyset=set(value.text.split(','))
            sdiff = keyset.difference(nkset) 
            if len(sdiff)==0 and write_time_series == False:
                return
            #Next try to convert to float
            try:
                d = float(value.text.replace(',',''))
                #If a number then return (OK)
                return
            except ValueError:
                write_time_series = True
            #Write the time series
            if write_time_series == True:
                f.write(uid)
                f.write(name+"#")
                f.write(s+value.text+"#\n")
            return
        else:
            #LULUCF
            #Check the values for the time series
            if len(yearls) < 24:
                write_time_series = True
            for year in yearls:
                rls = list(year)
                r = rls[0]
                valuels = list(r)
                value = valuels[0]
                if value.text == None:
                    value.text = 'None'
                #If a notation key then no need to write
                keyset = set(value.text.split(','))
                sdiff = keyset.difference(nkset) 
                if len(sdiff) == 0 and write_time_series == False:
                    return
                #Check if a number
                try:
                    d = float(value.text.replace(',',''))
                    #if success return
                    if write_time_series == False:
                        return
                except ValueError:
                    write_time_series = True
            #If any value is wrong kind or does not exist write the whole time series
            if write_time_series == True:
                f.write(uid)
                f.write(name+"#")
                for year in yearls:
                    rls = list(year)
                    r = rls[0]
                    valuels = list(r)
                    value = valuels[0]
                    f.write(value.text+"#")
                f.write('\n')
            return
            
def WriteVariables(f,variable,dictionary,all):
    yearcommentls = list(variable)
    years = yearcommentls[0]
    yearls = list(years)
    yearls.sort(key=SortYearList)
    uid = variable.get('uid')
    name = variable.get('name')
    if all==True or HasKeyword(keywordls,name):
        f.write(uid)
        print(name)
        #put square brackets into different columns
        name=name.replace('[','#[')
        f.write(name+"#")
        fname =""
        modified=""
        fowner=""
        #File data for the time series
        if uid in dictionary:
            fname = dictionary[uid][0]
            modified = dictionary[uid][1]
            fowner = dictionary[uid][2]
        for year_record in yearls:
            #A year_record has name and uid attributes, a single value and comment subtrees
            recordls = list(year_record)
            #Take the record itself that has the single value and the comment
            record=recordls[0]
            #Take the value and the comment
            valuecommentls=list(record)
            #Time series value is the first
            value = valuecommentls[0]
            if value.text != None:
                s=value.text
                #Documentation boxes may contain long explanations with newline characters
                s=s.replace('\n',' ')
                f.write(s+"#")
            else:
                f.write('#')
        f.write(fname+"#"+modified+"#"+fowner+"#")
        f.write("\n")
        
def CheckUIDInXml(uid,variablels):
    #Find the time series that match the UID
    varls = [var for var in variablels if var.get('uid')==uid]
    if len(varls)==0:
        return False
    else:
        return True
    
def InsertInventoryData(uid,variablels,datals,file_name,not_found_uid_ls,start_year,inventory_year,kp_1990=None):
    """Insert inventory data to the CRFReporter PartyProfile xml
       uid: The variable identifier
       variablels: the list of all variables from the CRFReporter xml
       datals: the time series/data to be inserted
       file_name: the time series file
       not_found_uid_ls: collect uid's not found in variables (perhaps due to a typo)
       start_year: Inventory start year (LULUCF 1990/KPLULUCF 1993)
       inventory_year: the last year in CRFReporter
    """
    #it = t.iter('variable')
    #variablels = [e for e in it if e.tag=='variable']
    #Find the time series that match the UID
    varls = [var for var in variablels if var.get('uid')==uid]
    if len(varls) == 0:
        #print("UID:", uid, "not found, doing nothing",file=sys.stderr)
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
        first_year=yearls[0]
        first_year_number=int(first_year.get('name'))
        if len(yearls) != len(datals):
            print("Warning! File:",file_name,uid,"datalength",len(datals),"differs from number of records",len(yearls),"in XML file")
            print("Warning! File:",file_name,uid,"datalength",len(datals),"differs from number of records",len(yearls),"in XML file",file=sys.stderr)
        if len(yearls) == 0:
            print('NO RECORD',uid, len(yearls), len(datals),file=sys.stderr)
        if start_year == kp_start_year:
            print("File:",file_name,"Inventory start 2013, assuming KPLULUCF")
            #Reverse both year records in XML and the inventory data list 
            yearls.reverse()
            #The last value is the current inventory year  in the data series
            datals.reverse()
            #Now, for KP LULUCF the inventory xml seems to be in constant change.
            #At the moment, fall 2015 Reporter version 5.10.x, the years 1990->2013 are present
            #But that will change back to previous, i.e years start from 2013. Another possible
            #change is that Kai Skoglund will kindly insert years up to 2020 as before.
            #The only stable solution is that at this point all years outside the inventory
            #will be filtered out.
            yearls=[x for x in yearls if int(x.get('name')) >= kp_start_year and int(x.get('name')) <= inventory_year]
        if first_year_number == lulu_hwp_start_year and start_year==lulu_start_year:
            yearls.reverse()
            datals.reverse()
            print("Note! File:",file_name,uid,"start year is", lulu_hwp_start_year,"filling XML from", yearls[0].get('name'),"backwards")
            print("Note! File:",file_name,uid,"start year is", lulu_hwp_start_year,"filling XML from", yearls[0].get('name'),"backwards",file=sys.stderr)
        for year_record,data in zip(yearls,datals):
            #A year_record has name and uid attributes, a single value (data to be inserted) and comment subtrees
            #Special case HWP requires Exported or Domestically consumed information
            #print(data)
            if data.startswith("Domestic"):
                data="Domestically consumed"
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
            try:
                #round to six decimals
                data_round = float(format(float(data),crf_precision))
                if data_round == 0.0:
                    #if the value is zero after rounding use with original accuracy
                    print(year_record.get('name'),value.text,"<----",str(data))
                    if (float(data)== 0.0):
                        print(file_name,uid,"Zero value",year_record.get('name'),file=sys.stderr)
                    value.text = str(data)
                else:
                    #otherwise use the rounded value
                    print(year_record.get('name'),value.text,"<----",str(data_round))
                    value.text = str(data_round)
            #Notation key or other string if not successfull conversion to floating point
            except ValueError:
                print(year_record.get('name'),value.text,"<----",str(data))
                value.text = str(data)
        #The  EU 529  Submission  requires the  (base)  year 1990  for
        #Cropland  management  KP.B.2   and  Grazing  land  management
        #KP.B.3. This is denoted in the file name.
        #From 2017 inventory the same applies also for the normal submission
        #The file kp_1990 denotes that single file.
        basename=os.path.basename(file_name)
        if "EU529" in basename or basename==kp_1990:
            yearls=list(years)
            yearls.sort(key=SortYearList)
            #1990 is now the first, the current inventory year last in datals
            datals.reverse()
            #Only 1990 is needed
            datals=datals[:1]
            print("KP file:",basename,"adding the base year 1990") 
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
                            print(file_name,uid,"Zero value",year_record.get('name'),file=sys.stderr)
                        value.text = str(data)
                    else:
                        #otherwise use the rounded value
                        print(year_record.get('name'),value.text,"<----",str(data_round))
                        value.text = str(data_round)
                #Notation key if not successfull conversion to floating point
                except ValueError:
                    print(year_record.get('name'),value.text,"<----",str(data))
                    value.text = str(data)


def main():
    #---------------------------------The main program begins--------------------------------------------------
    #Command line generator   
    parser = OP()
    parser.add_option("-u","--uid",dest="f1",help="Create '#' separated text file for each UID for excel")
    parser.add_option("-p","--pxml",dest="f2",help="Read CRFReporter Party Profile xml file")
    parser.add_option("-x","--xml",dest="f3",help="Write new Party profile populated with inventory results")
    parser.add_option("-c","--csv",dest="f4",help="Read GHG inventory csv files")
    parser.add_option("-a","--all",action="store_true",dest="f5",default=False,help="Print all UID identifiers")
    parser.add_option("-m","--map",dest="f6",help="CRFReporter 3.0.0 --> 5.0.0 UID mapping file")
    parser.add_option("-o","--check",dest="f7",help="Check inventory and quit")
    parser.add_option("-e","--false",dest="f8",help="Check for erroneus input and quit")
    parser.add_option("-s","--scen",action="store_true",dest="f9",default=False,help="Create '#' separated UID text file for excel and quit")
    parser.add_option("-y","--year",dest="f10",help="Current inventory year")
    parser.add_option("--oldxml",dest="f11",help="Check if UID exists in older CRFReporter version")
    (options,args) = parser.parse_args()

    if options.f2 is None:
        print("No input Reporter Party Profile XML data file")
        quit()
    #Generate UID file for those who make inventory
    if not os.path.isfile(user_information_file):
        print("Missing file",user_information_file,"mapping ghg inventory files to file owners")
        quit()

    dictionary = CreateUserInformation(user_information_file)

    #Print all UID identifiers (do not filter with LULU/KP keywords
    write_all = False
    if options.f5 is True:
        write_all=True
        
    write_scen = False
    if options.f9 is True:
        write_scen=True

    if options.f10 is None:
        print("Missing current inventory year")
        quit()

    current_inventory_year=int(options.f10)

    #Parse xml tree
    print("Parsing Party Profile xml from:",options.f2)
    t=ET()
    t.parse(options.f2)

    if options.f4 is None and options.f1:
        print("Generating UID file:",options.f1)
        f=open(options.f1,'w')
        it = t.iter('variable')
        variablels = [e for e in it if e.tag=='variable']
        variablels.sort(key=SortKey)
        WriteHeader(f,lulu_start_year,current_inventory_year)
        for x in variablels:
            WriteVariables(f,x,dictionary,write_all)
        f.close()
        print("Done")
        quit()
    #-------Optional checking of inventory---------------
    if options.f7 is not None:
        print("Checking inventory to file",options.f7)
        f=open(options.f7,'w')
        it = t.iter('variable')
        variablels = [e for e in it if e.tag=='variable']
        variablels.sort(key=SortKey)
        WriteHeader(f,lulu_start_year,2014)
        for x in variablels:
            WriteEmptyAndFalseVariables(f,x)
        f.close()
        print("Done")
        quit()

    if options.f8 is not None:
        print("Checking inventory for erroneous input to file",options.f8)
        f=open(options.f8,'w')
        it = t.iter('variable')
        variablels = [e for e in it if e.tag=='variable']
        variablels.sort(key=SortKey)
        WriteHeader(f,lulu_start_year,2014)
        for x in variablels:
            WriteFalseInput(f,x)
        f.close()
        print("Done")
        quit()
    #------------------------------------------------------

    #List the inventory files to be imported 
    dirfilels = []
    if options.f4 is None:
        print("Missing GHG Inventory csv files")
        quit()
    dirfilels = glob.glob(options.f4)
    #UID mapping from CRFReporter 3.4.0-->5.0.0
    if options.f6 is None:
        print("No CRFReporter 3.4.0 --> CRFReporter 5.0.0 UID mapping file")
        quit()
    (uid340set,uiddict340to500) = Create340to500UIDMapping(options.f6)
     #This is for Paula's scenario in year 2015
    if write_scen == True:
        print("Writing # separated scenario text file for excel to: options.f1")  
        CreateScenarioExcel(options.f1,t,dirfilels,uid340set,uiddict340to500)
        quit()
    
    time_series_count=0
    not_found_uid_ls=[]

    #Populate xml with inventory reults and write new xml file
    if not options.f3 is None:
        print("Populating Party Profile xml:", options.f2,"with inventory results")
        for file in dirfilels:
            f=open(file)
            start_year = lulu_start_year
            #Important!: all LULU files shall start with 'LU' and KP LULU files with 'KP'
            if file.startswith('KP'):
                start_year = kp_start_year
            elif file.startswith('LU'):
                start_year = lulu_start_year
            else:
                print("Cannot decide if KP LULUCF or LULUCF file", file)
            #Split each data row to  list of strings, delimeters are white
            #space  characters  The  data  file  can  contain  A)  comment
            #starting with  '#' for the  whole file spanning  over several
            #lines  and B)  comment for  the time  series in  front of  it
            #starting and  ending with '#'.  The following line (so called
            #list comprehension)  reads the  data file, filters  out lines
            #with single  '#', then  separates the  times series  from the
            #data comment and  finally splits the time series  into a list
            #of strings (datals).
            datals = [x.rpartition('#')[2].split() for x in f.readlines() if x.count('#') != 1]
            f.close()
            ##Retrieve user based on the first time series uid
            time_series=datals[0]
            #The first string in the list is the uid
            uid = time_series[0]
            uid_new = uid.strip('{}')
            fowner = dictionary[uid_new][2]
            #Find all varibles once
            it = t.iter('variable')
            variablels = [e for e in it if e.tag=='variable']
            print("--------------------------------------------------------------------------")
            print("File:",file,"User:",fowner)
            print("--------------------------------------------------------------------------")
            for time_series in datals:
                if len(time_series) == 0:
                    print(file,"Found empty line")
                else:
                    #The first string in the list is the uid
                    uid = time_series.pop(0)
                    uid_new = uid.strip('{}')
                    fowner = dictionary[uid_new][2]
                    #if fowner == 'aritt':
                    #Filter out Tarja until Tarja is ready
                    #   print("Found aritt, doing nothing")
                    #else:
                    time_series_count += 1
                    #Some UIDs have changed from CRFReporter version 3.4.0 to 5.0.0
                    uid_changed = MapUID340to500(uid_new,uid340set,uiddict340to500)
                    if uid_changed != uid_new:
                        print("UID changed:",uid_new,"-->",uid_changed)
                        uid_new = uid_changed
                    else:
                        print("UID:",uid_new)
                    InsertInventoryData(uid_new,variablels,time_series,file,not_found_uid_ls,start_year,current_inventory_year)
                print("--------------------------------------------------------------------------")
        print("Done, total of",time_series_count,"time series")
        if len(not_found_uid_ls)==0:
            print("Found all UIDs")
        else:
            print("REMEMBER TO UPDATE PARTY PROFILE XML AFTER NEW NODES IN THE INVENTORY!",file=sys.stderr)
            if not options.f11 is None:
                t2 = ET()
                print("Parsing Party Profile xml from:",options.f11,file=sys.stderr)
                t2.parse(options.f11)
                it = t2.iter('variable')
                variablels = [e for e in it if e.tag=='variable']
                truly_missing_uid_ls=[]
                for uid in not_found_uid_ls:
                    if not CheckUIDInXml(uid, variablels):
                        truly_missing_uid_ls.append(uid)
                print("------------------------------------------------------",file=sys.stderr)
                print("The following",len(truly_missing_uid_ls),"UIDs not found in the current inventory:",
                    options.f2,file=sys.stderr)
                print("or in inventory:",options.f11,file=sys.stderr)
                print("UID","File","Owner",file=sys.stderr)
                for uid in truly_missing_uid_ls:
                    file = dictionary[uid][0]
                    owner = dictionary[uid][2]
                    print(uid,file,owner,file=sys.stderr)
                if len(truly_missing_uid_ls)==0:
                    print("All UIDs found",file=sys.stderr)
            print("------------------------------------------------------",file=sys.stderr)
            print("The following",len(not_found_uid_ls),"UIDs not found in current invetory:",
                   options.f2,file=sys.stderr)
            print("UID","File","Owner",file=sys.stderr)
            for uid in not_found_uid_ls:
                file = dictionary[uid][0]
                owner = dictionary[uid][2]
                print(uid,file,owner,file=sys.stderr)
            print("------------------------------------------------------",file=sys.stderr)

    if not options.f1 is None:
        print("Generating UID file:",options.f1)
        f=open(options.f1,'w')
        it = t.iter('variable')
        variablels = [e for e in it if e.tag=='variable']
        variablels.sort(key=SortKey)
        WriteHeader(f,lulu_start_year,current_inventory_year)
        for x in variablels:
            WriteVariables(f,x,dictionary,write_all)
        f.close()
        print("Done")
    print("Pretty print xml for humans")
    PrettyPrint(t.getroot(),0,"   ")
    print("Writing xml to:",options.f3)
    if not options.f3 is None:
        t.write(options.f3)
        print("Done")

    print("Exit program")

if __name__ == "__main__":
    main()
