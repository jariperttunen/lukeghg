#!python
import os
from xml.etree.ElementTree import ElementTree as ET
from xml.etree.ElementTree import Element,SubElement
from optparse import OptionParser as OP
import pandas as pd
from lukeghg.crf.uid340to500mapping import MapUID340to500, Create340to500UIDMapping
from lukeghg.crf.crfxmlfunctions import ConvertFloat
import glob

#Notation Keys in CRFReporter
nkls = ['IE','NE','NO','NA', 'R']
methodls = ['T1','T2','T3']
#Return -1 if negative, otherwise 1 (i.e x >= 0)
def Sign(x):
    if x < 0:
        return -1
    else:
        return 1

def SameSign(x,y):
    s1 = Sign(x)
    s2 = Sign(y)
    return s1 == s2

def CompareTwoInventoryYears(dict1,dict2,tolerance,uidnotincurrentyear,uidnotinpreviousyear,file_out):
    """
    Comapare two inventory years collected into the two dictioniaries.
    The dict1 is the current inventory year and dict2 the previous one (or some else).
    Each time series has UID identifier that is the key to the dictionary.
    The value returned by the UID key is a three tuple (time_series,comment, file).
    This way a more informative output can be generated for results too different
    tolerance: the error (%) or greater that is not accepted
    file_out: output file for errors 
    """
    current_year_keyls=dict1.keys()
    #Collect differences into three dictionaries and print out to file_out
    #Each three dictionary contains the key uid, time_series, the comment and the file
    #{uid:((time_series, comment, file),(}
    method_diff_dict={}
    nk_diff_dict={}
    result_diff_dict={}
    zero_numbers_dict={}
    f=open(file_out,"w")
    for key in current_year_keyls:
        nk_diff_set=set()
        method_diff_set=set()
        value_diff_set=set()
        zero_numbers_set=set()
        relative_change_ls=[]
        if key in dict2:
            (time_series_current,comment_current,file_current) = dict1[key]
            (time_series_prev,comment_prev,file_prev) = dict2[key]
            #start comparing values, zip drops the last value from the current time series
            len_diff = len(time_series_current) - len(time_series_prev)
            #KP might have whole time series calculated or not
            #If not pad with '-' marks
            for item in range(0,len_diff-1):
                time_series_prev.insert(0,'-')
            for (val_current,val_prev) in zip(time_series_current,time_series_prev):
                #Start checking the reason for differences
                if (val_current != val_prev and val_prev != '-'):
                    stringls1=val_current.split(',')
                    stringls2=val_prev.split(',')
                    #Either of the value is a notation key
                    if (stringls1[0] in nkls) or (stringls2[0] in nkls):
                        nk_diff_set.add(True)
                    elif (stringls1[0] in methodls) or (stringls2[0] in methodls):
                        method_diff_set.add(True)
                    #Both must be numbers
                    #Check if nominator is zero
                    else:
                        f1 = float(val_current)
                        f2 = float(val_prev)
                        #Nominator might be zero
                        try:
                            relative_change_percentage=((f1-f2)/abs(f2))*100.0
                            if relative_change_percentage >= tolerance:
                                value_diff_set.add(True)
                        except ZeroDivisionError:
                            zero_numbers_set.add(True)
                #Special case: both might have zero value
                try:
                    f1 = float(val_current)
                    f2 = float(val_prev)
                    if f1 == 0.0 or f2 == 0.0:
                        zero_numbers_set.add(True)
                except ValueError:
                    pass
            #Time series is checked collect the results
            if True in nk_diff_set:
                nk_diff_dict[key]=(time_series_current,comment_current,time_series_prev,file_current,file_prev)
            if True in method_diff_set:
                method_diff_dict[key]=(time_series_current,comment_current,time_series_prev,file_current,file_prev)
            if True in zero_numbers_set:
                zero_numbers_dict[key]=(time_series_current,comment_current,time_series_prev,file_current,file_prev)
            #Calculate relative change for each year
            if True in value_diff_set:
                #More work: calculate difference for each year
                for (f1,f2) in zip(time_series_current,time_series_prev):
                    try:
                        relative_change=((float(f1)-float(f2))/abs(float(f2)))*100.0
                        relative_change_ls.append(relative_change)
                    except ValueError:
                        #Not possible to calculate relative change 
                        relative_change_ls.append('-')
                    except ZeroDivisionError:
                        relative_change_ls.append('ZERO')
                #Collect the relative changes
                result_diff_dict[key]=(time_series_current,comment_current,time_series_prev,relative_change_ls,file_current,file_prev)
    #Print the results for each three types of differences
    result_diff_keyls=result_diff_dict.keys()
    data_frame_list=[]
    f.write('Section Relative change more than '+str(tolerance)+'%'+'\n')
    data_frame_list.append(['Section Relative change more than '+str(tolerance)+'%'])
    for key in result_diff_keyls:
        (time_series_current,comment,time_series_prev,relative_change_ls,file_current,file_prev)=result_diff_dict[key]
        f.write(key+'#'+comment+'#'+file_prev+'#')
        len_diff = len(time_series_current)-len(time_series_prev)
        for item in range(0,len_diff-1):
            time_series_prev.insert(0,'-')
        for item in time_series_prev:
            f.write(item+'#')
        f.write('\n')
        f.write(key+'#'+comment+'#'+file_current+'#')
        for item in time_series_current:
            f.write(item+'#')
        f.write('\n')
        f.write(key+'#'+comment+'#'+'Relative change (%)'+'#')
        for item in relative_change_ls:
            try:
                item=float(format(float(item),'.3f'))
            except ValueError:
                item=item
            f.write(str(item)+'#')
        f.write('\n\n')
        time_series_prev=[ConvertFloat(x) for x in time_series_prev]
        time_series_current=[ConvertFloat(x) for x in time_series_current]
        relative_change_ls=[ConvertFloat(x) for x in relative_change_ls]
        data_frame_list.append([key,comment,file_prev]+time_series_prev)
        data_frame_list.append([key,comment,file_current]+time_series_current)
        data_frame_list.append([key,"","Difference"]+relative_change_ls)
    f.write('Section Change in Notation key\n')
    data_frame_list.append(['Section Change in Notation key'])
    result_nk_diff_keyls = nk_diff_dict.keys()
    for key in result_nk_diff_keyls:
        (time_series_current,comment,time_series_prev,file_current,file_prev)=nk_diff_dict[key]
        f.write(key+'#'+comment+'#'+file_prev+'#')
        len_diff = len(time_series_current)-len(time_series_prev)
        for item in range(0,len_diff-1):
            time_series_prev.insert(0,'-')
        for item in time_series_prev:
            f.write(item+'#')
        f.write('\n')
        f.write(key+'#'+comment+'#'+file_current+'#')
        for item in time_series_current:
            f.write(item+'#')
        f.write('\n\n')
        time_series_prev=[ConvertFloat(x) for x in time_series_prev]
        time_series_current=[ConvertFloat(x) for x in time_series_current]
        data_frame_list.append([key,comment,file_prev]+time_series_prev)
        data_frame_list.append([key,comment,file_current]+time_series_current)
    f.write('Section Change in Methods\n')
    data_frame_list.append(['Section Change in Methods'])
    result_method_diff_keyls = method_diff_dict.keys()
    for key in result_method_diff_keyls:
        (time_series_current,comment,time_series_prev,file_current,file_prev)=method_diff_dict[key]
        f.write(key+'#'+comment+'#'+file_prev+'#')
        len_diff = len(time_series_current)-len(time_series_prev)
        for item in range(0,len_diff-1):
            time_series_prev.insert(0,'-')
        for item in time_series_prev:
            f.write(item+'#')
        f.write('\n')
        f.write(key+'#'+comment+'#'+file_current+'#')
        for item in time_series_current:
            f.write(item+'#')
        f.write('\n\n')
        data_frame_list.append([key,comment,file_prev]+time_series_prev)
        data_frame_list.append([key,comment,file_current]+time_series_current)
    f.write('Section Found zeros (i.e. number 0)\n')
    data_frame_list.append(['Section Found zeros (i.e. number 0)'])
    result_zero_numbers_keyls = zero_numbers_dict.keys()
    for key in result_zero_numbers_keyls:
        (time_series_current,comment,time_series_prev,file_current,file_prev)=zero_numbers_dict[key]
        f.write(key+'#'+comment+'#'+file_prev+'#')
        len_diff = len(time_series_current)-len(time_series_prev)
        for item in range(0,len_diff-1):
            time_series_prev.insert(0,'-')
        for item in time_series_prev:
            f.write(item+'#')
        f.write('\n')
        f.write(key+'#'+comment+'#'+file_current+'#')
        for item in time_series_current:
            f.write(item+'#')
        f.write('\n\n')
        time_series_prev=[ConvertFloat(x) for x in time_series_prev]
        time_series_current=[ConvertFloat(x) for x in time_series_current]
        data_frame_list.append([key,comment,file_prev]+time_series_prev)
        data_frame_list.append([key,comment,file_current]+time_series_current)
    f.write('UID not in current year'+'#'+'Comment'+'#'+'File\n')
    data_frame_list.append(['UID not in current year','Comment','File'])
    for uid in uidnotincurrentyear:
        (time_series_prev,comment_prev,file_prev) = dict2[uid]
        f.write(uid+'#'+comment_prev+'#'+file_prev)
        f.write('\n')
        data_frame_list.append([uid,comment_prev,file_prev])
    f.write('UID not in previous year'+'#'+'Comment'+'#'+'File\n')
    data_frame_list.append(['UID not in previous year','Comment','File'])
    for uid in uidnotinpreviousyear:
        (time_series_current,comment_current,file_current) = dict1[uid]
        f.write(uid+'#'+comment_current+'#'+file_current)
        f.write('\n')
        data_frame_list.append([uid,comment_current,file_current])
    f.close()
    data_frame=pd.DataFrame(data_frame_list)
    ls=file_out.split('.')
    writer = pd.ExcelWriter(ls[0]+".xlsx",engine='xlsxwriter')
    data_frame.to_excel(writer,sheet_name="Inventory Check")
    writer.save()
    
