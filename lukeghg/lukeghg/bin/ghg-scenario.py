#!python
import argparse
import pandas as pd
import openpyxl
import lukeghg.scen.ghgscenario as ghgscen
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--files',type=str,dest='files',required=True,help='Scenario files (reqular expression)')
    parser.add_argument('--scen',type=str,dest='scen',required=True,help='Scenario excel template file')
    parser.add_argument('-m',type=str,dest='m',required=True,help='UID 300->500 mapping file (CRFReporter)')
    parser.add_argument('-o',type=str,dest='o',required=True,help='Scenario results excel output file')
    parser.add_argument('--start',type=int,dest='start',required=True,help="Start year (1990)")
    parser.add_argument('--end',type=int,dest='end',required=True,help="End year")
    parser.add_argument('--GWP',type=str,dest='gwp',default="AR5",help="Global warming potential, AR4 (GHG inventory) or AR5 (default)")
    parser.add_argument('--noformulas',action="store_true",help="Add up values in summary sheets. Default: Not present, generate excel formulas")
    args = parser.parse_args()
        
    #Default GWP AR5
    ch4co2eq = 28
    n2oco2eq = 265
    gwp_str = "AR5"
    formulas = True
    if args.noformulas:
        formulas=False
    if args.gwp == 'AR4':
       ch4co2eq = 25
       n2oco2eq = 298
       gwp_str="AR4"
    try:
        excel_writer = ghgscen.create_scenario_excel(args.o,args.files,args.scen,args.m,args.start,args.end,ch4co2eq,n2oco2eq,formulas,gwp_str)
        #The three lines demonstrating bug(?) in pandas 1.2.0 and above with openpyxl
        #writing files Excel considers having erroneous format
        #1 excel_writer = pd.ExcelWriter('Test.xlsx',engine='openpyxl')
        #2 df = pd.DataFrame([[1,2,3,4,],[5,6,7,8]])
        #3 df.to_excel(excel_writer,sheet_name='Sheet1')
        #After save and close erroneous excel file format
        excel_writer.save()
        excel_writer.close()
    except ghgscen.NoInventoryFiles:
        print("No scenario inventory files")

