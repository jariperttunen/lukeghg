import os
import datetime
import pathlib
import pandas as pd
import xlsxwriter
#from operator import add
#from optparse import OptionParser as OP
from lukeghg.crf.uid340to500mapping import MapUID340to500, Create340to500UIDMapping
import glob
from lukeghg.crf.crfxmlconstants import *
from lukeghg.crf.crfxmlfunctions import *
#inventory_year=2015

def FormatNumber(x,formatting):
    try:
        return format(x,formatting)
    except ValueError:
        return x
        
def ConvertToCO2AndRound(x,sign,conversion,decimals):
    """x: the emssions
       sign: 1.0 or -1.0: Emissions to atmosphere are positive, carbon sinks are negative
       conversion: N2O, CH4, C conversion or 1.0
       decimals: accuracy in rounding
    """
    try:#CRFREeporter uses kt, convert to Mt
        print(x)
        return RoundToNDecimals(ConvertToCO2(conversion,sign*x)/1000.0,decimals)
    except TypeError:
        return x
    
def FilterUID(data_ls,uid_set):
    ls = []
    for data in data_ls:
        if len(data) > 0 and data[0].strip('{}') in uid_set:
            data = [RoundToNDecimals(x,6) for x in data]
            ls.append(data)
            uid_set.remove(data[0].strip('{}'))
        elif len(data) == 0:
            print("Empty line in a file")
    if len(uid_set) > 0:
        print("UID not found")
        print(uid_set)
    return ls

def EmissionToMtCO2eqSum(file_ls,uid_ls,conversion,sign):
    data_ls = []
    for file in file_ls:
        data_ls = data_ls + ReadGHGInventoryFile(file)
    data_ls =  FilterUID(data_ls,set(uid_ls))
    sum_ls = data_ls.pop(0)
    sum_ls.pop(0)
    #Convert notation keys to zeros
    #sum_ls = [SumTwoValues(x,0.0) for x in sum_ls]
    #print(sum_ls)
    for ls in data_ls:
        ls.pop(0)
        print(ls)
        sum_ls = [SumTwoValues(x,y) for (x,y) in zip(ls,sum_ls)]
        #print("SUM",sum_ls)
    #Reporter uses kt, convert to Mt 
    sum_ls = [str(ConvertToCO2AndRound(x,sign,conversion,12)) for x in sum_ls]
    print("CO2",sum_ls)
    return sum_ls

def SumFileList(file_ls,toCO2):
    C_ls=[]
    for file in file_ls:
        C_ls = C_ls+ReadGHGInventoryFile(file)
    C_ls=[x[1:] for x in C_ls]
    C_sum_ls = C_ls.pop(0)
    C_sum_ls = [ConvertFloat(x) for x in C_sum_ls]
    for ls in C_ls:
        C_sum_ls = [SumTwoValues(ConvertFloat(x),ConvertFloat(y)) for (x,y) in zip(C_sum_ls,ls)]
    CO2_sum_ls=[toCO2*x/1000.0 for x in C_sum_ls]
    CO2_sum_ls=[str(format(ConvertSign(float(x)),'.20f')) for x in CO2_sum_ls]
    return CO2_sum_ls
