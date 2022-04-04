# Reference Manual Intro for lukeghg

 The *lukeghg* python package contains command line tools to generate CRF Reporter Inventory Software (a.k.a CRFReporter)
 xml file from GHG inventory results. The package has also programs for rudimentary validation
 of the inventory and to generate some ubiquitous NIR tables.
 The Reference Manual for the *lukghg* package is intended  to be generated with `doxygen`
 based on the comments in source files.

        doxygen Doxyfile 2> errors.txt

The [User Guide](LUKEGHG_INSTALL_AND_USAGE.md) is available in GitHub.

Linux `bash` shell redirection `2>` redirects error output to file *errors.txt'.

## Shortcuts to files and functions to generate CRFReporter xml file
 Files with hyphen (`-`) are command line programs. 
 + run-ghg-master.sh run-ghg-master.slurm run-eu529-ghg-master.sh run-eu529-ghg-master.slurm: Shell scripts to generate CRFReporter xml.
 + ghg-master.py: Generate complete CRFReporter xml file from GHG inventory results in a stepwise fashion.
   + ghg-inventory.py: Generate CRFReporter xml file from GHG inventory results for emissions and stocks.
      + ghginventory.py: Contains `ParseGHGInventoryFile()` and  `GHGToCRFReporter()` functions to parse GHG inventory files (emissions and stocks).

## Shortcuts to files and functions to validate GHG inventory
Files with hyphen (`-`) are command line programs. 
 + ghg-todo.py: Compare two inventories and list missing time series and UIDs not found.
 + check-inventory-values.py: Compare two inventories and check time series.
 \sa checkinventoryvalues.py Contains `CompareTwoInventoryYears()` function to compare inventories.
 + check-double-uid.py: Check if a UID appears twice or more in the inventory.
 \sa checkdoubleuid.py Collect UIDs appearing twice or more in the inventory.
   

## Shortcuts to programs to generate NIR tables
To appear.
## Shortcuts to utility programs
To appear.
