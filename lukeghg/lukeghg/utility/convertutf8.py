import glob
import argparse

def convert_utf8bom(file_name):
    """Convert UTF8BOM to UTF8"""
    print(file_name)
    s = open(file_name, mode='r', encoding='utf-8-sig').read()
    open(file_name, mode='w', encoding='utf-8').write(s)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f',type=str,dest='f',help='GHGInventory data csv files (wild card search)')
    args=parser.parse_args()
    if args.f==None:
        print('No GHG inventory file')
    file_ls=glob.glob(args.f)
    for file_name in file_ls:
        convert_utf8bom(file_name)
