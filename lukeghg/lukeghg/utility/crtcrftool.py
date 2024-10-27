import argparse
import glob
import json
import numpy as np
import pandas as pd
import xlsxwriter
import lukeghg.check.checkinventoryvalues as checkinv

def filter_remaining_uid(df):
    df = df[df['Variable UID'] == df['GHG_UID']]
    return df

def filter_obsolete_uid(df):
     df = df[pd.isnull(df['Variable UID'])]
     return df
 
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
 
def read_ghg_files(dirname:str):
    dirfilels = glob.glob(dirname+'/LU*.csv')
    uid_dict = checkinv.CreateDictionary(dirfilels)
    uidls = uid_dict.keys()
    uidset = set(uidls)
    df = pd.DataFrame()
    df['GHG_UID']=list(uidset)
    df['GHG_FILE'] = pd.NA
    for key in uid_dict.keys():
        df.loc[df.GHG_UID == key,"GHG_FILE"]=(uid_dict[key][2])
    df_sort = df.sort_values(by=['GHG_FILE'])
    return df_sort

def read_nk_comment_file(fname:str):
    cols = ['NK_UID','Allocation_by_party','Allocation_by_IPCC','NK_explanation']
    df = pd.read_table(fname,names=cols,sep=';')
    df_swap = swap_columns(df,'NK_explanation','Allocation_by_party')
    return df_swap

if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
        description=
        "Produce Excel file comparing UIDs from CRT metadata and from the obsolete CRFReporter.\n\n"+
        "Read CRT metadata Excel file, LULUCF sector sheet.\n"+
        "   -Download the file (e.g. CRT_Metadata_v1.27.4.xlsx) from ETF tool technical documentations.\n"+
        "   -Optionally filter lines with built-in rules.\n"+
        "Read GHG inventory files and extract 1) UIDs and 2) associated file name.\n"+
        "Read GHG notation key comments file and extract 1) UIDs and 2) associated comments.\n\n"+
        "Perform DataFrame merge (SQL type merge) based on UIDs from all three sets of files.\n"+
        "The output Excel file shows: \n"+
        "1) All UIDs used in the ETF tool/CRT json files in LULUCF sector,\n" +
        "2) Common UIDs in the ETF tool and in the previous CRFReporter in the same rows,\n"+
        "In their own rows (in the end of the Excel file):\n"+
        "3) UIDs used in time series in GHG inventory/CRFReporter but not found in ETF tool and\n"+
        "4) UIDs used in notation key comments in GHG inventory/CRFReporter but not found in ETF tool.\n\n"+
        "Optionally: \n"+
        "   -Filter CRT metadata with built-in keywords\n"+
        "   -Filter remaining UIDs (UID present both in the new ETF tool and the old CRF Reporter\n"+
        "   -Filter obsolete UIDs (UID present only in the old CRF Reporter")  
    
    parser.add_argument('-m','--CRT_metadata',dest="m",type=str,required=True,
                        help="CRT Metadata  Excel file (e.g. CRT_Metadata_v1.27.4.xlsx)")
    parser.add_argument('-d','--crf',dest="d",type=str,required=True,
                        help="GHG 'crf' directory of inventory results")
    parser.add_argument('-c','--nk_comments',dest="c",type=str,required=True,
                        help='Notation key comments file (e.g. crf/CLU_notation_explanations.csv)')
    parser.add_argument('-f','--filter',dest="f",action='store_true',help="Use built-in rules to filter lines from CRT Metadata LULUF sheet")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--remaining',dest="remaining",action='store_true',help="Filter existing UIDs")
    group.add_argument('--obsolete',dest="obsolete",action='store_true',help="Filter obsolete UIDs")
    parser.add_argument('-o','--out',dest="out",type=str,required=True,
                        help="Output Excel file")
    args = parser.parse_args()
    print("Reading Excel CRT Metadata file:",args.m) 
    df_lulucf = read_metadata_excel(args.m,"LULUCF")
    if args.f:
        print("  Filtering lines with built-in rules")
        df_lulucf = remove_surplus_lines(df_lulucf)
    print("Reading GHG inventory files from:",args.d)
    df_ghg = read_ghg_files(args.d)
    print("Reading Notation key comments file")
    df_comments=read_nk_comment_file(args.c)
    print("Merging",args.m,",",args.d,"and",args.c)
    df_merge=pd.merge(df_lulucf,df_ghg,how='outer',left_on='Variable UID',right_on='GHG_UID')
    df = pd.merge(df_merge,df_comments,how='outer',left_on='GHG_UID',right_on='NK_UID')
    df.sort_values(by=["Category parent","Category","Classification"],axis=0,ignore_index=True)
    sheet_name ='LULUCF_UID'
    if args.remaining == True:
        print("Filtering existing  UIDs")
        df = filter_remaining_uid(df)
        sheet_name='LULUCF_REMAINING_UID'
    if args.obsolete == True:
        print("Filtering obsolete UIDs")
        df = filter_obsolete_uid(df)
        df = df.drop(df.loc[:,'Variable UID':'Unit'].columns,axis=1)
        sheet_name='_LULUCF_OBSOLETE_UID'
    print("Writing Excel file:",args.out)
    xlsx_writer  = pd.ExcelWriter(args.out, engine='xlsxwriter')
    df.to_excel(xlsx_writer,index=False,sheet_name=sheet_name)
    worksheet = xlsx_writer.sheets[sheet_name]
    for i, col in enumerate(df.columns):
        width = max(df[col].apply(lambda x: max(len(str(x)), len(str(col)))))
        worksheet.set_column(i, i, width)
    xlsx_writer.close()
    print("Done")
