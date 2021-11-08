#Usage: python3 kptable-appendix-11b.py [-h] [--help]
import datetime
import pathlib
import pandas as pd
import xlsxwriter
from lukeghg.crf.crfxmlconstants import ch4co2eq, n2oco2eq, ctoco2
from lukeghg.crf.crfxmlfunctions import ConvertFloat,ConvertSign, ConvertToCO2, SumTwoValues, SumBiomassLs
from lukeghg.crf.crfxmlfunctions import PaddingList, GenerateRowTitleList

#These constants will come from CrfXMLConstants
#Please check the 
#ch4co2eq=25.0
#n2oco2eq=298.0
#ctoco2=44.0/12.0
#nkset={'IE','NA','NO','NE'}
#Sort the Records based on YearName in ascending order
def SortKey(x):
    return x.attrib['YearName']
#---------------------------------The main program begins--------------------------------------------------

def appendix11b(start,end,directory,file_name):
    #Command line generator   
    global ch4co2eq, n2oco2eq,ctoco2
    inventory_year=end
    #Output file, the table
    kptable_appendix_11b_file = file_name
    directory=directory+'/'
    #Table Appendix-11b Afforestation/Reforestation and Deforestation files
    #Deforestation "Conversion to water CH4" comes from NIR folder
    kp4a2_fl_to_waters_ch4_org=directory+'KP4A2_FLtowaters_orgsoil_CH4.csv'
    #The rest of the files are from  crf-folder.
    kp4a_agr_bm_gains_losses=directory+'KP4A_agr_bm_gains_losses.csv'
    #2015 file name change
    #2016 file name change
    #2015:kpa2_ar_under_D_gains='KP4A2_AR_und_defor_treebm_gains.csv'
    kpa2_ar_under_D_gains=directory+'KP4A2_AR_und_D_living_biomass_gains_trees.csv'
    kp4a2_sl_soil=directory+'KP4A2_SL_soil.csv'
    kp4a2_ar_under_d_soil=directory+'KP4A2_AR_und_defor_soils.csv'
    #2015 KP_MTT_UID.csv in two files: KP_defor_mineral.csv and KP_defor_organic.csv
    #kp_uid_mtt='KP_MTT_UID.csv'
    kp_defor_mineral=directory+'KP_defor_mineral.csv'
    kp_defor_organic=directory+'KP_defor_organic.csv'
    kp4a2_fl_to_wl_soil=directory+'KP4A2_FLtoWL_soils.csv'
    kp4a2_clglpewesl_deadwood=directory+'KP4A2_CLGLPEWESL_deadwood.csv'
    kp4a2_d_living_biomass_losses_trees=directory+'KP4A2_D_living_biomass_losses_trees.csv'
    kp4a2_fl_to_waters_org_soil=directory+'KP4A2_FLtowaters_orgsoil.csv'
    #2015 rename
    #kp4a2_d_mineralization='KP4A2_D_mineraalisationcl_gl_sl.csv'
    kp4a2_d_mineralization=directory+'KPA2_soil_leaching_N2O.csv'
    #2015 addition is Afforestation mineralization
    kp4_ar_mineralization=directory+'KP4_Affor_mineralization.csv' 
    kp4a2_fl_to_wl_non_co2=directory+'KP4A2_FLtoWL_soils_nonCO2.csv'
    kp4_living_biomass_gains_trees=directory+'KP4_living_biomass_gains_trees.csv'
    kp4_ar_living_biomass_losses_trees=directory+'KP4A1_AR_living_biomass_losses_trees.csv'
    kp4a1_clglsl_mineral_soil=directory+'KP4A1_CLGLSL_mineral_soil.csv'
    kp4a1_ar_org_soil=directory+'KP4A1_AR_Organic_soil_C.csv'
    kp4a11_wildfires=directory+'KP4A11_wildfires.csv'
    kp4a1_clglpewesl_organic_soils_nonco2=directory+'KP4A1_CLGLPEWESL_organic_soils_nonco2.csv'
    kp4_hwp_ard=directory+'KP4_HWP-AR.csv'
    #Data for the two Tables in Appendix 1
    #1. Deforestation: Conversion to water CH4
    #Change in 2015: use third (CH4) line in kp4a2_fl_to_waters_org_soil
    #----------------------------------------
    f = open(kp4a2_fl_to_waters_org_soil)
    #Read to a list [[year,val1],[year,val2]....,[year,valN]]
    ls = [x.rpartition('#')[2].split() for x in f.readlines() if x.count('#') != 1]
    #Third line is CH4
    ls = ls[2]
    #Convert to CO2
    ls.pop(0)
    fl_to_waters_ch4_co2_ls = [ConvertToCO2(ch4co2eq,x) for x in ls]
    f.close()
    #2. Agriculture Afforestation and Deforestation biomasses
    #---------------------------------------------------------
    f = open(kp4a_agr_bm_gains_losses)
    agr_ls = [x.rpartition('#')[2].split() for x in f.readlines() if x.count('#') != 1]
    #Pick the deforestation, the first part in the file
    agr_d_ls = agr_ls[0:8]
    #Pick the Afforestation and Reforestation, rest of the file
    agr_ar_ls = agr_ls[8:len(agr_ls)]
    #Deforestation: Sum the biomassess: Cropland, Grassland, North and South Finland,
    #above ground and below ground
    agr_d_bm_ls=SumBiomassLs(agr_d_ls)
    #Afforestation: Sum the biomassess: Cropland, Grassland, North and South Finland,
    #above ground and below ground
    agr_ar_bm_ls=SumBiomassLs(agr_ar_ls)
    #Convert to CO2 and convert sign: if biomass increases -> emissiosn decrease and vice versa
    agr_d_co2_ls=[ConvertSign(ConvertToCO2(ctoco2,x)) for x in agr_d_bm_ls]
    agr_ar_co2_ls=[ConvertSign(ConvertToCO2(ctoco2,x)) for x in agr_ar_bm_ls]
    f.close()
    #3. Deforestation biomass losses in trees
    #----------------------------------------
    f = open(kp4a2_d_living_biomass_losses_trees)
    d_trees_ls = [x.rpartition('#')[2].split() for x in f.readlines() if x.count('#') != 1]
    #Sum the biomasses, CL, GL, SETT, WL, North and South Finland, below and above ground
    trees_bm_ls = SumBiomassLs(d_trees_ls)
    #Convert to CO2 and convert sign: if biomass increases -> emissions decrease and vice versa
    trees_d_co2_ls = [ConvertSign(ConvertToCO2(ctoco2,x)) for x in trees_bm_ls]
    f.close()
    #Deforestation Biomass: Afforestation/Reforestation under Deforestation, gains
    #---------------------------------------------------------------------
    f = open(kpa2_ar_under_D_gains)
    ar_under_d_ls = [x.rpartition('#')[2].split() for x in f.readlines() if x.count('#') != 1]
    ar_under_d_sum_ls = SumBiomassLs(ar_under_d_ls)
    #Convert to CO2 and convert sign: if biomass increases -> emissions decrease and vice versa
    ar_under_d_co2_ls = [ConvertSign(ConvertToCO2(ctoco2,x)) for x in ar_under_d_sum_ls]
    f.close()
    #Deforestation: DOM+SOM Mineral soils
    #-----------------------------------
    f = open(kp4a2_sl_soil)
    d_sl_soil_ls =  [x.rpartition('#')[2].split() for x in f.readlines() if x.count('#') != 1]
    d_sl_soil_sum_ls = SumBiomassLs(d_sl_soil_ls)
    d_sl_soil_co2_ls = [ConvertSign(ConvertToCO2(ctoco2,x)) for x in d_sl_soil_sum_ls]
    f.close()
    f = open(kp4a2_ar_under_d_soil)
    d_ar_under_d_soil_ls = [x.rpartition('#')[2].split() for x in f.readlines() if x.count('#') != 1]
    #Sum the both lines
    d_ar_under_d_min_soil_sum_ls = SumBiomassLs(d_ar_under_d_soil_ls)
    d_ar_under_d_min_soil_co2_ls = [ConvertSign(ConvertToCO2(ctoco2,x)) for x in d_ar_under_d_min_soil_sum_ls]
    f.close()
    #Settlements are now in Mineral soil, take lines 9 and 10
    f = open(kp4a2_clglpewesl_deadwood)
    d_clglpewesl_deadwood_ls = [x.rpartition('#')[2].split() for x in f.readlines() if x.count('#') != 1]
    d_clglpewesl_deadwood_ls = d_clglpewesl_deadwood_ls[8:len(d_clglpewesl_deadwood_ls)]
    d_clglpewesl_deadwood_min_sum_ls = SumBiomassLs(d_clglpewesl_deadwood_ls)
    d_clglpewesl_deadwood_min_co2_ls =  [ConvertSign(ConvertToCO2(ctoco2,x)) for x in d_clglpewesl_deadwood_min_sum_ls]
    f.close()
    f = open(kp_defor_mineral)
    d_mtt_min_soil_ls = [x.rpartition('#')[2].split() for x in f.readlines() if x.count('#') != 1]
    d_mtt_min_soil_ls = d_mtt_min_soil_ls[0:4]
    d_mtt_min_soil_sum_ls = SumBiomassLs(d_mtt_min_soil_ls)
    d_mtt_min_soil_co2_ls = [ConvertSign(ConvertToCO2(ctoco2,x)) for x in d_mtt_min_soil_sum_ls]
    f.close()
    d_dom_som_min_soil_deadwood_sum_co2_ls = [SumTwoValues(a,SumTwoValues(b,SumTwoValues(c,d))) for (a,b,c,d) in zip(d_sl_soil_co2_ls,
                                                                                                                    d_ar_under_d_min_soil_co2_ls,
                                                                                                                    d_clglpewesl_deadwood_min_co2_ls,
                                                                                                                    d_mtt_min_soil_co2_ls)]
                                                                                                                 
    #Deforestation: DOM+SOM Organic soils + Deadwood
    #-----------------------------------------------
    f = open(kp4a2_fl_to_wl_soil)
    d_fl_to_wl_soil_ls = [x.rpartition('#')[2].split() for x in f.readlines() if x.count('#') != 1]
    d_fl_to_wl_soil_sum_ls = SumBiomassLs(d_fl_to_wl_soil_ls)
    d_fl_to_wl_soil_co2_ls = [ConvertSign(ConvertToCO2(ctoco2,x)) for x in d_fl_to_wl_soil_sum_ls]
    f.close()
    f = open(kp4a2_clglpewesl_deadwood)
    d_clglpewesl_deadwood_ls = [x.rpartition('#')[2].split() for x in f.readlines() if x.count('#') != 1]
    d_clglpewesl_deadwood_ls = d_clglpewesl_deadwood_ls[0:8]
    d_clglpewesl_deadwood_org_sum_ls = SumBiomassLs(d_clglpewesl_deadwood_ls)
    d_clglpewesl_deadwood_org_co2_ls =  [ConvertSign(ConvertToCO2(ctoco2,x)) for x in d_clglpewesl_deadwood_org_sum_ls]
    f.close()
    f = open(kp_defor_organic)
    d_mtt_org_soil_ls = [x.rpartition('#')[2].split() for x in f.readlines() if x.count('#') != 1]
    d_mtt_org_soil_sum_ls = SumBiomassLs(d_mtt_org_soil_ls)
    d_mtt_org_soil_co2_ls = [ConvertSign(ConvertToCO2(ctoco2,x)) for x in d_mtt_org_soil_sum_ls]
    #print(8,d_mtt_org_soil_co2_ls)
    f.close()
    d_dom_som_org_soil_deadwood_sum_co2_ls=[SumTwoValues(a,SumTwoValues(b,c)) for (a,b,c) in
                                            zip(d_fl_to_wl_soil_co2_ls,d_clglpewesl_deadwood_org_co2_ls,d_mtt_org_soil_co2_ls)]
    #Deforestation: Conversion to water CO2
    #Change in 2015: Lines 1 and 2 are C 
    #--------------------------------------
    f = open(kp4a2_fl_to_waters_org_soil)
    d_fl_to_waters_org_soil_ls = [x.rpartition('#')[2].split() for x in f.readlines() if x.count('#') != 1]
    #Lines 1,2 are C
    d_fl_to_waters_org_soil_ls = d_fl_to_waters_org_soil_ls[0:2]
    d_fl_to_waters_org_soil_sum_ls = SumBiomassLs(d_fl_to_waters_org_soil_ls)
    d_fl_to_waters_org_soil_co2_ls = [ConvertSign(ConvertToCO2(ctoco2,x)) for x in d_fl_to_waters_org_soil_sum_ls]
    f.close()
    #Deforestation: Mineralization
    #-----------------------------
    f = open(kp4a2_d_mineralization)
    d_mineralization_ls = [x.rpartition('#')[2].split() for x in f.readlines() if x.count('#') != 1]
    #2015 two last lines are N2O
    d_mineralization_ls = d_mineralization_ls[2:len(d_mineralization_ls)]
    d_mineralization_sum_ls =  SumBiomassLs(d_mineralization_ls)
    d_mineralization_co2_ls = [ConvertToCO2(n2oco2eq,x) for x in d_mineralization_sum_ls]
    f.close()
    #Deforestation: Drained and rewetted organic soils N2O
    #-----------------------------------------------------
    f = open(kp4a2_fl_to_wl_non_co2)
    d_fl_to_wl_ls = [x.rpartition('#')[2].split() for x in f.readlines() if x.count('#') != 1]
    d_fl_to_wl_n2o_ls = d_fl_to_wl_ls[0:1]
    d_fl_to_wl_n2o_sum_ls =  SumBiomassLs(d_fl_to_wl_n2o_ls)
    d_fl_to_wl_n2o_co2_ls = [ConvertToCO2(n2oco2eq,x) for x in d_fl_to_wl_n2o_sum_ls]
    f.close()
    #Deforestation: Drained and rewetted organic soils CH4
    #-----------------------------------------------------
    f = open(kp4a2_fl_to_wl_non_co2)
    d_fl_to_wl_ls = [x.rpartition('#')[2].split() for x in f.readlines() if x.count('#') != 1]
    d_fl_to_wl_ch4_ls = d_fl_to_wl_ls[1:2]
    d_fl_to_wl_ch4_sum_ls =  SumBiomassLs(d_fl_to_wl_ch4_ls)
    d_fl_to_wl_ch4_co2_ls = [ConvertToCO2(ch4co2eq,x) for x in d_fl_to_wl_ch4_sum_ls]
    f.close()
    #Deforestation HWP
    #-----------------
    #HWP is IE
    d_hwp_ls = ['IE']*(inventory_year-1990+1)
    #4. Afforestation living biomass gains and losses trees
    #-------------------------------------------
    f = open(kp4_living_biomass_gains_trees)
    ar_trees_ls = [x.rpartition('#')[2].split() for x in f.readlines() if x.count('#') != 1]
    f.close()
    #Pick the Afforestation part, 2015 mineral and organic are added (not separately in the file)
    ar_bm_gains_trees_ls = ar_trees_ls[4:len(ar_trees_ls)]
    #Sum the biomasses, CL, CL, WLpeat, WLorg, Settlement, mineral, orgaing, South and North Finland
    ar_bm_sum_gains_trees_ls = SumBiomassLs(ar_bm_gains_trees_ls)
    f = open(kp4_ar_living_biomass_losses_trees)
    ar_bm_losses_trees_ls = [x.rpartition('#')[2].split() for x in f.readlines() if x.count('#') != 1]
    f.close()
    ar_bm_sum_losses_trees_ls = SumBiomassLs(ar_bm_losses_trees_ls)
    ar_bm_net_trees_ls = [SumTwoValues(x,y) for (x,y) in zip(ar_bm_sum_gains_trees_ls,ar_bm_sum_losses_trees_ls)]                          
    #Convert to CO2 and convert sign: if biomass increases -> emissions decrease and vice versa
    trees_ar_co2_ls = [ConvertSign(ConvertToCO2(ctoco2,x)) for x in ar_bm_net_trees_ls]
    #5. Afforestation, DOM+SOM Mineral soils
    #----------------------------------------
    f = open(kp4a1_clglsl_mineral_soil)
    dom_som_min_soil_ls = [x.rpartition('#')[2].split() for x in f.readlines() if x.count('#') != 1]
    dom_som_min_soil_sum_ls = SumBiomassLs(dom_som_min_soil_ls)
    #Convert to CO2 and convert sign: if biomass increases -> emissions decrease and vice versa
    dom_som_min_soil_co2_ls = [ConvertSign(ConvertToCO2(ctoco2,x)) for x in dom_som_min_soil_sum_ls]
    f.close()
    #6. Afforestation, DOM+SOM Organinc soils
    #----------------------------------------
    f=open(kp4a1_ar_org_soil)
    dom_som_org_soil_ls = [x.rpartition('#')[2].split() for x in f.readlines() if x.count('#') != 1]
    dom_som_org_soil_sum_ls = SumBiomassLs(dom_som_org_soil_ls)
    #Convert to CO2 and convert sign: if biomass increases -> emissions decrease and vice versa
    dom_som_org_soil_co2_ls = [ConvertSign(ConvertToCO2(ctoco2,x)) for x in dom_som_org_soil_sum_ls ]
    f.close()
    #7. Biomass burning
    #------------------
    f=open(kp4a11_wildfires)
    biomass_burning_ls = [x.rpartition('#')[2].split() for x in f.readlines() if x.count('#') != 1]
    #CO2 South and North Finland
    bm_burning_co2_ls = biomass_burning_ls[0:2]
    bm_burning_co2_sum_ls = SumBiomassLs(bm_burning_co2_ls)
    #CH4 South and North Finland
    bm_burning_ch4_ls = biomass_burning_ls[2:4]
    bm_burning_ch4_sum_ls = SumBiomassLs(bm_burning_ch4_ls)
    #N2O South and North Finland
    bm_burning_n2o_ls  = biomass_burning_ls[4:6]
    bm_burning_n2o_sum_ls = SumBiomassLs(bm_burning_n2o_ls)
    #Convert ch4 and n2o to co2eq and sum all three emissions
    biomass_burning_ch4co2eq_ls = [ConvertToCO2(ch4co2eq,x) for x in bm_burning_ch4_sum_ls]
    biomass_burning_n2oco2eq_ls = [ConvertToCO2(n2oco2eq,x) for x in bm_burning_n2o_sum_ls]
    biomass_burning_co2_sum_ls = [SumTwoValues(x,SumTwoValues(y,z)) for (x,y,z) in zip(bm_burning_co2_sum_ls,biomass_burning_ch4co2eq_ls,biomass_burning_n2oco2eq_ls)]
    #print(biomass_burning_co2_sum_ls)
    f.close()
    #8. 2015 addition Mineralization
    #-------------------------------
    f=open(kp4_ar_mineralization)
    ar_mineralization_ls=[x.rpartition('#')[2].split() for x in f.readlines() if x.count('#') != 1]
    #South and North Fianland
    ar_mineralization_no2_ls = ar_mineralization_ls[0:2]
    ar_mineralization_n2o_sum_ls=SumBiomassLs(ar_mineralization_no2_ls)
    ar_mineralization_n2o_co2_ls = [ConvertToCO2(n2oco2eq,x) for x in ar_mineralization_n2o_sum_ls]
    #9.Drained organic soils N2O
    #---------------------------
    f=open(kp4a1_clglpewesl_organic_soils_nonco2)
    drained_org_soils_nonco2_ls =  [x.rpartition('#')[2].split() for x in f.readlines() if x.count('#') != 1]
    #Two lines in the file, the first one is CH4 
    drained_org_soils_sum_ch4_ls = drained_org_soils_nonco2_ls[0:1]
    drained_org_soils_sum_ch4_ls =  SumBiomassLs(drained_org_soils_sum_ch4_ls)
    #Convert from N2O to CO2
    drained_org_soils_sum_ch4co2eq_ls = [ConvertToCO2(ch4co2eq,x) for x in drained_org_soils_sum_ch4_ls]
    f.close()
    #10.Drained organic soils CH4
    #---------------------------
    f=open(kp4a1_clglpewesl_organic_soils_nonco2)
    drained_org_soils_nonco2_ls =  [x.rpartition('#')[2].split() for x in f.readlines() if x.count('#') != 1]
    #Two lines in the file, the second one is CH4
    drained_org_soils_sum_n2o_ls = drained_org_soils_nonco2_ls[1:2]
    drained_org_soils_sum_n2o_ls = SumBiomassLs(drained_org_soils_sum_n2o_ls)
    #Convert from CH4 to CO2
    drained_org_soils_sum_n2oco2eq_ls = [ConvertToCO2(n2oco2eq,x) for x in drained_org_soils_sum_n2o_ls]
    f.close()
    #11.HWP afforestation
    #--------------------
    f=open(kp4_hwp_ard)
    hwp_ard_ls =  [x.rpartition('#')[2].split() for x in f.readlines() if x.count('#') != 1]
    #2015 the file structure is in 3 parts: 1) Initial stock, 2) Gains and losses 3) half-time information
    #The sum of gains and losses will go to the table
    #2016 the file structure is for each item: 1) half life, 2) init stock, 3) gains and 4) losses
    #Pick every fourth item starting from the first right place in the list 
    hwp_ar_ls_gains = hwp_ard_ls[2::4]
    hwp_ar_ls_losses = hwp_ard_ls[3::4]
    hwp_ar_ls = hwp_ar_ls_gains+hwp_ar_ls_losses
    #print(hwp_ar_ls)
    hwp_ar_sum_ls = SumBiomassLs(hwp_ar_ls)
    #Removals are good for the atmosphere, change the sign
    hwp_ar_sum_ls = [ConvertSign(ConvertToCO2(ctoco2,x)) for x in hwp_ar_sum_ls]
    #HWP does not have full time series from 1990 
    hwp_padding_ls = PaddingList(inventory_year,hwp_ar_sum_ls)
    hwp_padding_ls = ['IE']*len(hwp_padding_ls)
    hwp_ar_sum_co2_ls = hwp_padding_ls+hwp_ar_sum_ls
    f.close()

    #Create the two tables Afforestation/Reforestation and Deforestation
    #-------------------------------------------------------------------
    print("Creating first text file for Afforestation/Reforestation and Deforestation in", file_name)
    f1 = open(kptable_appendix_11b_file,'w')
    delim ='#'
    table_name="Appendix_11b"
    table_header="Net emissions and removals from the ativities under Articles 3.3\n"
    table1title1="Table 1_App_11b Net emissions and removals from Afforestation and Reforestation, kt CO2eq.\n"
    table2title2="Table 2_App_11b Net emissions and removals from Deforestation, ktCO2eq.\n"  
    table1columns1=delim+"Biomass"+delim+"DOM+SOM Mineral soils"+delim+"DOM+SOM Organic soils"+delim+"Biomass burning"+delim+"Mineralization"+delim
    table1columns1=table1columns1+"Drained organic soils N2O"+delim+"Drained organic soils CH4"+delim+"HWP"+delim+"Total\n"
    table2columns2=delim+"Biomass"+delim+"DOM+SOM Mineral soils"+delim+"DOM+SOM Organic soils+Deadwood"+delim+"Conversion to water CO2"+delim+"Mineralization"+delim
    table2columns2=table2columns2+"Drained and rewetted organic soils CH4"+delim+"Drained and rewetted organic soils NO2"+delim
    table2columns2=table2columns2+"HWP"+delim+"Conversion to water CH4"+delim+"Total"+"#\n" 
    #Row titles from 199 to inventory year
    row_title_ls = GenerateRowTitleList(start,inventory_year)
    f1.write(table_name)
    f1.write(table_header)
    #Afforestation and Reforestation
    f1.write(table1title1)
    f1.write(table1columns1)
    for (year,agr_ar_co2,trees_ar_co2,dom_som_min,dom_som_org,bm_burning,ar_min_co2,n2oco2eq,ch4co2eq,hwp) in zip(row_title_ls,agr_ar_co2_ls,trees_ar_co2_ls,
                                                                                                                dom_som_min_soil_co2_ls,
                                                                                                                dom_som_org_soil_co2_ls,
                                                                                                                biomass_burning_co2_sum_ls,
                                                                                                                ar_mineralization_n2o_co2_ls,
                                                                                                                drained_org_soils_sum_n2oco2eq_ls,
                                                                                                                drained_org_soils_sum_ch4co2eq_ls,
                                                                                                                hwp_ar_sum_co2_ls):
        total=SumTwoValues(SumTwoValues(SumTwoValues(SumTwoValues(SumTwoValues(SumTwoValues(SumTwoValues(SumTwoValues(agr_ar_co2,trees_ar_co2),
                                                                                                        dom_som_min),dom_som_org),bm_burning),
                                                                                                        ar_min_co2),n2oco2eq),ch4co2eq),hwp)
        f1.write(str(year)+delim+str(SumTwoValues(agr_ar_co2,trees_ar_co2))+"#"+str(dom_som_min)+"#"+str(dom_som_org)+"#"+str(bm_burning)+"#")
        f1.write(str(ar_min_co2)+"#"+str(n2oco2eq)+"#"+str(ch4co2eq)+"#"+str(hwp)+"#"+str(total)+"#\n")
    f1.write("Data from:"+"#"+kp4a_agr_bm_gains_losses+" Lines:9-"+str(len(agr_ls))+"#"+kp4a1_clglsl_mineral_soil+"#"+kp4a1_ar_org_soil+"#"+kp4a11_wildfires+"#")
    f1.write(kp4_ar_mineralization+" Lines:1,2"+delim+kp4a1_clglpewesl_organic_soils_nonco2+" Line:1"+"#"+kp4a1_clglpewesl_organic_soils_nonco2+" Line:2"+"#"+kp4_hwp_ard+"#\n")
    f1.write("#"+kp4_living_biomass_gains_trees+" Lines:5-"+str(len(ar_trees_ls))+"#"+"#"+"#"+"CO2 Lines:1-2,CH4 Lines:3-4,N2O Lines:5-6"+"####"+"Gains Lines:3,7,11 etc."+"#\n")
    f1.write("#"+kp4_ar_living_biomass_losses_trees+"#######"+"Losses Lines:4,8,12 etc."+"#\n")
    f1.write('\n\n')

    #Deforestation
    f1.write(table2title2)
    f1.write(table2columns2)
    for (year,agr_d_co2,trees_d_co2,ar_under_d_co2,
        d_sl_soil_co2,d_ar_under_d_min_soil_co2,d_mtt_min_soil_co2,d_clglpewesl_deadwood_min_co2,
        dom_som_org_soil_deadwood_co2,
        d_fl_to_waters_org_soil_co2,
        d_mineralization_co2,
        d_fl_to_wl_ch4_co2,d_fl_to_wl_n2o_co2,
        d_hwp,
        to_waters_ch4) in zip(row_title_ls,agr_d_co2_ls,trees_d_co2_ls,ar_under_d_co2_ls,
                            d_sl_soil_co2_ls,d_ar_under_d_min_soil_co2_ls,d_mtt_min_soil_co2_ls,d_clglpewesl_deadwood_min_co2_ls,
                            d_dom_som_org_soil_deadwood_sum_co2_ls,
                            d_fl_to_waters_org_soil_co2_ls,
                            d_mineralization_co2_ls,
                            d_fl_to_wl_ch4_co2_ls,d_fl_to_wl_n2o_co2_ls,
                            d_hwp_ls,
                            fl_to_waters_ch4_co2_ls):
        biomass = SumTwoValues(agr_d_co2,trees_d_co2)
        biomass = SumTwoValues(biomass,ar_under_d_co2)
        dom_som_min_soil=SumTwoValues(d_sl_soil_co2,d_ar_under_d_min_soil_co2)
        dom_som_min_soil=SumTwoValues(dom_som_min_soil,d_mtt_min_soil_co2)
        dom_som_min_soil=SumTwoValues(dom_som_min_soil,d_clglpewesl_deadwood_min_co2)
        total1 = SumTwoValues(SumTwoValues(SumTwoValues(SumTwoValues(agr_d_co2,trees_d_co2),ar_under_d_co2),d_sl_soil_co2),d_ar_under_d_min_soil_co2)
        total2 = SumTwoValues(SumTwoValues(d_mtt_min_soil_co2,d_clglpewesl_deadwood_min_co2),dom_som_org_soil_deadwood_co2)
        total3 = SumTwoValues(SumTwoValues(d_fl_to_waters_org_soil_co2,d_mineralization_co2),d_fl_to_wl_ch4_co2)
        total4 = SumTwoValues(SumTwoValues(d_fl_to_wl_n2o_co2,d_hwp),to_waters_ch4)
        total = total1+total2+total3+total4
        f1.write(str(year)+delim+str(biomass)+delim+str(dom_som_min_soil)+delim+str(dom_som_org_soil_deadwood_co2)+delim+str(d_fl_to_waters_org_soil_co2)+delim+
                str(d_mineralization_co2)+delim+str(d_fl_to_wl_ch4_co2)+delim+str(d_fl_to_wl_n2o_co2)+delim+str(d_hwp)+delim+str(to_waters_ch4)+"#"+str(total)+"#\n")
    
    f1.write("Data from:"+"#"+kp4a_agr_bm_gains_losses+" Lines:1-8"+delim+kp4a2_sl_soil+delim+kp4a2_fl_to_wl_soil+delim+kp4a2_fl_to_waters_org_soil+" Lines:1,2"+"#")
    f1.write(kp4a2_d_mineralization+delim+kp4a2_fl_to_wl_non_co2+" Line:2"+delim+kp4a2_fl_to_wl_non_co2+" Line:1"+delim+"No file"+delim)
    f1.write(kp4a2_fl_to_waters_org_soil+" Line:3"+"#\n")
    f1.write("#"+kp4a2_d_living_biomass_losses_trees+delim+kp4a2_ar_under_d_soil+delim+kp4a2_clglpewesl_deadwood+" Lines:1-8"+"#\n")
    f1.write("#"+kpa2_ar_under_D_gains+delim+kp_defor_mineral+delim+kp_defor_organic+"#\n")
    f1.write("#"+delim+kp4a2_clglpewesl_deadwood+" Lines:9-10"+"#\n")
    now = datetime.datetime.now()
    #print(str(now))
    f1.write("Date produced: "+str(now)+"\n")
    f1.close()
    #Create excel
    p = pathlib.Path(file_name)
    stem = p.stem
    p_excel = pathlib.Path(stem+'.xlsx')
    print("Creating Excel file for Afforestation/Reforestation and Deforestation in", str(p_excel))
    #Define max number of columns, dataframe can adjust to it
    names=['col' + str(x) for x in range(12) ]
    df = pd.read_csv(file_name,engine='python',header=None,delimiter='#',keep_default_na=False,names=names,dtype=str)
    writer = pd.ExcelWriter(p_excel,engine='openpyxl')
    df_float = df.applymap(ConvertFloat) 
    df_float.to_excel(writer,file_name,header=False)
    writer.close()
