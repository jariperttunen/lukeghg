# lukeghg: Installation and usage in sorvi server
The *lukeghg* python package contains command line tools to generate CRF Reporter Inventory Software 
(hereafter CRFReporter) xml file from GHG inventory results for CRFReporter xml import.  The package has also
programs for rudimentary validation of the inventory and to generate some ubiquitous NIR tables. 
There are no intentions to make graphical user interface.

**The instructions are for `bash` shell in sorvi**.  Your default shell might be for example `tcsh` 
and you must for instance adjust quotation marks (') to fit shell's syntax. 

## Contents

1. Create python virtual environment
2. Install the lukeghg python package
3. Update  the lukeghg python package
4. GHG inventory to CRFReporter xml file
5. GHG Scenarios
6. Utility programs
+ Git version control
+ Reading


## 1. Create python virtual environment

Create python virtual environment (called e.g. lukeghg) in your home directory.
The *prompt%* denotes your terminal command line prompt:

	prompt% /usr/bin/python3 -m venv lukeghg

Activate the virtual environment:

	prompt% source lukeghg/bin/activate
	(lukeghg) prompt%

Note the name of the virtual environment *(lukeghg)* appearing in front of your command prompt.

Check you have the latest versions of `pip`, *setuptools* and *wheel* installed:

	(lukeghg) prompt% python3 -m pip install --upgrade pip
	(lukeghg) prompt% python3 -m pip install --upgrade setuptools wheel

You can now install *lukeghg* python package.

**Tips:** Python virtual environments are so omnipresent that it is customary to create all of them under one
directory (*venv* for example). You can quit virtual environment with `deactivate`.

**NB:** If you have any problems creating the virtual environment check your `.bashrc` file. For example 
if you are part of NFI or closely work with them you may have settings by NFI that  disrupt the `python3`
environment installed in sorvi.

## 2. Install the lukeghg python package
We assume that the working directory will be in */work/\<user\>/GHGInventory* in sorvi
server where *\<user\>* denotes your user name. For GitHub you need to have *.gitconfig* 
in your home directory (see [GitHub version control](#github-version-control) at the end).

Create *GHGInventory* directory and clone *lukeghg* from GitHub:

	(lukeghg) prompt% cd /work/<user>
	(lukeghg) prompt% mkdir GHGInvenory
	(lukeghg) prompt% cd GHGInventory
	(lukeghg) prompt% git clone https://github.com/jariperttunen/lukeghg.git

Create the *wheel package* for *lukeghg* and install it to your virtual environment. 
[`setup.py`](lukeghg/setup.py) is the configuration file with instructions 
for python package dependencies and virtual environment set-up:

	(lukeghg) prompt% cd GHGInventory/lukeghg/lukeghg
	(lukeghg) prompt% python3 setup.py bdist_wheel
	(lukeghg) prompt% python3 -m pip install --upgrade dist/lukeghg-1.0-py3-none-any.whl

All the command line programs in *lukeghg* package are now available in your virtual environment. 
The programs are located in [lukeghg/lukeghg/bin](lukeghg/lukeghg/bin) directory.

**Tips:** Naturally you can organise your work as you like. But as we will see the *lukeghg* package 
contains templates and configuration files that are preset for command line programs. So try this schema 
first and improve later.

## 3. Update the lukeghg python package

You need to update the *lukeghg* package from GitHub whenever you or someone else has made changes
and pushed the work there. Otherwise changes will not appear available in the virtual environment,

Remember to activate the virtual environment if needed (check your
prompt). The tilde (~) character in `bash` expands to your home directory: 

	prompt% source ~/lukeghg/bin/activate
	(lukeghg) prompt%

Update lukeghg package from GitHub. Make sure you are in `/work/<user>/GHGInventory/lukeghg/` directory:

	(lukeghg) prompt% cd /work/<user>/GHGInventory/lukeghg/
	(lukeghg) prompt% git pull

Update your lukeghg virtual environment next. As with the installation
recreate the wheel package, but now first remove the *lukeghg* package
and then upgrade *lukeghg* and its dependencies.
Make sure you are in `/work/<user>/GHGInventory/lukeghg/lukeghg`:

	(lukeghg) prompt% cd /work/<user>/GHGInventory/lukeghg/lukeghg
	(lukeghg) prompt% python3 setup.py bdist_wheel
	(lukeghg) prompt% python3 -m pip uninstall lukeghg
	(lukeghg) prompt% python3 -m pip install --upgrade dist/lukeghg-1.0-py3-none-any.whl


**Tips:** `pip` allows other ways to achieve the same result but this seems to be the most straightforward. 
Note we had to move around a bit inside the lukeghg package. In case `pip` requires update, upgrade 
also *setuptools* and *wheel* as in *1. Create python virtual environment*.

## 4. GHG inventory to CRFReporter xml file

[`run-ghg-master.sh`](lukeghg/lukeghg/bin/run-ghg-master.sh) is a shell script that sets directories 
and files for `ghg-master.py` python script to insert GHG inventory results in the CRFReporter PartyProfile xml. 
Edit the following command line arguments if needed and update lukeghg package as  in *3. Update lukeghg python package*:

- -c Location of the GHG inventory files.
- -n Location of the GHG iventory files for NIR section in CRFReporter.
- -i Location of the GHG inventory comment files for CRFReporter.
- -p Location of the empty (i.e. no inventory data) PartyProfile xml from CRFReporter.
     The naming convention is that it uses the name of the active inventory in CRFReporter
     (see also **NB1** at the end of chapter).
- -x Location of the PartyProfile result file to be imported to CRFReporter.
     The naming convention is  that it appends *_result* to the empty PartyProfile file name. 
- -y Inventory year (the last year in CRFReporter).

`ghg-master.py` has also the arguments -b, -k,-l and -m (not shown here) that 
refer to ubiquitous configuration files that come with the *lukeghg* package.
Each file has an accompanied README explaining the purpose of the file.

#### Produce CRFReporter xml file

Make sure you have activated *lukeghg* python virtual environment and you are in */work/\<user\>/GHGInventory*. 
Then create *crf* and *PartyProfile* directories for GHG Inventory result files and PartyProfile xml files respectively:

	(lukeghg) prompt% cd /work/<user>/GHGInventory/
	(lukeghg) prompt% mkdir crf
	(lukeghg( prompt% mkdir PartyProfile

Copy GHG inventory files to *crf* directory. Be sure the read rights for the files exists, e.g. 2020 inventory:

	(lukeghg) prompt% scp /projects/khk/ghg/2020/crf/*.csv crf/

It has been practice that all GHG inventory results are by year in the same *ghg/\<year\>/crf* directory on the server.

Log in CRFReporter *Import/Export* section, export PartyProfile xml and copy it to *PartyProfile* directory. 
Rename as denoted by the `-p`  argument in [`run-ghg-master.sh`](lukeghg/lukeghg/bin/run-ghg-master.sh). 
To produce the PartyProfile result file filled with the  GHG inventory results type the two commands:

	(lukeghg) prompt% convertutf8.py -f 'crf/*.csv'
	(lukeghg) prompt% run-ghg-master.sh > Import.log 2> Error.log

The GHG inventory result files (csv files) seem to use different encoding systems, most notably some files
seem to use UTF-8 BOM (Byte Order Marking). `convertutf8.py` converts files to UTF-8 encoding if needed 
(this is why they need to be copied first from *ghg/\<year\>/crf* folder). See also **NB2**.

The script `run-ghg-master.sh` will  run few minutes at most.  The `>`character redirects standard out 
terminal output to *Import.log* file and `2>` redirects standard error terminal output to *Error.log* file.

The final step is to import the PartyProfile result file to CRFReporter. Log in CRFReporter
*Import/Export* section and follow the instructions in *Excel/XML-import*. Read **NB3** carefully
before xml import.

For EU529 inventory there is similar [`run-eu529-ghg-master.sh`](lukeghg/lukeghg/bin/run-eu529-ghg-master.sh). 
Note EU529 concerns KPLULUCF files only (LULUCF files are not missing by accident).

#### Slurm
User logins to *interactive* node in sorvi. In addition four *computing* nodes can be used for batch jobs via Slurm.
`run-ghg-master.slurm` and `run-eu529-ghg-master.slurm` are scripts that can be submitted via `sbatch` for execution.
Both simply call `run-ghg-master.sh`and `run-eu529-ghg-master.sh` respectively. Therefore edits in these two files are
mirrored in the corresponding Slurm scripts. The usage is:

		(lukeghg) prompt% sbatch --mail-user firstname.lastname@luke.fi run-ghg-master.slurm
		(lukeghg) prompt% sbatch --mail-user firstname.lastname@luke.fi run-eu529-ghg-master.slurm 
		
Use `squeue` to see your job number in Slurm and `scancel` to remove it. The output will appear in *output_%j.txt* 
and *errors_%j.txt* files where *%j* is the Slurm job number. Although running the scripts takes up to only ten minutes (each),
it might be a good practice to send the work to computational nodes with Slurm.

#### GHG inventory result files
The GHG inventory result files are text (csv) files with white space as the delimeter mark. Each line
in the file represent one time series for an emission, area, stock change etc. in CRFReporter. 
The line begins with optional comment, then the UID (*unique identifier*) of the time series followed 
by the time series itself. For example:

		#CLorg# 810E194F-0D38-4486-8A88-96ACF87C2059 -0.119 -0.119 -0.119 ...  -0.882 -0.948 -0.948

The number sign (#) character denotes the beginning and the end of the comment. The UID (*810E194F-...-96ACF87C2059*) is CRFReporter generated. For details see [GHG_INVENTORY_RESULT_FILES](GHG_INVENTORY_RESULT_FILES.md).

**Tips:** Once you have this set-up you can use it also for the future inventories. 
Do xml imports incrementally, you can easily check if new results have become available. 
Always check that you have the right active inventory in CRFReporter. Each year CRFReporter requires 
[manual work](CRFREPORTER_ANNUAL_CHECK.md) that needs to be done.

**NB1:** CRFReporter requires that the version number of the PartyProfile 
xml matches the CRFReporter version. Each CRFReporter version update requires new
PartyProfile xml from CRFReporter, even during the same active inventory. 

**NB2:** It is important to  run `convertutf8.py`. Otherwise file reading might fail and string comparisons 
may go astray.

**NB3:** Make sure that you have write access *only and solely* to 4. LULUCF and 7. KPLULUCF sectors
in CRFReporter. The bulk xml import in CRFReporter tries first to clear all results in all sectors.
If by accident you have write access for example to 3. Agriculture sector you will delete existing results
there.

## 5. GHG Scenarios

`ghg-scenario.py` can generate excel file for GHG scenario calculations.
The command line is as follows. Brackets ([]) denote optional arguments. In `bash` 
the backslash (\\) denotes the command line continues to the next line:

	(lukeghg) prompt% ghg-scenario.py [-h] --files FILES  --scen SCEN \
	                  -m M -o O --start START --end END [--GWP GWP] [--noformulas]
     
- -h: python help
- --files: Give scenario csv files (wild card search).
- --scen: The template excel in *lukeghg* for results. 
- -m: The UID mapping file as in run-ghg-master.sh.
- -o: Excel output file
- --start: The start year of the scenario inventory
- --end: The end year of the scenario inventory
- --GWP: Global warming potential for CH4 and N2O, possible values AR4 (GHG inventory) or AR5 (default)
- --noformulas: Add up values in summary sheets. Default: Not present, generate excel formulas in summary sheets

For further details see [GHG_SCENARIO](GHG_SCENARIO.md).

## 6. Utility programs

The *lukeghg* package contains useful scripts to validate the inventory and to generate some ubiquitous tables 
to appear annually in the NIR report. Standard python -h (help) argument prints short explanation for each command line argument.

### ghg-todo.py
Compare two inventories and list missing time series from the current inventory, time series already in current inventory
and UIDs not found. This sample command assumes that 2018 inventory is in *2018crf*
directory and the current (2019) inventory in *crf* directory. The output excel file is GHGToDo2019.xlsx:

	(lukeghg) prompt% ghg-todo.py -f1 '2018crf/[KPLU]*.csv' -f2 'crf/[KPLU]*.csv' \ 
	                  -x PartyProfile/PartyProfile_FIN_2021_1.xml -o GHGToDo2019.xlsx \
			  -m lukeghg/CRFReporterMappings/300_500_mappings_1.1.csv -y 2019

The PartyProfile xml is needed to validate UID's found in the inventories. The 300_500_mappings_1.1.csv file 
maps the obsolete CRFReporter 3.0.0 UIDs used in GHG inventory result files to new UIDs corrected for the CRFReporter 5.0.0.

### check-inventory-values.py
Compare two inventories and check time series for 1) too large differences in inventory values, 2) changes in notation keys and 
3) UID's not accounted for. Results will appear in their respective sections in the output file.

The sample command line assumes 2018 inventory  is in *2018crf* directory and 2019 inventory in *crf* directory.
The excel file *GHGComparison.xlsx* will be generated:

	(lukeghg) prompt% check-inventory-values.py -p '2018crf/[KPLU]*.csv' -c 'crf/[KPLU]*.csv' \ 
	                  -m lukeghg/CRFReporterMappings/300_500_mappings_1.1.csv -o GHGComparison.xlsx -t 20
	  
The argument `-t` defines the values that disagree 20% or more will be accounted for. More precisely, 
if two values for some inventory year in the same time series from the two inventories differ 
more than this threshold value, the two time series will appear in the result file. 

#### Colouring
Differences exceeding the given tolerance value show up in red. Notation key changes are in orange. Notation keys changed to 
calculated values are in green. Calculated values changed to notation keys appear in red.
	
### check-double-uid.py

Check if a UID appears twice or more in the inventory:

	(lukeghg) check-double-uid.py -x DoubleUID2020.xlsx -c crf/'*.csv'
	
Ten time series come from two sources, forestry and agriculture, and will appear as multiple UIDs.

### lulucf-table-612.py
Produce NIR LULUCF Table 6.1-2 ("Grand Total") based on inventory result files directly. Time series are retrieved based
on their UIDs. In the command line example the inventory result files are in *crf* directory: 

	(lukeghg) prompt% lulucf-table-612.py -s 1990 -e 2019 -o LULUTable_6.1-2.xlsx -d crf/ \
	                  -b /data/projects/khk/ghg/2019/NIR/Table_6.1-2.csv

Inventory start year is 1990 and 2019 is the current inventory year. The `-b` option denotes the biomass file. The output file
is LULUTable_6.1-2.xlsx.

**NB:** `lulucf-table-612.py`  will fetch biomasses (the first two rows in the Table 6.1-2) 
from a precalculated file in *NIR/Table_6.1-2.csv* for the current inventory year.

### lulucf-table-622.py
Produce NIR LULUCF Table 6.2-2 for IPCC land use. For example:

	(lukeghg) prompt% lulucf-table-622.py -i /data/projects/khk/ghg/2019/areas/lulucf/results/lulucf_classes_all.txt \ 
	                                      -o LULUTable_6.2-2.xlsx -y 2019 \
					      -u /data/projects/khk/ghg/2019/NIR/LU_table6.2-2_UC_areas.csv
					      
For historic reasons the land areas are collected directly from *lulucf_classes_all.txt*. The uncertainties can be found 
in *NIR/LU_table6.2-2_UC_areas.csv*. Inventory year is 2019 and output file LULUTable_6.2-2.xlsx.

#### check-lulucf-table-622.py
Remember to compare results from lulucf-table-622.py with values in *NIR/LU_table6.2-2_areas.csv*:

	(lukeghg) prompt% check-lulucf-table622.py -x LULUTable_6.2-2.xlsx  -n /data/projects/khk/ghg/2019/NIR/LU_table6.2-2_areas.csv \
	                                           -y 2019

Inventory year is 2019. Program simply echoes if differences in results occur or not. The `lulucf-table-622.py` program needs 
to be rewritten so that IPCC areas are read directly from NIR/LU_table6.2-2_areas.csv.  
						 
### lulucf-table-641.py
Produce NIR LULUCF Table 6.4-1. The usage is:

	(lukeghg) prompt% lulucf-table-641.py [-h] -i F1 -y F2 -o F3 (--format_only | --check_total)

The `--format-only` option reads the input file to a dataframe and simply writes it to an Excel file. 
The `--check-total` option calculates totals and compares results with precalculated values and writes Excel file.
These two options are mutually exclusive but mandatory: one of them must be present. For example:

	(lukeghg) prompt% lulucf-table-641.py -i /data/projects/khk/ghg/2019/NIR/Table_6.4-1_FLRem_Areas_of_organic_soils.csv -y 2019 \ 
	                                      -o LULUTable_6.4-1.xlsx --format_only

The input file *Table_6.4-1_FLRem_Areas_of_organic_soils.csv* is located each year in NIR directory.
Inventory year is 2019  and output file LULUTable_6.4-1.xlsx. **Note** the summary columns may deviate from the sums of 
their respective column constituents (in the order of 1 kha, the magnitude in the Table 6.4-1). 
This is due to roundings in the original data.
	
### kptable-appendix11b.py
Produce NIR Table Appendix11b in KPTable_Appendix11b.txt. Then read it to dataframe with *#* as a column separator
and produce Excel file KPTable_Appendix11b.xlsx. In the command line example inventory files are in *crf* directory: 

	(lukeghg) prompt%  kptable-appendix11b.py -s 1990 -e 2019 -o KPTable_Appendix11b.txt -d crf/

Inventory years are from 1990 to 2019.

### kptable-appendix11c.py
Produce NIR KPLULUCF Table Appendix11c in KPTable_Appendix11c.txt. Then read it to dataframe  with *#* as a column separator
and produce Excel file KPTable_Appendix11c.xlsx. In the command line example inventory files are in 'crf' directory: 

	(lukeghg) prompt%:  kptable-appendix11c.py -s 1990 -e 2019 -o KPTable_Appendix11c.txt -d crf/

Inventory years are from 1990 to 2019.

**NB:** Unlike in  LULUCF Table 6.1-2, for historic reasons, values collected for the Appendix11b and Appendix11c 
are *not* based on time series UID but on file row number. That is, *files should maintain their structure*. 
The data sources (file names with row numbers) appear at the bottom of the tables for each column.

### pretty-print-xml.py
CRFReporter xml files come without line endings. `pretty-print-xml.py` formats xml to more human readable 
form. This is useful when new UIDs must be found for GHG inventory:
	
	(lukeghg) prompt%: pretty-print-xml.py -i xml_input_file.xml -o xml_output_file.xml

## GitHub version control

Currently *lukeghg* package is in GitHub. Sample minimum gitgonfig file for Git is available in [Git](Git) directory. 
Download it, edit your name, email address and install it as *.gitconfig* in your home directory. 

## ToDo
There is a bit to do to reorganise the *lukeghg* package so that it is a proper python package  
in Python Package Index (PyPI) installable simply by `pip install lukeghg` to use out of the box.

## Reading

+ https://sorvi-int1.ns.luke.fi/sorvi-guides/ug/
+ https://docs.python.org/3/library/venv.html
+ https://docs.python.org/3/distutils/index.html
+ https://docs.python.org/3/distutils/setupscript.html
