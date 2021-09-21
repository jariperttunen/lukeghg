# Manual work for a new GHG inventory in CRFReporter.


## Natural disturbances

`KP.B Article 3.4 Activities -> KP.B.1 Forest Management -> Carbon stock change -> 
Emissions and removals from natural disturbances -> Total natural disturbances`

Each year new element must be created manually. Then the UID identifier for each item 
of the element must be retrieved from the CRFReporter Simple xml.

**Tips**: write nonsense values for 1990 only that are not likely to appear anywhere in any sector of the inventory, 
export simple xml and find the nonsense values in the xml. This guides close to the UIDs needed.

## HWP Activity data

The years starting from 1961 miss the current inventory year. It is not automatically added.
The current inventory year must be inserted by hand. 
