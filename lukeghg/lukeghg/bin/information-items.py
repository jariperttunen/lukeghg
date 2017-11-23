#!python
import sys
from xml.etree.ElementTree import ElementTree as ET
from optparse import OptionParser as OP
from lukeghg.crf.uid340to500mapping import MapUID340to500, Create340to500UIDMapping
import string

#Notation Keys in CRFReporter
notation_key_ls = ["IE","NE","NO","NA"]
kp_start_year = 2013
inventory_year = 2015

def SortYearList(year):
    y = year.get('name')
    return int(y)

#Usage: PrettyPrint(t.getroot(),0,"    ")
def PrettyPrint(elem,level=0,space = " "):
    '''Pretty print XML
       Usage: PrettyPrint(t.getroot(),0,"    ")
    '''
    i = "\n" + level*space
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + space
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for e in  elem:
            PrettyPrint(e,level+1,space)
        if not e.tail or not e.tail.strip():
            e.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

#Find and return the data for the uid for the 'year'   
def FindKPLULUCFDataWithUID(t,uid,year):
    it = t.iter('variable')
    variablels = [e for e in it if e.tag=='variable']
    #Find the time series that match the UID
    varls = [var for var in variablels if var.get('uid')==uid]
    if len(varls) == 0:
        print("UID:", uid, "not found, doing nothing",file=sys.stderr)
        not_found_uid_ls.append(uid)
        return uid
    elif len(varls)> 1:
        print("UID:", uid, "not unique, found",len(uidls),"time series, doing nothing",file=sys.stderr)
        return uid
    else:
        #UID found, start retrieving the time series 
        variable=varls[0]
        #This element is a list of length two: a) the time series and b) the comment
        yearscommentls = list(variable)
        #Time series is the first one
        years = yearscommentls[0]
        #The time series is now in a list 
        yearls = list(years)
        #Sort the list in reverse, this KPLULUCF
        yearls.sort(key=SortYearList)
        yearls.reverse()
        #Find the year_record for the current year
        year_record_ls = [x for x in yearls if x.get('name') == year]
        if year_record_ls[0].get('name') == year:
            year_record = year_record_ls[0]
            #A year_record has name and uid attributes, a single value and comment subtrees
            recordls = list(year_record)
            #dump(year_record)
            #Take the record itsels that has the single value and the comment
            record = recordls[0]
            #dump(record)
            #Take the value and the comment
            valuecommentls = list(record)
            #Time series value is the first
            value = valuecommentls[0]
            #dump(value)
            print('Found',uid,year_record.get('name'),value.text)
            return value.text
        
def InsertKPLULUCFDataWithUID(t,uid,year,data):
    it = t.iter('variable')
    variablels = [e for e in it if e.tag=='variable']
    #Find the time series that match the UID
    varls = [var for var in variablels if var.get('uid')==uid]
    if len(varls) == 0:
        print("UID:", uid, "not found, doing nothing")
        return uid
    elif len(varls)> 1:
        print("UID:", uid, "not unique, found",len(uidls),"time series, doing nothing")
        return uid
    else:
        #UID found, start retrieving the time series 
        variable=varls[0]
        #This element is a list of length two: a) the time series and b) the comment
        yearscommentls = list(variable)
        #Time series is the first one
        years = yearscommentls[0]
        #The time series is now in a list 
        yearls = list(years)
        #Sort the list in reverse, this is KP and last years become first
        yearls.sort(key=SortYearList)
        yearls.reverse()
        #Find the year_record for the given year
        year_record_ls = [x for x in yearls if x.get('name') == year]
        if year_record_ls[0].get('name') == year:
            year_record = year_record_ls[0]
            #A year_record has name and uid attributes, a single value and comment subtrees
            recordls = list(year_record)
            #dump(year_record)
            #Take the record itsels that has the single value and the comment
            record = recordls[0]
            #dump(record)
            #Take the value and the comment
            valuecommentls = list(record)
            #Time series value is the first
            value = valuecommentls[0]
            value.text = str(data)
            #dump(value)
            print(uid,year_record.get('name'),'<----',value.text)

def GenerateAndInsertInformationItem(t,message,target_uid,source_uidls):
    #Generate  information items for Deforestation
    print('------------------------------------------------------------')
    print(message)
    nk_set=set()
    #kp_start_year and inventory_year are defined in the beginning of the file as global variables in this file
    for year in range(kp_start_year,inventory_year+1):
        sum=0.0
        for uid in source_uidls:
            data = FindKPLULUCFDataWithUID(t,uid,str(year))
            #If no data --> error
            if data is None:
                print(uid, "No Data (Data is None)",file=sys.stderr)
            elif data in notation_key_ls:
                #Collect all notation keys
                nk_set.add(data)
            #The last option is a number
            else:
                sum = sum+float(data)
        #If there is a sum, value must be different from zero
        if sum != 0:
            #Rounding to six decimals
            sum = float(format(sum,'.6f'))
            #print(target_uid,"<-------",str(sum))
            InsertKPLULUCFDataWithUID(t,target_uid,str(year),str(sum))
        #If the list of notation keys is not empty
        elif nk_set:
            nk_ls = list(nk_set)
            #print(nk_ls)
            #There is at least one element
            nk_first=nk_ls.pop(0) 
            #Append the rest of the notation keys to the first one
            for nk in nk_ls:
                nk_first=nk_first+','+nk
            #print(target_uid,"<-------",str(nk_first))
            InsertKPLULUCFDataWithUID(t,target_uid,str(year),str(nk_first))
        #This is error, no values, no notation keys
        else:
            print(target_uid,"Information item has no values") 
        print('------------------------------------------------------------')
    
