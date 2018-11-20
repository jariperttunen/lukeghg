#!python 
import subprocess
import argparse
from optparse import OptionParser as OP
#ghg-master.py gathers all steps of xml import into one (this) file
#For the 2017 inventory the single command line is as follows. NOTE the double quotes for correct wild card usage.
#ghg-master.py -c "/hsan2/khk/ghg/2017/crf/[KPLU]*.csv" -p /hsan2/khk/ghg/2017/FIN_2019_1/PartyProfile-2017-PP.xml \
#-x PartyProfileResults_2017.xml -b /hsan2/khk/ghg/lukeghg/KPLULU1990/KP_CM_GM_RV_WDR_UID_notaatioavain.csv \
#-k /hsan2/khk/ghg/lukeghg/KPLULUSummary/KPSummary.csv  -l /hsan2/khk/ghg/lukeghg/KPLULUSummary/LUSummary.csv \
#-m /hsan2/khk/ghg/lukeghg/300_500_mappings_1.1.csv -n "/hsan2/khk/ghg/2017/crf/NIR*.csv"\
#-i "/hsan2/khk/ghg/2017/crf/C*.csv" -y 2017
#If one wants to do import step by step
#1.
#ghg-inventory.py -c "/hsan2/khk/ghg/2017/crf/[KPLU]*.csv" -p /hsan2/khk/ghg/2017/FIN_2019_1/PartyProfile-2017-PP.xml \
#-x PartyProfileResults_2017.xml -b /hsan2/khk/ghg/lukeghg/KPLULU1990/KP_CM_GM_RV_WDR_UID_notaatioavain.\
#-m /hsan2/khk/ghg/lukeghg/300_500_mappings_1.1.csv -y 2017
#2.
#kp-lulu-summary.py -c "/hsan2/khk/ghg/2017/crf/KP*.csv" -p PartyProfileResults_2017.xml \
#-x PartyProfileResults_2017.xml -u /hsan2/khk/ghg/lukeghg/KPLULUSummary/KPSummary.csv \
#-m /hsan2/khk/ghg/lukeghg/300_500_mappings_1.1.csv,args.m -y 2017
#3.
#kp-lulu-summary.py -c "/hsan2/khk/ghg/2017/crf/LU*.csv" -p PartyProfileResults_2017.xml \
#-x PartyProfileResults_2017.xml -u /hsan2/khk/ghg/lukeghg/KPLULUSummary/LUSummary.csv \
#-m /hsan2/khk/ghg/lukeghg/300_500_mappings_1.1.csv,args.m -y 2017
#4.
#nir3-table.py -c "/hsan2/khk/ghg/2017/crf/NIR*.csv" -p PartyProfileResults_2017.xml -x PartyProfileResults_2017.xml\
#-m /hsan2/khk/ghg/lukeghg/300_500_mappings_1.1.csv,args.m -y 2017
#5.
#information-items.py -p PartyProfileResults_2017.xml -x PartyProfileResults_2017.xml\
#-m /hsan2/khk/ghg/lukeghg/300_500_mappings_1.1.csv,args.m -y 2017
#6.
#nk-comments.py -c "/hsan2/khk/ghg/2017/crf/C*.csv" -p PartyProfileResults_2017.xml -x PartyProfileResults_2017.xml\
#-m /hsan2/khk/ghg/lukeghg/300_500_mappings_1.1.csv,args.m 

#The filling of the Party Profile xml with inventory data follows
parser = argparse.ArgumentParser()
#ghg-inventory.py arguments, GHG inventory results
parser.add_argument('-c','--csv',type=str,dest='c',help='GHG Inventory csv files')
parser.add_argument('-p','--party_profile_xml',type=str,dest='p',help='CRFReporter Party Profile XML')
parser.add_argument('-x','--xml',type=str,dest='x',help='XML output file filled with inventory results')
parser.add_argument('-b','--kp1990',type=str,dest='b',help='Base year 1990 GHG inventory csv file')
parser.add_argument('-m','--uid_map',type=str,dest='m',help='UID mapping file for CRFReporter')
parser.add_argument('-y','--year',type=str,dest='y',help='GHG Inventory year (last year in CRFReporter)')
#kp-lulu-summary.py arguments, GHG results come from two different sources 
parser.add_argument('-k','--kpsummary',type=str,dest='k',help='KP Summary file')
parser.add_argument('-l','--lusummary',type=str,dest='l',help='LULUCF Summary file')
#nir3-table.oy part arguments, NIR3 table
parser.add_argument('-n','--nir3',type=str,dest='n',help='NIR3 files')
#nk-comments.py part arguments, comments
parser.add_argument('-i','--comments',type=str,dest='i',help='KP and LULUCF comment files')
args=parser.parse_args()

subprocess.run(["ghg-inventory.py","-c",args.c,"-p",args.p,"-x",args.x,"-b",args.b,"-m",args.m,"-y",args.y])
subprocess.run(["kp-lulu-summary.py","-c",args.c,"-p",args.x,"-x",args.x,"-u",args.k,'-m',args.m,"-y",args.y])
subprocess.run(["kp-lulu-summary.py","-c",args.c,"-p",args.x,"-x",args.x,"-u",args.l,'-m',args.m,"-y",args.y])
subprocess.run(["nir3-table.py","-c",args.n,"-p",args.x,"-x",args.x,"-m",args.m,"-y",args.y])
subprocess.run(["information-items.py","-p",args.x,"-x",args.x,"-m",args.m,"-y",args.y])
subprocess.run(["nk-comments.py","-c",args.i,"-p",result_xml,"-x",result_xml,"-m",uid_mapping])
