import glob
import argparse
import numpy as np
import pandas as pd
import openpyxl
import lukeghg.utility.xlmanip as xlp
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
    df_scen.loc[row_number,'1990':str(1990+len(new_row_ls)-1)]=new_row_ls
    return df_scen

def write_co2sum_formula(sheet,start_col,ncols,result_row,row_number_ls,color,scale=1):
    for i in range(start_col,ncols):
        cell = openpyxl.cell.cell.Cell(sheet,result_row,i)
        cell_coordinate = cell.coordinate
        cell_letter = xlp.cut_cell_number(cell_coordinate)
        cell_ls = []
        for row_number in row_number_ls:
            cell_ls.append(cell_letter+str(row_number))
        for cell_name in cell_ls:
            if sheet[cell_name].value == "":
                #It seems ordering of parameters matters in PatternFill!!
                sheet[cell_name].fill = openpyxl.styles.PatternFill(start_color='00FF0000',fill_type="solid") 
        formula = '=SUM('
        for cell_name in cell_ls:
            formula = formula+cell_name+','
        #replace last ',' with ')
        formula = formula[:len(formula)-1]
        formula = formula+')'+'*'+str(scale)
        #print(formula)
        sheet[cell_coordinate]=formula
        sheet[cell_coordinate].fill = openpyxl.styles.PatternFill(start_color=color, end_color=color,fill_type = "solid")
    return sheet

def create_scenario_excel(scen_excel_file:str,scen_files_reg_expr:str,uid_excel_file:str,scen_template_file:str,uid_300_500_file:str,
                          start_year,end_year,keys:bool=False):
    missing_uid_dict = dict()
    writer = pd.ExcelWriter(scen_excel_file,engine='openpyxl')
    d = create_ghg_file_dictionary(scen_files_reg_expr,uid_300_500_file,keys)
    df_uid = read_uid_matrix_file(uid_excel_file)
    df_scen_template = read_scenario_template_file(scen_template_file)
    ls = land_use_classes(df_uid)
    #print("CLASSES",ls)
    for class_name in ls:
        print("LAND USE",class_name)
        #Initialize missing uid list
        missing_uid_dict[class_name]=[]
        #Return for three columns from the UIDMatrix: Number, stock change/emission type, class_name
        df_uid_class=land_use_class_uid_df(df_uid,class_name)
        #Make a list of uids in class_name columns
        uid_ls = land_use_class_uid_ls(df_uid_class,class_name)
        df_scen_new = df_scen_template.copy()
        len_current_data_series_ls=0
        #1.Add time series to dataframe
        for uid in uid_ls:
            (name,id_number) = stock_change_name_id_number(df_uid,class_name,uid)
            #print("UID",uid,"ID",id_number,"NAME",name)
            if uid in d:
                data_series_ls = d[uid]
                len_current_data_series_ls = len(data_series_ls)
                #print("DATA",data_series_ls)
                #print("DIM",np.shape(df_scen_new))
                row_number = select_row_number(df_scen_template,id_number)
                #print("ROW",row_number)
                df_scen_new = add_data_series(df_scen_new,data_series_ls,row_number)
            else:
                missing_uid_dict[class_name].append(uid)
        column_ls = df_scen_new.columns
        year_ls = column_ls[2:]
        column_ls = ["Number","Source","Unit"]+list(range(start_year,start_year+len(year_ls)-1))
        df_scen_new.columns = column_ls
        df_scen_new.to_excel(writer,sheet_name=class_name)
        #2. Add sum rows
        sheets = writer.sheets
        sheet = sheets[class_name]
        #2.1 Biomass Net change
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,9,[7,8],'00FFFF00',1)
        #2.2 Biomass Total
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,14,range(9,14),'00FFFF00',1)
    missing_uid_df = pd.DataFrame.from_dict(missing_uid_dict,orient='index')
    sheet_name="UID not in Inventory"
    missing_uid_df.to_excel(writer,sheet_name=sheet_name)
    workbook = writer.book
    workbook.move_sheet(sheet_name,-(len(workbook.sheetnames)-1))
    return writer

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--files',type=str,dest='files',help='Scenario files (reqular expression)')
    parser.add_argument('--uid',type=str,dest='uid',help='UID matrix excel file')
    parser.add_argument('--scen',type=str,dest='scen',help='Scenario excel template file')
    parser.add_argument('--keys',dest='keys',action='store_false',help='Maintain notation keys')
    parser.add_argument('-m',type=str,dest='m',help='UID 300->500 mapping file (CRFReporter)')
    parser.add_argument('-o',type=str,dest='o',help='Scenario results excel output file')
    parser.add_argument('--start',type=int,dest='start',help="Start year (1990)")
    parser.add_argument('--end',type=int,dest='end',help="End year")
    args = parser.parse_args()
    if args.files == None:
        print("No input files")
    if args.uid == None:
        print("No UID matrix excel file")
    if args.scen == None:
        print("No Scenario excel template file")
    if args.m == None:
        print("No UID 300->500 mapping file (CRFReporter)")
    if args.o == None:
        print("No Scenario results excel output file")
    if args.start == None:
        print("No Start year (1990)")
    if args.end == None:
        print("No End year")
    result = args.files and args.uid and args.scen and args.m and args.o and args.start and args.end
    if result == None:
        quit()
    excel_writer = create_scenario_excel(args.o,args.files,args.uid,args.scen,args.m,args.start,args.end,args.keys)
    excel_writer.save()
    excel_writer.close()
