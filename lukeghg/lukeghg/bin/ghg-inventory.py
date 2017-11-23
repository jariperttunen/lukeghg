#!python
import glob
from optparse import OptionParser as OP
import lukeghg.crf.ghginventory as ghg

parser = OP()
parser.add_option("-c","--csv",dest="f1",help="Read GHG inventory csv files")
parser.add_option("-p","--pxml",dest="f2",help="Read CRFReporter Party Profile xml file")
parser.add_option("-x","--xml",dest="f3",help="Write new Party profile populated with inventory results")
parser.add_option("-m","--map",dest="f4",help="CRFReporter 3.0.0 --> 5.0.0 UID mapping file")
parser.add_option("-y","--year",dest="f5",help="Inventory year (the last year in CRFReporter)")
parser.add_option("-s","--sep",dest="f6",help="Time series value separator (default=None)") 
(options,arg)=parser.parse_args()
if options.f1 is None:
    print("No inventory GHG csv files")
    quit()
if options.f2 is None:
    print("No CRFReporter Party Profile XML file")
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
sep=None
if options.f6 is not None:
    print("Time series value separator",options.f6)
    sep=options.f6

file_ls=glob.glob(options.f1)
file_ls.sort()
print("Filling",options.f2,"with GHG inventory data from",options.f1)
print("REMEMBER TO UPDATE PARTY PROFILE XML FROM CRFREPORTER AFTER NEW NODES IN THE INVENTORY!")
ghg.GHGToCRFReporter(file_ls,options.f2,options.f3,options.f4,int(options.f5),sep1=sep)
