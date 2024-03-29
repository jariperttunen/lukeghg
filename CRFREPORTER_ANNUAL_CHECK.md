# Manual work for a new GHG inventory in CRFReporter.

**Note:** From 2021 GHG inventory (calendar year 2022) and onwards KPLULUCF sector is obsolete.

## Natural disturbances
Location in CRFReporter:

     KP.B Article 3.4 Activities -> KP.B.1 Forest Management -> Carbon stock change -> 
     Emissions and removals from natural disturbances -> Total natural disturbances

Each year a new element (node) must be created for *Total natural disturbances*. Then for each item of the new element the 
corresponding UID identifier must be retrieved from the CRFReporter Simple xml and handed over to the GHG inventory.

**Tips**: write nonsense values, nine in total, only for the year 1990 that are not likely to appear anywhere 
in any sector of the inventory. Export CRFReporter Simple xml and find the nonsense values in the xml. 
This guides close to the UIDs needed. Use `pretty-print-xml.py` to make the Simple xml human readable with line breaks
and indentations.

## HWP Activity data

The years starting from 1961 miss the current inventory year. It is not automatically added.
The current inventory year must be inserted by hand in CRFReporter. 

## CRFReporter PartyProfile xml

The CRFReporter PartyProfile xml is the template for the inventory results.
In the course of inventory in the fall there tends to be several CRFReporter updates. 
During PartyProfile xml import (with inventory results) CRFReporter checks that
the PartyProfile xml matches the CRFReporter version. Keep the PartyProfile xml
in sync with CRFReporter version.
