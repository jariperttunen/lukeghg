import functools as ft
import datetime

#Possible types of entry
NK="NK"
number="number"
dropdown="dropdown"

#Possible values for the 'type' key in a comment dictionary
nk_explanation="nk_explanation"
ipcc_comment="allocation_by_ipcc"
party_comment="allocation_by_party"
official_comment="official_comment"

#Dictionary of Notation keys, methods etc. from DataExchangeJSON_DescriptionDocument_v1.0.pdf
#for their decimal values
crtnk = {"":0,"C":1,"CR":2,"CS":4,"D":8,"GCV":16,
         "IE":32,"IO":64,"M":128,"NA":256,"NCV":512,
         "NE":1024,"NO":2048,"Reserved":4096,"OTH":8192,
         "PS":16384,"R":32768,"RA":65536,
         "T1":131072,"T1a":262144,"T1b":524288,"T1c":1048576,
         "T2":2097152,"T3":4194304,"FX":8388608}

def create_crt_time_stamp():
    local_time = datetime.datetime.now()
    crt_time_stamp = local_time.strftime("%Y/%m/%d %H:%M (Europe/Helsinki)")
    return crt_time_stamp

def crtvalue(s:str,sep=','):
    """
    Calculate decimal value for a sequence of notation keys, methods etc.
    @param s String of notation keys, methods etc. from the \p nk dictionary
    @param sep Separator between notation keys in \p s
    @retval crt_val Decimal value for \p s valid for CRT json
    @pre The string \p s must contain at least one Notation key
    """
    #Create a list of Notation keys 
    ls = s.split(sep)
    #Starting from zero the the first argument \p a is a number and
    # the second one \p b is one Notation key from the list \p ls
    crt_val = ft.reduce(lambda a,b:a+crtnk[b],ls,0)
    return crt_val

def is_ne_key(value:int):
    """
    Bitwise comparision with NE key
    @param value Integer value for a Notation key
    @return True if \p value has NE key False if not
    @note The decimal value for sequence of notation keys allowed
    """
    return value & crtnk['NE'] == crtnk['NE']

def is_na_key(value:int):
    """
    Bitwise comparision with NA key
    @param value Integer value for a Notation key
    @return True if \p value has NA key False if not
    @note The decimal value for sequence of notation keys allowed
    """
    return value & crtnk['NA'] == crtnk['NA']

def is_ie_key(value:int):
    """
    Bitwise comparision with IE key
    @param value Integer value for a Notation key or sequence of Notation keys
    @return True if \p value has IE key False if not
    @note The decimal value for sequence of notation keys allowed
    """
    return value & crtnk['IE'] == crtnk['IE']

def is_ghg_notation_key(value:int):
    """
    Bitwise scan for notation key.
    @param value Integer value for GHG Notation key or sequence of Notation keys
    @return True if Notation key found False otherwise
    @note The GHG notation keys used denote IE (Intergrated elsewhere), NA (Not applicable),
          NE (Not estimated) or NO (No occuring)
    """
    return (value & crtnk['IE'] or value & crtnk['NA'] or value & crtnk['NE'] or
            value & crtnk['NO']) != 0
                                                             
def is_dropdown_key(value:int):
    """
    Bitwise scan for Drop down notation key
    @param value Integer value for Drop dawn key or sequence of Drop down keys
    @return True if Drop down key found False otherwise
    @note Drop down keys are selected from the drop down menu in ETF tool when applicable
    """
    return (value & crtnk['C'] or  value & crtnk['D'] or value & crtnk['T1'] or
            value & crtnk['T1a'] or value & crtnk['T1b'] or value & crtnk['T1c'] or
            value & crtnk['T2'] or value & crtnk['T2'] or  value & crtnk['T3'] or
            value & crtnk['CR'] or value & crtnk['CS'] or  value & crtnk['M'] or
            value & crtnk['RA'] or value & crtnk['OTH']) != 0
