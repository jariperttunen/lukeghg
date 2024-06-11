import pandas as pd
import numpy as np
import lukeghg.checkinventoryvalues as checkinv

def create_uidset(dirfilels:list):
    uid_dict = checkinv.CreateDictionary(dirfilels)
    uidls = uid_dict.keys()
    uidset = set(uidls)
    return uidset

def select_crttool_uid(f:str):
    fxlsx = pd.ExcelFile(f)
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

def compare_uidsets(old_uid_set,crttool_uid_set):
    set_intersect = crttool_uid_set.intersect(old_uid_set)
    return set_intersect