def CreateDictionary(dirfilels):
    """Create a dictionary that associate a UID to its
       time series,comment and file name: {UID1:(time_series1,comment1,file1),UID2:(time_series2,comment2,file2),....}
    """
    dict={}
    for file in dirfilels:
        #print(file)
        f=open(file)
        datals = [x.rpartition('#') for x in f.readlines() if x.count('#') != 1]
        f.close()
        for tuple3 in datals:
            comment = tuple3[0]
            comment=comment.lstrip('#')
            time_series = tuple3[2].split()
            if len(time_series)==0:
                print("Found empty line:",file)
            else:
                uid = time_series.pop(0)
                uid_new = uid.strip('{}')
                #print(uid_new,time_series,len(time_series))
                dict[uid_new]=(time_series,comment,file)
    return dict

#---------------------------------The main program begins--------------------------------------------------
if __name__ == "__main__":
    #Command line generator   
    parser = OP()
    parser.add_option("-p","--prev",dest="f1",help="Read input ghg result files previous year (wild card search)")
    parser.add_option("-c","--curr",dest="f2",help="Read input ghg result files current year (wild card search)")
    parser.add_option("-m","--map",dest="f5", help="CRFReporter 3.0.0 --> 5.0.0 UID mapping file")
    parser.add_option("-f","--diff_file",dest="f6",help="Output text file containing: 1) too large differences, 2) change in Notation keys and methods, 3) missing UID")
    parser.add_option("-t","--tolerance",dest="f7",help="Tolerance for difference in percentage")
    (options,args) = parser.parse_args()

    if options.f1 is None:
        print("No input ghg inventory results files from previous year")
        quit()
    if options.f2 is None:
        print("No input ghg inventory results files from current year")
        quit()
    if options.f5 is None:
        print("No CRFReporter 3.0.0 --> 5.0.0 UID mapping file")
        quit()
    if options.f6 is None:
        print("No outputfile for differences")
        quit()
    if options.f7 is None:
        print("No tolerance in percenatge given for time series differences")
        quit()    
    (uid340set,uiddict340to500) = Create340to500UIDMapping(options.f5)
    print("Comparing two inventories:", options.f1,options.f2)
    dirfilels1 = glob.glob(options.f1)
    dirfilels2 = glob.glob(options.f2)
    #dictionary for previous year: {UID: time series}
    dictprev1=CreateDictionary(dirfilels1)
    #dictionary for previous year: {UID: time series}
    dictcurrent2=CreateDictionary(dirfilels2)
    #Check the existence of UID
    dictprev1keyls = dictprev1.keys()
    uidnotincurrentyear=[]
    for uid in dictprev1keyls:
        if not uid in dictcurrent2:
            uidnotincurrentyear.append(uid)
    print("Number of UID in previous year, not in current year:",len(uidnotincurrentyear))
    uidnotinpreviousyear=[]
    dictcurrent2keyls = dictcurrent2.keys()
    uidnotinpreviousyear=[]
    for uid in dictcurrent2keyls:
        if not uid in dictprev1:
            uidnotinpreviousyear.append(uid)
    print("Number of UID current year, not in previous year:",len(uidnotinpreviousyear))
    print("Number of UID previous year",len(dictprev1keyls))
    print("Number of UID current year",len(dictcurrent2keyls))
    file_name = options.f6
    tolerance = float(options.f7)
    print("Comparing two inventories for differences")
    print("Writing output to:", file_name)
    ls=file_name.split('.')
    print("Writing output to:", ls[0]+".xlsx")
    CompareTwoInventoryYears(dictcurrent2,dictprev1,tolerance,uidnotincurrentyear,uidnotinpreviousyear,file_name)
    print("Done\n")
