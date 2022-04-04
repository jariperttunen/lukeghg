#!python
import argparse
import glob
from lukeghg.crf.uid340to500mapping import MapUID340to500, Create340to500UIDMapping
from lukeghg.crf.crfxmlfunctions import ConvertFloat
import lukeghg.check.checkinventoryvalues as checkinv


if __name__ == "__main__":
    #Command line generator   
    parser = argparse.ArgumentParser()
    parser.add_argument("-p","--prev",dest="f1",type=str,required=True,help="Read input ghg result files previous year (wild card search)")
    parser.add_argument("-c","--curr",dest="f2",type=str,required=True,help="Read input ghg result files current year (wild card search)")
    parser.add_argument("-m","--map",dest="f5", type=str,required=True,help="CRFReporter 3.0.0 --> 5.0.0 UID mapping file")
    parser.add_argument("-o","--diff_file",dest="f6",type=str,required=True,help="Output text file containing: 1) too large differences, 2) change in Notation keys and methods, 3) missing UID")
    parser.add_argument("-t","--tolerance",type=int,dest="f7",required=True,help="Tolerance for difference in percentage")
    parser.add_argument("--NO", action="store_true",help="Collect NO notation keys in current inventory")
    args = parser.parse_args()

    (uid340set,uiddict340to500) = Create340to500UIDMapping(args.f5)
    print("Comparing two inventories:", args.f1,args.f2)
    dirfilels1 = glob.glob(args.f1)
    dirfilels2 = glob.glob(args.f2)
    #dictionary for previous year: {UID: time series}
    dictprev1=checkinv.CreateDictionary(dirfilels1)
    #dictionary for previous year: {UID: time series}
    dictcurrent2=checkinv.CreateDictionary(dirfilels2)
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
    file_name = args.f6
    tolerance = float(args.f7)
    print("Comparing two inventories for differences")
    print("Writing output to:", file_name)
    checkinv.CompareTwoInventoryYears(dictcurrent2,dictprev1,tolerance,uidnotincurrentyear,uidnotinpreviousyear,args.NO,file_name)
    print("Done\n")
