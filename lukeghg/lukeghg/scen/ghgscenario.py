import glob
import argparse
import numpy as np
import pandas as pd
import openpyxl
import lukeghg.utility.xlmanip as xlp
import lukeghg.crf.ghginventory as ghginv
import lukeghg.crf.crfxmlconstants as crfc

summary_color='00FFFF00'
error_color='00FF0000'

class NoInventoryFiles(Exception):
    pass

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
    if not d:
        raise NoInventoryFiles
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
    """
    start_col:start column of the time series
    ncols: number of columns (i.e. length) in the time series
    result_row: the row number of the sum
    row_number_ls: the rows to be added.
    color: background color
    scale: the final unit (e.g. Mt CO2 eq if needed)
    """
    for i in range(start_col,ncols):
        cell = openpyxl.cell.cell.Cell(sheet,result_row,i)
        cell_coordinate = cell.coordinate
        cell_letter = xlp.cut_cell_number(cell_coordinate)
        cell_ls = []
        for row_number in row_number_ls:
            cell_ls.append(cell_letter+str(row_number))
        for cell_name in cell_ls:
            #Fill missing cells with Red
            if sheet[cell_name].value == "":
                #It seems ordering of parameters matters in PatternFill!!
                sheet[cell_name].fill = openpyxl.styles.PatternFill(start_color=error_color,fill_type="solid")
        #Create the excel SUM formula
        formula = '=SUM('
        for cell_name in cell_ls:
            formula = formula+cell_name+','
        #replace last ',' with ')
        formula = formula[:len(formula)-1]
        formula = formula+')'+'*'+str(scale)
        #print(formula)
        sheet[cell_coordinate]=formula
        #Fill sum rows with yellow
        sheet[cell_coordinate].fill = openpyxl.styles.PatternFill(start_color=color, end_color=color,fill_type = "solid")
    return sheet

