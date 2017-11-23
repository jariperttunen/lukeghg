#!python
import glob
from optparse import OptionParser as OP
from lukeghg.nir import table612
start=1990
end=2015
file_name='Table-6.1-2.txt'
parser = OP()
parser.add_option("-s","--start",dest="f1",help="Inventory start year (1990)")
parser.add_option("-e","--end",dest="f2",help="Inventory end year")
parser.add_option("-o","--ofile",dest="f3",help="Output file name")
parser.add_option("-d","--crfdir",dest="f4",help="CRF directory for inventory results")
(options,args) = parser.parse_args()

if options.f1 is None:
    print("No inventory start year")
    quit()
start=int(options.f1)
if options.f2 is None:
    print("No inventory end year")
    quit()
end=int(options.f2)
if options.f3 is None:
    print("No output file name")
    quit()
file_name=options.f3
if options.f4 is None:
    print("No crf directory")
    quit()
d=options.f4

lulucftable612.WriteCO2eqTableData(start,end,file_name,d)
