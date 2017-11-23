from optparse import OptionParser as OP
from array import array
from lukeghg.crf.crfxmlconstants import ch4co2eq,n2oco2eq,ctoco2,nkset
from lukeghg.crf.crfxmlfunctions import *
import datetime

#These constants will come from CrfXMLConstants 
#ch4co2eq=25.0
#n2oco2eq=298.0
#ctoco2=44.0/12.0
#nkset={'IE','NA','NO','NE'}


#This  python  script  generates  KPTable  Table_1_Appendix_11c  based
#on  GHG inventory   files  in  crf  folder.  Thus  it  is  relatively
#fast  to  reproduce the table  if the  results change. The  script of
#kptable-appendix-11c.sh is  the shell  script that  calls this  script with
#output file name (i.e. command line) 


def appendix11c(start,end,file_name):
    global ch4co2eq,n2oco2eq,ctoco2,nkset
    #The two biomass files
    #Lines 1-4
    kp4b1_bm_gains_trees_file='KP4_living_biomass_gains_trees.csv'
    #Lines 1-4
    kp4b1_bm_losses_trees_file='KP4B1_FM_living_biomass_losses_trees.csv'
    #DOM+SOM mineral sink
    #As before (2013)
    kp4b1minsink='KP4B1_mineral_soil_sink.csv'
    #DOM+SOM organic emission
    #As before
    kp4b1orgemission='KP4B1_organic_soil_emission.csv'
    #Biomass burning files
    #As before
    kp4b1controlled_burning_file='KP4B1_controlledburning.csv'
    #As before
    kp4b1wildfires_file='KP4B1_wildfires.csv'
    #Lines 1-4
    kp4b1fertilization_file='KP_II_1_fertilisation.csv'
    #As before
    kp4b1drainage_n2o_file='KP4B1_N2O_drainaged_soils.csv'
    #As before
    kp4b1drainage_ch4_file='KP4B1_CH4_drainaged_soils.csv'
    #HWP, harvested wood products since 2013 inventory
    kp4hwp_file='KP4_HWP-FM.csv'

    #The biomasses
    f1 = open(kp4b1_bm_gains_trees_file)
    f2 = open(kp4b1_bm_losses_trees_file)

    #Read the files and slice the right biomass part from the list
    #From 2014 onwards GHG inventory files can/should have comments (with enclosing '#') 
    ls = [x.rpartition('#')[2].split() for x in f1.readlines() if x.count('#') != 1]
    ls1 = ls[0:4]
    ls = [x.rpartition('#')[2].split() for x in f2.readlines() if x.count('#') != 1]
    ls2 = ls[0:4]
    #Each biomass  is calculated  for South and  North Finland,  above and
    #below ground. Sum first to one biomass for each biomass class.
    bmls1 = SumBiomassLs(ls1)
    bmls2 = SumBiomassLs(ls2)
    #Convert C to CO2 and note biomass increment (as CO2 gains) is negative and vice versa
    bmls = [-(x+y)*ctoco2 for (x,y) in zip(bmls1,bmls2)]
    #The time series might not be fully calculated yet, fill with zeros
    fill_ls = PaddingList(end,bmls)
    bmls =fill_ls+bmls
    #The DOM+SOM mineral organic
    f5=open(kp4b1minsink)
    f6=open(kp4b1orgemission)

    ls5 = [x.rpartition('#')[2].split() for x in f5.readlines() if x.count('#') != 1]
    ls6 = [x.rpartition('#')[2].split() for x in f6.readlines() if x.count('#') != 1]
    f5.close()
    f6.close()

    #The sum of North and South Finland 
    domsom_min_sink_ls= SumBiomassLs(ls5)
    domsom_org_emission_ls = SumBiomassLs(ls6)
    domsom_min_sink_ls = [-x*ctoco2 for x in domsom_min_sink_ls]
    domsom_org_emission_ls = [-x*ctoco2 for x in domsom_org_emission_ls]

    #Biomass burning
    #Biomass burning files have CO2, CH4 and N20 in the same file in the same order
    f7=open(kp4b1controlled_burning_file)
    f8=open(kp4b1wildfires_file)
    #Two lines for each gas, South Finland and North Finland
    bmburningco2ls=[]
    bmburningco2ls.append(f7.readline())
    bmburningco2ls.append(f7.readline())
    bmburningco2ls.append(f8.readline())
    bmburningco2ls.append(f8.readline())
    bmburningco2ls = [x.rpartition('#')[2].split() for x in bmburningco2ls if x.count('#') !=1]
    #Sum controlled burning and wildfires, South and North Finland
    bmburningco2ls = SumBiomassLs(bmburningco2ls)

    bmburningch4ls=[]
    bmburningch4ls.append(f7.readline())
    bmburningch4ls.append(f7.readline())
    bmburningch4ls.append(f8.readline())
    bmburningch4ls.append(f8.readline())
    bmburningch4ls = [x.rpartition('#')[2].split() for x in bmburningch4ls if x.count('#') !=1]
    bmburningch4ls = SumBiomassLs(bmburningch4ls)
    #CH4 to CO2 equivalent
    bmburningch4ls = [x*ch4co2eq for x in bmburningch4ls]

    bmburningn2ols=[]
    bmburningn2ols.append(f7.readline())
    bmburningn2ols.append(f7.readline())
    bmburningn2ols.append(f8.readline())
    bmburningn2ols.append(f8.readline())
    f7.close()
    f8.close()
    bmburningn2ols = [x.rpartition('#')[2].split() for x in bmburningn2ols if x.count('#') !=1]
    bmburningn2ols = SumBiomassLs(bmburningn2ols)
    #N2O to CO2 equivalent
    bmburningn2ols =  [x*n2oco2eq for x in bmburningn2ols]

    #Fertilization
    f9=open(kp4b1fertilization_file)
    ls = [x.rpartition('#')[2].split() for x in f9.readlines() if x.count('#')!=1]
    #The first four lines
    fertilization_ls=ls[0:4]
    #The second and the fourth line are emissions (see comments in csv file)
    fertilization_ls.pop(0)
    fertilization_ls.pop(1)
    f9.close()
    #print(fertilization_ls)
    fertilization_ls = SumBiomassLs(fertilization_ls)
    #print(fertilization_ls)
    fertilization_ls = [x*n2oco2eq for x in fertilization_ls]
    fill_ls = PaddingList(end,fertilization_ls)
    fertilization_ls = fill_ls+fertilization_ls
    #print(fertilization_ls)

    #Drainaged
    f10 = open(kp4b1drainage_n2o_file)
    drainage_n2o_ls = [x.rpartition('#')[2].split() for x in f10.readlines() if x.count('#') !=1]
    f10.close()
    drainage_n2o_ls = SumBiomassLs(drainage_n2o_ls)
    #print(drainage_n2o_ls)
    drainage_n2o_ls = [x*n2oco2eq for x in drainage_n2o_ls]
    #print(drainage_n2o_ls)
    f11 = open(kp4b1drainage_ch4_file)
    drainage_ch4_ls = [x.rpartition('#')[2].split() for x in f11.readlines() if x.count('#') !=1]
    f11.close()
    drainage_ch4_ls = SumBiomassLs(drainage_ch4_ls)
    #print(drainage_ch4_ls)
    drainage_ch4_ls = [x*ch4co2eq for x in drainage_ch4_ls]
    #print(drainage_ch4_ls)

    f12=open(kp4hwp_file)
    hwp_ls=[x.rpartition('#')[2].split() for x in f12.readlines() if x.count('#') !=1]
    #2015 the file structure is in 3 parts: 1) Initial stock, 2) Gains and losses 3) half-time information
    #The sum of gains and losses will go to the table
    #2016 the file structure is for each item: 1) half life, 2) init stock, 3) gains and 4) losses
    #Pick every fourth item starting from the first right place in the list 
    hwp_ls_gains = hwp_ls[2::4]
    hwp_ls_losses = hwp_ls[3::4]
    hwp_ls = hwp_ls_gains+hwp_ls_losses
    print(hwp_ls)
    hwp_sum_ls = SumBiomassLs(hwp_ls)
    #C to CO2
    #Removals are good for the atmosphere, change the sign
    hwp_co2_ls = [-x*ctoco2 for x in hwp_sum_ls]
    ls = PaddingList(end,hwp_co2_ls)
    #Replace 0 with NA
    fill_ls = ['NA']*len(ls)
    #The list to be inserted in the table for HWP
    hwp_co2_ls = fill_ls+hwp_co2_ls

    #Create the KPTable Table 1_App_11c
    delim='#'
    table_title='KPTable Appendix_11c Net emissions and removals from the activities under Article 3.4\n'
    row_title_ls = GenerateRowTitleList(start,end)
    ftable = open(file_name,"w")
    ftable.write(table_title)
    ftable.write("Table 1_App_11c Net emssions and removals from ForestManagement, kt CO2 eq.\n")
    ftable.write(delim+"Biomass"+delim+"DOM+SOM mineral soils"+delim+"DOM+SOM organic soils"+delim+delim+"Biomass burning"+delim+delim+"Fertilization"+delim)
    ftable.write("Drained organic soils N2O"+delim+"Drained organic soils CH4"+delim+"HWP"+delim+"Total\n")
    ftable.write(delim+delim+delim+delim+"CO2"+delim+"CH4"+delim+"N2O"+delim+"N2O"+delim+"\n")
    #Write data
    for (year,bm,domsommin,domsomorg,burnco2,burnch4,burnn2o,fertn2o,drainedn2o,drainedch4,hwp) in zip(row_title_ls,bmls,domsom_min_sink_ls,domsom_org_emission_ls,
                                                                                                    bmburningco2ls,bmburningch4ls,bmburningn2ols,fertilization_ls,
                                                                                                    drainage_n2o_ls,drainage_ch4_ls,hwp_co2_ls):
        total = SumTwoValues(SumTwoValues(SumTwoValues(SumTwoValues(SumTwoValues(SumTwoValues(SumTwoValues(SumTwoValues(bm,domsommin),domsomorg),burnco2),burnch4),
                                                                    burnn2o),fertn2o),drainedn2o),drainedch4)
        if not (hwp in nkset):
            total = total+hwp
        ftable.write(str(year)+delim+str(bm)+delim+str(domsommin)+delim+str(domsomorg)+delim+str(burnco2)+delim+str(burnch4)+delim+str(burnn2o)+delim+str(fertn2o)+delim)
        ftable.write(str(drainedn2o)+delim+str(drainedch4)+delim+str(hwp)+delim+str(total)+'\n')
    #Write data file names for each column
    ftable.write(delim+kp4b1_bm_gains_trees_file+" Lines:1-4"+delim+kp4b1minsink+delim+kp4b1orgemission+delim+kp4b1controlled_burning_file+delim+kp4b1controlled_burning_file+delim)
    ftable.write(kp4b1controlled_burning_file+delim+kp4b1fertilization_file+" Lines:2,4"+delim+kp4b1drainage_n2o_file+delim+kp4b1drainage_ch4_file+delim+
                kp4hwp_file+'\n')
    ftable.write(delim+kp4b1_bm_losses_trees_file+" Lines:1-4"+delim+delim+delim+kp4b1wildfires_file+delim+kp4b1wildfires_file+delim+kp4b1wildfires_file+"####"+"Gains Lines:3,7,11 etc."+'\n')
    ftable.write("##########"+"Losses Lines:4,8,12 etc"+'\n')
    #Sign with the date time
    now = datetime.datetime.now()
    print(str(now))
    ftable.write("Date produced: "+str(now)+"\n")
    ftable.close()
