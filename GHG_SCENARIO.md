# Produce GHG scenario excel #

`ghg-scenario.py` reads GHG scenario result files and using
excel template file produces scenario inventory summary in excel format. 

## Input files ##

Input files have exactly the same format as in the annual GHG inventory.
The files are text (csv) files with white space as delimiter. Each line
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

The *UIDMatrix* sheet represent carbon stock changes and other emissions by gases. The columns
define land use and land use change classes and rows their respective stock changes and emissions.
The column A contains numbers (red) that guide `ghg-scenario.py`to insert the time series
into the right row based derived from the same number (red) found in the *LandUse* template sheet. 

The sheet cells contain UIDs of the time series. For example 4A48C2F0-02C0-4EAB-8547-6A109929DDCD 
denotes *CL-FL biomass gains*. **Only those time series having UID entry will appear in result Excel**. 
Note that not all cells have an UID because those cases simply do not occur.

### LandUse sheet ###

The LandUse sheet is the template for the results for each land use class or groupings of classes 
whether straightforwardly collected from the result files or summarised from other sheets.
The sheet columns contain inventory years from 1990 to 2050. *The missing years from the end of the
time series to 2050 will appear as zeros in results*. Scenarios intended from 1990 beyond 2050
require matching number of years in the (new) template sheet. The sheet rows contain Carbon stock changes
and emissions by gases. The column A has numbers (red) that corresponds to numbers (red)
in the matching column A in the UID Matrix sheet.

### LULUCF sheet ###

The LULUCF sheet will be the summary for the whole scenario. `ghg-scenario.py` will fill sheet
rows with appropriate excel formulas to collect results from land use classes and land use class
groupings.

## Excel result file ##

`ghg-scenario.py` produces excel file for scenarios in three parts: 1) LULUCF summary
sheet covering the whole inventory, 2) excel summary sheets for land use clusters
generated from 3) excel sheets for land use and land use change classes constructed from scenario
results. In addition the first sheet  lists UIDs in the UIDMatrix sheet that are not found in inventory input files. 
The second sheet contains Global Warming Potentials (GWP) used.

The undescore ('_') in a sheet name denotes summary for a land use cluster and hyphen ('-') change in land use.
For example Lands_FL means lands to forest land and CL-FL means cropland to forest land. 
The land use summary sheets are defined as follows:

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
 + WLpeat_summary = WL-WL(peatextraction) + Lands_WLpeat
 + WLflooded_summary = WL-WL(flooded) + Lands_WLflooded
 + WLother_summary = WL-WL(other) + Lands_WLother

The last three wetlands summaries (WLpeat_summary, WLflooded_summary, WLother_summary) contain emissions
from peat productions, artificial lakes, wetlands etc. regardless being remaining or converted areas.

### Color coding ###

Yellow color in excel sheets denotes summary rows. The grey color in summary sheets denotes formulas 
are used in excel cells. Red color denotes missing values (not necessarily an error). 

## Usage ##

The command line is as follows. Bracktes ([]) denote optional arguments:

	(lukeghg) prompt% ghg-scenario.py [-h] --files FILES  --scen SCEN \
     -m M -o O --start START --end END [--GWP GWP] [--noformulas] 
     
- -h: python help
- --files: Give scenario csv files (wild card search). The format of
the files is the  same as in ghg inventory. A row consists of optional
but highly recommended comment part, UID of the time series followed by the time series.
- --scen: The template excel for results. The file is in [ScenarioTemplate](ScenarioTemplate) directory.
  It contains three sheets:
  - UIDMatrix: contains  UIDs  identifying times series.
  - LandUse: template for results for land use and land use change.
  - LULUCF: template for collecting LULUCF totals from LandUse sheets, land use and land use change. 
- -m: The UID mapping file as in run-ghg-master.sh.
- -o: Excel output file
- --start: The start year of the scenario inventory
- --end: The end year of the scenario inventory
- --GWP: Global warming potential for CH4 and N2O, possible values AR4 (GHG inventory) or AR5 (default)
- --noformulas: Add up values in summary sheets. Default: Not present, generate excel formulas

For the sample command line set your working directory to [*lukeghg*](../lukeghg) package so that you can find 
ScenarioTemplate and  300_500_mapping files as denoted in the command line options. Then, assuming the scenario result 
files are under *hiisi* directory type:

	(lukeghg) prompt% ghg-scenario.py --files 'hiisi/wem/crf/LU*.csv' --scen lukeghg/ScenarioTemplate/ScenarioTemplate.xlsx \
	                  -m lukeghg/300_500_mappings_1.1.csv -o Hiisi_1990_2050.xlsx --start 1990 --end 2050
			 
The scenario results will appear in Hiisi_1990_2050.xlsx.
