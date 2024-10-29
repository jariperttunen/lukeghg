import argparse
import glob
import pandas as pd
import numpy as np
import lukeghg.check.checkinventoryvalues as checkinv

def create_uidset(dirfilels:list):
    """
    Create a set of UID's used in GHG inventory
    @param dirfilels List of files in GHG inventory 'crf' directory
    @retval uidset Set of UID's used in GHG inventory
    """
    uid_dict = checkinv.CreateDictionary(dirfilels)
    uidls = uid_dict.keys()
    uidset = set(uidls)
    return uidset

def select_crttool_uid(fname:str):
    """
    Read CRT Excel file listing all LULUCF UIDs and return
    the set of UIDs.
    @param fname Excel file name
    @retval uidset Set of UIDs found in the Excel file
    @note The file name has been CRT_LULUCF_variables.xlsx.
    """
    fxlsx = pd.ExcelFile(fname)
    df_dict = pd.read_excel(fxlsx,sheet_name=None)
    keyls = df_dict.keys()
    uidset=set()
    for key in keyls:
        df = df_dict[key]
        valuels=np.ndarray.flatten(df.values)
        uidls = [x for x in valuels if isinstance(x,str) and len(x)==36 and '-' in x]
        tmp_set = set(uidls)
        uidset=uidset.union(tmp_set)
    return uidset

def common_uidset(ghg_uidset,crttool_uidset):
    """
    Create set of UIDs still valid in the new CRT json
    @param ghg_uidset The set of UIDs used in GHG inventory
    @param crttool_uidset The set of UIDs in the new CRT json
    @retval set_intersect Set of UIDs both in ghg_uidset and crttool_uidset
    """
    set_intersect = crttool_uidset.intersection(ghg_uidset)
    return set_intersect

def new_uidset(ghg_uidset,crttool_uidset):
    """
    Create a set of UIDs in the new CRT tool but not in GHG inventory
    @param ghg_uidset The set of UIDs used in GHG inventory
    @param crttool_uidset The set of UIDs in the new CRT json
    @retval set_diff UIDs in CRT tool but not in GHG inventory
    """
    set_diff = crttool_uidset.difference(ghg_uidset)
    return set_diff

def select_lulucf(fname:str):
    """
    Read Excel file containing common UIDs in all secors
    between the new CRT tool and previous CRF Reporter.
    @note The file name has been CRF-CRT_CommonVariables.xlsx.
    @param fname Excel file containing all common UID's
    @retval df_lulucf DataFrame of LULUCF sector common UID's
    @pre It assumed that LULUCF is located between the rows 18696 and 21070
    """
    fxlsx = pd.ExcelFile(fname)
    df = pd.read_excel(fxlsx,sheet_name=0)
    df_lulucf = df.iloc[(df.index >= 18696) & (df.index <= 21070)]
    df_lulucf.index = range(0,len(df_lulucf.index))
    return df_lulucf

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=
        "Read CRF-CRT common UIDs Excel file. Read GHG inventory files (from 'crf' directory).\n"+
        "Produce Excel file containing LULUCF UIDs and in addition file name for\n"+
        "common UID found in GHG inventory")
    parser.add_argument('-e','--excel_uid',dest="excel",type=str,required=True,
                        help="CRF-CRT Common variables Excel file for all sectors")
    parser.add_argument('-c','--crf',dest="crf",type=str,required=True,
                        help="'crf' directory for GHG inventory results")
    parser.add_argument('-o','--excel_out',dest="out",type=str,required=True,
                        help="Excel file output for LULUCF common variables")
    args = parser.parse_args()
    dirfilels = glob.glob(args.crf+'/LU*.csv')
    ghg_uidset = create_uidset(dirfilels)
    crt_lulucf = select_lulucf(args.excel)
    crt_uidset = set(crt_lulucf['UID'])
    common_set = common_uidset(ghg_uidset,crt_uidset)
    print("CRF-CRT Common variables Excel file:",args.excel)
    print("Common LULUCF UIDs:", len(common_set))
    new_set = new_uidset(ghg_uidset,crt_uidset)
    print("New LULUCF UIDs: ",len(new_set))
    crt_lulucf['GHG_FILE']=pd.NA
    uid_dict = checkinv.CreateDictionary(dirfilels)
    #Go through all GHG inventory UID's add the file name to GHG_FILE column to
    #row denoted by the UID
    for key in uid_dict.keys():
        if key in common_set:
            crt_lulucf.loc[crt_lulucf.UID == key,"GHG_FILE"]=(uid_dict[key][2])
    #To Excel, adjust column widths
    xlsx_writer  = pd.ExcelWriter(args.out, engine='xlsxwriter')
    crt_lulucf.to_excel(xlsx_writer,index=False, sheet_name='Sheet1')
    worksheet = xlsx_writer.sheets['Sheet1']
    for i, col in enumerate(crt_lulucf.columns):
        width = max(crt_lulucf[col].apply(lambda x: len(str(x))).max(), len(col))
        worksheet.set_column(i, i, width)
    xlsx_writer.close()
    print("Done")
