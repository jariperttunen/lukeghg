#!python
# -*- coding: iso-8859-1 -*-
import pandas as pd
import xlsxwriter
from optparse import OptionParser as OP

parser = OP()
parser.add_option("-i","--input",dest="f1",help="Read Areas of organic soils (peatlands) of forest land remaining forest land by site type (1 000 ha)")
parser.add_option("-y","--year",dest="f2",help="GHG inventory year")

(options,args) = parser.parse_args()
if options.f1 is None:
    print("No input file")
    quit()
if options.f2 is None:
    print("No GHG inventory year")
    quit()

columnls=['Mineral','Undrained','Herb-rich type (Rhtg)','Vaccinium myrtillus type (Mtkg)','Vaccinium vitis-idaea type (Ptkg)',
          'Dwarf shrub type (Vatkg)','Caldina type (Jätkg)']
df_title=pd.DataFrame(['Table 6.4-1 Areas of organic soils (peatlands) of forest land remaining forest land by site type (1 000 ha)']).transpose()
df = pd.read_table(options.f1,delim_whitespace=True,names=columnls,usecols=range(1,8),header=None)
df.index=list(range(1990,int(options.f2)+1))
df['Drained organic']=df['Herb-rich type (Rhtg)']+df['Vaccinium myrtillus type (Mtkg)']+df['Vaccinium vitis-idaea type (Ptkg)']+df['Dwarf shrub type (Vatkg)']+df['Caldina type (Jätkg)']
df['Organic']=df['Drained organic']+df['Undrained']
df['Total (Mineral+Organic)']=df['Mineral']+df['Organic']

df_explain1=pd.DataFrame(['Drained organic = Herb-rich type (Rhtg)+Vaccinium myrtillus type (Mtkg)+Vaccinium vitis-idaea type (Ptkg)+Drwarf shrub type(Vatkg)+Caldina type (Jätkg)']).transpose()
df_explain2=pd.DataFrame(['Organic  = Drained organic+Undrained']).transpose()
df_explain3=pd.DataFrame(['Total (Mineral+Organic) = Mineral+Organic']).transpose()
writer=pd.ExcelWriter('LUTable_641.xlsx',engine='xlsxwriter')
df_title.to_excel(writer,'LUTable6-4.1',startrow=0,startcol=0,header=False,index=False)
df.to_excel(writer,'LUTable6-4.1',startrow=1,startcol=0)
df_explain1.to_excel(writer,'LUTable6-4.1',startrow=31,startcol=0,header=False,index=False)
df_explain2.to_excel(writer,'LUTable6-4.1',startrow=32,startcol=0,header=False,index=False)
df_explain3.to_excel(writer,'LUTable6-4.1',startrow=33,startcol=0,header=False,index=False)

writer.save()
