#!/nas1/home/jarip/lukeghg/bin/python
import pandas as pd
import xlsxwriter
from numpy import *
import os
import sys
from optparse import OptionParser as OP
import datetime

def GenerateRowTitleList(begin,end):
    row_title_ls=[]
    for item in range(begin,end+1):
        row_title_ls.append(str(item))
    return row_title_ls

parser = OP()
parser.add_option("-i","--ipcc",dest="f1",help="Read IPCC land-use category file")
parser.add_option("-o",dest="f2",help="Output  file")
parser.add_option("-y",dest="f3",help="Inventory year")
parser.add_option("-u",dest="f4",help="Read uncertainty for areas")
(options,args) = parser.parse_args()
if options.f1 is None:
    print("No input file")
    quit()
if options.f2 is None:
    print("No output file")
    quit()
if options.f3 is None:
    print("No inventory year")
    quit()
if options.f4 is None:
    print("No uncerainty file")
    quit()
#Inventory year for the row titles
inventory_year=int(options.f3)

table_title="The areas of IPCC land-use categories (1 000 ha). The last row shows the uncertainties, which are twice the relative standard errors, in area estimates due to sampling."
header_title="# Forest land# Cropland# Grassland# # # Wetlands # #Settlements# Other land# # Total\n"
column_title="Year# # # # Other wetlands# Peat extraction# Inland Waters # Wetlands total # # # Land# Land and inland waters\n"
row_title_ls=GenerateRowTitleList(1990,inventory_year)

lulucf_classes_all_file=options.f1

table_file=open(options.f2,"w")
#print(row_title_ls)
#Read the raw data
df = pd.read_table(lulucf_classes_all_file,delim_whitespace=True)
df_uncertainty=pd.read_table(options.f4,sep=';')
#Force one decimal even if zero
#df_uncertainty = df_uncertainty.applymap("{0:.1f}".format)
df_uncertainty.insert(6,column='Wetlands total',value='')
df_uncertainty['InWater']=""
df_uncertainty.index=['Uncertainty']

df=df[(df['region']==99) & (df['soil']==99)]
a=loadtxt(lulucf_classes_all_file,float,skiprows=1)
#Select sum rows first
check=logical_and(a[:,0]==99,a[:,2]==99)
b=a[check,:]
#print(b)
#Select land class one by one
#1=Forest land
fl_array=b[b[:,1]==1]
fl=fl_array[0,]
fl_ls=fl[4:len(fl)]
df_fl=df[df['ipcc']==1]
df_fl=df_fl.iloc[:,4:]
#print(fl_ls)
#print(df_fl)
#2=Cropland
cl_array=b[b[:,1]==2]
cl=cl_array[0,]
cl_ls=cl[4:len(cl)]
df_cl=df[df['ipcc']==2]
df_cl=df_cl.iloc[:,4:]
#print(cl_ls)
#print(df_cl)
#3=Grassland
#Collect all grassland: 3, 3.3, 3.5 etc.
grass_all = logical_and(b[:,1] >= 3,b[:,1] < 4)
gl_array=b[grass_all,:]
#Sum the columns
gl_array_sum=gl_array.sum(axis=0)
#Convert the array to list
gl=list(gl_array_sum)
gl_ls=gl[4:len(gl)]
df_gl=df[(df['ipcc']>=3) & (df['ipcc']<4)]
df_gl=df_gl.iloc[:,4:]
df_gl=df_gl.sum(axis=0)
df_gl=df_gl.to_frame().transpose()
#4=Other wetland
owl_array=b[b[:,1]==4]
owl=owl_array[0,]
owl_ls=owl[4:len(owl)]
df_owl=df[df['ipcc']==4]
df_owl=df_owl.iloc[:,4:]
#42=Peat extraction
peat_extr_array=b[b[:,1]==42]
peat_extr=peat_extr_array[0,]
peat_extr_ls=peat_extr[4:len(peat_extr)]
df_peat_extr=df[df['ipcc']==42]
df_peat_extr=df_peat_extr.iloc[:,4:]
#5=Settlement
sett_array=b[b[:,1]==5]
sett=sett_array[0,]
sett_ls=sett[4:len(sett)]
df_sett=df[df['ipcc']==5]
df_sett=df_sett.iloc[:,4:]
#6=Other land 
ol_array=b[b[:,1]==6]
ol = ol_array[0,]
ol_ls=ol[4:len(ol)]
df_ol=df[df['ipcc']==6]
df_ol=df_ol.iloc[:,4:]
#80=Inland waters
inland_waters_array=b[b[:,1]==80]
inland_waters=inland_waters_array[0,]
inland_waters_ls=inland_waters[4:len(inland_waters)]
df_inland_waters=df[df['ipcc']==80]
df_inland_waters=df_inland_waters.iloc[:,4:]
#99=Total area 
total_area_array=b[b[:,1]==99]
total_area=total_area_array[0,]
total_area_ls=total_area[4:len(total_area)]
df_total_area=df[df['ipcc']==99]
df_total_area=df_total_area.iloc[:,4:]
df_total_area.columns=list(range(1990,inventory_year+1))
df_all_wetlands_ls=[df_owl,df_peat_extr,df_inland_waters]
df_all_wetlands=pd.concat(df_all_wetlands_ls)
df_all_wetlands_sum=df_all_wetlands.sum(axis=0).to_frame().transpose()
df_all_land_ls=[df_fl,df_cl,df_gl,df_owl,df_peat_extr,df_sett,df_ol]
df_all_land=pd.concat(df_all_land_ls)
df_all_land_sum=df_all_land.sum(axis=0).to_frame().transpose()
df_total_ls=[df_inland_waters,df_all_land_sum]
df_total=pd.concat(df_total_ls)
df_total_sum=df_total.sum(axis=0).to_frame().transpose()
df_all_land_use_ls=[df_fl,df_cl,df_gl,df_owl,df_peat_extr,df_inland_waters,
                    df_all_wetlands_sum,df_sett,df_ol,df_all_land_sum,df_total_sum]
