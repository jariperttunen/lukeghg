# Manual work for a new GHG inventory in CRFReporter.


## Natural disturbances

`KP.B Article 3.4 Activities -> KP.B.1 Forest Management -> Carbon stock change -> 
Emissions and removals from natural disturbances -> Total natural disturbances`

Each year a new element (node) must be created. Then for each item of the new element the corresponding 
UID identifier must be retrieved from the CRFReporter Simple xml and handed over to the GHG inventory.

**Tips**: write nonsense values, nine in total, only for the year 1990 that are not likely to appear anywhere 
in any sector of the inventory, export simple xml and find the nonsense values in the xml. 
This guides close to the UIDs needed.

## HWP Activity data

The years starting from 1961 miss the current inventory year. It is not automatically added.
The current inventory year must be inserted by hand. 
