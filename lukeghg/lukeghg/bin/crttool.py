#!python
import sys
import argparse
import glob
import json
import numpy as np
import pandas as pd
import lukeghg.utility.crtnotationkeys as nk
import crtcomments as crtc


#Decimal precision used in ETF reporter 
DECIMAL_PRECISION=6

#Two UIDs that appear two times. These are added up in json.
#See  ghg_inventory_to_crtjson() 
CL_FL_UID = '60EB12FB-2993-433B-81F9-451C56919187'.casefold()
GL_FL_UID = '18C29684-3802-456A-8925-FAC535734216'.casefold()

def isnumeric(n):
    """
    Test with conversion to float.
    @param n Number or Notation key string
    @return True if \p n is number
    @return False if \p is not a number
    """
    try:
        float(n)
        return True
    except ValueError:
        return False
    
def add_two_lists(ls1:list,ls2:list):
    """
    Add two lists element-wise. Check the lists for notation keys.
    @param ls1 The first list
    @param ls2 The second lists
    @return The sum of two lists.
    """
    sum_ls=[]
    for (n1,n2) in zip(ls1,ls2):
        if (n1==0) and (not isnumeric(n2)):
            #If the first is the initial value zero and the second one notation key
            #return the notation key
            sum_ls.append(n2)
        elif isnumeric(n1) and isnumeric(n2):
            sum_ls.append(str(float(n1)+float(n2)))
        elif isnumeric(n1):
            sum_ls.append(n1)
        elif isnumeric(n2):
            sum_ls.append(n2)
        else:
            #No other options: concatinate the two notation keys 
            sum_ls.append(n1+","+n2)
    return sum_ls
    
def has_crt_uid_entry(year_entry:dict,uid:str):
    """
    Check if \p uid exists in the CRT json
    @param year_entry One year from the 'values' section
    @param uid The UID to be found
    @return True if \p uid is found False otherwise
    """
    uid_entry_ls = year_entry['values']
    uid_entry = [x for x in uid_entry_ls if x['variable_uid']==uid]
    if uid_entry:
        return True
    else:
        return False

def generate_crt_years(time_series_ls,inventory_year:int):
    """
    Generate sequence of years to be filled with inventory data.
    @param time_series_ls The time series from the inventory results.
    @param inventory_year Current inventory year (last year in ETF tool
    @retval ls The list of inventory years in the \p time_series_ls
    @note The basic inventory runs from 1990 to \p inventory_year but some time series
          begin from 1960.
    """
    length = len(time_series_ls)
    start_year = inventory_year-length+1
    ls = list(range(start_year,inventory_year+1))
    return ls

def find_crt_uid_entry(year_entry:dict,uid:str):
    """
    From the year entry find the right UID
    @param year_entry One year from the 'values' section
    @param uid The UID to be found
    @return The UID entry
    @pre It is assumed that the \p uid exists
    @sa find_crt_inventory_year has_crt_uid_entry
    """
    uid_entry_ls = year_entry['values']
    uid_entry = [x for x in uid_entry_ls if x['variable_uid']==uid]
    return uid_entry[0]

def find_crt_inventory_year(crt_value_ls:list,year:str):
    """
    From the `values` section retrieve inventory year
    @param crt_value_ls The list of inventory years from the `values` section
    @param year The inventory year
    @return Entry for the \p year
    @pre The \p year exists
    @note Maybe a bit slow but we cannot be sure is the list is sorted
    @sa crtvalues
    """
    val_ls = [x for x in crt_value_ls if x['inventory_year']==year]
    return val_ls[0]

def insert_value(crt_value_ls:list,uid:str,val:str,year:str,val_type:str):
    """
    Insert one year inventory data for one UID
    @param crt_value_ls The `values` section from the json file
    @param uid The UID of the inventory time series
    @param val The value for the UID
    @param year The inventory year for the \p value
    @pre The \p uid exists
    @pre Inventory \p year exists
    @sa insert_time_series
    """
    year_entry = find_crt_inventory_year(crt_value_ls,year)
    uid_entry = find_crt_uid_entry(year_entry,uid)
    entry= uid_entry['value']
    entry['type'] = val_type
    entry['value'] = val
    
def insert_ghg_time_series(crt_value_ls:list,uid:str,time_series_ls,years:list):
    """
    Insert one time series to CRT json file
    @param crt_value_ls The `values` section from the json file
    @param uid The UID of the inventory time series
    @param time_series_ls One time series for the \p uid
    @param years Inventory years
    @post Decimal values are rounded to 6 decimals
    @post Full precision is used if rounding results 0 value
    @post Scientific notation is converted to decimal representation
    """
    l = len(time_series_ls)
    for (val,year) in zip(time_series_ls,years):
        if isnumeric(val):
            #Insert numeric value
            print(year,val,"Inserting numeric value")
            #Rounding to DECIMAL_PRECISION decimal points and change scientific notation to decimal notation for json
            val_rounded = float(np.format_float_positional(float(val),precision=DECIMAL_PRECISION))
            #If 0 (zero) then use full precision
            if val_rounded == 0.0:
                val_rounded = float(np.format_float_positional(float(val)))
                print(" ",year,val_rounded,"Rounding resulted 0, using full precision")
            insert_value(crt_value_ls,uid,val_rounded,str(year),nk.number)
        else:
            #Notation key from a dropdown list in the ETF tool
            decimal_val = nk.crtvalue(val)
            if nk.is_dropdown_key(decimal_val):
                print(year,val,decimal_val,"Inserting Dropdown value")
                insert_value(crt_value_ls,uid,decimal_val,str(year),nk.dropdown)
            #Notation key used in LULUCF inventory
            elif nk.is_ghg_notation_key(decimal_val):
                print(year,val,"Inserting Notation key value")
                insert_value(crt_value_ls,uid,decimal_val,str(year),nk.NK)
            else:
                print(uid,year,val,"Unknown value type",file=sys.stderr)
                