#Listing for information items in 4(KP)-->KP.A Article 3.3 Activities->Activity A.2
#Forest land vs AR_under_D (reforestation of deforested area)
#Forest land, region 1 and 2, mineral, organic, above, gains
uid_ard_r1_above_gains='36C7F909-72A6-4CA8-B3A2-AAC412EDBC20'#old UID '022ECC7E-FD75-4EDC-AEB9-48C09AD4DFF0'
uid_ard_r2_above_gains='92994FFD-B00E-48A4-90E5-25AD40AC7239'#old UID 'D7ACD658-D320-4AB5-BCCC-1AC624DF1980'
uid_ard_r1r2_above_gains_ls = [uid_ard_r1_above_gains,uid_ard_r2_above_gains]
uid_fl_above_gains_info='40640AB0-D6E0-4745-983F-6599A013E5B5'
#Forest land, region 1 and 2, mineral, organic, above, losses
uid_ard_r1_above_losses='686F7370-16F8-46F2-9A29-03BEA9CFA5AB'#'270886C3-4190-48EA-B8BD-935A4FF9A38E'
uid_ard_r2_above_losses='46955778-120C-4AE0-A99F-0B4983906CA7'#'2C11925A-7BE3-440A-A7A7-B720CA0E7955'
uid_ard_r1r2_above_losses_ls=[uid_ard_r1_above_losses,uid_ard_r2_above_losses]
uid_fl_above_losses_info='1EBE9478-B389-4825-B902-887B5489D4AE'
#Forest land, region 1 and 2, mineral, organic, below, gains
uid_ard_r1_below_gains='2FA33D1B-5260-450C-8B7A-F376DE8DCC79'#'C89E9973-1590-431F-9A2F-D684B38C3692'
uid_ard_r2_below_gains='F0D34731-A05E-49CD-9A25-05A3E0179786'#'9803C414-CBAC-4C84-B595-5BEADC4420FB'
uid_ard_r1r2_below_gains_ls=[uid_ard_r1_below_gains,uid_ard_r2_below_gains]
uid_fl_below_gains_info='DC2DA7BD-B554-49DE-9C5F-A0C91ADE3A0F'
#Forest land, region 1 and 2, mineral, organic, below, losses
uid_ard_r1_below_losses='2EFC886C-DABE-4602-910E-5129E7C262F1'#'9A766888-513B-4599-ABAF-55CA56BA8BF2'
uid_ard_r2_below_losses='7F203F77-E0E4-4A4E-94CB-FE0D0DEFAE9D'#'695255FB-EAAA-4377-947A-E935C2EDBFBC'
uid_ard_r1r2_below_losses_ls=[uid_ard_r1_below_losses,uid_ard_r2_below_losses]
uid_ard_fl_below_losses_info='BC887DE2-7D60-477A-A5BD-F79596CDDCC7'
#Forest land, region 1 and 2, mineral, organic, net carbon change litter
uid_ard_r1_litter='23926412-58AE-45AB-8934-9ABF639FF413'#'BB5683A9-76CC-46A1-9FC5-A874C554F88F'
uid_ard_r2_litter='600544D5-2F89-4B2A-A0E4-6EC155068C02'#'2EF6EE50-EDFE-4B2E-BB06-51879958D442'
uid_ard_r1r2_litter_ls=[uid_ard_r1_litter,uid_ard_r2_litter]
uid_ard_fl_litter_info='8D0B9FFD-D5E5-4A02-8826-98E2BD48F685'
#Forest land, region 1 and 2, mineral, organic, net carbon change dead wood
uid_ard_r1_dead_wood='E2D6815C-759C-4309-AED8-825DBC8720CA'#'6C454D9E-9AB3-4CBB-A011-ADE762C61EBB'
uid_ard_r2_dead_wood='FB58EDFC-0A09-4501-BCAE-D42324C65B0F'#'AA033662-1BE9-4373-A944-55579639799C'
uid_ard_r1r2_dead_wood_ls=[uid_ard_r1_dead_wood,uid_ard_r2_dead_wood]
uid_ard_fl_dead_wood_info='4839EF6D-4390-4AF9-93A2-B0F0E30256F6'
#Forest land, region 1 and 2, mineral, net carbon stock change soils
uid_ardmin_r1_soil='293F9495-1F72-489D-9DC6-7BC7E514A977'#'E2AAB52E-FCB5-43DC-9403-E25A88ECA215'
uid_ardmin_r2_soil='950BB73B-00CA-4A1C-9C0A-4003DF64C959'#'5B933A58-95C4-4E63-9614-00578C9A741C'
uid_ardmin_r1r2_soil_ls=[uid_ardmin_r1_soil,uid_ardmin_r2_soil]
uid_ardmin_fl_soil_info='94562EAF-7A35-4C09-BFC1-F6752097F2EE'
#Forest land, region 1 and 2, organic, net carbon stock change soils
uid_ardorg_r1_soil='4E3763D4-672B-4CFB-9953-4BA0E6C14105'#'6E9BB5FE-1E42-4064-9386-E0755CF80755'
uid_ardorg_r2_soil='93A8A5C7-4388-4D52-970E-9512746AC7DC'#'ECC0E131-52A0-475F-AA4E-B8C775DEF2B0'
uid_ardorg_r1r2_soil_ls=[uid_ardorg_r1_soil,uid_ardorg_r2_soil]
uid_ardorg_fl_soil_info='00078940-8C75-4B04-BCDC-43E55DEBCD56'
#Cropland, region 1 and 2, mineral, organic, above, gains
#uid_clmin_r1_above_gains='671A277A-625C-44AC-A497-2C1E63BAF6D5'
uid_cl_r1_above_gains='1092A04E-B1BF-4C05-83C8-04FFB916294F'
uid_cl_r2_above_gains='E15434EB-2BD7-4CB5-9CE1-06595063A54B'
#uid_clmin_r2_above_gains='567AB66B-EDF8-44E8-A8D6-02E8EDA393EE'
#uid_clorg_r1_above_gains='3220F765-7E97-422B-A2AB-82FE59528B91'
#uid_clorg_r2_above_gains='9751219B-B84C-47F4-B3B5-698EEAEE9A65'
uid_cl_above_gains_ls = [uid_cl_r1_above_gains,uid_cl_r2_above_gains]
uid_cl_r12_above_gains_info='4FF801BB-1B23-4E3E-BF5F-956E6F9163AF'
#Cropland, region 1 and 2, mineral, organic, below, gains
uid_cl_r1_below_gains='85C0194D-AB7D-454C-B080-9FFA119F626B'
uid_cl_r2_below_gains='1B759BDE-4F35-4AC1-B1A0-260D36940D87'
#uid_clmin_r1_below_gains='2B0EA5A2-3B44-4027-B030-BA975A70C691'
#uid_clmin_r2_below_gains='F2AFA406-45A9-4474-8DFA-6793DF8DB360'
#uid_clorg_r1_below_gains='8380F027-E54B-4608-B1DD-007ACB359BAE'
#uid_clorg_r2_below_gains='39CAB127-B786-4882-9D56-70EEE76F5CAE'
uid_cl_below_gains_ls = [uid_cl_r1_below_gains,uid_cl_r2_below_gains]
uid_cl_r12_below_gains_info='C9DB1E1C-33DF-4A28-BB4B-CF3252882CAA'
#Cropland, region 1 and 2, mineral, organic, above, losses
uid_cl_r1_above_losses='1859E602-E330-48AF-82AB-45E927255542'
uid_cl_r2_above_losses='0EFFF519-BC85-4B1F-B3B8-D554D37B75DA'
#uid_clmin_r1_above_losses='DD40F765-844B-4D0C-B825-DADD0DB1D72E'
#uid_clmin_r2_above_losses='C8ACEF59-0FAA-4E7F-B40A-75F12DBBF1FD'
#uid_clorg_r1_above_losses='602550EF-E5F8-4134-B3DD-166F82BB729B'
#uid_clorg_r2_above_losses='AA2A84B4-E96F-48CA-AE10-06A0BE6ABD4D'
uid_cl_above_losses_ls = [uid_cl_r1_above_losses,uid_cl_r2_above_losses]
uid_cl_r12_above_losses_info='D0DD0BC4-5481-4510-AD99-4331AE340632'
#Cropland, region 1 and 2, mineral, organic, below, losses
uid_cl_r1_below_losses='6399C1C3-7EA2-45C1-8A14-EDA50EFCA608'
uid_cl_r2_below_losses='EE8D457A-CD37-4D90-81E8-EA28078337C7'
#uid_clmin_r1_below_losses='B3E1EAAB-23F2-42C8-9385-AC8F343B101D'
#uid_clmin_r2_below_losses='553CCA31-14B8-4D48-B956-F182B48F68B4'
#uid_clorg_r1_below_losses='9F9FDE69-6C62-4B9C-87DB-47DBEB8CFD43'
#uid_clorg_r2_below_losses='4056D66E-381B-43F0-88F3-D31284D0C552'
uid_cl_below_losses_ls = [uid_cl_r1_below_losses,uid_cl_r2_below_losses]
uid_cl_r12_below_losses_info='5D2F8254-8534-4B8D-BF13-BE807508877B'
#Cropland, region 1 and 2, net carbon stock change in litter
uid_cl_r1_litter='B2192137-8C89-40AC-90D1-6C133E7B7607'
uid_cl_r2_litter='51CFF739-E93E-492A-AB44-7E9D70AFD007'
#uid_clmin_r1_litter='C87E42F0-2B78-4CE7-8A62-BA314994E23D'
#uid_clmin_r2_litter='AC749AD2-54A3-4CC2-9FA7-914AE2E92702'
#uid_clorg_r1_litter='F62A09F7-CCEB-45CF-B727-D5751D88AACF'
#uid_clorg_r2_litter='D399E3BF-7DD7-4D96-B062-816F836A5D08'
uid_cl_litter_ls=[uid_cl_r1_litter,uid_cl_r2_litter]
uid_cl_r12_litter_info='7ACD801F-9315-4FB4-80EC-B0EB6FB9FA2E'
#Cropland, region 1 and 2, net carbon stock change in dead wood
uid_cl_r1_dead_wood='6A4ED694-1E41-4805-948C-EA05E942BE23'
uid_cl_r2_dead_wood='0F10FF29-FC19-42DB-B3FA-1E581064FE23'
#uid_clmin_r1_dead_wood='E9251E47-ED34-49D4-A86F-6E28AF8012AF'
#uid_clmin_r2_dead_wood='6739EAAE-8B08-4EA4-AC9A-D0E0E7B08BD0'
#uid_clorg_r1_dead_wood='D77C2A94-6CC2-43E4-B151-EB1583306B8D'
#uid_clorg_r2_dead_wood='4F82D126-9EA8-4C15-A2F2-2964685A2CD4'
uid_cl_deadwood_ls=[uid_cl_r1_dead_wood,uid_cl_r2_dead_wood]
uid_cl_r12_dead_wood_info='F8CA44FA-9F75-4457-9D49-51FE88CEEBDE'
#Cropland, , region 1 and 2, mineral, net carbon stock change in soils
uid_clmin_r1_net_change_soils='02280693-172D-4715-9705-5C4B8152D788'#'179A45A7-F794-4ACE-B766-31A6BEEC2CED'
uid_clmin_r2_net_change_soils='D139BFED-F714-4386-9F83-7D8A56A18FFA'#'0C769DF7-73B6-4C4F-A638-DBC63C6A6C58'
uid_clmin_net_change_soils_ls=[uid_clmin_r1_net_change_soils,uid_clmin_r2_net_change_soils]
uid_clmin_r1r2_net_change_soils_info='F26F3915-EC0A-4F5B-B7B3-242DB1BD89C5'
#Cropland, , region 1 and 2, organic, net carbon stock change in soils
uid_clorg_r1_net_change_soils='69B462FE-F685-48FD-AC5C-B285CD601448'#'F11BD0CE-D637-4D2B-8C7E-01137B77B57D'
uid_clorg_r2_net_change_soils='80B45284-C600-4CFF-BD2A-F4DFDF732DD1'#'4D8A0F1F-9308-48D4-83A4-DCF36DD586DB'
uid_clorg_net_change_soils_ls=[uid_clorg_r1_net_change_soils,uid_clorg_r2_net_change_soils]
uid_clorg_r1r2_net_change_soils_info='33A02248-EBF8-4995-B52F-A19D1C73FF54'
#Grassland, region 1 and 2, mineral, organic, above, gains
uid_gl_r1_above_gains='97A0E1D8-391B-4CC1-9F2C-1A1A82957D08'
uid_gl_r2_above_gains='F116DC9B-CBCD-4C7A-A7CE-5F8E368DEA22'
#uid_glmin_r1_above_gains='4D0E9269-0FE8-41E3-88B6-4F1615332E13'
#uid_glmin_r2_above_gains='CFE9F418-E6E4-4FA0-AB9C-47B4A9E1827C'
#uid_glorg_r1_above_gains='94ED0E9D-FB26-4594-8A44-A10F132EFA0A'
#uid_glorg_r2_above_gains='F9A4390E-A700-40DC-803F-1326777C5096'
uid_gl_above_gains_ls=[uid_gl_r1_above_gains,uid_gl_r2_above_gains] 
uid_gl_r12_above_gains_info='680EECAB-9E3E-463F-8058-5876A4C25361'
#Grassland, region 1 and 2, mineral, organic, below, gains
uid_gl_r1_below_gains='12DEB3CB-227C-4590-8913-04BD725A4F1D'
uid_gl_r2_below_gains='992EDCE3-DF75-42DF-B949-F24663068DEF'
#uid_glmin_r1_below_gains='2A65DFEA-8C66-45B0-A326-9B02D07B87A9'
#Corrected UID for uid_gl_r2_below_gains
#uid_glmin_r2_below_gains='9552C636-F52A-481B-AE88-8E406F4E05B5'
#uid_glorg_r1_below_gains='60255701-414B-4E06-B4F7-CEB818A9C610'
#Corected UID for uid_glorg_r2_below_gains
#uid_glorg_r2_below_gains='1FC5AC48-6359-437C-994F-454DD3F42BF2'
uid_gl_below_gains_ls=[uid_gl_r1_below_gains,uid_gl_r2_below_gains]
uid_gl_r12_below_gains_info='C5DF3DBB-2E5A-4FDA-B6ED-D4FC79F51284'
#Grassland, region 1 and 2, mineral, organic, above, losses
uid_gl_r1_above_losses='15F6102D-94C0-4A48-AC02-FE75DA0D9FBC'
uid_gl_r2_above_losses='BECE24B4-BC2F-434E-ABB7-46F5CB26B6AB'
#uid_glmin_r1_above_losses='1AA1D01F-1AF9-4AA8-9720-DF05D491E0F1'
#uid_glmin_r2_above_losses='AA4BAFA8-9B89-46F2-A537-3C8B6BA538B0'
#uid_glorg_r1_above_losses='C56F8B65-E071-4CF2-8EA8-3A457497D6BD'
#uid_glorg_r2_above_losses='4C88ECCF-F02D-4F0A-A7C4-DDE3495690A3'
uid_gl_above_losses_ls = [uid_gl_r1_above_losses,uid_gl_r2_above_losses]
uid_gl_r12_above_losses_info='1943D2D5-9AF9-4F96-BB6C-1A8F0944862E'
#Grassland, region 1 and 2, mineral, organic, below, losses
uid_gl_r1_below_losses='1D0D09FF-8900-475E-B68B-11B012F0AF38'
uid_gl_r2_below_losses='90FEFA5A-04D4-4E63-B6CC-57F21EEB8AD2'
#uid_glmin_r1_below_losses='0D724687-0F8F-4342-8523-B6809F4607BE'
#uid_glmin_r2_below_losses='9B8D0422-F953-4758-B55F-F556C52FF8BF'
#uid_glorg_r1_below_losses='EECCF337-DD00-43DF-8245-37C3FC768F84'
#uid_glorg_r2_below_losses='16530123-0011-4B30-AF8E-6848410E8693'
uid_gl_below_losses_ls = [uid_gl_r1_below_losses,uid_gl_r2_below_losses]
uid_gl_r12_below_losses_info='C8B90368-BD16-4A80-A44D-BCA4B7B3BF96'
#Grassland, region 1 and 2, net carbon stock change in litter
uid_gl_r1_litter='5C17F31B-07D1-4488-8A38-0AACB3794DA3'
uid_gl_r2_litter='74A26CDA-F634-41DC-B062-79CD1023F290'
#uid_glmin_r1_litter='5BA8C1E4-78A6-421B-9966-F453F7AC01C5'
#uid_glmin_r2_litter='FC188AA5-5712-43B8-BCE5-FCD5F9D4F387'
#uid_glorg_r1_litter='ADE7ED30-5202-4646-9992-935A9D849507'
#uid_glorg_r2_litter='37FDB853-49C1-42FF-9588-A0E39391BF82'
uid_gl_litter_ls=[uid_gl_r1_litter,uid_gl_r2_litter]
uid_gl_r12_litter_info='3369D3AA-CD2E-4285-84A7-6A3BFC839E21'
#Grassland, region 1 and 2, net carbon stock change in dead wood
uid_gl_r1_dead_wood='30B07E32-2B43-44AF-8012-9E7E037D5F5E'
uid_gl_r2_dead_wood='E5019B9C-9379-48AC-BA24-813863288203'
#uid_glmin_r1_dead_wood='2682C345-67F4-4D04-9655-D67FE1B90F44'
#uid_glmin_r2_dead_wood='D7750D3D-36E9-4235-A723-8F836A9D8205'
#uid_glorg_r1_dead_wood='432A0A5B-767C-4BC3-A639-2179C3AE5409'
#uid_glorg_r2_dead_wood='DD49F575-6ACE-4063-91F6-BB442B271CB0'
uid_gl_dead_wood_ls=[uid_gl_r1_dead_wood,uid_gl_r2_dead_wood]
uid_gl_r12_dead_wood_info='C64A7027-05C1-4B19-BB9D-5E306E92934C'
#Grassland,  region 1 and 2, mineral, net carbon stock change in soils
uid_glmin_r1_net_change_soils='1E45B590-25AE-496D-AD6D-D432EA02A1C7'#'38A7E575-EE83-48B7-9923-B81CCAEC5EBF'
uid_glmin_r2_net_change_soils='4DF3265C-FB92-4617-90B6-61B151B8C6B4'#'1A685A7B-9083-482E-A3F6-9BF6B61907DA'
uid_glmin_net_change_soils_ls=[uid_glmin_r1_net_change_soils,uid_glmin_r2_net_change_soils]
uid_glmin_r1r2_net_change_soils_info='825D40BA-1DF2-4230-8862-C5D73D6D2580'
#Grassland,  region 1 and 2, organic, net carbon stock change in soils
uid_glorg_r1_net_change_soils='157DBC0C-3C2C-4F20-B640-49FC7DC0CC98'#'B2171886-CEDE-417E-A1B4-B4EF9A35FF0B'
uid_glorg_r2_net_change_soils='26F2BDB2-3D26-4905-91DE-D8E2664129C5'#'C4534C15-3628-4EEF-AEE1-44DA87DFB955'
uid_glorg_net_change_soils_ls=[uid_glorg_r1_net_change_soils,uid_glorg_r2_net_change_soils]
uid_glorg_r1r2_net_change_soils_info='1994BBC1-2211-4F06-98B6-75039BB22EEC'
#Settlement, region 1 and 2, above, gains
uid_sett_r1_above_gains='348EE250-C274-4A29-8F4A-7E445E40074D'#'82B6455F-D28F-4425-8989-4C4E65720DA7'
uid_sett_r2_above_gains='7E12718A-9B5E-48F2-AB1F-C13A4CA044C6'#'08C2F880-B084-450A-9012-FAF3BB3ADAC5'
uid_sett_above_gains_ls = [uid_sett_r1_above_gains,uid_sett_r2_above_gains]
uid_sett_r12_above_gains_info='9A73A1DC-09E6-4F39-8514-74EED9C272B5'
#Settlement, region 1 and 2, below, gains
uid_sett_r1_below_gains='7116F5B6-C676-4107-ABE3-6C9917902F38'#'CAA2A23B-9910-4931-B6E0-2B9F1B26D4E4'
uid_sett_r2_below_gains='16F0E281-C000-4D36-8C29-FB638FC7E987'#'AA35182B-59BF-48FE-B650-CFE4A67957CF'
uid_sett_below_gains_ls = [uid_sett_r1_below_gains,uid_sett_r2_below_gains]
uid_sett_r12_below_gains_info='BFD9CA04-4FF8-40A8-A4F2-3D743E9D5D63'
#Settlement, region 1 and 2, above, losses
uid_sett_r1_above_losses='75C15A00-35F1-4BF9-AA86-BD2EC4865E1C'#'56643959-5F16-4E77-A984-B9311D159DF9'
uid_sett_r2_above_losses='C062CF87-88E3-42BA-A894-959E59648843'#'A5D572F9-03E6-470C-9352-5E921555A1AE'
uid_sett_above_losses_ls = [uid_sett_r1_above_losses,uid_sett_r2_above_losses]
uid_sett_r12_above_losses_info='B180DFC1-0959-4F2F-839D-122F8BCE7FDA'
#Settlement, region 1 and 2, below, losses
uid_sett_r1_below_losses='47AE06F6-EB49-45E8-BAD1-8F42786D73C9'#'931A782A-23BF-47C4-9059-D46A1B446632'
uid_sett_r2_below_losses='113C47E2-633A-4DC2-AF35-A446D5D6A2CA'#'ECC11019-D28B-4524-8A40-9AFC0E68EDD0'
uid_sett_below_losses_ls = [uid_sett_r1_below_losses,uid_sett_r2_below_losses]
uid_sett_r12_below_losses_info='987FB906-AEA4-4090-8EB6-B26F033D27B8'
#Settlement, region 1 and 2, carbon stock change in litter
uid_sett_r1_litter='7A1326A0-EF6B-465A-8C79-5DFB1477F00B'#'9DC2DF91-C1E3-4ED5-9EFC-89E894F9C2BE'
uid_sett_r2_litter='5E01AF86-9C33-4E48-8E46-05C037CBF062'#'1AE91C4F-CBA3-4E7C-B8D0-B974BB3B3D8E'
uid_sett_litter_ls=[uid_sett_r1_litter,uid_sett_r2_litter]
uid_sett_r1r2_litter_info='ED9A3A77-FCE9-4F8F-856D-B013DFCE02C6'
#Settlement, region 1 and 2, carbon stock change in dead wood
uid_sett_r1_dead_wood='02AAC03B-212E-47D6-A207-9A8296371228'#'309685E4-C1A9-47E7-80A5-175CCD0D11C4'
uid_sett_r2_dead_wood='FBF9EA03-2942-4537-A453-9FED7530E864'#'E6B81C41-4F29-4F38-B044-A5284C4F2EB1'
uid_sett_dead_wood_ls=[uid_sett_r1_dead_wood,uid_sett_r2_dead_wood]
uid_sett_r1r2_dead_wood_info='F91E3D3D-6B7E-4E60-81E3-28D8D14CC016'
#Settlement,  region 1 and 2, mineral, net carbon stock change in soils
uid_settmin_r1_net_change_soils='6A467795-0205-4AD3-A962-AE09F218E318'#'1CE81FDB-2F8D-43B2-9C1B-03741700AB74'
uid_settmin_r2_net_change_soils='FAB5A274-2A71-49E0-BA8D-60BD30A07A5A'#'36E6ACAF-E091-4057-8E52-3FE0B3A4FFA0'
uid_settmin_net_change_soils_ls=[uid_settmin_r1_net_change_soils,uid_settmin_r2_net_change_soils]
uid_settmin_r1r2_net_change_soils_info='E364A539-ABCF-4F78-9C71-FD9D058FC859'
#Settlement,  region 1 and 2, organic, net carbon stock change in soils
uid_settorg_r1_net_change_soils='BAC5033D-F9AB-4EFA-9C17-2CF1D9C6D48D'#'13147F6F-A99A-402B-9FA1-EEBA44AFC415'
uid_settorg_r2_net_change_soils='2FC6A389-6D81-41BE-8852-FAE354AEF040'#'18DF3025-CC90-4284-B7C1-7A92D1FA2F93'
uid_settorg_r1r2_net_change_soil_ls=[uid_settorg_r1_net_change_soils,uid_settorg_r2_net_change_soils]
uid_settorg_r1r2_net_change_soils_info='5D77B4FA-4F37-4600-BC31-66A88EA7E849'
#Wetlands,  region 1 and 2, mineral, organic, above, gains
#1) Wetlands-peatland
uid_wlpeat_r1_above_gains='271F3F27-ED5C-46F6-AA48-35E944F35056'#'12547D4B-C427-4AC1-915F-FEC71AC8BE9F'
uid_wlpeat_r2_above_gains='B522F313-7CA3-4707-9EEA-BE03A850C5EA'#'A52AE22D-23AD-4C3C-90E0-6A8CF34495FF'
#2) Wetlands-peat_extraction
uid_wlpeat_extraction_r1_above_gains='E60E60FC-B246-466C-AF6D-D37113B91CEA'#'48BD74B9-57E5-4169-8071-0DA7DDB594FD'
uid_wlpeat_extraction_r2_above_gains='E03B5B32-A72D-4F41-836D-4A217D51D788'#'774E3784-E3B5-4486-8C15-E30BC272340A'
#3) Wetlands-inland_waters
uid_wlwaters_r1_above_gains='8DB64174-7BE5-4184-950F-C59B7FF8F3B8'#'03795D1B-86C8-4FA1-B10F-D285D95122F1'
uid_wlwaters_r2_above_gains='7491E95B-712C-4FCF-81AF-4878E57F8DF2'#'F796FBC2-D0CF-4465-AA74-7FA11C51865A'
uid_wl_above_gains_ls = [uid_wlpeat_r1_above_gains,uid_wlpeat_r2_above_gains,
                         uid_wlpeat_extraction_r1_above_gains,uid_wlpeat_extraction_r2_above_gains,
                         uid_wlwaters_r1_above_gains,uid_wlwaters_r2_above_gains]
