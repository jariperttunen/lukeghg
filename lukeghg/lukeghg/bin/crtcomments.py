#!python
import sys
import argparse
import glob
import json
import pandas as pd
import lukeghg.utility.crtnotationkeys as nk
import crttool

IPCC='Allocation as per IPCC Guidelines'
PARTY='Allocation used by the Party'
EXPLANATION='EXPLANATION'

def read_lulucf_comment_file(fname:str):
    """
    Read LULUCF file for Notation key explanations for IE and NE 
    @param fname File name
    @retval datalss List of lists of Notation key explanations
    @post UID is case folded, i.e. case distinctions are removed for UID comparisons
    @note Reads old crf/CLU*.csv files 
    """
    f=open(fname,'r',encoding='utf-8')
    datalss = [x.rstrip().rpartition('#')[2].split(';') for x in f.readlines() if x.count('#') != 1]
    datalss = [casefold_uid(x) for x in datalss]
    f.close()
    return datalss

def read_ghg_comment_csv(fname:str,sep=','):
    """
    Read LULUCF Notation key explanations for IE and NE from a csv file.
    @param fname File name
    @param sep The item seperator in the csv file, default is comma (`,`)
    @retval datalss List of lists of Notation key explanations
    @pre The csv file is produced from the Excel file produced for the EFT tool \author Sofia Vikström
    @post UID is case folded, i.e. case distinctions are removed for UID comparisons
    @sa  read_ghg_comment_excel
    """
    df = pd.read_table(fname,sep=sep,skiprows=1,usecols=[0,3,4,5])
    df['UID']=df['UID'].map(lambda x:x.casefold(),na_action='ignore')
    df['Explanation']=df['Explanation'].map(lambda x: " ".join(x.split()),na_action='ignore')
    return df

def read_ghg_comment_excel(fname:str):
    """
    Read Excel file for Notation key comments. Return dataframes for NE and IE notation keys.
    @param fname Excel files
    @retval (dfne,dfie) Pair of dataframes  \p dfne and \p dfie for NE and IE comments respectively
    @post UID values are casefolded for caseless comparison in CRT json
    @post New line characters stripped in *Explanation* column  
    @note Excel file is prepared for the EFT tool \author Sofia Vikström
    """
    dfne = pd.read_excel(fname,sheet_name='NE',skiprows=1,usecols=[0,4])
    dfne['UID']=dfne['UID'].map(lambda x:x.casefold(),na_action='ignore')
    dfne['Explanation']=dfne['Explanation'].map(lambda x: " ".join(x.split()),na_action='ignore')
    dfie = pd.read_excel(fname,sheet_name='IE',skiprows=1,usecols=[0,3,4,5])
    dfie['UID']=dfie['UID'].map(lambda x:x.casefold(),na_action='ignore')
    dfie['Allocation as per IPCC Guidelines']=dfie['Allocation as per IPCC Guidelines'].map(lambda x: x.strip(),na_action='ignore')
    dfie['Allocation used by the Party']=dfie['Allocation used by the Party'].map(lambda x: x.strip(),na_action='ignore')
    dfie['Explanation']=dfie['Explanation'].map(lambda x: x.strip(),na_action='ignore')
    return (dfne,dfie)

def create_nk_comment_list(df):
    """
    Convert to dataframe to list to match create_crt_comment_dictionary_list
    @param df Dataframe for notation key comments
    @retval List of list of notation key comments
    """
    return df.to_numpy().tolist()

def casefold_uid(x):
    """
    @param x UID string
    @retval x Casefolded version of \p x for caseless comparison
    """
    x[0]=x[0].casefold()
    return x

def create_crt_comment_dictionary_list(cls:list):
    """
    Single Notation key explanation or comments in CRT json can have one or three comments.
    Create comment for NE or IE notation keys.
    @param cls Single Notation key comments, one for NE, three for IE
    @return List of comments. Each comment is a dictionary. 
    @pre \p Length cls == 1
    @post For NE return one comment
    @post For IE return three comments
    """
    tstamp = nk.create_crt_time_stamp()
    if (len(cls)==2):
        #NE comment
        nkc = {'comment':cls[1],'time_stamp':tstamp,'type':nk.nk_explanation}
        return [nkc]
    else:
        #IE comment
        #1. Allocation by party
        ipcc = {'comment':cls[1],'time_stamp':tstamp,'type':nk.ipcc_comment}
        #2. Allocation by IPCC                 
        party = {'comment':cls[2],'time_stamp':tstamp,'type':nk.party_comment}
        #3. Notation key explanation
        nkc = {'comment':cls[3],'time_stamp':tstamp,'type':nk.nk_explanation}
        return [nkc,ipcc,party]


