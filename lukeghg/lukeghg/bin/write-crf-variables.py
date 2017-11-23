#!python
import glob
from optparse import OptionParser as OP
from xml.etree.ElementTree import ElementTree as ET
from xml.etree.ElementTree import Element,SubElement,dump
from lukeghg.crf.crfxmlconstants import lulu_start_year
import lukeghg.crf.crfreporter as crfreporter
import lukeghg.crf.fileowner as fileowner


parser = OP()
parser.add_option("-c","--csv",dest="f1",help="Read GHG inventory csv files")
parser.add_option("-p","--pxml",dest="f2",help="Read CRFReporter Party Profile xml file")
parser.add_option("-o","--out",dest="f3",help="CRFReporter variable output file")
parser.add_option("-y","--year",dest="f4",help="GHG Inventory year")

(options,arg)=parser.parse_args()
if options.f1 is None:
    print("No inventory GHG csv files")
    quit()
if options.f2 is None:
    print("No CRFReporter Party Profile XML file")
    quit()
if options.f3 is None:
    print("No CRFReporter variable output file name")
    quit()
if options.f4 is None:
    print("No GHG Inventory year given")
    quit()

print("Generating UID file:",options.f3)
dirfilels=glob.glob(options.f1)
dictionary=fileowner.FileOwner(dirfilels)
t=ET()
t.parse(options.f2)
it = t.iter('variable')
variablels =list(it)
variablels.sort(key=crfreporter.SortKey)
f = open(options.f3,'w')
crfreporter.WriteHeader(f,lulu_start_year,int(options.f4))
for variable in variablels:
    crfreporter.WriteVariables(f,variable,dictionary,False)
print("Done")
