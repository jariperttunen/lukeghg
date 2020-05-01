#!/bin/bash
#run-eu529-ghg-master.sh: Run (2017) EU529 inventory xml import in one step. 
#Note the use of double quotes to allow wild card file reading.
#See "/hsan2/khk/ghg/lukeghg/InstallAndUpdateLukeGHG.txt" to setup 'lukeghg' python virtual environment. 
#To redirect output type e.g.: run-eu529-ghg-master.sh > output.txt 2> errors.txt.  
source ~/lukeghg/bin/activate
ghg-master.py -c "EU529_2018/KP*.csv" -p GHG2018_EU529_FIN_2020_5_template.xml\
	      -x GHG2018_EU529_FIN_2020_5.xml\
	      -b lukeghg/KPLULU1990/KP_CM_GM_RV_WDR_UID_notaatioavain.csv\
	      -k lukeghg/KPLULUSummary/KPSummary.csv\
	      -m lukeghg/300_500_mappings_1.1.csv\
	      -n "EU529_2018/NIR*.csv"\
	      -i "EU529_2018/C*.csv"\
	      -y 2018
deactivate
