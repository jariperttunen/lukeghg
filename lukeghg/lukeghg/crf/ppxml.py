from xml.etree.ElementTree import ElementTree as ET
from xml.etree.ElementTree import Element,SubElement
from optparse import OptionParser as OP
import string

#Pretty print XML in human readable format
#Usage: PrettyPrint(t.getroot(),0,"    ")
def PrettyPrint(elem,level=0,space = " "):
    '''Pretty print XML
       Usage: PrettyPrint(t.getroot(),0,"    ")
    '''
    i = "\n" + level*space
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + space
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for e in  elem:
            PrettyPrint(e,level+1,space)
        if not e.tail or not e.tail.strip():
            e.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