def create_scenario_excel(scen_excel_file:str,scen_files_reg_expr:str,uid_excel_file:str,scen_template_file:str,uid_300_500_file:str,
                          start_year,end_year,keys,ch4co2eq,n2oco2eq):
    missing_uid_dict = dict()
    writer = pd.ExcelWriter(scen_excel_file,engine='openpyxl')
    #Read inventory to dictionary: UID:time series
    d = create_ghg_file_dictionary(scen_files_reg_expr,uid_300_500_file,keys)
    df_uid = read_uid_matrix_file(uid_excel_file)
    #Column values, i.e. land use classes from UIDMatrix
    ls = land_use_classes(df_uid)
    df_scen_template = read_scenario_template_file(scen_template_file)
    #print("CLASSES",ls)
    for class_name in ls:
        print("LAND USE",class_name)
        #Initialize missing uid list
        missing_uid_dict[class_name]=[]
        #Return for three columns from the UIDMatrix: Number, stock change/emission type, class_name
        df_uid_class=land_use_class_uid_df(df_uid,class_name)
        #Make a list of uids in class_name column
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
        #2.Add sum rows
        sheets = writer.sheets
        sheet = sheets[class_name]
        #1 Biomass Net change
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,9,[7,8],summary_color,1)
        #2 Biomass Total
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,14,range(9,13+1),summary_color,1)
        #3 Direct N2O emissions from N fertilization
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,19,[17,18],summary_color,1)
        #4 Indirect N20 emissions from managed soils
        #Total
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,41,[39,40],summary_color,1)
        #5 Biomass burning
        #Biomass burning total CO2
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,54,[44,49],summary_color,1)
        #Biomass burning total CH4
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,55,[45,50],summary_color,1)
        #Biomass burning total N2O
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,56,[46,51],summary_color,1)
        #5 HWP
        #1 Sawnwood total
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,62,[60,61],summary_color,1)
        #2 Wood panels
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,65,[63,64],summary_color,1)
        #3 Paper and paperboard
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,68,[66,67],summary_color,1)
        #4 HWP Total
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,69,[62,65,68],summary_color,1)
        #3. ---------- Grand totals MtCO2 eq. ----------------
        #1 Biomass MtCO2 eq.
        #If more grained classification above is needed this MtCO2 eq set is rather easily moved downwards
        #by changing the the  MtCO2eq_start for Gains to right row.
        MtCO2eq_start_row=76
        #Gains
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row,[7],summary_color,(crfc.ctoco2)/1000.0)
        #Losses
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+1,[8],summary_color,(crfc.ctoco2)/1000.0)
        #Net change
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+2,[MtCO2eq_start_row,MtCO2eq_start_row+1],summary_color,1)
        #Dead wood
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+3,[10],summary_color,(crfc.ctoco2)/1000.0)
        #Litter
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+4,[11],summary_color,(crfc.ctoco2)/1000.0)
        #Mineral soil
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+5,[12],summary_color,(crfc.ctoco2)/1000.0)
        #Organic soil
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+6,[13],summary_color,(crfc.ctoco2)/1000.0)
        #Total
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+7,range(MtCO2eq_start_row+2,MtCO2eq_start_row+6+1),
                             summary_color,1)
        #2 Direct N20 emissions from N fertilization
        #Inorganic
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+10,[17],summary_color,n2oco2eq/1000.0)
        #Organic
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+11,[18],summary_color,n2oco2eq/1000.0)
        #Total
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+12,[MtCO2eq_start_row+10,MtCO2eq_start_row+11],
                             summary_color,1)
        #3 Drainage and rewetting
        #3.1 Drained organing N2O
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+15,[22],summary_color,n2oco2eq/1000.0)
        #3.2 Drained organic CH4
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+16,[23],summary_color,ch4co2eq/1000.0)
        #Drained organic total
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+17,[MtCO2eq_start_row+15,MtCO2eq_start_row+16],
                             summary_color,1)
        #3.3 Rewetted organing N2O
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+18,[25],summary_color,n2oco2eq/1000.0)
        #3.4 Rewetted organing CH4
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+19,[26],summary_color,ch4co2eq/1000.0)
        #Rewetted organic total
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+20,[MtCO2eq_start_row+18,MtCO2eq_start_row+19],summary_color,1)
        #3.5 Drained mineral N20
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+21,[28],summary_color,n2oco2eq/1000.0)
        #3.6 Drained mineral CH4
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+22,[29],summary_color,ch4co2eq/1000.0)
        #Drained mineral total
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+23,[MtCO2eq_start_row+21,MtCO2eq_start_row+22],summary_color,1)
        #3.7 Rewetted mineral N20
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+24,[31],summary_color,n2oco2eq/1000.0)
        #3.8 Rewetted mineral CH4
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+25,[32],summary_color,ch4co2eq/1000.0)
        #Rewetted mineral total
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+26,[MtCO2eq_start_row+24,MtCO2eq_start_row+25],summary_color,1)
        #4 Direct N2O emissions mineralization (total)
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+29,[36],summary_color,n2oco2eq/1000.0)
        #5 Indirect N2O emissions managed soils
        #5.1 Atmospheric deposition N2O
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+32,[39],summary_color,n2oco2eq/1000.0)
        #5.2 Nitrogen leaching and run-off N2O
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+33,[40],summary_color,n2oco2eq/1000.0)
        #Indirect N2O managed soils total
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+34,[MtCO2eq_start_row+32,MtCO2eq_start_row+33],summary_color,1)
        #6 Biomass burning
        #Controlled burning CO2
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+37,[44],summary_color,(crfc.ctoco2)/1000.0)
        #Controlled burning CH4
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+38,[45],summary_color,ch4co2eq/1000.0)
        #Controlled burning N2O
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+39,[46],summary_color,n2oco2eq/1000.0)
        #Total
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+40,
                             [MtCO2eq_start_row+37,MtCO2eq_start_row+38,MtCO2eq_start_row+39],summary_color,1)
        #Wildfires CO2
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+42,[49],summary_color,(crfc.ctoco2)/1000.0)
        #Wildfires CH4
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+43,[50],summary_color,ch4co2eq/1000.0)
        #Wildfires N2O
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+44,[51],summary_color,n2oco2eq/1000.0)
        #Total
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+45,
                             [MtCO2eq_start_row+42,MtCO2eq_start_row+43,MtCO2eq_start_row+44],summary_color,1)
        #8 HWP
        #Sawnwood
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+48,[62],summary_color,(crfc.ctoco2)/1000.0)
        #Wood panels
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+49,[65],summary_color,(crfc.ctoco2)/1000.0)
        #Paper and paper board
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+50,[68],summary_color,(crfc.ctoco2)/1000.0)
        #Total
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+51,
                             [MtCO2eq_start_row+48,MtCO2eq_start_row+49,MtCO2eq_start_row+50],summary_color,1)
        #GRAND TOTAL MtCO2eq
        write_co2sum_formula(sheet,5,end_year-start_year+1+5,MtCO2eq_start_row+53,
                             [MtCO2eq_start_row+7,MtCO2eq_start_row+12,MtCO2eq_start_row+17,MtCO2eq_start_row+20,
                              MtCO2eq_start_row+23,MtCO2eq_start_row+26,MtCO2eq_start_row+29,MtCO2eq_start_row+34,
                              MtCO2eq_start_row+40,MtCO2eq_start_row+45,MtCO2eq_start_row+51],summary_color,1)
    missing_uid_df = pd.DataFrame.from_dict(missing_uid_dict,orient='index')
    sheet_name="UIDMatrix UID not in Inventory"
    missing_uid_df.to_excel(writer,sheet_name=sheet_name)
    ls = [['CO2','CH4','N2O'],[1,ch4co2eq,n2oco2eq]]
    df = pd.DataFrame(ls)
    gwp_sheet="GWP"
    df.to_excel(writer,sheet_name=gwp_sheet)
    workbook = writer.book
    workbook.move_sheet(gwp_sheet,-(len(workbook.sheetnames)-1))
    workbook.move_sheet(sheet_name,-(len(workbook.sheetnames)-1))
    return writer