#Forest land
#domsom_mineral_file_ls = glob.glob("LU4A*Mineral_soil.csv")
#domsom_organic_file_ls = glob.glob("LU4A*Organic_soil.csv")
#N_fertilisation_file = "LU4_I_fertilisation.csv"
#biomass_burning_file_ls = ["LU4A1_controlledburning.csv","LU4A1_wildfires.csv"]
#N_mineralisation_file = "LU4III_fl_mineralisaatio_excelissa_tehty_09march2016.csv"
#CH4_N2O_drainage_file_ls =["LU4AII_CH4_drainaged_soils.csv","LU4AII_N2O_drainaged_soils.csv"]
#wl_dead_wood_file = 'LU4A2_WLSL_deadwood.csv'
#wl_som_file_ls = ['LU4D1_peat_ext_rem.csv','LU4D1_peat_ext_from_wl.csv','LU4_floodedwaters_soil_C_CH4.csv',
#                  'LU4D23_peat_ext_land_to_otherWL_CO2.csv','LU4D13_other_WL_managed_C.csv',
#                  'LU4D21_peat_ext_land_to_pe_CO2.csv','LU4D231_regressed_forests_C_soils.csv']
#wl_ch4_n2o_file_ls = ['LU4DII_peat_extraction_nonCO2_soils.csv','LU4_floodedwaters_soil_C_CH4.csv',
#                      'LU4DII_regressed_forests_nonCO2_soils.csv']
#sl_biomass_file_ls = ['LU4A2-4F2_living_biomass_losses_trees.csv','LU4_agr_bm_gains_losses.csv',
#                      'LU4B-E_from_oWL_living_biomass_losses_trees.csv']
#sl_som_file_ls = ['LU4E21_soil.csv']
#sl_N2O_mineralisation_file_ls = ['LU4E21_soil_N2O_mineralisation.csv']
#hwp_file_ls = ['LULUCF_HWP_CRF.csv']
#Cropland
#mtt_file = "LULUCF_UID_MTT.csv"
#agr_bm_file = "LU4_agr_bm_gains_losses.csv"
#agr_bm_losses_file = "LU4A2-4F2_living_biomass_losses_trees.csv"
#agr_wl_cl_bm_losses_file = 'LU4B-E_from_oWL_living_biomass_losses_trees.csv'

dom_som_mineral_uid_ls = ['48E78285-3774-46F3-AEBC-1F02736B1869','A4DB34A0-1847-401A-92BA-7CCE37611F1A',
                          '334088D5-54BD-44A2-A0EA-EFDD842DB36C','B34584B9-54FC-436F-9750-4D4E604DBDAB']
dom_som_organic_uid_ls = ['846E5F70-532C-4787-BBF3-5458B7BA2D5D','F6FB5D56-CF24-4A98-A516-A870BF67244A',
                          '41EB6051-3F79-4920-8331-0563481BC899','3B50B4A3-3C70-4ADC-8C0E-F8186DE147F2']
N_mineralisation_uid_ls = ['7CC2DF97-BECD-4191-A3B1-FBB01FF83D43','109C3AB7-0077-4367-8C74-E2467ACE7D16',
                           '5B0C3BF7-7EE6-4C33-8D72-A21669C92918','87FC6342-FA45-4030-89E6-0E02A2BFC648']
#Grassland
#biomass_gains_trees_file = "LU4C1_GL-GL_Living_biomass_gains_trees.csv"
#Wetlands
wl_biomass_uid_ls = ['92DFB34F-5B75-4BCB-A758-7F346C1E918D','A4A7D7FA-23F9-4ADA-B643-10307BD31C8B',
                     '7C6816AA-0A8A-434B-84CD-62A1D52D3E88','892E3E41-F618-4A95-844A-8FDF9A6FBFA5',
                     'D2528CC8-D398-422B-AEBA-27CE5A44091F','54D18A8E-B90E-4521-93AB-E8599CA5AE29',
                     'EC5492F0-F9E4-4C2A-B994-585206486EBB','788519B8-6B25-4D79-A20B-D05E20407DEE']
wl_dead_wood_uid_ls = ['80DA0459-04A7-494B-960D-74CA4BC2EAE1']
#Ask from uid 375196C2-F23E-431E-9002-D4F9F131F75B onwards where the numbers are in CRFReporter
wl_som_uid_ls = ['D0CD1135-8684-4AA6-A5B6-D4838AA51401','1F66B5AA-2CE8-4AC7-98B8-D1225EB7908E',
                 'FA5944EB-397A-4A9F-B1AB-621F095589D9','6CD89939-66E5-432F-8ADC-3D30C6F27776',
                 '07707982-3317-46B1-AEA8-C0EBFEDA37F0','3EC71220-A20F-4D17-9E21-61052B40C018',
                 'E45E4D33-EF70-44B3-B677-411E0AE64D26','D25586E2-DC67-4941-B692-EF1D721E3E43',
                 '6294235D-9C28-4AA3-89EF-7FF6A9EE6E68','26C39115-0D31-4A9D-A05B-6A9514813B84',
                 '375196C2-F23E-431E-9002-D4F9F131F75B',
                 '9C84D2FE-B631-4004-829D-D61688D50086','43107214-F52D-49AB-8D60-BB5A547BE291',
                 'D4126FA3-991C-4253-A5D9-E1E61C0BC9D5','D328C711-A441-4587-B515-B67E3B024FE2']