uid_wl_r12_above_gains_info='F300A063-CF92-44E9-9B17-FB45D2E54F67'
#Wetlands,  region 1 and 2, mineral, organic, below, gains
#1) Wetlands-peatland
uid_wlpeat_r1_below_gains='855426D2-EE23-419A-A479-04CD51F9C37A'#'AD16BE17-CC6D-4A07-8EDE-23831E2D28F5'
uid_wlpeat_r2_below_gains='DE46842C-F8D1-4D0F-BF2F-C402E6A23944'#'A52AE22D-23AD-4C3C-90E0-6A8CF34495FF'
#2) Wetlands-peat_exraction
uid_wlpeat_extraction_r1_below_gains='D3354B5C-8727-448F-812C-9210929C2BBE'#'6502DD2E-D840-47EF-A9F2-F5C807DE2E67'
uid_wlpeat_extraction_r2_below_gains='216F9FD2-6669-449F-A390-25DDFDD66743'#'4B54719C-A21D-4E31-82EE-61F9B6F48D34'
#3) Wetlands-inland_waters
uid_wlwaters_r1_below_gains='AA19980B-357B-4C94-9C33-D88183DA37FA'#'056DA5E8-0991-4D78-B0C4-48F0B4E99D3B'
uid_wlwaters_r2_below_gains='C6F9EF13-EC7D-4227-B96B-51F7941C9641'#'9B4AFA5E-F4CE-4EE8-8FCC-E95187556905'
uid_wl_below_gains_ls = [uid_wlpeat_r1_below_gains,uid_wlpeat_r2_below_gains,
                         uid_wlpeat_extraction_r1_below_gains,uid_wlpeat_extraction_r2_below_gains,
                         uid_wlwaters_r1_below_gains,uid_wlwaters_r2_below_gains]
