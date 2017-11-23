from numpy import *
import os
import sys
from optparse import OptionParser as OP

def GenerateRowTitleList(begin,end):
    row_title_ls=[]
    for item in range(begin,end+1):
        row_title_ls.append(str(item))
    return row_title_ls

parser = OP()
parser.add_option("-c","-i",dest="f1",help="Read IPCC land-use category file")
parser.add_option("-o",dest="f2",help="Output  file")
parser.add_option("-y",dest="f3",help="Inventory year")
(options,args) = parser.parse_args()
if options.f1 is None:
    print("No input file")
    quit()
if options.f2 is None:
    print("No output file")
    quit()
if options.f2 is None:
    print("No inventory year")
    quit()

#Inventory year for the row titles
inventory_year=float(options.f3)

table_title="The areas of IPCC land-use categories (1 000 ha). The last row shows the uncertainties, which are twice the relative standard errors, in area estimates due to sampling.#\n"
header_title="# Forest land# Cropland# Grassland# # # Wetlands # #Settlements# Other land# # Total\n"
column_title="Year# # # # Other wetlands# Peat extraction# Inland Waters # Wetlands total # # # Land# Land and inland waters\n"
row_title_ls=GenerateRowTitleList(1990,inventory_year)

lulucf_classes_all_file=options.f1

table_file=open(options.f2,"w")
#print(row_title_ls)
#Read the raw data
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
#print(fl_ls)
#2=Cropland
cl_array=b[b[:,1]==2]
cl=cl_array[0,]
cl_ls=cl[4:len(cl)]
#3=Grassland
#Collect all grassland: 3, 3.3, 3.5 etc.
grass_all = logical_and(b[:,1] >= 3,b[:,1] < 4)
gl_array=b[grass_all,:]
#Sum the columns
gl_array_sum=gl_array.sum(axis=0)
#Convert the array to list
gl=list(gl_array_sum)
gl_ls=gl[4:len(gl)]
#4=Other wetland
owl_array=b[b[:,1]==4]
owl=owl_array[0,]
owl_ls=owl[4:len(owl)]
#42=Peat extraction
peat_extr_array=b[b[:,1]==42]
peat_extr=peat_extr_array[0,]
peat_extr_ls=peat_extr[4:len(peat_extr)]
#5=Settlement
sett_array=b[b[:,1]==5]
sett=sett_array[0,]
sett_ls=sett[4:len(sett)]
#6=Other land 
ol_array=b[b[:,1]==6]
ol = ol_array[0,]
ol_ls=ol[4:len(ol)]
#80=Inland waters
inland_waters_array=b[b[:,1]==80]
inland_waters=inland_waters_array[0,]
inland_waters_ls=inland_waters[4:len(inland_waters)]
#99=Total area 
total_area_array=b[b[:,1]==99]
total_area=total_area_array[0,]
total_area_ls=total_area[4:len(total_area)]
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