wl_ch4_uid_ls = ['33640199-E4E9-4FAB-BE6F-6562C740009A','DB376B9F-1843-48DA-B8D1-A7B18AB5D212',
                 '6D6EB223-A61B-4E2C-AB00-E4BF9F6C69D5']
wl_n2o_uid_ls = ['7BB50E49-6297-4259-B504-A79DB85FA7E4','2739FA34-7967-43C3-9557-BE220021A050']
#Settlement
sl_biomass_uid_ls = ['E3719388-E913-43D0-8346-1B13D6663079','EB8699FD-1FAA-4739-8A01-F450C5097C54',
                     'DB6253EB-8660-4C1C-B880-10991D8E2DC5','DAA0FB40-3EE2-4BB6-AE86-8C8BE148216B']
sl_dead_wood_uid_ls = ['6E9B1091-9498-487A-8C33-268D053181AA']
sl_som_uid_ls = ['0C26CC53-5EEB-41F2-ABCF-8651816E847E']
sl_N2O_mineralisation_uid_ls =['283CB017-2D3E-4817-AFAB-CC3D885151AB']
#HWP
hwp_CO2_uid_ls = ['9A097CDD-B6B9-4B64-B84E-588C5F7D8ACC','2B037393-00BD-4D5B-BB82-BF4637E0BE97',
                  '70708E1D-8D36-40FE-B5F9-DBF2915F7CC2','37A8F8B1-2BD9-4FFD-8A3C-0AD5DDAE8379',
                  '41B5B0BB-564D-422C-8456-491AFEA5C5C6','AE250397-65B7-42B2-A337-85F5B902FEFE']
N2O_indirect_uid_ls = ['E3A677C8-0818-417A-9D7C-053DEFD1F14E']

#-------------------------------------------
#This list collects all results
CO2eq_table_data_ls = []
#-------------------------------------------
def CreateCO2eqTableData(crf_dir):
    lulucf_file_ls = glob.glob(crf_dir+"/"+"LU*.csv")
    biomass_file="Table_6.1-2.csv"
#Forest land
#1. 4A Biomass, mineral and organic
    f = open(biomass_file)
    biomass_data_ls = [x.split() for x in f.readlines()]
    f.close()
    biomass_data_ls.pop(0)
    biomass_data_ls = [list(map(lambda x: format(float(x),'.6f'),ls)) for ls in biomass_data_ls] 
    #-------------------------------------------
    place_holder_ls = ['0']*len(biomass_data_ls[0])
    print(biomass_data_ls[0])
    print(biomass_data_ls[1])
    CO2eq_table_data_ls.append(place_holder_ls)
    CO2eq_table_data_ls.append(biomass_data_ls[0])
    CO2eq_table_data_ls.append(biomass_data_ls[1])
#2. 4A DOM+SOM, mineral and organic
    fl_dom_som_mineral_uid_ls = ['33B17FCF-CEF0-4C52-A083-41E77975CC17','9CD08E1A-B433-497D-9209-EC017CA23724',
                                'B3F95305-ACF3-4064-A83E-705F560B39C8','E396B346-95B8-4F15-B0DD-AF88CD396A1D',
                                '8F57EF8B-E304-4EF0-8EC6-0FC6E8C2CDB0']
    fl_dom_som_organic_uid_ls = ['1632C1F2-832E-48D5-BA76-AA1DFAA643DC','BD9A7BB8-BBAA-47A5-9437-0F5517385FCE',
                                '5E64A07B-D172-42ED-8E28-0BAA407A9D59',
                                '4CA589AF-132A-4C1E-AAFE-FF384EABE789','661092F5-C566-4018-8792-41A7A3FED14C',
                                '758A489C-2516-4828-9DD7-DAA8C3FE2BAD']
    mineral_sum_ls = EmissionToMtCO2eqSum(lulucf_file_ls,fl_dom_som_mineral_uid_ls,ctoco2,-1.0)
    organic_sum_ls = EmissionToMtCO2eqSum(lulucf_file_ls,fl_dom_som_organic_uid_ls,ctoco2,-1.0)
    print(mineral_sum_ls)
    CO2eq_table_data_ls.append(mineral_sum_ls)
    print(organic_sum_ls)
    CO2eq_table_data_ls.append(organic_sum_ls)