uid_wl_r12_below_gains_info='4634871A-F878-41CA-A439-11FE7F5AEE98'
#Wetlands,  region 1 and 2, mineral, organic, above, losses
#1) Wetlands-peatland
uid_wlpeat_r1_above_losses='83828340-6726-41AC-A41F-15B53854C936'#'D61138A0-4630-482F-8F69-EA8D2E76D504'
uid_wlpeat_r2_above_losses='FDD18FE4-D813-49E4-9D5C-879585A1712E'#'01F1F5E1-281C-4FB9-BDAC-2E32EBD1382D'
#2) Wetlands-peat_extraction
uid_wlpeat_extraction_r1_above_losses='E7A0A4E4-5C9D-4E37-9988-2F708E713D3C'#'16B11D57-2B8A-4B4A-8670-6BB50501C862'
uid_wlpeat_extraction_r2_above_losses='1B457F4E-1BE7-46E1-BD0D-8C922FF1615D'#'57A00FAC-9092-4857-A6CA-3809A5B508A7'
#3) Wetlands-inland_waters
uid_wlwaters_r1_above_losses='66C5F2D8-09F8-4460-A1D9-DC6C95D4FB3E'#'93EB674F-71D7-4C74-95A7-966F723CF2B8'
uid_wlwaters_r2_above_losses='B17E2D36-15D3-4FB6-9C2E-3B6FFC5935D5'#'80827FF4-7151-45DD-845A-55068BF0A277'
uid_wl_above_losses_ls = [uid_wlpeat_r1_above_losses,uid_wlpeat_r2_above_losses,
                          uid_wlpeat_extraction_r1_above_losses,uid_wlpeat_extraction_r2_above_losses,
                          uid_wlwaters_r1_above_losses,uid_wlwaters_r2_above_losses]
