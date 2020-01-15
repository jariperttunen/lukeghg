import glob
import argparse
import numpy as np
import pandas as pd
import xlsxwriter
import lukeghg.crf.ghginventory as ghginv

def convert_to_float(x:str, keys:bool=True):
    """
    keys: maintain notation keys
    """
    try:
        return float(x)
    except:
        if keys:
            return 0
        else:
            return x

def insert_ghg_file_to_dictionary(d:dict,fname:str,uid_mapping_file:str,keys:bool=False):
    datalss = ghginv.ParseGHGInventoryFile(fname,uid_mapping_file)
    for datals in datalss:
        uid=datals.pop(0)
        datals=[convert_to_float(x,keys) for x in datals]
        d[uid] = datals
    return d

def create_ghg_file_dictionary(reg_expr:str,uid_mapping_file:str,keys:bool=False):
    filels = glob.glob(reg_expr)
    d=dict()
    for fname in filels:
        d=insert_ghg_file_to_dictionary(d,fname,uid_mapping_file,keys)
    return d

def read_uid_matrix_file(excel_file:str,skip_rows=4):
    df = pd.read_excel(excel_file,sheet_name="UIDMatrix",skiprows=skip_rows,
                       header=0)
    return df

def read_scenario_template_file(excel_file:str,skip_rows=2):
    df = pd.read_excel(excel_file,sheet_name="LandUse",skiprows=skip_rows,
                       header=0)
    #Change column names to strings, easier to index and slice
    df.columns = [str(x) for x in list(df.columns)]
    return df

def land_use_classes(df_uid_matrix,index:int=2):
    """
    Slice column names and return land use classes
    """  
    columnls = list(df_uid_matrix.columns)
    return columnls[index:]

def land_use_class_uid_df(df,name:str):
    """
    name: land use name
    Return 3 columns: Number, stock change/emission type and the 
    corresponding land use UID's
    """
    #print("NAME",name)
    df1=df[[df.columns[0],df.columns[1],name]]
    df2=df1[pd.notna(df1[name])]
    #print(df2)
    return df2

def land_use_class_uid_ls(df,name):
    """
    name: land use name
    return: The list of land use stock change/emission type UID's
    """
    s = df[name]
    return list(s)

def stock_change_name(df,name,uid):
    """
    name: land use name
    uid: stock change/emission type UID
    return: stock change/emission type name
    """
    df1 = df[df[name]==uid]
    s = df1[df1.columns[1]]
    ls = list(s)
    return ls[0]

def stock_change_id_number(df,name,uid):
    """
    name: land use name
    uid: stock change/emission type UID
    return: stock change/emission type id_number 
    """
    df1 = df[df[name]==uid]
    s = df1[df1.columns[0]]
    ls = list(s)
    return ls[0]

def stock_change_name_id_number(df,name,uid):
    n = stock_change_name(df,name,uid)
    id_number = stock_change_id_number(df,name,uid)
    return (n,id_number)

def select_row_number(df_template,id_number):
    """"
    df_template: UID template sheet or scenario result template sheet
    First (i.e. 0) column is the column name where id_numbers are
    Return row number corresponding to id_number
    """
    name = df_template.columns[0]
    df_tmp1 = df_template[df_template[name]==id_number]
    number = df_template[df_template[name]==id_number].index[0]
    return number

def add_data_series(df_scen,new_row_ls,row_number:int):
    """
    Add/replace scenario template data series
    df_scen: Scenario template sheet
    new_row_ls: scenario data series (from the dictionary)
    row_number: the row where the data series belongs to
    """
    df_scen.loc[row_number,'1990':]=new_row_ls
    return df_scen
              


def create_scenario_excel(scen_excel_file:str,scen_files_reg_expr:str,uid_excel_file:str,scen_template_file:str,uid_300_500_file:str,keys:bool=False):
    writer = pd.ExcelWriter(scen_excel_file,engine='xlsxwriter')
    d = create_ghg_file_dictionary(scen_files_reg_expr,uid_300_500_file,keys)
    df_uid = read_uid_matrix_file(uid_excel_file)
    df_scen_template = read_scenario_template_file(scen_template_file)
    ls = land_use_classes(df_uid)
    #print("CLASSES",ls)
    for class_name in ls:
        print("LAND USE",class_name)
        df_uid_class=land_use_class_uid_df(df_uid,class_name)
        uid_ls = land_use_class_uid_ls(df_uid_class,class_name)
        df_scen_new = df_scen_template.copy()
        for uid in uid_ls:
            (name,id_number) = stock_change_name_id_number(df_uid,class_name,uid)
            #print("UID",uid,"ID",id_number,"NAME",name)
            data_series_ls = d[uid]
            #print("DATA",data_series_ls)
            #print("DIM",np.shape(df_scen_new))
            row_number = select_row_number(df_scen_template,id_number)
            #print("ROW",row_number)
            df_scen_new = add_data_series(df_scen_new,data_series_ls,row_number)
        df_scen_new.to_excel(writer,sheet_name=class_name)
    return writer

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--files',type=str,dest='files',help='Scenario files (reqular expression)')
    parser.add_argument('--uid',type=str,dest='uid',help='UID matrix excel file')
    parser.add_argument('--scen',type=str,dest='scen',help='Scenario excel template file')
    parser.add_argument('--keys',dest='keys',action='store_false',help='Maintain notation keys')
    parser.add_argument('-m',type=str,dest='m',help='UID 300->500 mapping file (CRFReporter)')
    parser.add_argument('-o',type=str,dest='o',help='Scenario results excel file')
    args = parser.parse_args()
    excel_writer = create_scenario_excel(args.o,args.files,args.uid,args.scen,args.m,args.keys)
    excel_writer.save()
    excel_writer.close()
