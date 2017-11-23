import csv
import pandas as pd
import numpy as np
import xlsxwriter


def ReadAgriExcelFile(file,sheet,inventory_year):
    """Read Agriculutre GHG inventory Excel file
       and produce text files ('csv') to be included in ghg inventory.
       Output file names are generated from lines in excel files that contain
       only group name (without comment) for the following set of inventory data
       file: excel file name
       sheet_name: excel sheet for the GHG inventory data
    """
    xlsx = pd.ExcelFile(file)
    namels=['CRFTable','Comment']+list(range(1990,int(inventory_year)+1))
    #df = pd.read_excel(xlsx,sheet_name,names=namesls,skiprows=1,keep_default_na=False,na_values=['EMPTY'])
    df=pd.read_excel(xlsx,sheet_name=sheet,names=namels,skiprows=1,usecols=len(namels)-1,keep_default_na=False,na_values=['EMPTY'])
    dfg = df.groupby('CRFTable',sort=False)
    for (key,group) in dfg:
        print(key)
        file_name = 'Agri'+key
        file_name = file_name.replace(' ','')
        file_name = file_name.replace('.','')
        file_name = file_name+'.csv'
        shape = group.shape
        rows = shape[0]
        datals=[]
        columnls= list(group.columns)
        columnls=[str(x) for x in columnls]
        group.columns=columnls
        group=group.replace({'\n':''},regex=True)
        group=group.replace({':':''},regex=True)
        group=group.replace('\r','',regex=True)
        group_values=group[group['Comment'].str.contains('Documentation')==False]
        shape=group_values.shape
        if shape[0] > 0:
            group_values.loc[:,'Comment':inventory_year].to_csv(file_name,header=None,index=None,sep=' ',escapechar=' ',quoting=csv.QUOTE_NONE)
        group_document_box=group[group['Comment'].str.contains('Documentation')==True]
        columnls.pop(0)
        columnls.pop(0)
        #group_document_box.loc[:,columnls]=';'+group_document_box.loc[:,columnls].astype(str)
        group_document_box.is_copy = False
        group_document_box.loc[:,columnls]=group_document_box[columnls].applymap(lambda x: ';'+x)
        #group_document_box.loc[group_document_box.index,columnls]=tmp_df.copy()
        shape=group_document_box.shape
        if shape[0] > 0:
            file_name = 'DAgri'+key
            file_name = file_name.replace(' ','')
            file_name = file_name.replace('.','')
            file_name = file_name+'.csv'
            group_document_box.loc[:,'Comment':inventory_year].to_csv(file_name,header=None,index=None,sep=' ',escapechar=' ',quoting=csv.QUOTE_NONE)
