#!/bin/bash
#run-eu529-ghg-master.sh: Run (2017) EU529 inventory xml import in one step. 
#Note the use of double quotes to allow wild card file reading.
#See "/hsan2/khk/ghg/lukeghg/InstallAndUpdateLukeGHG.txt" to setup 'lukeghg' python virtual environment. 
#To redirect output type e.g.: run-eu529-ghg-master.sh > output.txt 2> errors.txt.  
#It is assumed that this script is in python virtual environment (lukeghg)
ghg-master.py -c "EU529/KP*.csv" -p PartyProfile/PartyProfile_FIN_2021_4.xml\
	      -x PartyProfile/PartyProfile_FIN_2021_4_result.xml\
	      -b lukeghg/KPLULU1990/KP_CM_GM_RV_WDR_UID_notaatioavain.csv\
	      -k lukeghg/KPLULUSummary/KPSummary.csv\
	      -m lukeghg/CRFReporterMappings/300_500_mappings_1.1.csv\
	      -n "EU529/NIR*.csv"\
	      -i "EU529/C*.csv"\
	      -y 2019

