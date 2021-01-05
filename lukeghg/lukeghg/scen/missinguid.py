import glob
import pathlib
import pandas as pd
import xlsxwriter
import ghgscenario as gs
import lukeghg.crf.ghginventory as ghg

uid_file_dict = dict()

def uidmatrix_cell_count(uid_set:set):
    return len(uid_set)

def possible_missing_uid(scenuid_set,uidmatrix_set):
    return scenuid_set.difference(uidmatrix_set)

def scen_files_to_uid_set(files:str,uid_mapping_file:str):
    file_ls = glob.glob(files)
    uid_set = set()
    for fname in file_ls:
        p=pathlib.Path(fname)
        ls = ghg.ParseGHGInventoryFile(fname,uid_mapping_file)
        for x in ls:
            if len(x) == 0:
                print("Empty line")
            else:
                uid = x.pop(0)
                uid_set.add(uid)
                uid_file_dict[uid]=p.name
    return uid_set

def uid_matrix_to_uid_cells(uid_matrix_file:str):
    df = gs.read_uid_matrix_file(uid_matrix_file)
    df = df.loc[:,'FL-FL':]
    a = df.to_numpy()
    a = a.flatten()
    uid_set = set(a)
    return uid_set

def uid_matrix_to_uid_set(uid_matrix_file:str):
    df = gs.read_uid_matrix_file(uid_matrix_file)
    #Start column is FL-FL 
    df = df.loc[:,'FL-FL':]
    #This will be array of arrays
    a = df.to_numpy()
    #This will be an array
    a = a.flatten()
    #The set data type
    uid_set = set(a)
    #Filter out empty cells
    uid_set = {x for x in a if pd.notna(x)}
    return uid_set

def create_uid_df(uidmatrix_count,uidmatrix_set,scenuid_set,missing_uid_set):
    ls1 = sorted(list(uidmatrix_set))
    ls2 = sorted(list(missing_uid_set))
    ls3 = sorted(list(scenuid_set))
    fname_ls2 = [uid_file_dict[uid] for uid in ls2]
    fname_ls3 = [uid_file_dict[uid] for uid in ls3]
    ls_table = [ls1,ls2,fname_ls2,ls3,fname_ls3]
    df = pd.DataFrame(ls_table)
    df = df.transpose()
    df.columns=["In UIDMatrix: "+str(len(ls1)),"Missing from UIDMatrix: "+str(len(ls2)),"File",
                "In Scenario files: "+str(len(ls3)),"File"]
    df.index.name="All UIDMatrix entries: "+str(uidmatrix_count)
    return df

def create_missing_scen_uid_excel(uid_matrix_file:str,scen_files:str,uid_mapping_file:str,excel_file:str):
    """Create excel file containing missing uid from the inventory
    uid_matrix_file: template uid matrix file
    scen_files: scenario inventory files (wild card search)
    uid_mapping_file: the uid mapping file
    excel_file: output file for missing uid
    """
    uidmatrix_count = uidmatrix_cell_count(uid_matrix_to_uid_cells(uid_matrix_file))
    uidmatrix_set = uid_matrix_to_uid_set(uid_matrix_file)
    scenuid_set = scen_files_to_uid_set(scen_files,uid_mapping_file)
    missing_uid_set =  possible_missing_uid(scenuid_set,uidmatrix_set)
    df = create_uid_df(uidmatrix_count,uidmatrix_set,scenuid_set,missing_uid_set)
    writer = pd.ExcelWriter(excel_file,engine='xlsxwriter')
    df.to_excel(writer,sheet_name='UIDMatrix')
    writer.close()

