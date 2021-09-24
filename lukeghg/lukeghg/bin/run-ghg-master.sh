#!/bin/bash
#run-ghg-master.sh: Run inventory xml import in one step. 
#Note the use of double quotes to allow wild card file reading.
#See GitHub https://github.com/jariperttunen/lukeghg InstallAndUpdateLukeGHG.md
#to setup 'lukeghg' python virtual environment and usage. 
#To redirect output type e.g.: run-ghg-master.sh > output.txt 2> errors.txt.
#It assumed that this script is in python virtual environment (lukeghg)
ghg-master.py -c "crf/[KPLU]*.csv"\
              -p PartyProfile/PartyProfile_FIN_2022_2.xml\
	      -x PartyProfile/PartyProfile_FIN_2022_2_result.xml\
	      -b lukeghg/KPLULU1990/KP_CM_GM_RV_WDR_UID_notaatioavain.csv\
	      -k lukeghg/KPLULUSummary/KPSummary.csv\
	      -l lukeghg/KPLULUSummary/LUSummary.csv\
	      -m lukeghg/CRFReporterMappings/300_500_mappings_1.1.csv\
	      -n "crf/NIR*.csv"\
	      -i "crf/C*.csv"\
	      -y 2020