#3. 4A1 N fertilisation
    n_fertilization_uid_ls = ['22DBD636-5D80-4C41-AD31-CB2CA289CAEA']
    n_fertilisation_ls = EmissionToMtCO2eqSum(lulucf_file_ls,n_fertilization_uid_ls,n2oco2eq,1.0)
    print(n_fertilisation_ls)
    CO2eq_table_data_ls.append(n_fertilisation_ls)
#4. Biomass burning
#I. Controlled burning
    co2_cb_uid_ls = ['AF726EED-F8EB-4079-9B68-A8352BBB42B4']
    ch4_cb_uid_ls = ['C7587797-74A3-4CBB-A0FA-207D86FEE948']
    n2o_cb_uid_ls = ['7063055F-F00B-4788-BE25-0AF9148C3A78']
    fl_cb_co2_ls = EmissionToMtCO2eqSum(lulucf_file_ls,co2_cb_uid_ls,1.0,1.0)
    fl_cb_ch4_ls = EmissionToMtCO2eqSum(lulucf_file_ls,ch4_cb_uid_ls,ch4co2eq,1.0)
    fl_cb_n2o_ls = EmissionToMtCO2eqSum(lulucf_file_ls,n2o_cb_uid_ls,n2oco2eq,1.0)
#II. Wildfires
    co2_wf_uid_ls = ['62C0BC06-B962-478B-92DD-2F699532DF30']
    ch4_wf_uid_ls = ['3B6FC0DA-115F-46DA-8613-255B19BC0A3E']
    n2o_wf_uid_ls = ['67583DDF-4B65-4348-BFFE-2FF41FDD6DDE']
    fl_wf_co2_ls = EmissionToMtCO2eqSum(lulucf_file_ls,co2_wf_uid_ls,1.0,1.0)
    fl_wf_ch4_ls = EmissionToMtCO2eqSum(lulucf_file_ls,ch4_wf_uid_ls,ch4co2eq,1.0)
    fl_wf_n2o_ls = EmissionToMtCO2eqSum(lulucf_file_ls,n2o_wf_uid_ls,n2oco2eq,1.0)
#III. LU4A2V_wildfires
    co2_wfV_uid_ls = ['9EF9FD3E-B8CA-4F79-80F0-1146942ED230']
    ch4_wfV_uid_ls = ['24695657-1FA1-4EAC-8EBD-97DB95000A5F']
    n2o_wfV_uid_ls = ['1029419D-4591-4132-A65B-083D18C12BC6']
    fl_wfV_co2_ls = EmissionToMtCO2eqSum(lulucf_file_ls,co2_wfV_uid_ls,1.0,1.0)
    fl_wfV_ch4_ls = EmissionToMtCO2eqSum(lulucf_file_ls,ch4_wfV_uid_ls,ch4co2eq,1.0)
    fl_wfV_n2o_ls = EmissionToMtCO2eqSum(lulucf_file_ls,n2o_wfV_uid_ls,n2oco2eq,1.0)
#I + II
    bm_burning_ls = [FormatNumber(SumTwoValues(a,SumTwoValues(b,SumTwoValues(c,SumTwoValues(d,SumTwoValues(e,f))))),'.12f')
                    for (a,b,c,d,e,f) in zip(fl_cb_co2_ls,fl_cb_ch4_ls,fl_cb_n2o_ls,fl_wf_co2_ls,fl_wf_ch4_ls,fl_wf_n2o_ls)]