def insert_crt_comment(year,year_entry:dict,uid:str,comment_ls:list):
    """
    Insert notation key comment for the \p uid and \p year
    @param  year Year for the time series
    @param year_entry Year entry dictionary from CRT json
    @param uid UID fot the time series
    @param comment_ls List of notation key comments
    @pre Inventory results have been inserted with `crttool`
    @pre Time series year must contain notation key
    """ 
    uid_entry = crttool.find_crt_uid_entry(year_entry,uid)
    value_entry = uid_entry['value']
    value_type = value_entry['type']
    if value_type == nk.NK:
        if len(comment_ls)==1:
            if nk.is_na_key(value_entry['value']):
                comment_ls[0]['type'] = nk.official_comment
            print(year,value_entry['value'],value_type,comment_ls[0]['comment'],comment_ls[0]['type'])
        else:
            print(year,value_entry['value'],value_type,comment_ls[0]['comment'],';',
                  comment_ls[1]['comment'],';',comment_ls[2]['comment'])
        uid_entry['comments'] = comment_ls
    else:
        print(year,value_type,"Not Notation key entry, notation key comment not applicable:",file=sys.stderr)
        
def insert_crt_comments(crt_json:dict,commentlss:list,yearls:list):
    """
    Insert notation key comments to CRT json
    @param crt_json CRT json dictionary
    @param commentlss List of list of comments
    @param yearls The inventory years
    @retval crt_json CRT json dictionary with notation key comments
    """    
    crtvaluesls = crttool.crtvalues(crt_json)
    year = yearls[0]
    year_entry = crttool.find_crt_inventory_year(crtvaluesls,str(year))
    for commentls in commentlss:
        uid = commentls[0]
        if  not pd.isna(uid) and crttool.has_crt_uid_entry(year_entry,uid):
            commentdictls = create_crt_comment_dictionary_list(commentls)
            print(uid,"Inserting notation key comment")
            for year in yearls:
                year_entry = crttool.find_crt_inventory_year(crtvaluesls,str(year))
                insert_crt_comment(year,year_entry,uid,commentdictls)
        else:
            print(uid,"UID not found",file=sys.stderr)
    return crt_json

if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
        description=
        "Read GHG inventory Notation key comment file and the CRT json data exchange file.\n"+
        "Fill the CRT json file with inventory results and write new CRT json file for the ETF tool.\n"+
        "NOTE that the GHG inventory results must have been inserted with 'crttool.py' first")
    input_group = parser.add_argument_group('Input file group','Input files can be Excel or CSV file')
    input_exclusive_group = input_group.add_mutually_exclusive_group(required=True)
    input_exclusive_group.add_argument('-x','--excel',dest="x",type=str,
                             help="GHG inventory notation key Excel file(e.g. NK_explanations_elokuu.xlsx)")
    input_exclusive_group.add_argument('-c','--csv',dest='c',type=str,
                             help="GHG inventory notation key CSV file (e.g. crf/CLU_notation_explanations.csv)")
    parser.add_argument('-j','-json' ,dest="j",type=str,required=True,
                        help="CRT json data exchange file")
    parser.add_argument('-b','--begin',dest="b",type=int,default=1990,
                        help="Inventory begin year, defaults to 1990")
    parser.add_argument('-y','--year',dest="y",type=int,required=True,
                        help="Inventory year, the last year in ETF tool")
    parser.add_argument('-o','--out',dest="o",type=str,required=True,
                        help="CRT json output file for ETF tool")
    args = parser.parse_args()
    yearls = list(range(args.b,args.y+1)) 
    print("Reading CRT json file:", args.j)
    crt_json = crttool.crtjson(args.j)
    if args.x:
        print("Reading Notation key comment file:",args.x)
        (dfne,dfie) = read_ghg_comment_excel(args.x)
        #print("Inserting NE Notation key comments")
        #nelss = create_nk_comment_list(dfne)
        #crt_json2 = insert_crt_comments(crt_json,nelss,yearls)
        print("Inserting IE Notation keys")
        ielss = create_nk_comment_list(dfie)
        crt_json3 = insert_crt_comments(crt_json,ielss,yearls)
        print("Writing CRT json file:",args.o)
        crttool.crtjsondump(args.o,crt_json3)
    else:
        print("Reading Notation key comment file:",args.c)
        df = read_ghg_comment_csv(args.c)
        nk_lss = create_nk_comment_list(df)
        print("Inserting Notation key comments")
        #nelss = create_nk_comment_list(dfne)
        crt_json2 = insert_crt_comments(crt_json,nk_lss,yearls)
        print("Writing CRT json file:",args.o)
        crttool.crtjsondump(args.o,crt_json2)
    