uid_wl_r12_above_losses_info='2788C746-2194-4649-A857-99A3EAC34EE2'
#Wetlands,  region 1 and 2, mineral, organic, below, losses
#1) Wetlands-peatland
uid_wlpeat_r1_below_losses='0E7BC0AE-D6DD-4A4C-8028-4BFC3E74CFE0'#'D0E7CAD6-BC0E-41EF-8EF1-8D718DBF0F80'
uid_wlpeat_r2_below_losses='2B6D1146-5701-46FE-A104-84AFF04E65D9'#'9FFA2649-B21C-49FC-8536-1373DA3CE8BB'
#2) Wetlands-peat_extraction
uid_wlpeat_extraction_r1_below_losses='D61444DC-8E2E-4D61-BD36-83FE47D966F4'#'158B48C3-540D-4840-AFEA-A01F374108C5'
uid_wlpeat_extraction_r2_below_losses='92CD8840-F8B5-429A-BC1B-DFAD9E74A491'#'27C75E19-8641-4655-A74A-277EFD7520D5'
#3) Wetlands-inland_waters
uid_wlwaters_r1_below_losses='0F7E9198-B6C2-4E31-BFE0-CF1C722863CA'#'4D2849CC-09A4-4958-B327-28636EE672A6'
uid_wlwaters_r2_below_losses='B10BC694-178E-42C0-B5EB-E295C0FE29FE'#'320CCC74-53D8-4B31-8D8D-C3AC30519B3F'
uid_wl_below_losses_ls = [uid_wlpeat_r1_below_losses,uid_wlpeat_r2_below_losses,
                          uid_wlpeat_extraction_r1_below_losses,uid_wlpeat_extraction_r2_below_losses,
                          uid_wlwaters_r1_below_losses,uid_wlwaters_r2_below_losses]
