#!/bin/bash
#run-ghg-master.sh: Run (2017) inventory xml import in one step. 
#Note the use of double quotes to allow wild card file reading.
#See "/hsan2/khk/ghg/lukeghg/InstallAndUpdateLukeGHG.txt" to setup 'lukeghg' python virtual environment. 
#To redirect output type e.g.: run-ghg-master.sh > output.txt 2> errors.txt.  
source ~/lukeghg/bin/activate
ghg-master.py -c "crf/[KPLU]*.csv" -p PartyProfile/PartyProfile_FIN_2021_1.xml\
	      -x PartyProfile/PartyProfile_FIN_2021_1_result.xml\
	      -b lukeghg/KPLULU1990/KP_CM_GM_RV_WDR_UID_notaatioavain.csv\
	      -k lukeghg/KPLULUSummary/KPSummary.csv\
	      -l lukeghg/KPLULUSummary/LUSummary.csv\
	      -m lukeghg/300_500_mappings_1.1.csv\
	      -n "crf/NIR*.csv"\
	      -i "crf/C*.csv"\
	      -y 2019
deactivate
