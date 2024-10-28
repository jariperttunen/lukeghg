#!python
import argparse
import xlrd
import pandas as pd

agri_excel_sheet_names_ls = ['CH4 manure','CH4 enteric']

def agri_excel_to_csv(fname:str,sheet_name_ls:list,inventory_year:int):
    df_ls=[]
    for sheet_name in sheet_name_ls:
        print("Sheet name",sheet_name) 
        df = pd.read_excel(fname,sheet_name,engine='xlrd')
        ls=list(df.columns)
        ls = [str(x) for x in ls]
        ls[1] = 'UID'
        df.columns = ls
        df1 = df[df['UID'].apply(lambda x: not pd.isna(x))]
        df2 = df1.loc[:,'UID':str(inventory_year)]
        df_ls.append(df2)
    df_result = pd.concat(df_ls,ignore_index=True)
    return df_result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
        description=
        "Read Agri GHG Excel file and required sheets.\n"+
        "Concatinate dataframes into one and write to csv file.\n",
        epilog="Use 'crttool.py' to insert the csv file to CRT json file.")
    parser.add_argument('-e','--excel',dest="e",type=str,required=True,
                        help="Agri GHG Excel file")
    parser.add_argument('-s','--sheets', dest="s",nargs='+', type=str,default=agri_excel_sheet_names_ls,
                        help="Excel sheet names")
    parser.add_argument('-y','--year',dest="y",type=int,required=True,
                        help="Inventory year, the last year in the ETF tool")
    parser.add_argument('-o','--out',dest="o",type=str,required=True,
                        help="Agri GHG csv output file")
    args = parser.parse_args()
    print("Reading excel file",args.e)
    df = agri_excel_to_csv(args.e,args.s,args.y)
    print("Writing time series to", args.o)
    df.to_csv(args.o,sep=' ',header=False,index=False)
    print("Done")
