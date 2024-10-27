import argparse
import json
import pandas as pd
import xlsxwriter

def check_name_prefix(x:str):
    return (x['name'].startswith('4.',1,3)==True) or\
           (x['name'].startswith('4(',1,3)==True) or\
           (x['name'].startswith('Memo',1,5)==True) or\
           (x['name'].startswith('Forest',1,7)==True) or\
           (x['name'].startswith('HWP',1,4)==True)
           
def read_crt_metafile(f_name:str):
    """"
    Read json file and retrieve Metadata.
    @note The file name has been CRT_metadata_v1.27.4.json.
    @param f_name CRT JSON Metafile
    @retval crftmetadatadict Metadata as dictinary
    """
    f = open(f_name,mode='r',encoding='utf-8')
    crtjson = json.load(f)
    crtmetadatals = crtjson['Metadata']
    crtmetadatadict = crtmetadatals[0]
    return crtmetadatadict

def read_lulucf_variables(crtmetadata:dict):
    """
    Retrieve LULUCF variables from the CRT Metadata.
    @param crtmetadata CRT Metadata as dictionary
    @retval luluvarls List of LULUCF variables
    @pre It assummed all LULUCF variables begin with '4.'
    @post luluvarls is sorted by name
    """
    varls = crtmetadata['variable']
    #The name is a string but it is in parts defined by list notation
    #using square brackets (a hypercube definition?).
    #Ignore the first '[' in the first part of the name.
    luluvarls = [x for x in varls if check_name_prefix(x)]
    #Sort by name
    luluvarls.sort(key=lambda x: x['name'])
    return luluvarls

def create_lulucf_var_dataframe(luluvarls:list):
    """
    Retrieve 'name' and 'uid' from LULUCF variables.
    @param luluvarls LULUCF variables
    @retval dfnameuid Dataframe containing LULUCF variables and thier UID's
    """
    df = pd.DataFrame(luluvarls)
    dfnameuid = pd.DataFrame()
    dfnameuid[['name','uid']] = df[['name','uid']]
    return dfnameuid

def create_lulucf_var_excel(fname:str,df:pd.DataFrame):
    """
    Create excel file from the dataframe of LULUCF variables and their UID's.
    @param fname Excel file name
    @df Dataframe of LULUCF variables and their names
    """
    xlsx_writer  = pd.ExcelWriter(fname, engine='xlsxwriter')
    df.to_excel(xlsx_writer,index=False,sheet_name='Variables')
    worksheet = xlsx_writer.sheets['Variables']
    for i, col in enumerate(df.columns):
        width = max(df[col].apply(lambda x: max(len(x), len(col))))
        worksheet.set_column(i, i, width)
    xlsx_writer.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=
        "Read CRT Metafile json file and create Excel file for LULUCF UID file")
    parser.add_argument('-i','--json',dest="json",type=str,required=True,
                        help="CRT Excel file (CRT_Metadata_v1.27.4.xlsx) for JSON Metadata\
                              for all sectors from ETF Tool technical documentation")
    parser.add_argument('-o','--excel_output',dest="excel_output",type=str,required=True,
                        help="Excel file containg LULUCF variables and their UID's")
    args = parser.parse_args()
    crtdict = read_crt_metafile(args.json)
    luluvarls = read_lulucf_variables(crtdict)
    dfnameuid = create_lulucf_var_dataframe(luluvarls)
    create_lulucf_var_excel(args.excel_output,dfnameuid)
    print("Done")
    
