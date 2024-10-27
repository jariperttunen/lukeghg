import argparse
import json
import pandas as pd
import xlsxwriter

def read_excel(fname:str):
    fxlsx = pd.ExcelFile(fname)
    df = pd.read_excel(fxlsx,sheet_name=None)
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=
        "Read GHG-CRT common variables UID and CRT LULUCF variable UID Excel files.\n"+
        "Produce Excel file using SQL type merge based on UID from both files.")
    parser.add_argument('-c','--GHG_CRT_common',dest="e1",type=str,required=True,
                        help="GHG-CRT LULUCF Common variables Excel file")
    parser.add_argument('-l','--CRT_LULUCF_variables',dest="e2",type=str,required=True,
                        help="CRT LULUCF variables Excel file")
    parser.add_argument('-o','--output',dest="out",type=str,required=True,
                        help="Output Excel file")
    args = parser.parse_args()
    df_common = pd.read_excel(args.e1)
    df_lulucf = pd.read_excel(args.e2)
    #outer join to show file names in  common UID rows
    df_uid_fname = pd.DataFrame()
    df_uid_fname[['UID','GHG_FILE']] = df_common[['UID','GHG_FILE']]
    df_tmp=df_uid_fname['UID'].apply(lambda x: x.casefold())
    df_uid_fname['UID']=df_tmp
    print("Number of variables in common in CRT and CRF tools",len(df_uid_fname['UID']))
    print("Number of variables in LULUCF",len(df_lulucf['uid']))
    df=pd.merge(df_lulucf,df_uid_fname,how='outer',left_on='uid',right_on='UID')
    df.columns=['CRT_Name','Variable_UID','Common_UID','GHG_FILE']
    xlsx_writer  = pd.ExcelWriter(args.out, engine='xlsxwriter')
    df.to_excel(xlsx_writer,index=False,sheet_name='Variables')
    worksheet = xlsx_writer.sheets['Variables']
    for i, col in enumerate(df.columns):
        width = max(df[col].apply(lambda x: max(len(str(x)), len(str(col)))))
        worksheet.set_column(i, i, width)
    xlsx_writer.close()
    print("Done")