#(I+II)+III
    bm_burning_ls = [FormatNumber(SumTwoValues(a,SumTwoValues(b,SumTwoValues(c,d))),'.12f')
                    for (a,b,c,d) in zip(fl_wfV_co2_ls,fl_wfV_ch4_ls,fl_wfV_n2o_ls,bm_burning_ls)]
    print("3. BM burning")
    print(bm_burning_ls)
    CO2eq_table_data_ls.append(bm_burning_ls)
#5. N mineralisation
    fl_N_mineralisation_uid_ls = ['1FDFE900-D9C3-44C5-9CCE-2AA4B6713DBB','E82036FA-99A3-4048-9B1F-5EC104BA0337',
                                'B598E180-C1C5-492A-B7FA-C0FAB7816050','860D7B59-2124-4518-A98E-A9BA913F9118',
                                '2EFC222A-3826-43A0-BE19-D0D51BBF46B2']
    N_mineralisation_sum_ls = EmissionToMtCO2eqSum(lulucf_file_ls,fl_N_mineralisation_uid_ls,n2oco2eq,1.0)
    print(N_mineralisation_sum_ls)
    CO2eq_table_data_ls.append(N_mineralisation_sum_ls)
#6. CH4 and N2O from drainaged forest land
    fl_ch4_uid_ls = ['50671AEF-56F6-44DA-B196-85D05206FCFB']
    fl_n2o_uid_ls = ['7B385269-08A9-422C-95EF-AF5D03598484','041A2374-870C-4C8C-B803-8F5FD91C500A']
    fl_ch4_ls = EmissionToMtCO2eqSum(lulucf_file_ls,fl_ch4_uid_ls,ch4co2eq,1.0)
    fl_n2o_ls = EmissionToMtCO2eqSum(lulucf_file_ls,fl_n2o_uid_ls,n2oco2eq,1.0)
    sum_ch4n2oco2eq_ls = [FormatNumber(SumTwoValues(x,y),'.12f') for (x,y) in zip(fl_ch4_ls,fl_n2o_ls)]
    print(sum_ch4n2oco2eq_ls)
    CO2eq_table_data_ls.append(sum_ch4n2oco2eq_ls)
#7. 4B Cropland biomass
    cl_biomass_uid_ls = ['176984AA-39DD-46BD-8783-2632BEF3C520','0A0CAA48-DB6F-412A-AFBD-8F078B1AF8A6',
                        '36CD6D26-94F4-4BDA-9111-5550B936E473','8B60CCEA-6FB6-49EC-A94E-AAC77C144727',
                        '3F56BC8A-08E4-45CA-B1F7-8DAA14BE39C1','2398E95A-4527-434A-9503-BF0E9FD260A9',
                        '942BC69D-81D0-40F7-B034-DED89D2D4E00','4F79582F-31DB-41D4-966D-9DBCD04B722A',
                        '2F5B1083-7134-4982-9FBC-238D55BFB41F']
    CO2eq_table_data_ls.append(place_holder_ls)
    #cl_biomass_file_ls = [mtt_file,agr_bm_file,agr_bm_losses_file,agr_wl_cl_bm_losses_file]
    sum_cl_biomass_co2_ls  =  EmissionToMtCO2eqSum(lulucf_file_ls,cl_biomass_uid_ls,ctoco2,-1.0)
    print(sum_cl_biomass_co2_ls)
    CO2eq_table_data_ls.append(sum_cl_biomass_co2_ls)
#8. 4B Dead wood
    deadwood_uid_ls = ['810E194F-0D38-4486-8A88-96ACF87C2059']
    sum_deadwood_co2_ls = EmissionToMtCO2eqSum(lulucf_file_ls,deadwood_uid_ls,ctoco2,-1.0)
    print("8. CL Dead wood")
    print(sum_deadwood_co2_ls)
    CO2eq_table_data_ls.append(sum_deadwood_co2_ls)
#9. 4B DOM+SOM mineral and organic soil
#Mineral
    sum_dom_som_min_co2_ls =  EmissionToMtCO2eqSum(lulucf_file_ls,dom_som_mineral_uid_ls,ctoco2,-1.0)
    print(sum_dom_som_min_co2_ls)
    CO2eq_table_data_ls.append(sum_dom_som_min_co2_ls)
