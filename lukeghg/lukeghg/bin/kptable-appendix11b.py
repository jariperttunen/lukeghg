#!python
import datetime
from optparse import OptionParser as OP
#from crfxmlconstants import *
#from crfxmlfunctions import *
from lukeghg.nir import kptableappendix11b

start = 1990
end = 2015
file_name = 'KPTableAppenddix11b.txt'
parser = OP()
parser.add_option("-s","--start",dest="f1",help="Inventory start year (1990)")
parser.add_option("-e","--end",dest="f2",help="Inventory end year")
parser.add_option("-o","--ofile",dest="f3",help="Output file name")
(options,args) = parser.parse_args()

if options.f1 is not None:
    start=int(options.f1)
if options.f2 is not None:
    end=int(options.f2)
if options.f3 is not None:
    file_name=options.f3

kptableappendix11b.appendix11b(start,end,file_name)  
 
