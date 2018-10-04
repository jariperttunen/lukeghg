import glob
import argparse
from lukeghg.crf.crfxmlfunctions import RoundToNDecimals, ReadGHGInventoryFile

def FilterUID(data_ls,uid_set):
    ls = []
    for data in data_ls:
        if len(data) > 0 and data[0].strip('{}') in uid_set:
            #This uses the same accuracy as in CRFReporter
            data = [RoundToNDecimals(x,6) for x in data]
            ls.append(data)
            uid_set.remove(data[0].strip('{}'))
        elif len(data) == 0:
            print("Empty line in a file")
    if len(uid_set) > 0:
        print("UID not found")
        print(uid_set)
    return ls

def FilterFilesWithUID(file_ls,uid_ls):
    """
    ReadGHGInventoryFile returns the content of a single
    inventory file as a list [[UID1, val1,val2,...,valn],[UID2,val1,val2,...,valn],...,[UIDN,val1,...,valn]].
    data_ls concatination (+) returns the content of all files (file_ls)  in such a single flattened list
    FilterUID filters out those with matching UID and the resulting list is returned
    """
    data_ls = []
    for file in file_ls:
        data_ls = data_ls + ReadGHGInventoryFile(file)
    data_ls = FilterUID(data_ls,set(uid_ls))
    #data_ls = [ls for f in file_ls for ls in ReadGHGInventoryFile(f)]
    return data_ls

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f',type=str,dest='f',help='Files to list (wildcard search)')
    args=parser.parse_args()
    print(args.f)
    ls = glob.glob(args.f)
    print(ls)
    
