#!python 
import subprocess
import argparse
from optparse import OptionParser as OP
## \file ghg-master.py
#
# The script `ghg-master.py` gathers all stages of CRFReporter xml assembly.
# See `run-ghg-master.sh` bash shell script to run GHG inventory xml in a single step.
#
# If one wants to  assemble the CRFReporter xml in stages execute the following 5 steps.
# Each program has '-h' (help) option that gives command arguments and their descriptions
# See also the end of this file, where the commands are executed with `subprocess.run`
#
# 1. Basic xml import (emissions and stocks).
#
#          ghg-inventory.py -c "/hsan2/khk/ghg/2017/crf/[KPLU]*.csv" -p /hsan2/khk/ghg/2017/FIN_2019_1/PartyProfile-2017-PP.xml 
#          -x PartyProfileResults_2017.xml -b /hsan2/khk/ghg/lukeghg/KPLULU1990/KP_CM_GM_RV_WDR_UID_notaatioavain.csv
#          -m /hsan2/khk/ghg/lukeghg/300_500_mappings_1.1.csv -y 2017
#
# 2. Some CL and GL inventory results come from two sources (forestry and agriculture). Add and import to xml.
#
#          kp-lulu-summary.py -c "/hsan2/khk/ghg/2017/crf/KP*.csv" -p PartyProfileResults_2017.xml 
#          -x PartyProfileResults_2017.xml -u /hsan2/khk/ghg/lukeghg/KPLULUSummary/KPSummary.csv 
#          -m /hsan2/khk/ghg/lukeghg/300_500_mappings_1.1.csv -y 2017
#
#          kp-lulu-summary.py -c "/hsan2/khk/ghg/2017/crf/LU*.csv" -p PartyProfileResults_2017.xml 
#          -x PartyProfileResults_2017.xml -u /hsan2/khk/ghg/lukeghg/KPLULUSummary/LUSummary.csv 
#          -m /hsan2/khk/ghg/lukeghg/300_500_mappings_1.1.csv -y 2017
#
# 3. NIR3 table requires own algorithm for xml import.
#
#          nir3-table.py -c "/hsan2/khk/ghg/2017/crf/NIR*.csv" -p PartyProfileResults_2017.xml -x PartyProfileResults_2017.xml
#          -m /hsan2/khk/ghg/lukeghg/300_500_mappings_1.1.csv  -y 2017
#
# 4. Information items are calculated from the deforestation results.
#
#          information-items.py -p PartyProfileResults_2017.xml -x PartyProfileResults_2017.xml
#          -m /hsan2/khk/ghg/lukeghg/300_500_mappings_1.1.csv  -y 2017
#
# 5. Finally, insert KPLULUCF and LULUCF comments for notation keys.
#
#          nk-comments.py -c "/hsan2/khk/ghg/2017/crf/C*.csv" -p PartyProfileResults_2017.xml -x PartyProfileResults_2017.xml
#          -m /hsan2/khk/ghg/lukeghg/300_500_mappings_1.1.csv 
#
##\page runghgmaster Create CRFReporter inventory XML file
##Run the following script to produce CRFReport XML from the GHG inventory files.
##Set the input and output XML files and inventory year (-y option)
##To make the changes to take effect recreate the *lukeghg* package and update the virtual environment. 
##\include run-ghg-master.sh 
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
#subprocess.run(["kp-lulu-summary.py","-c",args.c,"-p",args.x,"-x",args.x,"-u",args.k,'-m',args.m,"-y",args.y])
#EU529 does not have LULUCF sector 
if args.l != None:
    subprocess.run(["kp-lulu-summary.py","-c",args.c,"-p",args.x,"-x",args.x,"-u",args.l,'-m',args.m,"-y",args.y])
#subprocess.run(["nir3-table.py","-c",args.n,"-p",args.x,"-x",args.x,"-m",args.m,"-y",args.y])
#subprocess.run(["information-items.py","-p",args.x,"-x",args.x,"-m",args.m,"-y",args.y])
subprocess.run(["nk-comments.py","-c",args.i,"-p",args.x,"-x",args.x,"-m",args.m])
