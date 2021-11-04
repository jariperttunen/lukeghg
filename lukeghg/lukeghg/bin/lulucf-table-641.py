#!python
import argparse
import pandas as pd
import xlsxwriter

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--input",dest="f1",required=True,help="Read Areas of organic soils (peatlands) of forest land remaining forest land by site type (1 000 ha)")
    parser.add_argument("-y","--year",dest="f2",required=True,help="GHG inventory year")
    parser.add_argument("-o","--output",dest="f3",required=True,help="Output file")
    parser.add_argument('--format_only',action="store_true",help="Genrate Table 6.4-1 as is") 
    args= parser.parse_args()

    if args.format_only:
        print("Format only")
        columnls=['Mineral','Undrained','Herb-rich type (Rhtg)','Vaccinium myrtillus type (Mtkg)','Vaccinium vitis-idaea type (Ptkg)',
                  'Dwarf shrub type (Vatkg)','Caldina type (Jätkg)',"Drained organic","Organic", "Total(Mineral+Organic)"]
        df = pd.read_table(args.f1,sep=',',names=columnls,skiprows=1)
    else:
        print("Calculating totals")
        columnls=['Mineral','Undrained','Herb-rich type (Rhtg)','Vaccinium myrtillus type (Mtkg)','Vaccinium vitis-idaea type (Ptkg)',
                  'Dwarf shrub type (Vatkg)','Caldina type (Jätkg)']
        df = pd.read_table(args.f1,sep=',',names=columnls,usecols=range(1,8),skiprows=1)
        df['Drained organic']=df['Herb-rich type (Rhtg)']+df['Vaccinium myrtillus type (Mtkg)']+df['Vaccinium vitis-idaea type (Ptkg)']+df['Dwarf shrub type (Vatkg)']+df['Caldina type (Jätkg)']
        df['Organic']=df['Drained organic']+df['Undrained']
        df['Total (Mineral+Organic)']=df['Mineral']+df['Organic']
    
    df.index=list(range(1990,int(args.f2)+1))
    df_title=pd.DataFrame(['Table 6.4-1 Areas of organic soils (peatlands) of forest land remaining forest land by site type (1 000 ha)']).transpose()
    df_explain1=pd.DataFrame(['Drained organic = Herb-rich type (Rhtg)+Vaccinium myrtillus type (Mtkg)+Vaccinium vitis-idaea type (Ptkg)+Drwarf shrub type(Vatkg)+Caldina type (Jätkg)']).transpose()
    df_explain2=pd.DataFrame(['Organic  = Drained organic+Undrained']).transpose()
    df_explain3=pd.DataFrame(['Total (Mineral+Organic) = Mineral+Organic']).transpose()
    df_datafrom=pd.DataFrame(['Data from: '+args.f1])
    writer=pd.ExcelWriter(args.f3,engine='xlsxwriter')
    df_title.to_excel(writer,'LUTable6-4.1',startrow=0,startcol=0,header=False,index=False)
    df.to_excel(writer,'LUTable6-4.1',startrow=1,startcol=0)
    comment_start=len(df.index)+1
    df_explain1.to_excel(writer,'LUTable6-4.1',startrow=comment_start+1,startcol=0,header=False,index=False)
    df_explain2.to_excel(writer,'LUTable6-4.1',startrow=comment_start+2,startcol=0,header=False,index=False)
    df_explain3.to_excel(writer,'LUTable6-4.1',startrow=comment_start+3,startcol=0,header=False,index=False)
    df_datafrom.to_excel(writer,'LUTable6-4.1',startrow=comment_start+4,startcol=0,header=False,index=False)

    writer.save()