def read_ghg_inventory_file(fname:str):
    """
    Read one GHG inventory file
    @param fname File name
    @retval datalss List of lists of time series with time series UID in the file \p fname 
    @post Comments in the file \p fname are stripped
    """
    f=open(fname)
    datalss = [x.rpartition('#')[2].split(sep=None) for x in f.readlines() if x.count('#') != 1]
    f.close()
    return datalss

def ghgfiles(glob_expr:str):
    """
    GHG inventory directory listing. 
    @param glob_expr Glob expression that can list files in a directory
    @retval ls List of file names
    @note The LULUCF inventory files can be listed for example as \a crf/LU*.csv.
    """
    ls = glob.glob(glob_expr)
    return ls

def crtvalues(crt_json:dict):
    """
    Read CRT tool LULUCF inventory json dictionary and
    retrieve the `values` section.
    @param fname LULUCF inventory json dictionary
    @retval crt_values The list of the 'values' section from the json file
    @sa crtjson
    """
    crt_data = crt_json['data']
    crt_value_ls = crt_data['values']
    return crt_value_ls

def crtjsondump(fname:str,crt_json:dict):
    """
    Write json dictionary to a file
    @param fname File name
    @param crt_json CRT json dictionary
    """
    with open(fname,'w',encoding='utf-8') as f:
        json.dump(crt_json,f,indent=8)
        
def crtjson(fname:str):
    """
    Read CRT tool json file to memory as a dictionary
    @param fname CRT tool json file
    """
    with open(fname,encoding='utf-8') as f:
        crt_json = json.load(f)
        return crt_json
    
def ghg_inventory_to_crtjson(fjson:str,glob_expr:str,inventory_start:int,inventory_year:int):
    """
    List LULUCF inventory files. Read time series from the files
    and insert into CRT json.
    @param fjson CRT json file name
    @param glob_expr Glob expression that can list (all) GHG inventory files
    @param inventory_year Inventory year (last year in the ETF tool)
    @retval crt_json Updated CRT json dictionary
    @sa insert_ghg_time_series
    """
    file_ls  = ghgfiles(glob_expr)
    crt_json = crtjson(fjson)
    crt_values_ls = crtvalues(crt_json)
    year_entry = find_crt_inventory_year(crt_values_ls,str(inventory_year))
    number_of_years = len(list(range(inventory_start,inventory_year+1)))
    cl_fl_ls = [0]*number_of_years
    gl_fl_ls = [0]*number_of_years
    for file in file_ls:
        time_series_lss = read_ghg_inventory_file(file)
        for time_series_ls in time_series_lss:
            uid = time_series_ls.pop(0)
            #For historic reasons remove first potential trailing '{' and '}'
            #Then casefold for caseless comparison with new UIDs in CRT json
            uid = uid.strip('{}').casefold()
            if has_crt_uid_entry(year_entry,uid):
                print(uid,"Inserting time series", file)
                years = generate_crt_years(time_series_ls,inventory_year)
                if uid == CL_FL_UID:
                    cl_fl_orig_ls = cl_fl_ls 
                    cl_fl_ls = add_two_lists(cl_fl_ls,time_series_ls)
                    print(uid,"Inserting CL_FL: ",cl_fl_orig_ls,'+',time_series_ls,'=',cl_fl_ls)
                    insert_ghg_time_series(crt_values_ls,uid,cl_fl_ls,years)
                elif uid == GL_FL_UID:
                    gl_fl_ls_orig = gl_fl_ls
                    gl_fl_ls =  add_two_lists(gl_fl_ls,time_series_ls)
                    print(uid,"Inserting GL_FL: ",gl_fl_ls_orig,'+',time_series_ls,'=',gl_fl_ls)
                    insert_ghg_time_series(crt_values_ls,uid,gl_fl_ls,years)
                else:
                    insert_ghg_time_series(crt_values_ls,uid,time_series_ls,years)
            else:
                print(uid,"Not found in CRT json",file,file=sys.stderr)
    return crt_json

if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
        description=
        "Read GHG inventory files and the CRT json data exchange file.\n"+
        "Fill the CRT json file with inventory results.\n"+
        "Write the new CRT json file for the ETF tool.\n"+
        "NOTE: Notation key comments are inserted with crtcomments.py")
    parser.add_argument('-c','--crf',dest="c",type=str,required=True,
                        help="Glob expression listing GHG LULUCF files (e.g. 'crf/LU*.csv')")
    parser.add_argument('-j','--json' ,dest="j",type=str,required=True,
                        help="CRT json data exchange file")
    parser.add_argument('-s','--start',dest="s",type=int,default=1990)
    parser.add_argument('-y','--year',dest="y",type=int,required=True,
                        help="Inventory year, the last year in ETF tool")
    parser.add_argument('-o','--out',dest="o",type=str,required=True,
                        help="CRT json output file for ETF tool")
    args = parser.parse_args()
    print("Inserting GHG inventory to CRT json",args.j)
    print("File glob expression",args.c)
    crt_json = ghg_inventory_to_crtjson(args.j,args.c,args.s,args.y)
    print("Writing CRT json to file:",args.o)
    crtjsondump(args.o,crt_json)
    print("Done")