#Organic
    sum_dom_som_org_co2_ls = EmissionToMtCO2eqSum(lulucf_file_ls,dom_som_organic_uid_ls,ctoco2,-1.0)
    print(sum_dom_som_org_co2_ls)
    CO2eq_table_data_ls.append(sum_dom_som_org_co2_ls)
#10. N mineralisation
    sum_N_mineralisation_ls = EmissionToMtCO2eqSum(lulucf_file_ls,N_mineralisation_uid_ls,n2oco2eq,1.0)
    print(sum_N_mineralisation_ls)
    CO2eq_table_data_ls.append(sum_N_mineralisation_ls)
#4 C Grassland
    gl_biomass_uid_ls = ['9268C483-1CDF-492B-A0CC-510A18787438','53255AB3-3284-479F-9451-7AA403AC0C99',
                        'CB120EB8-E3C5-4A9D-948A-84800B40BB85','96E8D24F-CBF5-4E09-BD19-D240F3DAEC67',
                        'BEFED697-594C-4A84-8732-583E6A28379F','29C9BDB9-5F4B-425C-AC6F-568A6BA18E5A',
                        '96022841-C27D-42CF-8EE3-0D1A5437AD6B','BB8A06DB-3524-4658-B3F4-39C8B3E3B9C4',
                        'FFD8E79B-1DA0-4399-910A-6E875F1A8F58']
    gl_dead_wood_uid_ls = ['197C9403-609C-45DA-9A25-A0AD0BBA5930']
    gl_dom_som_mineral_uid_ls = ['CED9F314-185E-4B57-A302-3CEA41396C3D','6FAE66FC-C7F1-4721-BB8E-37A0830465E3',
                                '74FDB2BF-3FC6-4EB3-A1FD-F580F27CAC1A']
    gl_dom_som_organic_uid_ls = ['A9A40D5A-95E7-47DF-8D15-CA9EF8916317','6B9C03D8-C39C-439D-993E-0F444F1EB30E',
                                '3F22874A-DA26-43B4-9D5E-DB968F0025C4','0E97BE1E-C32F-4C75-AB79-A3B8893CB7FE']
    gl_N_mineralisation_uid_ls = ['A5505411-C5E5-431C-BB58-25E152436833','6B7A581C-6A5E-4A77-86C9-FBB3BDEFC87E',
                                '29D1D560-ACF2-487D-9AF0-291BF6750BE0','D8ECB802-B474-4EFD-8A83-0BA019E9B019']
    gl_wf_co2_uid_ls = ['BD322158-494A-4BC0-AA2B-9821F925CB7E']
    gl_wf_ch4_uid_ls = ['A60D8558-4AB5-444E-84C3-F697036626EB']
    gl_wf_n2o_uid_ls = ['C67D494D-213C-4FE2-B4F8-0AE6D51387D7']
#11. Biomass
    CO2eq_table_data_ls.append(place_holder_ls)
    #gl_biomass_file_ls = [biomass_gains_trees_file,mtt_file,agr_bm_file,agr_bm_losses_file,
    #                    agr_wl_cl_bm_losses_file]
    sum_gl_biomass_ls = EmissionToMtCO2eqSum(lulucf_file_ls,gl_biomass_uid_ls,ctoco2,-1.0)
    print(sum_gl_biomass_ls)
    CO2eq_table_data_ls.append(sum_gl_biomass_ls)
#12. Dead wood
    sum_gl_deadwood_ls = EmissionToMtCO2eqSum(lulucf_file_ls,gl_dead_wood_uid_ls,ctoco2,-1.0)
    print(sum_gl_deadwood_ls)
    CO2eq_table_data_ls.append(sum_gl_deadwood_ls)
#13. DOM+SOM mineral
    sum_gl_dom_som_mineral_ls = EmissionToMtCO2eqSum(lulucf_file_ls,gl_dom_som_mineral_uid_ls,ctoco2,-1.0)
    print(sum_gl_dom_som_mineral_ls)
    CO2eq_table_data_ls.append(sum_gl_dom_som_mineral_ls)
