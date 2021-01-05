#!python
import argparse
import lukeghg.scen.ghgscenario as ghgscen

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--files',type=str,dest='files',help='Scenario files (reqular expression)')
    parser.add_argument('--uid',type=str,dest='uid',help='UID matrix excel file')
    parser.add_argument('--scen',type=str,dest='scen',help='Scenario excel template file')
    parser.add_argument('--keys',dest='keys',action='store_false',help='Maintain notation keys')
    parser.add_argument('-m',type=str,dest='m',help='UID 300->500 mapping file (CRFReporter)')
    parser.add_argument('-o',type=str,dest='o',help='Scenario results excel output file')
    parser.add_argument('--start',type=int,dest='start',help="Start year (1990)")
    parser.add_argument('--end',type=int,dest='end',help="End year")
    args = parser.parse_args()
    if args.files == None:
        print("No input files")
    if args.uid == None:
        print("No UID matrix excel file")
    if args.scen == None:
        print("No Scenario excel template file")
    if args.m == None:
        print("No UID 300->500 mapping file (CRFReporter)")
    if args.o == None:
        print("No Scenario results excel output file")
    if args.start == None:
        print("No Start year (1990)")
    if args.end == None:
        print("No End year")
    result = args.files and args.uid and args.scen and args.m and args.o and args.start and args.end
    if result == None:
        quit()
    try:
        excel_writer = ghgscen.create_scenario_excel(args.o,args.files,args.uid,args.scen,args.m,args.start,args.end,args.keys)
        excel_writer.save()
        excel_writer.close()
    except NoInventoryFiles:
        print("No scenario inventory files")

