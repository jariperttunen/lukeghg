#!python
import argparse
import lukeghg.scen.ghgscenario as ghgscen

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--files',type=str,dest='files',required=True,help='Scenario files (reqular expression)')
    parser.add_argument('--uid',type=str,dest='uid',required=True,help='UID matrix excel file')
    parser.add_argument('--scen',type=str,dest='scen',required=True,help='Scenario excel template file')
    parser.add_argument('--keys',dest='keys',action='store_false',help='Maintain notation keys')
    parser.add_argument('-m',type=str,dest='m',required=True,help='UID 300->500 mapping file (CRFReporter)')
    parser.add_argument('-o',type=str,dest='o',required=True,help='Scenario results excel output file')
    parser.add_argument('--start',type=int,dest='start',required=True,help="Start year (1990)")
    parser.add_argument('--end',type=int,dest='end',required=True,help="End year")
    parser.add_argument('--GWP',type=str,dest='gwp',default="AR5",help="Global warming potential, AR4 (GHG inventory) or AR5 (default)")
    args = parser.parse_args()
    result = args.files and args.uid and args.scen and args.m and args.o and args.start and args.end
    if result == None:
        quit()
    ch4co2eq = 28
    n2oco2eq = 265
    if args.gwp == 'AR4':
       ch4co2eq = 25
       n2oco2eq = 298
    try:
        excel_writer = ghgscen.create_scenario_excel(args.o,args.files,args.uid,args.scen,args.m,args.start,args.end,args.keys,ch4co2eq,n2oco2eq)
        excel_writer.save()
        excel_writer.close()
    except ghgscen.NoInventoryFiles:
        print("No scenario inventory files")

