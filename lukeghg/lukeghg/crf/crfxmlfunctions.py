from xml.etree.ElementTree import ElementTree as ET
from xml.etree.ElementTree import Element,SubElement
from  lukeghg.crf.crfxmlconstants import crfreporter_rounding as crfround

def RoundToNDecimals(data,n):
    try:
        #round to n decimals
        data_round = float(format(float(data),'.'+str(n)+'f'))
        if data_round == 0.0:
            return data
        else:
            #otherwise use the rounded value
            return data_round
        #Notation key if not successfull conversion to floating point
    except ValueError:
        return data
        
def ReadGHGInventoryFile(file_name):
    """
    Read and parse GHG Inventory file. See documentation for the file format
    that defines the use of comments.  Return the list of time
    series. Each time series is a list consisting of CRFReporter  UID followed by the
    time series. The returned list is as follows:
    [[UID1, val1,val2,...,valn],[UID2,val1,val2,...,valn],...,[UIDN,val1,...,valn]]
    The values are character strings and not converted to numbers.
    """
    #print("GHG FILE",file_name)
    f = open(file_name)
    ls = [x.rpartition('#')[2].split() for x in f.readlines() if x.count('#') != 1]
    f.close()
    return ls

def InsertInventoryData(uid,t,datals,file,not_found_uid_ls,start_year,inventory_year):
    """
    Insert time series to CRFReporter Party Profile xml file
    uid: The CRFReporter unique identifier for the time series
    t:   The ElementTree representation of the Party Profile xml file
    not_found_uid_ls: Collect UIDs not found to this list
    start_year: Inventory start year (LULUCF 1990, KPLULUCF 2013
    inventory_year: Current inventory year, i.e. the last year in CRFReporter.
    """
    it = t.iter('variable')
    variablels = [e for e in it if e.tag=='variable']
    #Find the time series that match the UID
    varls = [var for var in variablels if var.get('uid')==uid]
    if len(varls) == 0:
        print("UID:", uid, "not found, doing nothing")
        not_found_uid_ls.append(uid)
    elif len(varls)> 1:
        print("UID:", uid, "not unique, found",len(uidls),"time series, doing nothing")
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
        if len(yearls) != len(datals):
            print("Warning! File:",file,"datalength",len(datals),"differs from number of records",len(yearls),"in XML file")
        if len(yearls) == 0:
            print('NO RECORD',uid, len(yearls), len(datals))
        if start_year == kp_start_year:
            print("File:",file,"Inventory start 2013, assuming KPLULUCF")
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
        for year_record,data in zip(yearls,datals):
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
            try:
                #round to six decimals
                data_round = float(format(float(data),'.'+str(crfround)+'f'))
                if data_round == 0.0:
                    #if the value is zero after rounding use with original accuracy
                    print(year_record.get('name'),value.text,"<----",str(data))
                    value.text = str(data)
                else:
                    #otherwise use the rounded value
                    print(year_record.get('name'),value.text,"<----",str(data_round))
                    value.text = str(data_round)
            #Notation key if not successfull conversion to floating point
            except ValueError:
                print(year_record.get('name'),value.text,"<----",str(data))
                value.text = str(data)
                
def PaddingList(inventory_year,time_series_ls):
    """
    Generate list of zeroes to fill time series not
    fully calculated
    """
    #if length of the time series is from 1990 to the inventory year then no padding neede
    #For example (2013-1990+1) = 24 numbers
    return [0]*((inventory_year-1990+1)-len(time_series_ls))

def ConvertSign(x):
    """
    If x is number multiply with -1.0
    """
    try:
        x = -1.0*float(x)
        return x
    except ValueError:
        return x
def ConvertToCO2(toco2,x):
    """If x number multiply with toco2 
    """
    try:
        x = toco2*float(x)
        return x
    except ValueError:
        return x
    
def SumTwoValues(x,y):
    """If both x and y are numbers return their sum
       If x is a number return x
       If y is a number return y
       Otherwise return the concatination of notation keys
       (x and are both notation keys)
    """
    try:
        z = float(x)+float(y)
        return z
    except ValueError:
        pass
    try:
        float(x)
        return x
    except ValueError:
        pass
    try:
        float(y)
        return y
    except ValueError:
        pass
    #Not just concatination of two notation keys
    z = x+','+y
    #split to a list of strings
    ls=z.split(',')
    #make a set to remove duplicates 
    nkset=set(ls)
    #back to list of strings
    ls = list(nkset)
    #construct new string with ',' separated notation keys 
    s=ls.pop(0)
    for item in ls:
        s=s+','+item
    return s
    
def ConvertFloat(x):
    """
    If x can be converted to float return the numeric value.
    Otherwise return x 
    """
    try:
        x = float(x)
        return x
    except ValueError:
        return x
        
def SumBiomassLs(bmls):
    """Sum time series in the list and take care if a notation key is encountered
    """
    #The first time series
    ls = bmls.pop(0)
    #The first element is the tiem series UID 
    ls.pop(0)
    ls = list(map(ConvertFloat,ls))
    for ls1 in bmls:
        #The first item is the time series UID
        ls1.pop(0)
        #print(1,len(ls),len(ls1))
        #Add togehter two time series
        ls=[SumTwoValues(ConvertFloat(x),ConvertFloat(y)) for (x,y) in zip(ls,ls1)]
        #print(2,len(ls))
    return ls

#Generate years for tables, e.g. 1990, 1991,...,2013
def GenerateRowTitleList(begin,end):
    row_title_ls=[]
    for item in range(begin,end+1):
        row_title_ls.append(str(item))
    return row_title_ls

#Sort the Records based on YearName in ascending order
def SortKey(x):
    return x.attrib['YearName']
def SortYearList(year):
    y = year.get('name')
    return int(y)

def GenerateInventoryYears(begin,end):
    inventory_years_ls=[]
    for item in range(begin,end+1):
        inventory_years_ls.append(str(item))
    return inventory_years_ls

def FindTimeSeries(uid,t):
    it = t.iter('variable')
    variablels =  [e for e in it if e.tag=='variable']
    #Find the time series that match the UIDs
    #FL, living biomass
    varls = [var for var in variablels if var.get('uid') == uid]
    var = varls[0]
    #Time series and its comment
    yearscommentls = list(var)
    #Time series
    years = yearscommentls[0]
    #Time series as a list
    yearls = list(years)
    #Sort the list
    yearls.sort(key=SortYearList)
    time_series_ls=[]
    for year_record in yearls:
        recordls = list(year_record)
        record = recordls[0]
        valuecommentls = list(record)
        value = valuecommentls[0]
        text = value.text
        text = text.replace(',','')
        time_series_ls.append(text)
    #Return the time series
    return time_series_ls
