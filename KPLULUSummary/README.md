The speciality for 2015 inventory and onwards 
is that for one UID in PartyProfile xml data comes from two sources:
agriculture and  forestry. In practice this means 
double UID exists in inventory for these cases.

As the last step to fill PartyProfile xml `kp-lulu-summary.py` can read file where
each line is of format:

    #comment# UID_TO UID1_FROM [UID2_FROM .... UIDN_FROM]

UID_TO is the CRFReporter UID and the sums of time series in UID1_FROM ... UIDN_FROM found 
are calculated  and inserted to PartProfile xml as a single unit.

Routinely there are two sources (agriculture and forestry) with the same UID_FROM 
and also UID_TO is (usually) the same as UID_FROM.

If necessary insert the data (UID) to following two files:
    
+ KPSummary.csv: UID's from KPLULUCF 
+ LUSummary.csv: UID's from LULUCF
