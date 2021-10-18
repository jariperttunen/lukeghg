import argparse
import checkinventoryvalues


if __name__ == "__main__":
    #Command line generator   
    parser = OP()
    parser.add_option("-p","--prev",dest="f1",help="Read input ghg result files previous year (wild card search)")
    parser.add_option("-c","--curr",dest="f2",help="Read input ghg result files current year (wild card search)")
    parser.add_option("-m","--map",dest="f5", help="CRFReporter 3.0.0 --> 5.0.0 UID mapping file")
    parser.add_option("-o","--diff_file",dest="f6",help="Output text file containing: 1) too large differences, 2) change in Notation keys and methods, 3) missing UID")
    parser.add_option("-t","--tolerance",dest="f7",help="Tolerance for difference in percentage")
    (options,args) = parser.parse_args()

    if options.f1 is None:
        print("No input ghg inventory results files from previous year")
        quit()
    if options.f2 is None:
        print("No input ghg inventory results files from current year")
        quit()
    if options.f5 is None:
        print("No CRFReporter 3.0.0 --> 5.0.0 UID mapping file")
        quit()
    if options.f6 is None:
        print("No outputfile for differences")
        quit()
    if options.f7 is None:
        print("No tolerance in percenatge given for time series differences")
        quit()    
    (uid340set,uiddict340to500) = Create340to500UIDMapping(options.f5)
    print("Comparing two inventories:", options.f1,options.f2)
    dirfilels1 = glob.glob(options.f1)
    dirfilels2 = glob.glob(options.f2)
    #dictionary for previous year: {UID: time series}
    dictprev1=CreateDictionary(dirfilels1)
    #dictionary for previous year: {UID: time series}
    dictcurrent2=CreateDictionary(dirfilels2)
    #Check the existence of UID
    dictprev1keyls = dictprev1.keys()
    uidnotincurrentyear=[]
    for uid in dictprev1keyls:
        if not uid in dictcurrent2:
            uidnotincurrentyear.append(uid)
    print("Number of UID in previous year, not in current year:",len(uidnotincurrentyear))
    uidnotinpreviousyear=[]
    dictcurrent2keyls = dictcurrent2.keys()
    uidnotinpreviousyear=[]
    for uid in dictcurrent2keyls:
        if not uid in dictprev1:
            uidnotinpreviousyear.append(uid)
    print("Number of UID current year, not in previous year:",len(uidnotinpreviousyear))
    print("Number of UID previous year",len(dictprev1keyls))
    print("Number of UID current year",len(dictcurrent2keyls))
    file_name = options.f6
    tolerance = float(options.f7)
    print("Comparing two inventories for differences")
    print("Writing output to:", file_name)
    ls=file_name.split('.')
    print("Writing output to:", ls[0]+".xlsx")
    CompareTwoInventoryYears(dictcurrent2,dictprev1,tolerance,uidnotincurrentyear,uidnotinpreviousyear,file_name)
    print("Done\n")
