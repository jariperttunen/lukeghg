#!python
#Sample usage: ghg-master.py -c 'ghg/2016/crf/[LUKP]*.csv' -p party_profile_232429.xml -x FIN_2018_3_PartyProfile.xml -m ghg/2016/lukeghg/300_500_mappings_1.1.csv -y 2016 > Import.log 2>Importerror.log
import glob
import subprocess
from optparse import OptionParser as OP

parser = OP()
parser.add_option("-c","--csv",dest="f1",help="Read GHG inventory csv files")
parser.add_option("-p","--pxml",dest="f2",help="Read CRFReporter Party Profile xml file")
parser.add_option("-x","--xml",dest="f3",help="Write new Party profile populated with inventory results")
parser.add_option("-m","--map",dest="f4",help="CRFReporter 3.0.0 --> 5.0.0 UID mapping file")
parser.add_option("-y","--year",dest="f5",help="Inventory year (the last year in CRFReporter)")
(options,arg)=parser.parse_args()
if options.f1 is None:
    print("No inventory GHG csv files")
    quit()
if options.f2 is None:
    print("No CRFReporter Party Profile XML input file")
    quit()
if options.f3 is None:
    print("No CRFReporter XML output file name")
    quit()
if options.f4 is None:
    print("No CRFReporter v3.0.0 to CRFReporter v5.0.0 UID mapping file")
    quit()
if options.f5 is None:
    print("No last inventory year")
    quit()

subprocess.run(["ghg-inventory.py","-c",options.f1,"-p",options.f2,"-x",options.f3,"-m",options.f4,"-y",options.f5])
subprocess.run(["kp-lulu-summary.py","-c","ghg/2016/crf/KP*.csv","-p",options.f3,"-x",options.f3,"-u",
                "ghg/2015/crf/KPLULUSummary2015/KPSummary.csv",'-m',options.f4,"-y",options.f5])
subprocess.run(["kp-lulu-summary.py","-c","ghg/2016/crf/LU*.csv","-p",options.f3,"-x",options.f3,"-u",
                "ghg/2015/crf/KPLULUSummary2015/LUSummary.csv",'-m',options.f4,"-y",options.f5])
subprocess.run(["nir3-table.py","-c","ghg/2016/crf/NIR*.csv","-p",options.f3,"-x",options.f3,"-m",options.f4,"-y","2016"])
subprocess.run(["information-items.py","-p",options.f3,"-x",options.f3,"-m", options.f4,"-y",options.f5])
subprocess.run(["nk-comments.py","-c","ghg/2016/crf/C*.csv","-p",options.f3,"-x",options.f3,"-m",options.f4])