df_title_ls=[table_title]
df_title=pd.DataFrame(df_title_ls).transpose()
df_title.index=['Table 6-2.2']
df_first_row=pd.DataFrame(['Forest land','Cropland','Grass land','','','Wetlands','','Settlements','Other land','','Total']).transpose()
df_first_row.index=[' ']
df_second_row=pd.DataFrame(['','','','Other wetlands','Peat extraction','Inland waters','Wetlands total','','','Land','Land and inland waters']).transpose()
df_second_row.index=['Year']
df_all_land_use=pd.concat(df_all_land_use_ls,ignore_index=True)
df_all_land_use=df_all_land_use.transpose()
df_all_land_use.index=list(range(1990,inventory_year+1))
df_data_from=pd.DataFrame(['Data from: '+options.f1]).transpose()
df_uncertainty_from=pd.DataFrame(['Uncertainty from: '+options.f4]).transpose()
df_total_from_file=pd.DataFrame(['Total area (land and inland waters) in: '+options.f1]).transpose()
date_now=datetime.datetime.now()
df_date_now=pd.DataFrame(['Date:',str(date_now)]).transpose()
writer=pd.ExcelWriter('LUTable_622.xlsx',engine='xlsxwriter')
df_title.to_excel(writer,sheet_name='LUTable622',startrow=0,startcol=0,header=False)
df_first_row.to_excel(writer,sheet_name='LUTable622',startrow=1,startcol=0,header=False)
df_second_row.to_excel(writer,sheet_name='LUTable622',startrow=2,startcol=0,header=False)
df_all_land_use.to_excel(writer,sheet_name='LUTable622',startrow=3,startcol=0,header=False)
df_uncertainty.to_excel(writer,sheet_name='LUTable622',startrow=3+len(list(range(1990,inventory_year+1))),startcol=0,header=False)
df_data_from.to_excel(writer,sheet_name='LUTable622',startrow=6+len(list(range(1990,inventory_year+1))),startcol=0,index=False,header=False)
df_uncertainty_from.to_excel(writer,sheet_name='LUTable622',startrow=7+len(list(range(1990,inventory_year+1))),startcol=0,index=False,header=False)
df_total_from_file.to_excel(writer,sheet_name='LUTable622',startrow=10+len(list(range(1990,inventory_year+1))),startcol=0,index=False,header=False)
df_total_area.to_excel(writer,sheet_name='LUTable622',startrow=11+len(list(range(1990,inventory_year+1))),startcol=0,index=False)
df_date_now.to_excel(writer,sheet_name='LUTable622',startrow=14+len(list(range(1990,inventory_year+1))),startcol=0,index=False,header=False)
print(df_all_land_use.head())
print("Done")
writer.save()
writer.close()
#Quit now, Fix the file naming so that the text file does not override excel file
#or remove the text file part because now it is innecessary

#Create the table)
table_file.write(table_title)
table_file.write(header_title)
table_file.write(column_title)
for (row_title,fl,cl,gl,owl,peat_extr,sett,ol,inland_waters,total_area) in zip(row_title_ls,fl_ls,cl_ls,
                                                                               gl_ls,owl_ls,peat_extr_ls,
                                                                               sett_ls,ol_ls,inland_waters_ls,
                                                                               total_area_ls):
    total_land_area=fl+cl+gl+owl+peat_extr+sett+ol
    total_wetlands=owl+peat_extr+inland_waters
    #Markus may want to change the order of the columns
    table_file.write(row_title+"#"+str(fl)+"#"+str(cl)+"#"+str(gl)+"#"+str(owl)+"#"+str(peat_extr)+"#"+
                     str(inland_waters)+"#"+str(total_wetlands)+"#"+str(sett)+"#"+str(ol)+"#"+str(total_land_area)+"#"+
                     str(total_area)+"\n")

table_file.write("\n\n\n\n")
table_file.write("Data from:#\n")
table_file.write(lulucf_classes_all_file+"#\n")
table_file.write("\n\n")
table_file.write("Calculating total areas:#")
for item in row_title_ls:
    table_file.write(item+"#")
table_file.write("\n")
sum_total_area_ls=[]
for (fl,cl,gl,owl,peat_extr,sett,ol,inland_waters) in zip(fl_ls,cl_ls,gl_ls,owl_ls,peat_extr_ls,
                                                          sett_ls,ol_ls,inland_waters_ls):
    sum_total_area_ls.append(fl+cl+gl+owl+peat_extr+sett+ol+inland_waters)

table_file.write("Total area (sum from the Table)#")
for item in sum_total_area_ls:
    table_file.write(str(item)+"#")
table_file.write("\n")
table_file.write("Total area (in "+lulucf_classes_all_file+")#")
for item in total_area_ls:
    table_file.write(str(item)+"#")
table_file.write("\n")
table_file.write("Difference:#")

for (tot1,tot2) in zip(sum_total_area_ls,total_area_ls):
    diff = tot1-tot2
    table_file.write(str(diff)+"#")
table_file.write("\n")

