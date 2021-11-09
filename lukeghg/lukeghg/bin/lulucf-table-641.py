#!python
import argparse
import pandas as pd
import xlsxwriter

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--input",dest="f1",required=True,default="Table_6.4-1_FLRem_Areas_of_organic_soils.csv",
                        help="Read areas of organic soils (peatlands) of forest land remaining forest land by site type (1 000 ha),\n"+
                              "default Table_6.4-1_FLRem_Areas_of_organic_soils.csv in NIR directory")
    parser.add_argument("-y","--year",dest="f2",required=True,help="Inventory year")
    parser.add_argument("-o","--output",dest="f3",required=True,help="Output file")
    args_group = parser.add_mutually_exclusive_group(required=True)
    args_group.add_argument('--format_only',action="store_true",help="Generate Table 6.4-1 as is in the input file")
    args_group.add_argument('--check_total',action="store_true",help="Calculate totals and compare with precalculated totals")
    args= parser.parse_args()

    df = pd.DataFrame()
    if args.format_only:
        print("Format only")
        columnls=['Mineral','Undrained','Herb-rich type','Vaccinium myrtillus type','Vaccinium vitis-idaea type',
                  'Dwarf shrub type','Cladina type',"Drained organic","Total organic","Total"]
        df = pd.read_table(args.f1,sep=',',usecols=columnls)
    else:
        print("Checking total")
        columnls=['Mineral','Undrained','Herb-rich type','Vaccinium myrtillus type','Vaccinium vitis-idaea type',
                  'Dwarf shrub type','Cladina type',"Drained organic","Total organic","Total"]
        df = pd.read_table(args.f1,sep=',',usecols=columnls)
        df['Drained organic calculated'] = df['Herb-rich type']+df['Vaccinium myrtillus type']+df['Vaccinium vitis-idaea type']+df['Dwarf shrub type']+df['Cladina type']
        df['Drained organic difference'] = df['Drained organic'] - df['Drained organic calculated']
        df['Total organic calculated'] = df['Drained organic calculated']+df['Undrained']
        df['Total organic difference'] = df['Total organic'] - df['Total organic calculated'] 
        df['Total calculated'] = df['Mineral']+df['Total organic calculated']
        df["Total difference"] = df['Total'] - df['Total calculated']
 
    df.index=list(range(1990,int(args.f2)+1))
    df_title=pd.DataFrame(['Table 6.4-1 Areas of organic soils (peatlands) of forest land remaining forest land by site type (1 000 ha)']).transpose()
    df_explain1=pd.DataFrame(['Drained organic = Herb-rich type + Vaccinium myrtillus type + Vaccinium vitis-idaea type + Drwarf shrub type + Cladina type']).transpose()
    df_explain2=pd.DataFrame(['Total organic  = Drained organic+Undrained']).transpose()
    df_explain3=pd.DataFrame(['Total = Mineral+ Total organic']).transpose()
    df_datafrom=pd.DataFrame(['Data from: '+args.f1])
    writer=pd.ExcelWriter(args.f3,engine='xlsxwriter')
    df_title.to_excel(writer,'LUTable6-4.1',startrow=0,startcol=0,header=False,index=False)
    df.to_excel(writer,'LUTable6-4.1',startrow=1,startcol=0,header=True)
    comment_start=len(df.index)+1
    df_explain1.to_excel(writer,'LUTable6-4.1',startrow=comment_start+1,startcol=0,header=False,index=False)
    df_explain2.to_excel(writer,'LUTable6-4.1',startrow=comment_start+2,startcol=0,header=False,index=False)
    df_explain3.to_excel(writer,'LUTable6-4.1',startrow=comment_start+3,startcol=0,header=False,index=False)
    df_datafrom.to_excel(writer,'LUTable6-4.1',startrow=comment_start+4,startcol=0,header=False,index=False)

    writer.save()
