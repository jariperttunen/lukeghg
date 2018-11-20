#!/bin/bash
#Run 2017 inventory xml import in one step. Note the use of double quotes to allow wild card file reading. 
source ~/lukeghg/bin/activate
ghg-master.py -c "/hsan2/khk/ghg/2017/crf/[KPLU]*.csv" -p /hsan2/khk/ghg/2017/FIN_2019_1/PartyProfile-2017-PP.xml\
	      -x PartyProfileResults_2017.xml\
	      -b /hsan2/khk/ghg/lukeghg/KPLULU1990/KP_CM_GM_RV_WDR_UID_notaatioavain.csv\
	      -k /hsan2/khk/ghg/lukeghg/KPLULUSummary/KPSummary.csv\
	      -l /hsan2/khk/ghg/lukeghg/KPLULUSummary/LUSummary.csv\
	      -m /hsan2/khk/ghg/lukeghg/300_500_mappings_1.1.csv\
	      -n "/hsan2/khk/ghg/2017/crf/NIR*.csv"\
	      -i "/hsan2/khk/ghg/2017/crf/C*.csv"\
	      -y 2017
deactivate
