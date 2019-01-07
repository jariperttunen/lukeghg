#!/bin/bash
#run-eu529-ghg-master.sh: Run (2017) EU529 inventory xml import in one step. 
#Note the use of double quotes to allow wild card file reading.
#See "/hsan2/khk/ghg/lukeghg/InstallAndUpdateLukeGHG.txt" to setup 'lukeghg' python virtual environment. 
#To redirect output type e.g.: run-ghgr-.master.sh > output.txt 2> errors.txt.  
source ~/lukeghg/bin/activate
ghg-master.py -c "/hsan2/khk/ghg/2017/EU529/KP*.csv" -p /hsan2/khk/ghg/2017/FIN_2019_3/PartyProfile-EU529-2017-PP.xml\
	      -x PartyProfileEU529Results_2017.xml\
	      -b /hsan2/khk/ghg/lukeghg/KPLULU1990/KP_CM_GM_RV_WDR_UID_notaatioavain.csv\
	      -k /hsan2/khk/ghg/lukeghg/KPLULUSummary/KPSummary.csv\
	      -m /hsan2/khk/ghg/lukeghg/300_500_mappings_1.1.csv\
	      -n "/hsan2/khk/ghg/2017/EU529/NIR*.csv"\
	      -i "/hsan2/khk/ghg/2017/EU529/C*.csv"\
	      -y 2017
deactivate
