#!python
import datetime
from optparse import OptionParser as OP
#from crfxmlconstants import *
#from crfxmlfunctions import *
from lukeghg.nir import kptableappendix11c

start = 1990
end = None
file_name = 'KPTableAppenddix11c.txt'
directory=None
parser = OP()
parser.add_option("-s","--start",dest="f1",help="Inventory start year (1990)")
parser.add_option("-e","--end",dest="f2",help="Inventory end year")
parser.add_option("-o","--ofile",dest="f3",help="Output file name")
parser.add_option("-d","--dir",dest="f4",help="Inventory crf directory")
(options,args) = parser.parse_args()

if options.f1 is not None:
    start=int(options.f1)
if options.f2 is not None:
    end=int(options.f2)
if options.f3 is not None:
    file_name=options.f3
if options.f4 is not None:
    directory=options.f4
if end is None:
    print("No inventory end year")
    quit()
if directory is None:
    print("No inventory crf directory")
    quit()
kptableappendix11c.appendix11c(start,end,directory,file_name)  
 
