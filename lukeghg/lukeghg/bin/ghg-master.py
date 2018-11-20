#!python 
import subprocess
import argparse
from optparse import OptionParser as OP


#The basic xml import
inventory_year="2017"
crf_files="/hsan2/khk/ghg/2017/crf/[KPLU]*.csv"
partyprofile="/hsan2/khk/ghg/2017/FIN_2019_1/PartyProfile-2017-PP.xml"
result_xml="PartyProfileResults_2017.xml"
uid_mapping="/hsan2/khk/ghg/lukeghg/300_500_mappings_1.1.csv"
#some CLGL items need the base year 1990
add_1990="/hsan2/khk/ghg/lukeghg/KPLULU1990/KP_CM_GM_RV_WDR_UID_notaatioavain.csv"
#Some items from agriculture come from two sources
kp_files="/hsan2/khk/ghg/2017/crf/[KP]*.csv"
lulu_files="/hsan2/khk/ghg/2017/crf/[LU]*.csv"
kpsummary="/hsan2/khk/ghg/lukeghg/KPLULUSummary/KPSummary.csv"
lulusummary='"/hsan2/khk/ghg/lukeghg/KPLULUSummary/LUSummary.csv"'
#NIR3 table is also a special case in xml import
nir3_files="/hsan2/khk/ghg/2017/crf/NIR*.csv"
#Finally add comments
comment_files="/hsan2/khk/ghg/2017/crf/C*.csv"

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