#14. DOM+SOM organic
    sum_gl_dom_som_organic_ls = EmissionToMtCO2eqSum(lulucf_file_ls,gl_dom_som_organic_uid_ls,ctoco2,-1.0)
    print(sum_gl_dom_som_organic_ls)
    CO2eq_table_data_ls.append(sum_gl_dom_som_organic_ls)
#15. N mineralisation
    sum_gl_N_mineralisation_ls = EmissionToMtCO2eqSum(lulucf_file_ls,gl_N_mineralisation_uid_ls,n2oco2eq,1.0)
    print(sum_gl_N_mineralisation_ls)
    CO2eq_table_data_ls.append(sum_gl_N_mineralisation_ls)
#Wildfires
    gl_wf_co2_ls = EmissionToMtCO2eqSum(lulucf_file_ls,gl_wf_co2_uid_ls,1.0,1.0)
    gl_wf_ch4_ls = EmissionToMtCO2eqSum(lulucf_file_ls,gl_wf_ch4_uid_ls,ch4co2eq,1.0)
    gl_wf_n2o_ls = EmissionToMtCO2eqSum(lulucf_file_ls,gl_wf_n2o_uid_ls,n2oco2eq,1.0)
    sum_gl_bm_burning_co2_ls = [FormatNumber(SumTwoValues(SumTwoValues(x,y),z),'.12f') for (x,y,z) in zip(gl_wf_co2_ls,gl_wf_ch4_ls,gl_wf_n2o_ls)]
    CO2eq_table_data_ls.append(sum_gl_bm_burning_co2_ls)
#Wetlands
#16. Biomass
    CO2eq_table_data_ls.append(place_holder_ls)
    #wl_biomass_file_ls = [biomass_gains_trees_file,mtt_file,agr_bm_file,agr_bm_losses_file,
    #                      agr_wl_cl_bm_losses_file]
    sum_wl_biomass_ls = EmissionToMtCO2eqSum(lulucf_file_ls,wl_biomass_uid_ls,ctoco2,-1.0)
    print(sum_wl_biomass_ls)
    CO2eq_table_data_ls.append(sum_wl_biomass_ls)
#17. Deadwood
    sum_wl_dead_wood_ls =  EmissionToMtCO2eqSum(lulucf_file_ls,wl_dead_wood_uid_ls,ctoco2,-1.0)
    print(sum_wl_dead_wood_ls)
    CO2eq_table_data_ls.append(sum_wl_dead_wood_ls)
#18. SOM (organic soil)
    sum_wl_som_ls = EmissionToMtCO2eqSum(lulucf_file_ls,wl_som_uid_ls,ctoco2,-1.0)
    print(sum_wl_som_ls)
    CO2eq_table_data_ls.append(sum_wl_som_ls)
#19. 4(II) CH4 and N2O emissions
#CH4
    ch4_ls = EmissionToMtCO2eqSum(lulucf_file_ls,wl_ch4_uid_ls,ch4co2eq,1.0)
#N2O
    n2o_ls = EmissionToMtCO2eqSum(lulucf_file_ls,wl_n2o_uid_ls,n2oco2eq,1.0)
#CH4+N2O
    sum_wl_ch4_n2o_ls = [FormatNumber(SumTwoValues(x,y),'.12f') for (x,y) in zip(ch4_ls,n2o_ls)]
    print(sum_wl_ch4_n2o_ls)
    CO2eq_table_data_ls.append(sum_wl_ch4_n2o_ls)
#Settlements
#20. Biomass
    CO2eq_table_data_ls.append(place_holder_ls)
    sum_sl_biomass_ls = EmissionToMtCO2eqSum(lulucf_file_ls,sl_biomass_uid_ls,ctoco2,-1.0)
    print(sum_sl_biomass_ls)
    CO2eq_table_data_ls.append(sum_sl_biomass_ls)
#21. Deadwood
    sum_sl_dead_wood_ls = EmissionToMtCO2eqSum(lulucf_file_ls,sl_dead_wood_uid_ls,ctoco2,-1.0)
    print(sum_sl_dead_wood_ls)
    CO2eq_table_data_ls.append(sum_sl_dead_wood_ls)