uid_wl_r12_below_losses_info='0CFBA830-8824-4A74-8E0A-DA455181C7B6'
#Wetlands, region 1 and 2, mineral, organic, net change in litter
#1) Wetlands-peatland
uid_wlpeat_r1_litter='58AF7727-B5F0-4431-AE28-B80CF362CAE1'#'F7CC44CD-5A8A-40E8-9485-3BA05776D08C'
uid_wlpeat_r2_litter='0FC0D375-9F6A-4934-90BB-3D5E222A4D91'#'13941E2D-6DF4-4A67-8BCC-DA6CD0BFB465'
#2) Wetlands-peat_extraction
uid_wlpeat_extraction_r1_litter='AEA34728-E4A5-4A07-A46E-4B0307828378'#'ABC7C1C8-CB7D-4D34-BB0A-8F28227260C4'
uid_wlpeat_extraction_r2_litter='2489CE79-E62E-4894-B205-2768E63EB998'#'B92A654B-169A-4172-A86A-5C1A3C59C686'
#3) Wetlands-inland_waters
uid_wlwaters_r1_litter='7E8B9ABA-DC18-453D-AAA1-38344C8113A2'#'AF9679BD-4993-45EF-9FFA-8B1E7730E6A9'
uid_wlwaters_r2_litter='986930D1-7264-40BB-BE16-2750CADE8BFD'#'5643C294-523D-41F2-84FA-AD7BE97828E6'
uid_wl_litter_ls = [uid_wlpeat_r1_litter,uid_wlpeat_r2_litter,
                    uid_wlpeat_extraction_r1_litter,uid_wlpeat_extraction_r2_litter,
                    uid_wlwaters_r1_litter,uid_wlwaters_r2_litter]
uid_wetland_litter_info='BC31ED17-28E3-4FFC-A08F-564BEA09245B'
#Wetlands, region 1 and 2, mineral, organic, net change in dead wood
#1) Wetlands-peatland
uid_wlpeat_r1_dead_wood='7B2C94C5-832D-4D00-9FFA-817097C324C7'#'0F638458-CE2A-4D1B-80AF-6B22378B1979'
uid_wlpeat_r2_dead_wood='6BCE4E11-A1A5-4EA8-BC7B-AB70EC865CA8'#'6BC0A7EC-4CF9-4A0A-8C5B-480D068D156A'
#2) Wetlands-peat_extraction
uid_wlpeat_extraction_r1_dead_wood='1CB9E9ED-1239-4D28-BED8-433E4775653C'#'6EF895D5-4539-4FED-9615-DBF90FDA88DE'
uid_wlpeat_extraction_r2_dead_wood='2129D5E7-7DDF-4D66-94FB-5945561F1D61'#'F2615B2F-6637-4047-B167-546087945AF9'
#3) Wetlands-inland_waters
uid_wlwaters_r1_dead_wood='E0FF70DF-164F-481D-BD1E-0384F2310A33'#'FD057AAC-5318-4C37-B967-A60A0222C4CD'
uid_wlwaters_r2_dead_wood='72C9178F-F8DF-4645-BBBC-64AA8C0D6866'#'9B466EEC-B0F3-489E-8D0F-AE493168A5F4'
uid_wl_dead_wood_ls=[uid_wlpeat_r1_dead_wood,uid_wlpeat_r2_dead_wood,
                     uid_wlpeat_extraction_r1_dead_wood,uid_wlpeat_extraction_r2_dead_wood,
                     uid_wlwaters_r1_dead_wood,uid_wlwaters_r2_dead_wood]
uid_wetland_dead_wood_info='A827495A-A62A-4C88-B02D-03846EFF03C1'
#Wetlands, region 1 and 2, mineral, net change in soils
#1) Wetlands-peatland
uid_wlpeatmin_r1_soil='DEFD3DA9-F18B-43A8-A1D1-209AADF1BD6B'#'7CC18324-9D8E-4BA0-A1C9-4109E3AECA8F'
uid_wlpeatmin_r2_soil='7B5A32D1-D448-42E5-9071-D28F799AF05A'#'091970D0-3C53-42FD-9C80-44555D29013F'
#2) Wetlands-peat_extraction
uid_wlpeat_extraction_min_r1_soil='0D586F94-97F4-4D75-9CF4-E099E3B2863B'#'998D4387-57E9-4F37-8F17-DE009859100F'
uid_wlpeat_extraction_min_r2_soil='64079418-23D3-4B0F-BF66-43886E96DE41'#'6D7ADF2F-9234-45B4-92D6-B53E2156C08C'
#3) Wetlands-inland_waters
uid_wlwatersmin_r1_soil='9F1669E1-6C57-442F-801E-01FF078038CA'#'6D7ADF2F-9234-45B4-92D6-B53E2156C08C'
uid_wlwatersmin_r2_soil='BD23A6A3-CCA7-4C5F-85AB-B105FFBED64F'#'1AFC882B-20C8-4BB3-A843-CB48714D0767'
uid_wlwatersmin_soil_ls=[uid_wlpeatmin_r1_soil,uid_wlpeatmin_r2_soil,
                         uid_wlpeat_extraction_min_r1_soil,uid_wlpeat_extraction_min_r2_soil,
                         uid_wlwatersmin_r1_soil,uid_wlwatersmin_r2_soil]
