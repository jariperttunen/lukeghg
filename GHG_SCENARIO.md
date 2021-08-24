# Produce GHG scenario excel #

`ghg-scenario.py` reads GHG scenario result files and using
excel template file produces scenario inventory summary in excel format. 

## Input files ##

Input files have exactly the same format as in the annual GHG inventory.
The files are text (csv) files with white space as separator. Each line
in the file represent one time series for an emission, some area etc.
The line begins with optional comment followed by the UID ("unique identifier")
of the time series and after that the time series itself. For example:

       #fl.to.cl# A4DB34A0-1847-401A-92BA-7CCE37611F1A -29.903 -28.157 -26.926 ... -14.865 -14.865 -14.865

The *#* character denotes the beginning and the end of the comment. The UID (*A4DB3 ...611F1A*) is CRFReporter generated or
user defined. In the latter case the times series used in GHG inventory has been
divided into two or more parts to provide finer level of detail.

## Excel template file ##

The excel template file gives `ghg-scenario.py` information about the times series to collect
them into their proper sheets and rows in the final excel result file. The template file
has three sheets: UIDMatrix, LandUse and LULUCF.

### UIDMatrix sheet ###

The UIDMatrix sheet represent carbon stock changes and other emissions by gases. The columns
define land use and land use change classes and rows their respective stock changes and emissions.
The column A contains numbers (in red) that guide `ghg-scenario.py`to insert the time series
into the right row (with the same number) in the LandUse template sheet. The sheet cells contain UIDs of the
time series. For example 4A48C2F0-02C0-4EAB-8547-6A109929DDCD denotes *CL-FL biomass gains*.
Note that not all cells have an UID because those cases simply do not occur.

### LandUse sheet ###

The LandUse sheet is the template for the results for each land use class or groupings of classes 
whether straightforwardly collected from the result files or summarised from other sheets.
The sheet columns contain inventory years from 1990 to 2050. The missing years from the end of the
time series to 2050 will appear as zeros. Scenarios intended from 1990 beyond 2050
require matching number of years in the template sheet. The sheet rows contain Carbon stock changes
and emissions by gases. The column A has numbers (in red) that corresponds to numbers (in red)
in the matching column A in the UID Matrix sheet.

### LULUCF sheet ###

The LULUCF sheet will be the summary for the whole scenario. `ghg-scenario.py` will fill sheet
rows with appropriate excel formulas to collect results from land use classes and land use class
groupings.

## Excel result file ##

`ghg-scenario.py` produces excel file for scenarios in three parts: 1) LULUCF summary
sheet covering the whole inventory, 2) excel summary sheets for land use groupings and
3) excel sheets for land use and land use change classes. In addition the first
sheet lists UIDs in the UIDMatrix sheet that are not found in inventory input files.
The second sheet contains GWPs used.

The land use grouping sheets are defined as follows:

 + Lands_FL = CL-FL + GL-FL + WLpeat-FL + WLother-FL + SE-FL
 + FL_Lands = FL-CL + FL-GL + FL-WLpeat + FL-WLflooded + FL-WLother + FL-SE
 + Lands_CL = FL-CL + GL-CL + WLpeat-CL + WLother-CL + SE-CL
 + Lands_GL = FL-GL + CL-GL + WLpeat-GL + WLother-Gl + SE-GL
 + Lands_SE = FL-SE + CL-SE + GL-SE + WLpeat-SE + WLother-SE
 + Lands_WLpeat = FL-WLpeat + CL-WLpeat + GL-WLpeat
 + Lands_WLflooded = FL-WLflooded + CL-WLflooded + GL-WLflooded + SE-WLflooded + OL-WLflooded
 + Lands_WLother = FL-WLother + CL-WLother + GL-WLother
 + Lands_WL = Lands_WLpeat + Lands_WLflooded + Lands_WLother
 + WL_WL = WL-WL(peatextraction) + WLother-WLpeat + WL-WL(flooded) + WL-WL(other) + WLpeat-WLother
 

The undescore ('_') denotes lands use grouping (summary) and hyphen ('-') change in land use,
for example CL-FL means cropland to forest land.

### Color coding ###

Yellow color denotes summary rows. Red color denotes missing values. The latter is not necessarily
an error.

## Usage ##

`ghg-scenario.py` can generate excel file for ghg scenario calculations.
The command line is as follows. The `[]` denotes optional arguments:

	(lukeghg) prompt% ghg-scenario.py [-h] --files FILES  --scen SCEN \
     -m M -o O --start START --end END [--GWP GWP]
     
- -h: python help
- --files: Give scenario csv files (wild card search). The format of
the files is the  same as in ghg inventory. A row consists of optional
but highly recommended comment part, UID of the time series followed by the time series.

- --scen: The template excel for results. The file is in [ScenarioTemplate](ScenarioTemplate) directory.
  It contains three sheets:
  - UIDMatrix: contains  UIDs  identifying times series.
  - LandUse: template for results for land use and land use change.
  - LULUCF: template for collecting LULUCF totals from land use and land use change. 

- -m: The UID mapping file as in run-ghg-master.sh.

- -o: Excel output file

- --start: The start year of the scenario inventory

- --end: The end year of the scenario inventory

- --GWP: Global warming potential for CH4 and N2O, possible values AR4 (GHG inventory) or AR5 (default)

