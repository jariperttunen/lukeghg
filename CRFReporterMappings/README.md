Early versions of CRFReporter reconstructed UID's for the times series. 

The 300_500_mappings_1.1.csv contains the mappings of 
the variables that have changed UID  between versions 3.0.0 
and 5.0.0. The first column is the  version 3.0.0 UID, 
second column is version 5.0.0 UID.

If the version 3.0.0 UID is used in GHG inventory, that will
be automatically converted to version 5.0.0 UID during
the filling of PartyProfile xml file with inventory results. 

After CRFReporter version 5.0.0 the UID's have been stable.