uid_wetland_soil_min_info='FC7B0263-12CE-4E22-A3CD-D4D6085C603B'
#Wetlands, region 1 and 2, organic, net change in soils
#1) Wetlands-peatland
uid_wlpeatorg_r1_soil='AECBB3CD-8EB1-479B-AE20-5ADC93401634'#'0CCF7C25-B42D-4985-B35E-359A6FE34ACE'
uid_wlpeatorg_r2_soil='137B3314-9563-4575-8741-C4075B4637CB'#'21524A21-E0D3-4BEF-B6FA-49EED076F77D'
#2) Wetlands-peat_extraction
uid_wlpeat_extraction_org_r1_soil='4DC27D02-4335-4E15-9D33-DBE0D359BB6D'#'58221757-B1C9-48D8-8455-5AD858F8C5FF'
uid_wlpeat_extraction_org_r2_soil='D57993D7-D6B2-4F40-9FF7-7ABF6474A51A'#'243F63F1-E419-46E2-898B-9ED88EB2AC96'
#3) Wetlands-inland_waters
uid_wlwatersorg_r1_soil='CC4AE425-1AA1-49CF-8C6A-F7438D545FFA'#'688E959B-2554-4F1F-BB31-8161F3412BE3'
uid_wlwatersorg_r2_soil='EB82E5ED-9A8A-4F77-99D5-2B64AD454B65'#'2FF3231A-6957-4BEE-9FB7-41C7220EE39A'
uid_wlwatersorg_soil_ls=[uid_wlpeatorg_r1_soil,uid_wlpeatorg_r2_soil,
                         uid_wlpeat_extraction_org_r1_soil,uid_wlpeat_extraction_org_r2_soil,
                         uid_wlwatersorg_r1_soil,uid_wlwatersorg_r2_soil]
uid_wetland_soil_org_info='32B7106F-14DF-41A2-8620-3C1BB3099FFB'

#-----------------------------------------------------------------------
#Other land is an exception: because land areas are NA, so are all the values NA
#Other land, region 1 and 2, above, gains
uid_ol_above_gains_info='28277AEB-644F-4F96-8DB3-B97DCF0DE6AC'
#Other land, region 1 and 2, above, losses
uid_ol_above_losses_info='0DCC2DC0-E69E-4D73-AEB2-656440DE9FAE'
#Other land, region 1 and 2, below, gains
uid_ol_below_gains_info='A7012112-7397-4BC6-B9A5-5F76AFBBCEE4'
#Other land, region 1 and 2, below, losses
uid_ol_below_losses_info='9189F9ED-54E0-410A-A8E8-EEA8EF8F7704'
#Other land, region 1 and 2, net change litter
uid_ol_litter_info='3BDF7C91-BE36-4BFB-AD49-A93F2749A5B2'
#Other land, region 1 and 2, net change dead wood
uid_ol_dead_wood_info='D7C6A3F7-00B2-466A-91A9-CD750109D039'
#Other land, region 1 and 2, net change mineral soils
uid_olmin_soil_info='A5C32353-9286-481F-8167-502C424DF540'
#Other land, region 1 and 2, net change organic soils
uid_olorg_soil_info='DEE47AC1-81FB-40A5-8658-F564BBDAD3A2'
#Command line generator   
parser = OP()
parser.set_defaults(r=False)
parser.add_option("-p",dest="f1",help="Read CRFReporter XML file")
parser.add_option("-x",dest="f2",help="Pretty print output XML file")
parser.add_option("-m","--map",dest="f3",help="CRFReporter 3.0.0 --> 5.0.0 UID mapping file")
parser.add_option("-y","--year",dest="f4",help="Current inventory year")
(options,args) = parser.parse_args()

#Parse the simple xml file
t = ET()
if options.f1 is None:
	print("No input xml file")
	quit()
if options.f2 is None:
	print("No output xml file")
	quit()
if options.f3 is None:
    print("No CRFReporter 3.4.0 --> CRFReporter 5.0.0 UID mapping file")
    quit()
if options.f4 is None:
    print("No current inventory year given")
    quit()

print("Parsing the file",options.f1)
t.parse(options.f1)
print("Done")

inventory_year=int(options.f4)
(uid340set,uiddict) =  Create340to500UIDMapping(options.f3)

 #Generate  information items for Deforestation
print("Writing Information Items")
#Forest land
GenerateAndInsertInformationItem(t,"Forest land, region 1 and 2, mineral, organic, above, gains",uid_fl_above_gains_info,uid_ard_r1r2_above_gains_ls)
GenerateAndInsertInformationItem(t,"Forest land, region 1 and 2, mineral, organic, above, losses",uid_fl_above_losses_info,uid_ard_r1r2_above_losses_ls)
GenerateAndInsertInformationItem(t,"Forest land, region 1 and 2, mineral, organic, below, gains",uid_fl_below_gains_info,uid_ard_r1r2_below_gains_ls)
GenerateAndInsertInformationItem(t,"Forest land, region 1 and 2, mineral, organic, below, losses",uid_ard_fl_below_losses_info,uid_ard_r1r2_below_losses_ls)
GenerateAndInsertInformationItem(t,"Forest land, region 1 and 2, mineral, organic, net carbon change litter",uid_ard_fl_litter_info,uid_ard_r1r2_litter_ls)
GenerateAndInsertInformationItem(t,"Forest land, region 1 and 2, mineral, organic, net carbon change dead wood",uid_ard_fl_dead_wood_info,uid_ard_r1r2_dead_wood_ls)
GenerateAndInsertInformationItem(t,"Forest land, region 1 and 2, mineral, net carbon stock change soils",uid_ardmin_fl_soil_info,uid_ardmin_r1r2_soil_ls)
GenerateAndInsertInformationItem(t,"Forest land, region 1 and 2, organic, net carbon stock change soils",uid_ardorg_fl_soil_info,uid_ardorg_r1r2_soil_ls)
#Cropland
GenerateAndInsertInformationItem(t,"Cropland, region 1 and 2, mineral, organic, above, gains",uid_cl_r12_above_gains_info,uid_cl_above_gains_ls)
GenerateAndInsertInformationItem(t,"Cropland, region 1 and 2, mineral, organic, below, gains",uid_cl_r12_below_gains_info,uid_cl_below_gains_ls)
GenerateAndInsertInformationItem(t,"Cropland, region 1 and 2, mineral, organic, above, losses",uid_cl_r12_above_losses_info,uid_cl_above_losses_ls)
GenerateAndInsertInformationItem(t,"Cropland, region 1 and 2, mineral, organic, below, losses",uid_cl_r12_below_losses_info,uid_cl_below_losses_ls)
GenerateAndInsertInformationItem(t,"Cropland, region 1 and 2, net carbon stock change in litter",uid_cl_r12_litter_info,uid_cl_litter_ls)
GenerateAndInsertInformationItem(t,"Cropland, region 1 and 2, net carbon stock change in dead wood",uid_cl_r12_dead_wood_info,uid_cl_deadwood_ls)
GenerateAndInsertInformationItem(t,"Cropland, region 1 and 2, mineral, net carbon stock change in soils",uid_clmin_r1r2_net_change_soils_info,
                                 uid_clmin_net_change_soils_ls)
GenerateAndInsertInformationItem(t,"Cropland, region 1 and 2, organic, net carbon stock change in soils",uid_clorg_r1r2_net_change_soils_info,
                                 uid_clorg_net_change_soils_ls)
