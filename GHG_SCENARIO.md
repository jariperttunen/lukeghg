# Produce GHG scenario excel #

GHG inventory software is freqently used to make projections about future emissions. `ghg-scenario.py` reads GHG scenario result files
and using Excel template file produces scenario inventory summary in Excel format. It is part of the 
[*lukeghg*](LUKEGHG_INSTALL_AND_USAGE.md) python package. 

It is difficult, may even be impossible, to produce completely automated construction of the final Excel file
for GHG scenarios. However, the aim is to provide some flexibility to react to different wishes and specifications 
within the framework of GHG inventory.

## 1. GHG scenario result files ##

GHG scenario results, input for `ghg-scenario.py`, have exactly the same file format as in the annual GHG inventory
([see details for file format](GHG_INVENTORY_RESULT_FILES.md)).
Files are text (csv) files with white space as delimiter. Each line in a file represent one 
time series for an emission, stock change, area etc. The line begins with optional comment followed by 
the UID ("unique identifier") of the time series and after that the time series itself. For example:

       #fl.to.cl# A4DB34A0-1847-401A-92BA-7CCE37611F1A -29.903 -28.157 -26.926 ... -14.865 -14.865 -14.865

The *#* character denotes the beginning and the end of the comment. The UID (*A4DB3 ...611F1A*) is CRFReporter generated or
user defined. In the latter case the time series used in GHG inventory may for example have been divided into two or more parts 
to provide finer level of detail.

## 2. Excel template file ##

The [Excel template file](ScenarioTemplate) gives to `ghg-scenario.py` information about the times series to collect
them into their proper sheets and rows in the final excel result file. The template file
has three sheets: UIDMatrix, LandUse and LULUCF.

### UIDMatrix sheet ###

The UIDMatrix sheet represent carbon stock changes and other emissions by gases. The columns
define land use and land use change classes and rows their respective stock changes and emissions.
The column A contains numbers (red) that guide `ghg-scenario.py`to insert the time series
into the right row deduced from the same number (red) found in the *LandUse* template sheet. 

The sheet cells contain UIDs of the time series. For example 4A48C2F0-02C0-4EAB-8547-6A109929DDCD 
denotes *CL-FL biomass gains*. **Only those time series having UID entry will appear in the result Excel file**. 
Some scenario results may not be used on GHG inventory. Those time series can have a user defined tag ("UID").
This tag can be any alphanumerical sequence of characters as in GHGInventory. Note that some sheet cells cannot have an UID
simply because such land use vs. emissions or stock change cases do not occur.

### LandUse sheet ###

The LandUse sheet is the template for the results for each land use class or clusters of land use classes 
straightforwardly collected from the result files or summarised from other sheets.
The sheet columns contain inventory years from 1990 to 2050. 

*The missing years from the end of the time series to 2050 will appear as zeros in results. Too long
time series are shortened from the end to match the template years from 1990 to 2050*. Scenarios intended 
from 1990 beyond 2050 require a new template sheet with matching number of scenario years. 

The sheet rows contain Carbon stock changes and emissions by gases. The column A has numbers (in red) 
that corresponds to numbers (in red) in the matching column A in the UID Matrix sheet.

### LULUCF sheet ###

The LULUCF sheet is the template for the scenario summary. `ghg-scenario.py` will fill the sheet
rows with appropriate excel formulas to collect results from land use classes and land use class
clusters.

## 3. Excel result file ##
The first Excel sheet  lists UIDs in the UIDMatrix sheet not found in inventory input files. 
The second sheet contains UIDs and lengths of the time series that differ from the number of inventory years 
between 1990 and 2050 (i.e. 61 years). The third sheet has the Global Warming Potentials (GWP) used.

The results for scenarios are in three parts: 

  1. LULUCF summary sheet presenting the total tally
  2. Land use summary sheets for land use clusters generated from 
  3. Land use and land use change classes sheets in turn constructed from scenario results. 

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
from peat productions, artificial lakes, wetlands etc. regardless originating from remaining or converted areas.

### Colour coding ###

Yellow color in excel sheets denotes summary rows. The grey color in summary sheets denotes formulas 
are used in excel cells. Red color denotes missing values (not necessarily an error). 

## 4. Usage ##

The `ghg-scenario.py` command line is as follows. Bracktes ([]) denote optional arguments, the backslash (\\) 
in `bash` denotes line continuation:

	(lukeghg) prompt% ghg-scenario.py [-h] --files FILES  --scen SCEN \
     -m M -o O --start START --end END [--GWP GWP] [--noformulas] 
     
- -h: python help
- --files: Give scenario csv files (wild card search).
- --scen: The template excel for results. The file is in [ScenarioTemplate](ScenarioTemplate) directory.
  It contains three sheets:
  - UIDMatrix: contains  UIDs  identifying times series.
  - LandUse: template for results.
  - LULUCF: template for collecting GHG scenario totals from LandUse sheets. 
- -m: The UID mapping file as in run-ghg-master.sh.
- -o: Excel output file
- --start: The start year of the scenario inventory
- --end: The end year of the scenario inventory
- --GWP: Global warming potentials for CH4 and N2O, possible values AR4 (GHG inventory) or AR5 (default)
- --noformulas: Add up values in summary sheets. Default: Not present, generate excel formulas

To run `ghg-scenario.py` set your working directory next to [*lukeghg*](https://github.com/jariperttunen/lukeghg) 
package so that you can find *ScenarioTemplate.xlsx* and *300_500_mappings_1.1.csv* files as shown in the 
command line arguments `--scen` and `-m`. Then, assuming the scenario result  files are under *hiisi* directory 
(argument `--files`) type:

	(lukeghg) prompt% ghg-scenario.py --files 'hiisi/wem/crf/LU*.csv' --scen lukeghg/ScenarioTemplate/ScenarioTemplate.xlsx \
	                  -m lukeghg/CRFReporterMappings/300_500_mappings_1.1.csv -o Hiisi_1990_2050.xlsx --start 1990 --end 2050
			 
The scenario results will appear in Hiisi_1990_2050.xlsx.
