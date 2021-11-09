#!python
import argparse
import pandas as pd

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-x","--excel",dest="f1",type=str,required=True,help="Excel from lulucf_classes_all.txt")
    parser.add_argument("-n","--nir_file",dest="f2",type=str,required=True,help="NIR LU_table6.2-2_UC_areas.csv")
    parser.add_argument("-y","--year",dest="i1",type=int,required=True,help="Inventory year")
    parser.add_argument("-s","--sheet",dest="f3",type=str,default="LUTable622",help="Sheet name (default: %(default)s)")
    args = parser.parse_args()

    #Read the excel and select the actual data, rearrange the columns
    df1 = pd.read_excel(args.f1,sheet_name=args.f3,skiprows=2,nrows=(args.i1-1990+1))
    df1 = df1.iloc[:,1:]
    df1.columns = list(range(0,len(df1.columns)))
    #This is the column order in LU_table6.2-2_UC_areas.csv
    df1 = df1[[0,1,2,3,7,8,4,5,10]]
    #Set the columns once more to range(0,11)
    df1.columns = list(range(0,len(df1.columns)))
    #Read LU_table6.2-2_UC_areas.csv
    df2 = pd.read_csv(args.f2,sep=',',skiprows=1)
    #Remove years
    df2 = df2.iloc[:,1:]
    #Set the columns once more to range(0,11)
    df2.columns = list(range(0,len(df2.columns)))
    #Check zero matrix
    df3 = df1.subtract(df2)
    #any(): if any value != 0 return True 
    series= df3.any()
    ls = series.values.tolist()
    s = set(ls)
    if True in s:
        print("Data in", args.f1,"differ from data in",args.f2)
    else:
        print("Data in", args.f1,"and in",args.f2,"are the same")
