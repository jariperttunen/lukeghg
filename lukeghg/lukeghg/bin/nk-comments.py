#!python
from xml.etree.ElementTree import ElementTree as ET
from xml.etree.ElementTree import Element,SubElement,dump
from optparse import OptionParser as OP
import glob
import lukeghg.crf.nkcomments as comments
import lukeghg.crf.ppxml as ppxml
#---------------------------------The main program begins--------------------------------------------------
if __name__ == "__main__":
    #Command line generator
    parser = OP()
    parser.add_option("-c","--csv",dest="f1",help="Read GHG inventory Notation Key comment files")
    parser.add_option("-p","--pxml",dest="f2",help="Read CRFReporter Party Profile xml file")
    parser.add_option("-x","--xml",dest="f3",help="Write new Party profile populated with Notation Key comments")
    parser.add_option("-m","--map",dest="f4",help="CRFReporter 3.0.0 --> 5.0.0 UID mapping file")
    (options,args) = parser.parse_args()
 
    if options.f1 is None:
        print("No input Notation Key files")
        quit()
    if options.f2 is None:
        print("No input Party Profile xml file")
        quit()
    if options.f3 is None:
        print("No output Party Profile xml file")
        quit()
    if options.f4 is None:
        print("No CRFReporter 3.0.0 --> 5.0.0 UID mapping file")
        quit()

    print("Inserting Notation key comments.")    
    #List the inventory files to be imported 
    dirfilels = glob.glob(options.f1)
    print("Parsing  Party Profile xml from:",options.f2)
    t=ET()
    t.parse(options.f2)
    print("Creating UID mapping from", options.f4)
    comments.InsertAllNKComments(t,dirfilels,options.f4)
    print("Pretty printing xml to human readable form")
    ppxml.PrettyPrint(t.getroot(),0,"   ")
    print("Writing xml file to",options.f3)
    t.write(options.f3)
