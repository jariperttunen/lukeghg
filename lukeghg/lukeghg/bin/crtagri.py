#!python
import argparse
import glob
import json
import numpy as np
import pandas as pd
import xlsxwriter

def swap_columns(df,col1:str,col2:str):
    cols = list(df.columns)
    i1 = cols.index(col1)
    i2 = cols.index(col2)
    cols[i1] = col2
    cols[i2] = col1
    df_swap = df.reindex(columns=cols)
    return df_swap

def drop_column(df,name:str):
    df_drop = df.drop(name,axis=1)
    return df_drop

def read_metadata_excel(fname:str,sheet:str):
    df = pd.read_excel(fname,sheet)
    df_swap = swap_columns(df,"Category","Category parent")
    df_drop = drop_column(df_swap,"Variable name (CRF)")
    return df_drop

def remove_surplus_lines(df):
    df1 = df.loc[df['Category parent'] != "Sectors/Totals"]
    df1 = df1.loc[df1['Category parent'].apply(lambda x: not "Template" in str(x))]
    df1 = df1.loc[df1['Category'].apply(lambda x: not "Template" in str(x))]
    df1 = df1.loc[df1['Category'].apply(lambda x: not "Final" in str(x))]
    df1 = df1.loc[df1['Classification parent'].apply(lambda x: not "Template" in str(x))]
    df1 = df1.loc[df1['Classification'].apply(lambda x: not "Template" in str(x))]
    df1 = df1.loc[df1['Category parent'].apply(lambda x:len(x.split('.')) >= 3)]
    df1 = df1.loc[df1['Category parent'].apply(lambda x:len(x.split('.')) >= 3)]
    df1 = df1.loc[df1['Measure Type'].apply(lambda x: not "Implied" in str(x))]
    df1 = df1.loc[df1['Measure'].apply(lambda x: not "Documentation" in str(x))]
    df1 = df1.loc[df1['Measure'].apply(lambda x: not "Total" in str(x))]
    df1 = df1.loc[df1['Category'].apply(lambda x: not "Net" in str(x))]
    #df1 = df1.loc[df1['Category'] != "All [IPCC Software]"]
    #df1 = df1.loc[df1["Category"].apply(lambda x:  not "Land transition" in str(x))]
    
    #df1 = df1.loc[df1['Category'].apply(lambda x: not "Template" in str(x))]
    #df1 = df1.loc[df1['Measure'].apply(lambda x: not "Emission factor information" in str(x))]
    
    #df1 = df1.loc[df1['Classification'].apply(lambda x: not "All [IPCC Software]" in str(x))]
    #df10 = df9.loc[df9['Classification'].apply(lambda x: not "no classification" in str(x))]
    #df11 = df10.loc[df10['Classification parent'].apply(lambda x: not "no classification" in str(x))]
    df1 = df1.sort_values(by=["Category parent","Category","Classification"],axis=0,ignore_index=True)
    return df1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
        description=
        "Produce Excel file for Agriculture UIDs filtered with built-in keywords.\n\n"+
        "Read CRT metadata Excel file, Agriculture sector sheet.\n"+
        "   -Download the file (e.g. CRT_Metadata_v1.27.4.xlsx) from ETF tool technical documentations.\n"+
        "Filter rows with built-in keywords\n"+
        "Write Excel file with remaining Agriculture UIDs after filtering.\n")
       
    parser.add_argument('-m','--CRT_metadata',dest="m",type=str,required=True,
                        help="CRT Metadata  Excel file (e.g. CRT_Metadata_v1.27.4.xlsx)")
    parser.add_argument('-o','--out',dest="out",type=str,required=True,
                        help="Output Excel file")
    args = parser.parse_args()
    print("Reading Excel CRT Metadata file:",args.m) 
    df_agri = read_metadata_excel(args.m,"Agriculture")
    df_agri = remove_surplus_lines(df_agri)
    print("Writing Excel file:",args.out)
    xlsx_writer  = pd.ExcelWriter(args.out, engine='xlsxwriter')
    sheet_name='Agriculture'
    df_agri.to_excel(xlsx_writer,index=False,sheet_name=sheet_name)
    worksheet = xlsx_writer.sheets[sheet_name]
    #Set widths for each column 
    for i, col in enumerate(df_agri.columns):
        width = max(df_agri[col].apply(lambda x: max(len(str(x)), len(str(col)))))
        worksheet.set_column(i, i, width)
    xlsx_writer.close()
    print("Done")
