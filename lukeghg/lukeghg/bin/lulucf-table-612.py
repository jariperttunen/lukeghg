#!python
import glob
import argparse
from lukeghg.nir import lulucftable612
#start=1990
#end=2017
#file_name='Table-6.1-2.txt'
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s","--start",dest="f1",type=int,default=1990,help="Inventory start year (1990)")
    parser.add_argument("-e","--end",dest="f2",type=int,required=True,help="Inventory end year")
    parser.add_argument("-o","--ofile",dest="f3",type=str,required=True,help="Output file name")
    parser.add_argument("-d","--crfdir",dest="f4",type=str,required=True,help="CRF directory for inventory results")
    parser.add_argument("-b","--biomass",dest="f5",type=str,default="Table_6.1-2.csv",help="Biomass file, default Table_6.1-2.csv")
    args = parser.parse_args()
    start=args.f1
    end=args.f2
    file_name=args.f3
    d=args.f4
    bmass_file = args.f5
    lulucftable612.WriteCO2eqTableData(start,end,file_name,d,bmass_file)
