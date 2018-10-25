The speciality for 2015 inventory is that for one 
UID data comes from two sources, agriculture and 
forestry, that needs to be summed.

For the summation "kp-summary.py" can read the file where
each line is of format

  #comment# UID_TO UID1_FROM UID2_FROM .... UIDN_FROM

where UID_TO is the CRFReporter UID where the sums of 
UID1_FROM ... UIDN_FROM are calculated.

The algorithm in kp-summary.py accepts one (normal case), two (double-uid)
or more time series for one uid but makes a warning for three or more.

In practice this is the last phase when importing data 
with crfreporter-2014.sh. LULUCF inventory starts from 1990
and KPLULUCF from 2013. To determine this automatically
please insert the data (UID) to following two files
    
KPSummary.csv: UID's from KPLULUCF 
LUSummary.csv: UID's from LULUCF