#22. SOM (mineral soil)
    sum_sl_som_ls =  EmissionToMtCO2eqSum(lulucf_file_ls,sl_som_uid_ls,ctoco2,-1.0)
    print(sum_sl_som_ls)
    CO2eq_table_data_ls.append(sum_sl_som_ls)
#23. N mineralisation
    sum_sl_N2O_mineralisation_ls = EmissionToMtCO2eqSum(lulucf_file_ls,sl_N2O_mineralisation_uid_ls,n2oco2eq,1.0)
    print(sum_sl_N2O_mineralisation_ls)
    CO2eq_table_data_ls.append(sum_sl_N2O_mineralisation_ls)
#24. HWP (in CO2)
    sum_hwp_ls = EmissionToMtCO2eqSum(lulucf_file_ls,hwp_CO2_uid_ls,1.0,1.0)
    print(sum_hwp_ls)
    CO2eq_table_data_ls.append(sum_hwp_ls)
#25. Indirect N2O emissions
    sum_N2O_indirect_ls = EmissionToMtCO2eqSum(lulucf_file_ls,N2O_indirect_uid_ls,n2oco2eq,1.0)
    print('---')
    print(sum_N2O_indirect_ls)
    CO2eq_table_data_ls.append(sum_N2O_indirect_ls)
    CO2eq_table_data_ls.append(place_holder_ls)
#End of CreateCO2eqTableData
#---------------------------------------------------------------------------------------------------
#Write data to a file
def WriteCO2eqTableData(start,end,file_name,crf_dir):
    CreateCO2eqTableData(crf_dir)
    separator = '#'
    row_title_ls = GenerateRowTitleList(start,end)
    row_title_ls1 = ["Mt CO2 eq"]+row_title_ls
    column_title_ls = ["4.A Forest land","Biomass, mineral soils","Biomass, organic soils",
                    "DOM+SOM, mineral soils", "DOM+SOM, organic soils", "4(I) N fertilisation",
                    "4(V) Biomass burning", "4(III) N mineralisation", "4(II) CH4 and N2O emissions from drained forest land",
                    "4.B Cropland", "Biomass", "Dead wood", "DOM+SOM, mineral soils", "DOM+SOM organic soils",
                    "4(III) N mineralisation", "4.C Grassland", "Biomass", "Dead wood", "DOM+SOM, mineral soils",
                    "DOM+SOM organic soils", "4(III) N mineralisation", "4(V) Biomass burning", "4.D Wetlands", "Biomass", "Dead wood", "SOM",
                    "4(II) CH4 and N2O emissions", "4.E Settlements", "Biomass", "Dead wood", "SOM", "4(III) N mineralisation",
                    "4.G Harvested wood products", "4(IV) Indirect N2O emissions", "4 Total CO2 eq"]
    if len(CO2eq_table_data_ls) != len(column_title_ls):
        print(len(CO2eq_table_data_ls),len(column_title_ls))
        quit()
    
    f = open(file_name,'w')
    for title in row_title_ls1:
        f.write(title+separator)
    f.write('\n')
    for (title,data_ls) in zip(column_title_ls,CO2eq_table_data_ls):
        f.write(title+separator)
        for data in data_ls:
            f.write(data+separator)
        f.write('\n')
    f.write('\n')
#Sign with the date time
    now = datetime.datetime.now()
    print(str(now))
    f.write("Date produced: "+str(now)+"\n")
    f.write("Data from: "+crf_dir)
    f.close()
    p = pathlib.Path(file_name)
    parent = str(p.parent)+'/'
    stem = p.stem
    excel_file_name=parent+stem+'.xlsx' 
    writer = pd.ExcelWriter(excel_file_name,engine='xlsxwriter')
    row_title_ls = [int(x) for x in row_title_ls]  
    df=pd.DataFrame(CO2eq_table_data_ls,columns=row_title_ls,index=column_title_ls)
    df_float=df.applymap(ConvertFloat)
    df_float.index.name="Mt CO2eq"
    df_float.to_excel(writer,sheet_name='Table-6.1-2')
#End of WriteCO2eqTableData
if __name__ == "__main__":
    start=1990
    end=2015
    file_name='Table-6.1-2.txt'
    WriteCO2eqTableData(start,end,file_name)

    
