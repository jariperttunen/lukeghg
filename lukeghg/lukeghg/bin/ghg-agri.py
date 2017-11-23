#!python
from optparse import OptionParser as OP
import agrighg


parser = OP()
parser.add_option("-x","--excel",dest="f1",help="Read Agriculture GHG Excel File")
parser.add_option("-s","--sheet",dest="f2",help="Excel Sheet for GHG inventory data")
parser.add_option("-y","--year",dest="f3",help="Inventory year (last year in CRFREporter)")

(options,arg) = parser.parse_args()
excel_file=""
excel_sheet="XML-testi"
if options.f1 is None:
    print("No Agriculture GHG Excel File")
    quit()
excel_file=options.f1
if options.f3 is None:
    print("No GHG inventory year")
    quit()
if options.f2 is None:
    print("No excel sheet, assuming sheet name: XML-testi")
else:
    excel_sheet=options.f2


print("Reading excel file", excel_file,"Sheet",excel_sheet)
agrighg.ReadAgriExcelFile(options.f1,excel_sheet,options.f3)
