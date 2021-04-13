import glob
import argparse
import numpy as np
import pandas as pd
import openpyxl
import lukeghg.utility.xlmanip as xlp
import lukeghg.crf.ghginventory as ghginv
import lukeghg.crf.crfxmlconstants as crfc

#Lands_FL classes (forestation)
Lands_FL = ['CL-FL','GL-FL','WLpeat-FL','WLother-FL','SE-FL']
#FL_Lands classes (deforestation)
FL_Lands =['FL-CL','FL-GL','FL-WLpeat','FL-WLflooded','FL-WLother','FL-SE']
#Lands_CL classes
Lands_CL = ['FL-CL','GL-CL','WLpeat-CL','WLother-CL','SE-CL']
#Lands_GL classes
Lands_GL = ['FL-GL','CL-GL','WLpeat-GL','WLother-GL','SE-GL']
#Lands_WLpeat classes
Lands_WLpeat = ['FL-WLpeat','CL-WLpeat','GL-WLpeat']
#Lands_WLflooded classes
Lands_WLflooded = ['FL-WLflooded','CL-WLflooded','GL-WLflooded','SE-WLflooded','OL-WLflooded']
#Lands_WLother
Lands_WLother = ['FL-WLother','CL-WLother','GL-WLother'] 
#Lands_WL classes, all three above
Lands_WL = ['Land-WLpeat','Land-WLflooded','Land-WLother']
#Lands_SE classes
Lands_SE = ['FL_SE','CL-SE','GL-SE','WLpeat-SE','WLother-SE']

#Some colors
summary_color='00FFFF00'
error_color='00FF0000'
white_color='FFFFFF'

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
                       header=0,engine='openpyxl')
    return df

def read_scenario_template_file(excel_file:str,skip_rows=2):
    df = pd.read_excel(excel_file,sheet_name="LandUse",skiprows=skip_rows,
                       header=0,engine='openpyxl')
    #Change column names to strings, easier to index and slice
    df.columns = [str(x) for x in list(df.columns)]
    return df

def read_scenario_lulucf_file(excel_file:str):
    df = pd.read_excel(excel_file,sheet_name="LULUCF",engine='openpyxl')
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

def add_data_series(df_scen,new_row_ls,start:str,end:str,row_number:int):
    """
    Add scenario template data series to summary data frame (eventually excel sheet)
    df_scen: Scenario template sheet
    new_row_ls: scenario data series to be added to total
    row_number: the row where the data series belongs to
    """
    length_row = len(new_row_ls)
    length_series = int(end)-int(start)+1
    if length_row < length_series:
        diff = length_series-length_row
        #print("PADDING",diff)
        padding_ls = [0]*diff
        new_row_ls = new_row_ls+padding_ls
    #print("COLS",type(start),type(end))
    #Slicing dataframe with columns as strings or integers is straightforward
    #but mixing strings and integers will get slicing complicated
    #print("ADD DATA:",len(new_row_ls),new_row_ls)
    df_scen.loc[row_number,start:end]=df_scen.loc[row_number,start:end]+new_row_ls
    return df_scen

def set_data_series(df_scen,new_row_ls,start:str,end:str,row_number:int):
    """
    Set scenario template data series
    df_scen: Scenario template sheet
    new_row_ls: scenario data series
    row_number: the row where the data series belongs to
    """
    length_row = len(new_row_ls)
    length_series = int(end)-int(start)+1
    if length_row < length_series:
        diff = length_series-length_row
        #print("PADDING",diff)
        padding_ls = [0]*diff
        new_row_ls = new_row_ls+padding_ls
    #print("COLS",type(start),type(end))
    #Slicing dataframe with columns as strings or integers is straightforward
    #but mixing strings and integers will get slicing complicated
    #print("SET DATA:",len(new_row_ls),new_row_ls)
    df_scen.loc[row_number,start:end]=new_row_ls
    return df_scen

