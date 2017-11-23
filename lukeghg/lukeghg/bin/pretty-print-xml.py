#!python
from lukeghg.crf.ppxml import PrettyPrint
from xml.etree.ElementTree import ElementTree as ET
from optparse import OptionParser as OP
import string

if __name__ == "__main__":
    #Command line generator   
    parser = OP()
    parser.set_defaults(r=False)
    parser.add_option("-i",dest="f1",help="Read simple CRFReporter XML file")
    parser.add_option("-o",dest="f2",help="Pretty print output XML file")
    (options,args) = parser.parse_args()
    if options.f1 is None:
        print("No input CRFReporter xml file")
        quit()
    if options.f2 is None:
        print("No output CRFReporter xml file")
        quit()
    #Parse the simple xml file
    t = ET()
    print("Parsing the file",options.f1)
    t.parse(options.f1)
    #Write ouput file
    PrettyPrint(t.getroot(),0,"    ")
    t.write(options.f2) 

