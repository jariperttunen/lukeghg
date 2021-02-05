The speciality for 2015 inventory and onwards 
is that for one UID in xml data comes from two sources, 
agriculture and  forestry. In practice this means 
double UID exists in inventory for these cases.

For the summation "kp-summary.py" can read file where
each line is of format

    #comment# UID_TO UID1_FROM [UID2_FROM .... UIDN_FROM]

where UID_TO is the CRFReporter UID where the sums of 
UID1_FROM ... UIDN_FROM are calculated. 

Usually there are two sources with the same UID_FROM (one UID_FROM) 
and also UID_TO is (usually) the same as UID_FROM.

In practice this is the last phase when importing data
and has been stable regarding new items or changes. If necessary
insert the data (UID) to following two files:
    
+ KPSummary.csv: UID's from KPLULUCF 
+ LUSummary.csv: UID's from LULUCF