def write_subtract_formula(sheet,start_col,ncols,result_row,subtract_row):
    """Subract cell from existing formula"""
    for i in range(start_col,ncols):
        cell = openpyxl.cell.cell.Cell(sheet,result_row,i)
        cell_subtract = openpyxl.cell.cell.Cell(sheet,subtract_row,i)
        cell_coordinate = cell.coordinate
        cell_subtract_coordinate = cell_subtract.coordinate
        cell_formula=sheet[cell_coordinate].value
        cell_formula=cell_formula+'-'+cell_subtract_coordinate
        sheet[cell_coordinate]=cell_formula
    return sheet
    
def write_co2sum_formula(sheet,start_col,ncols,result_row,row_number_ls,color,scale=1,sheet_ref=""):
    """
    start_col: start column of the time series
    ncols: number of columns (i.e. length) in the time series
    result_row: the row number of the sum
    row_number_ls: the rows to be added to total.
    color: background color
    scale: the final unit (e.g. scale ktC to Mt CO2 eq if needed)
    sheet_ref:refer to another sheet (e.g. sheet_ref="FL-FL!") if needed 
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
            formula = formula+sheet_ref+cell_name+','
        #replace last ',' with ')
        formula = formula[:len(formula)-1]
        formula = formula+')'+'*'+str(scale)
        #print(formula)
        sheet[cell_coordinate]=formula
        #Fill sum rows with yellow
        sheet[cell_coordinate].fill = openpyxl.styles.PatternFill(start_color=color, end_color=color,fill_type = "solid")
    return sheet

def make_zeros(x,index):
    x[index:]=0.0
    return x

def create_sum_rows(sheet,start_year,end_year):
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
    return sheet

def create_lulucf_sum_rows(sheet,start_year,end_year):
    #Total LULUCF
    write_co2sum_formula(sheet,5,end_year-start_year+1+5,2,[3,6,9,12,15,18],summary_color,1)
    #Forest land
    write_co2sum_formula(sheet,5,end_year-start_year+1+5,3,[4,5],summary_color,1)
    write_co2sum_formula(sheet,5,end_year-start_year+1+5,4,[129],white_color,1,"'FL-FL'!")
    write_co2sum_formula(sheet,5,end_year-start_year+1+5,5,[129],white_color,1,"'Lands_FL'!")
    #Cropland
    write_co2sum_formula(sheet,5,end_year-start_year+1+5,6,[7,8],summary_color,1)
    write_co2sum_formula(sheet,5,end_year-start_year+1+5,7,[129],white_color,1,"'CL-CL'!")
    write_co2sum_formula(sheet,5,end_year-start_year+1+5,8,[129],white_color,1,"'Lands_CL'!")
    #Grassland
    write_co2sum_formula(sheet,5,end_year-start_year+1+5,9,[10,11],summary_color,1)
    write_co2sum_formula(sheet,5,end_year-start_year+1+5,10,[129],white_color,1,"'GL-GL'!")
    write_co2sum_formula(sheet,5,end_year-start_year+1+5,11,[129],white_color,1,"'Lands_GL'!")
    #Wetlands
    write_co2sum_formula(sheet,5,end_year-start_year+1+5,14,[129],white_color,1,"'Lands_WL'!")
    #Settlements
    write_co2sum_formula(sheet,5,end_year-start_year+1+5,15,[16,17],summary_color,1)
    write_co2sum_formula(sheet,5,end_year-start_year+1+5,16,[129],white_color,1,"'SE-SE'!")
    write_co2sum_formula(sheet,5,end_year-start_year+1+5,17,[129],white_color,1,"'Lands_SE'!")
    #HWP from FL-FL sheet
    write_co2sum_formula(sheet,5,end_year-start_year+1+5,18,[127],summary_color,1,"'FL-FL'!")
    #Deforestation
    write_co2sum_formula(sheet,5,end_year-start_year+1+5,19,[129],summary_color,1,"'FL_Lands'!")
    write_co2sum_formula(sheet,5,end_year-start_year+1+5,20,[129],white_color,1,"'FL-CL'!")
    write_co2sum_formula(sheet,5,end_year-start_year+1+5,21,[129],white_color,1,"'FL-GL'!")
    write_co2sum_formula(sheet,5,end_year-start_year+1+5,22,[129],white_color,1,"'FL-WLpeat'!")
    write_co2sum_formula(sheet,5,end_year-start_year+1+5,23,[129],white_color,1,"'FL-WLflooded'!")
    write_co2sum_formula(sheet,5,end_year-start_year+1+5,24,[129],white_color,1,"'FL-WLother'!")
    write_co2sum_formula(sheet,5,end_year-start_year+1+5,25,[129],white_color,1,"'FL-SE'!")
    #Check row
    write_co2sum_formula(sheet,5,end_year-start_year+1+5,26,[20,21,22,23,24,25],white_color,1)
    write_subtract_formula(sheet,5,end_year-start_year+1+5,26,19)
    #Afforestation
    write_co2sum_formula(sheet,5,end_year-start_year+1+5,27,[129],summary_color,1,"'Lands_FL'!")
    write_co2sum_formula(sheet,5,end_year-start_year+1+5,28,[129],white_color,1,"'CL-FL'!")
    write_co2sum_formula(sheet,5,end_year-start_year+1+5,29,[129],white_color,1,"'GL-FL'!")
    write_co2sum_formula(sheet,5,end_year-start_year+1+5,30,[129],white_color,1,"'WLpeat-FL'!")
    #write_co2sum_formula(sheet,5,end_year-start_year+1+5,31,[129],white_color,1,"'WLflooded-FL'!")
    write_co2sum_formula(sheet,5,end_year-start_year+1+5,32,[129],white_color,1,"'WLother-FL'!")
    write_co2sum_formula(sheet,5,end_year-start_year+1+5,33,[129],white_color,1,"'SE-FL'!")
    #Check row
    write_co2sum_formula(sheet,5,end_year-start_year+1+5,34,[28,29,30,31,32,33],white_color,1)
    write_subtract_formula(sheet,5,end_year-start_year+1+5,34,27)
    return sheet

def create_MtCO2eq_rows(sheet,MtCO2eq_start_row,start_year,end_year,ch4co2eq,n2oco2eq):
    """
    ---------- Grand totals MtCO2 eq. ----------------
    Create excel formulas for emissions summary as MtCO2eq. 
    MtCO2eq_start_row: Given the start row the block of MtCO2eq summaries should move correctly as a single block
    start_year,end_year: scenario start and end years 
    ch4co2eq,n2oco2eq: GWP, either AR4 (GHG inventory) or AR5 (scenarios, usually)
    """
    #1 Biomass MtCO2 eq.
    #If more detailed classification above is needed this MtCO2 eq part is rather easily moved downwards
    #as a single block by changing the value of  MtCO2eq_start_row for Biomass Gains to the right row.
    #The work needed is to check and correct the lists of rows for each case to be summed and converted to MtCO2eq 
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
    return sheet

def create_scenario_excel(scen_excel_file:str,scen_files_reg_expr:str,scen_template_file:str,uid_300_500_file:str,
                          start_year:int,end_year:int,keys,ch4co2eq,n2oco2eq):
    missing_uid_dict = dict()
    writer = pd.ExcelWriter(scen_excel_file,engine='openpyxl')
    #Read inventory to dictionary: UID:time series
    d = create_ghg_file_dictionary(scen_files_reg_expr,uid_300_500_file,keys)
    df_uid = read_uid_matrix_file(scen_template_file)
    #Column values, i.e. land use classes from UIDMatrix
    ls = land_use_classes(df_uid)
    #LULUCF summary sheet
    df_lulucf = read_scenario_lulucf_file(scen_template_file)
    df_scen_template = read_scenario_template_file(scen_template_file)
    #Land-Forestland transition (afforestation)
    df_lfl = df_scen_template.copy()
    #This simply initializes the emission time series to 0 for Land->Forestland
    df_lfl[df_lfl[df_lfl.columns[0]].astype(str).str.isnumeric()]=\
    df_lfl[df_lfl[df_lfl.columns[0]].astype(str).str.isnumeric()].apply(lambda x: make_zeros(x,3),axis=1)
    #df_lfl.iloc[:,3:]=0.0
    #Forestland-Land transition (deforeastation)
    df_fll = df_scen_template.copy()
    #This simply initializes the emission time series to 0 for Forestland->Land
    df_fll[df_fll[df_fll.columns[0]].astype(str).str.isnumeric()]=\
    df_fll[df_fll[df_fll.columns[0]].astype(str).str.isnumeric()].apply(lambda x: make_zeros(x,3),axis=1)
    #df_fll.iloc[:,3:]=0.0
    #Land to Cropland
    df_lcl =  df_scen_template.copy()
    df_lcl[df_lcl[df_lcl.columns[0]].astype(str).str.isnumeric()]=\
    df_lcl[df_lcl[df_lcl.columns[0]].astype(str).str.isnumeric()].apply(lambda x: make_zeros(x,3),axis=1)
    #Land to Grassland
    df_lgl =  df_scen_template.copy()
    df_lgl[df_lgl[df_lgl.columns[0]].astype(str).str.isnumeric()]=\
    df_lgl[df_lgl[df_lgl.columns[0]].astype(str).str.isnumeric()].apply(lambda x: make_zeros(x,3),axis=1)
    #Land to Peatland
    df_lwlpeat =  df_scen_template.copy()
    df_lwlpeat[df_lwlpeat[df_lwlpeat.columns[0]].astype(str).str.isnumeric()]=\
    df_lwlpeat[df_lwlpeat[df_lwlpeat.columns[0]].astype(str).str.isnumeric()].apply(lambda x: make_zeros(x,3),axis=1)
    #Land to Flooded
    df_lwlflooded =  df_scen_template.copy()
    df_lwlflooded[df_lwlflooded[df_lwlflooded.columns[0]].astype(str).str.isnumeric()]=\
    df_lwlflooded[df_lwlflooded[df_lwlflooded.columns[0]].astype(str).str.isnumeric()].apply(lambda x: make_zeros(x,3),axis=1)
    #Land to WLother
    df_lwlother =  df_scen_template.copy()
    df_lwlother[df_lwlother[df_lwlother.columns[0]].astype(str).str.isnumeric()]=\
    df_lwlother[df_lwlother[df_lwlother.columns[0]].astype(str).str.isnumeric()].apply(lambda x: make_zeros(x,3),axis=1)
    #Land to WL, all three above
    df_lwl =  df_scen_template.copy()
    df_lwl[df_lwl[df_lwl.columns[0]].astype(str).str.isnumeric()]=\
    df_lwl[df_lwl[df_lwl.columns[0]].astype(str).str.isnumeric()].apply(lambda x: make_zeros(x,3),axis=1)
    #Land to SE
    df_lse =  df_scen_template.copy()
    df_lse[df_lse[df_lse.columns[0]].astype(str).str.isnumeric()]=\
    df_lse[df_lse[df_lse.columns[0]].astype(str).str.isnumeric()].apply(lambda x: make_zeros(x,3),axis=1)
    for class_name in ls:
        print("LAND USE",class_name)
        #Initialize missing uid list
        missing_uid_dict[class_name]=[np.NaN]
        #Return for three columns from the UIDMatrix: Number, stock change/emission type, class_name
        df_uid_class=land_use_class_uid_df(df_uid,class_name)
        #Make a list of uids in class_name column
        uid_ls = land_use_class_uid_ls(df_uid_class,class_name)
        df_scen_new = df_scen_template.copy()
        #1.Add time series to dataframe
        for uid in uid_ls:
            (name,id_number) = stock_change_name_id_number(df_uid,class_name,uid)
            if uid in d:
                data_series_ls = d[uid]
                row_number = select_row_number(df_scen_template,id_number)
                df_scen_new = set_data_series(df_scen_new,data_series_ls,str(start_year),str(end_year),row_number)
                if class_name in Lands_FL:
                    df_lfl=add_data_series(df_lfl,data_series_ls,str(start_year),str(end_year),row_number)
                elif class_name in FL_Lands:
                    df_fll=add_data_series(df_fll,data_series_ls,str(start_year),str(end_year),row_number)
                elif class_name in Lands_CL:
                    df_lcl = add_data_series(df_lcl,data_series_ls,str(start_year),str(end_year),row_number)
                elif class_name in Lands_GL:
                    df_lgl = add_data_series(df_lgl,data_series_ls,str(start_year),str(end_year),row_number)
                elif class_name in Lands_WLpeat:
                    df_lwlpeat = add_data_series(df_lwlpeat,data_series_ls,str(start_year),str(end_year),row_number)
                    #Land to WL,df_lwl, includes all three cases: peat, flooded and other
                    df_lwl = add_data_series(df_lwl,data_series_ls,str(start_year),str(end_year),row_number)
                elif class_name in Lands_WLflooded:
                    df_lwlflooded = add_data_series(df_lwlflooded,data_series_ls,str(start_year),str(end_year),row_number)
                    df_lwl = add_data_series(df_lwl,data_series_ls,str(start_year),str(end_year),row_number)
                elif class_name in Lands_WLother:
                    df_lwlother = add_data_series(df_lwlother,data_series_ls,str(start_year),str(end_year),row_number)
                    df_lwl = add_data_series(df_lwl,data_series_ls,str(start_year),str(end_year),row_number)
                elif class_name in Lands_SE:
                    df_lse = add_data_series(df_lse,data_series_ls,str(start_year),str(end_year),row_number)
                else:
                    pass
            else:
                print("MISSING",class_name,uid)
                missing_uid_dict[class_name].append(uid)
        #Convert years to numbers for excel (no alerts in excel)
        column_ls = df_scen_new.columns
        year_ls = column_ls[2:]
        column_ls = ["Number","Source","Unit"]+list(range(start_year,start_year+len(year_ls)-1))
        df_scen_new.columns = column_ls
        df_scen_new.to_excel(writer,sheet_name=class_name)
        #2.Add sum rows
        sheets = writer.sheets
        sheet = sheets[class_name]
        sheet = create_sum_rows(sheet,start_year,end_year)
        #3. ---------- Grand totals MtCO2 eq. ----------------
        sheet = create_MtCO2eq_rows(sheet,76,start_year,end_year,ch4co2eq,n2oco2eq)
    #Excel sheet for missing UID values
    missing_uid_df = pd.DataFrame.from_dict(missing_uid_dict,orient='index')
    #missing_uid_df = missing_uid_df.dropna()
    uid_sheet_name="UIDMatrix UID not in Inventory"
    missing_uid_df.to_excel(writer,sheet_name=uid_sheet_name)
    #Excel sheet for GWP
    ls = [['CO2','CH4','N2O'],[1,ch4co2eq,n2oco2eq]]
    df = pd.DataFrame(ls)
    gwp_sheet="GWP"
    df.to_excel(writer,sheet_name=gwp_sheet)
    df_lulucf.to_excel(writer,sheet_name='LULUCF')
    column_ls = df_lfl.columns
    year_ls = column_ls[2:]
    column_ls = ["Number","Source","Unit"]+list(range(start_year,start_year+len(year_ls)-1))
    df_lfl.columns = column_ls
    df_fll.columns = column_ls
    df_lcl.columns = column_ls
    df_lgl.columns = column_ls
    df_lwlpeat.columns = column_ls
    df_lwlflooded.columns = column_ls
    df_lwlother.columns = column_ls
    df_lse.columns = column_ls
    df_fll.to_excel(writer,sheet_name='FL_Lands')
    df_lfl.to_excel(writer,sheet_name='Lands_FL')
    df_lcl.to_excel(writer,sheet_name='Lands_CL')
    df_lgl.to_excel(writer,sheet_name='Lands_GL')
    df_lse.to_excel(writer,sheet_name='Lands_SE')
    df_lwl.to_excel(writer,sheet_name='Lands_WL')
    df_lwlpeat.to_excel(writer,sheet_name='Lands_WLpeat')
    df_lwlflooded.to_excel(writer,sheet_name='Lands_WLflooded')
    df_lwlother.to_excel(writer,sheet_name='Lands_WLother')
    sheets = writer.sheets
    sheet_fll = sheets['FL_Lands']
    sheet_lfl = sheets['Lands_FL']
    sheet_lcl = sheets['Lands_CL']
    sheet_lgl = sheets['Lands_GL']
    sheet_lwlpeat = sheets['Lands_WLpeat']
    sheet_lwlflooded = sheets['Lands_WLflooded']
    sheet_lwlother = sheets['Lands_WLother']
    sheet_lwl = sheets['Lands_WL']
    sheet_lse = sheets['Lands_SE']
    sheet_lulucf = sheets['LULUCF']
    #Summation for LULUCF and land change classes: FL_Lands, Lands_FL etc.
    sheet_fll = create_sum_rows(sheet_fll,start_year,end_year)
    sheet_fll = create_MtCO2eq_rows(sheet_fll,76,start_year,end_year,ch4co2eq,n2oco2eq)
    sheet_lfl = create_sum_rows(sheet_lfl,start_year,end_year)
    sheet_lfl = create_MtCO2eq_rows(sheet_lfl,76,start_year,end_year,ch4co2eq,n2oco2eq)
    sheet_lcl = create_sum_rows(sheet_lcl,start_year,end_year)
    sheet_lcl = create_MtCO2eq_rows(sheet_lcl,76,start_year,end_year,ch4co2eq,n2oco2eq)
    sheet_lgl = create_sum_rows(sheet_lgl,start_year,end_year)
    sheet_lgl = create_MtCO2eq_rows(sheet_lgl,76,start_year,end_year,ch4co2eq,n2oco2eq)
    sheet_lwlpeat = create_sum_rows(sheet_lwlpeat,start_year,end_year)
    sheet_lwlpeat = create_MtCO2eq_rows(sheet_lwlpeat,76,start_year,end_year,ch4co2eq,n2oco2eq)
    sheet_lwlflooded = create_sum_rows(sheet_lwlflooded,start_year,end_year)
    sheet_lwlflooded = create_MtCO2eq_rows(sheet_lwlflooded,76,start_year,end_year,ch4co2eq,n2oco2eq)
    sheet_lwlother = create_sum_rows(sheet_lwlother,start_year,end_year)
    sheet_lwlother = create_MtCO2eq_rows(sheet_lwlother,76,start_year,end_year,ch4co2eq,n2oco2eq)
    sheet_lwl = create_sum_rows(sheet_lwl,start_year,end_year)
    sheet_lwl = create_MtCO2eq_rows(sheet_lwl,76,start_year,end_year,ch4co2eq,n2oco2eq)
    sheet_lse = create_sum_rows(sheet_lse,start_year,end_year)
    sheet_lse = create_MtCO2eq_rows(sheet_lse,76,start_year,end_year,ch4co2eq,n2oco2eq)
    sheet_lulucf = create_lulucf_sum_rows(sheet_lulucf,start_year,end_year)
    #Rotate sheets from the end to the beginning
    workbook = writer.book
    workbook.move_sheet('Lands_WLother',-(len(workbook.sheetnames)-1))
    workbook.move_sheet('Lands_WLflooded',-(len(workbook.sheetnames)-1))
    workbook.move_sheet('Lands_WLpeat',-(len(workbook.sheetnames)-1))
    workbook.move_sheet('Lands_WL',-(len(workbook.sheetnames)-1))
    workbook.move_sheet('Lands_SE',-(len(workbook.sheetnames)-1))
    workbook.move_sheet('Lands_GL',-(len(workbook.sheetnames)-1))
    workbook.move_sheet('Lands_CL',-(len(workbook.sheetnames)-1))
    workbook.move_sheet('Lands_FL',-(len(workbook.sheetnames)-1))
    workbook.move_sheet('FL_Lands',-(len(workbook.sheetnames)-1))
    workbook.move_sheet('LULUCF',-(len(workbook.sheetnames)-1))
    workbook.move_sheet(gwp_sheet,-(len(workbook.sheetnames)-1))
    workbook.move_sheet(uid_sheet_name,-(len(workbook.sheetnames)-1))
    workbook.active=0
    return writer