#Grassland
GenerateAndInsertInformationItem(t,"Grassland, region 1 and 2, mineral, organic, above, gains",uid_gl_r12_above_gains_info,uid_gl_above_gains_ls)
GenerateAndInsertInformationItem(t,"Grassland, region 1 and 2, mineral, organic, below, gains",uid_gl_r12_below_gains_info,uid_gl_below_gains_ls)
GenerateAndInsertInformationItem(t,"Grassland, region 1 and 2, mineral, organic, above, losses",uid_gl_r12_above_losses_info,uid_gl_above_losses_ls)
GenerateAndInsertInformationItem(t,"Grassland, region 1 and 2, mineral, organic, below, losses",uid_gl_r12_below_losses_info,uid_gl_below_losses_ls)
GenerateAndInsertInformationItem(t,"Grassland, region 1 and 2, net carbon stock change in litter",uid_gl_r12_litter_info,uid_gl_litter_ls)
GenerateAndInsertInformationItem(t,"Grassland, region 1 and 2, net carbon stock change in dead wood",uid_gl_r12_dead_wood_info,uid_gl_dead_wood_ls)
GenerateAndInsertInformationItem(t,"Grassland, region 1 and 2, mineral, net carbon stock change in soils",uid_glmin_r1r2_net_change_soils_info,
                                 uid_glmin_net_change_soils_ls)
GenerateAndInsertInformationItem(t,"Grassland, region 1 and 2, organic, net carbon stock change in soils",uid_glorg_r1r2_net_change_soils_info,
                                 uid_glorg_net_change_soils_ls)
#Wetland
GenerateAndInsertInformationItem(t,"Wetlands, region 1 and 2, mineral, organic, above, gains",uid_wl_r12_above_gains_info,uid_wl_above_gains_ls)
GenerateAndInsertInformationItem(t,"Wetlands, region 1 and 2, mineral, organic, below, gains",uid_wl_r12_below_gains_info,uid_wl_below_gains_ls)
GenerateAndInsertInformationItem(t,"Wetlands, region 1 and 2, mineral, organic, above, losses",uid_wl_r12_above_losses_info,uid_wl_above_losses_ls)
GenerateAndInsertInformationItem(t,"Wetlands, region 1 and 2, mineral, organic, below, losses",uid_wl_r12_below_losses_info,uid_wl_below_losses_ls)
GenerateAndInsertInformationItem(t,"Wetlands, region 1 and 2, mineral, organic, net change in litter",uid_wetland_litter_info,uid_wl_litter_ls)
GenerateAndInsertInformationItem(t,"Wetlands, region 1 and 2, mineral, organic, net change in dead wood",uid_wetland_dead_wood_info,uid_wl_dead_wood_ls)
GenerateAndInsertInformationItem(t,"Wetlands, region 1 and 2, mineral, net carbon stock change in soils",uid_wetland_soil_min_info,uid_wlwatersmin_soil_ls)
GenerateAndInsertInformationItem(t,"Wetlands, region 1 and 2, organic, net carbon stock change in soils",uid_wetland_soil_org_info,uid_wlwatersorg_soil_ls)
#Settlement
GenerateAndInsertInformationItem(t,"Settlement, region 1 and 2, above, gains",uid_sett_r12_above_gains_info,uid_sett_above_gains_ls)
GenerateAndInsertInformationItem(t,"Settlement, region 1 and 2, below, gains",uid_sett_r12_below_gains_info,uid_sett_below_gains_ls)
GenerateAndInsertInformationItem(t,"Settlement, region 1 and 2, above, losses",uid_sett_r12_above_losses_info,uid_sett_above_losses_ls)
GenerateAndInsertInformationItem(t,"Settlement, region 1 and 2, below, losses",uid_sett_r12_below_losses_info,uid_sett_below_losses_ls)
GenerateAndInsertInformationItem(t,"Settlement, region 1 and 2, carbon stock change in litter",uid_sett_r1r2_litter_info,uid_sett_litter_ls)
GenerateAndInsertInformationItem(t,"Settlement, region 1 and 2, carbon stock change in dead wood",uid_sett_r1r2_dead_wood_info,uid_sett_dead_wood_ls)
GenerateAndInsertInformationItem(t,"Settlement,  region 1 and 2, mineral, net carbon stock change in soils",uid_settmin_r1r2_net_change_soils_info,
                                 uid_settmin_net_change_soils_ls)
GenerateAndInsertInformationItem(t,"Settlement,  region 1 and 2, organic, net carbon stock change in soils",uid_settorg_r1r2_net_change_soils_info,
                                 uid_settorg_r1r2_net_change_soil_ls)
#Other land
print("Other Land - At the moment land area NA")
for year in range(kp_start_year,inventory_year+1):
    InsertKPLULUCFDataWithUID(t,uid_ol_above_gains_info,str(year),'NA')
    InsertKPLULUCFDataWithUID(t,uid_ol_above_losses_info,str(year),'NA')
    InsertKPLULUCFDataWithUID(t,uid_ol_below_gains_info,str(year),'NA')
    InsertKPLULUCFDataWithUID(t,uid_ol_below_losses_info,str(year),'NA')
    InsertKPLULUCFDataWithUID(t,uid_ol_litter_info,str(year),'NA')
    InsertKPLULUCFDataWithUID(t,uid_ol_dead_wood_info,str(year),'NA')
    InsertKPLULUCFDataWithUID(t,uid_olmin_soil_info,str(year),'NA')
    InsertKPLULUCFDataWithUID(t,uid_olorg_soil_info,str(year),'NO')
#Generate conversion from N2O to C
#Region 1
#print("Converting N2O to C emissions")
#print("Region 1")
#uid_n2o_r1 = '56E4C1F1-ECA6-4322-B7BC-4B8B1EE491DE'
#uid_c_r1 = '6827D291-9965-4634-AD34-671C0C233770'
#for year in range(kp_start_year,inventory_year+1):
#    n2o_data_r1 = FindKPLULUCFDataWithUID(t,uid_n2o_r1,str(year))
#    if n2o_data_r1 is not None:
#        c_data_r1 = 15.0*100.0*(28.0/44.0)*float(n2o_data_r1)
#        c_data_r1 = float(format(c_data_r1,'.6f'))
#        InsertKPLULUCFDataWithUID(t,uid_c_r1,str(year),str(c_data_r1))
#    else:
#        print("Region 1, N2O is None")
#Region2
#print("Region 2")
#uid_n2o_r2 = 'C9C98B2C-D925-493D-AAE0-457EB27AE741'
#uid_c_r2 = '5C732186-0B1C-4D0A-901E-FF3E136963AF'
#for year in range(kp_start_year,inventory_year+1):
#    n2o_data_r2 = FindKPLULUCFDataWithUID(t,uid_n2o_r2,str(year))
#    if n2o_data_r2 is not None:
#        c_data_r2 = 15.0*100.0*(28.0/44.0)*float(n2o_data_r2)
#        c_data_r2 = float(format(c_data_r2,'.6f'))
#        InsertKPLULUCFDataWithUID(t,uid_c_r2,str(year),str(c_data_r2))
#    else:
#        print("Region 2, N2O is None")
#Write ouput file
print("Writing output file for the CRFReporter:",options.f2)
PrettyPrint(t.getroot(),0,"    ")
t.write(options.f2) 
print("Done")
