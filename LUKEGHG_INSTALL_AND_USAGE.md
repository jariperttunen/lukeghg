# lukeghg: Installation and usage in sorvi server
The *lukeghg* python package contains tools to generate CRFReporter xml file from GHG inventory results for CRFReporter import, 
check missing work, compare results with previous year and generate some ubiquitous NIR tables.

## Contents

+ A Setup your working environment
+ B Install lukeghg python package
+ C Update  lukeghg python package
+ D GHG inventory to CRFReporter xml file
+ E GHG Scenarios
+ F Some other useful programs
+ Version control
+ Notes on hirsi server
+ References

The instructions are for `bash` shell in sorvi.  Your default shell
might be for example `tcsh` and you must for instance adjust hyphens
in command lines containing wild card searches accordingly.

## A Create python virtual environment

Create python virtual environment (called e.g. lukeghg) in your home directory
(The *prompt%* denotes your terminal command line prompt):

	prompt% /usr/bin/python3 -m venv lukeghg

Activate the virtual environment:

	prompt% source lukeghg/bin/activate
	(lukeghg) prompt%

Note the *(lukeghg)* appearing in front of your command prompt.

Check you have the latest versions of setuptools and wheel:

	(lukeghg) prompt% python3 -m pip install --upgrade setuptools wheel

**Tips**: It might make sense to create all python virtual environments under one directory
(with name *venv* for example): easier to locate and remember.

## B Install the lukeghg python package
We assume that the working directory will be in /data/shared/\<user\> in sorvi
where \<user\> denotes user name. For GitHub you need to have *.gitconfig* 
in your home directory. See *G Version control* at the end.

Create *GHGInventory* directory and clone lukeghg from GitHub. 

	(lukeghg) prompt% cd /data/shared/<user>
	(lukeghg) prompt% mkdir GHGInvenory
	(lukeghg) prompt% cd GHGInventory
	(lukeghg) prompt% git clone https://github.com/jariperttunen/lukeghg.git

Create the *wheel package* for lukeghg and install it to your virtual environment

	(lukeghg) prompt% cd GHGInventory/lukeghg/lukeghg
	(lukeghg) prompt% python3 setup.py sdist bdist_wheel
	(lukeghg) prompt% python3 -m pip install --upgrade dist/lukeghg-1.0-py3-none-any.whl

Now all the command line programs in lukeghg package are available. 

**Tips**: Naturally you can organise your work as you like including directory names. 
But as we will see lukeghg package contains template and configuration files that make 
the use of command line programs easier.

## C Update lukeghg python package

You need to update lukeghg package from GitHub whenever someone has made changes
and pushed the work there. Otherwise changes will not appear available in the virtual environment,

Remember to activate the virtual environment if needed (check your
prompt). The `~` character refers to your home directory. 

	prompt% source ~/lukeghg/bin/activate
	(lukeghg) prompt%

Update lukeghg package from GitHub. Make sure you are in `/data/shared/<user>/GHGInventory/lukeghg/` directory:

	(lukeghg) prompt% cd /data/shared/<user>/GHGInventory/lukeghg/
	(lukeghg) prompt% git pull

Update your lukeghg virtual environment next. As with the installation
recreate the wheel package, but now first remove the lukeghg package
and then upgrade lukeghg and its dependencies.
Make sure you are in `/data/shared/<users>/GHGInventory/lukeghg/lukeghg` where you
can see the *setup.py*  file.

	(lukeghg) prompt% cd data/shared/<user>/GHGInventory/lukeghg/lukeghg
	(lukeghg) prompt% python3 setup.py sdist bdist_wheel
	(lukeghg) prompt% python3 -m pip uninstall lukeghg
	(lukeghg) prompt% python3 -m pip install --upgrade dist/lukeghg-1.0-py3-none-any.whl

The `pip`command line allows other ways to achieve the same result but
this seems to be straightforward. Note that if `pip` is upgraded then `setuptools` 
and `wheel` must be upgraded too as in section *A Create python virtual envitonment*.  

**Tips**: Note we had to move a a bit inside the lukeghg package.

## D GHG inventory to CRFReporter xml file

`run-ghg-master.sh` is a script that sets directories and files for the current ghg inventory 
and inserts inventory results to CRFReporter PartyProfile xml.

The [`run-ghg-master.sh`](lukeghg/lukeghg/bin/run-ghg-master.sh) is located in [lukeghg/lukeghg/bin](lukeghg/lukeghg/bin)
directory. Edit the following command options if needed and update lukeghg package
as  in *C Update lukeghg python package*:

- -c Location of the GHG inventory files
- -n Location of the GHG iventory files for NIR section in CRFReporter
- -i Location of the GHG inventory comment files for CRFReporter
- -p Location of the empty (i.e. no inventory data) PartyProfile xml from CRFReporter.
     The naming convention is that it uses the name of the active inventory in CRFReporter.
     (see also **NB** at the end of chapter)
- -x Location of the PartyProfile result file to be imported to CRFReporter.
     The naming convention is  that it uses *_result* in addition of the name of the empty PartyProfile file. 
- -y Inventory year (the last year in CRFReporter)

`run-ghg-master.sh` contains also the options -b, -k,-l and -m (not shown here) that 
refer to ubiquitous configuration files and directories that come with the lukeghg package. 

#### Produce CRFReporter xml file
Make sure you are in /data/shared/\<user\>/GHGInventory/. First, create *crf* and *PartyProfile*
directories:

	(lukeghg) prompt% cd /data/shared/<user>/GHGInventory/
	(lukeghg) prompt% mkdir crf
	(lukeghg( prompt% mkdir PartyProfile

Second, copy GHG inventory files to *crf* directory:

	(lukeghg) prompt% scp <user>@hirsi.in.metla.fi:/hsan2/khk/ghg/2019/crf/*.csv crf/

It has been practice that all GHG inventory files are in the same *crf* directory.
Be sure the read rights to the files exists. Then download PartyProfile xml 
from CRFReporter and copy it to *PartyProfile* directory. Rename as denoted by the `-p` 
option in `run-ghg-master.sh`. To produce the PartyProfile  result file filled with the 
GHG inventory results type the two commands:

	(lukeghg) prompt% convertutf8.py -f crf/'*.csv'
	(lukeghg) prompt% run-ghg-master.sh > Import.log 2> Error.log

The GHG inventory result files (csv files) seem to use different encoding systems.
`convertutf8.py` converts them to utf8 if needed (this is why they need to be copied 
with `scp` to *crf* directory first). 

The script `run-ghg-master.sh` will run few minutes at most. 
The `>`character redirects standard out terminal output to *Import.log* file 
and `2>` redirects standard error terminal output to *Error.log* file.

The final step is to import the PartyProfile result file to CRFReporter.

For EU529 inventory there is similar `run-eu529-ghg-master.sh` script  in [lukeghg/lukeghg/bin](lukeghg/lukeghg/bin)
directory. Note EU529 concerns KPLULUCF files only (LULUCF files are not missing by accident).

**Tips**: Once you have this set-up you can use it also for the future inventories. 

#### GHG inventory files
The files are text (csv) files with white space as separator. Each line
in the file represent one time series for an emission, some area etc.
in the CRFReporter. The line begins with optional comment followed by the UID ("unique identifier")
of the time series and after that the time series itself. For example:

       #fl.to.cl# A4DB34A0-1847-401A-92BA-7CCE37611F1A -29.903 -28.157 -26.926 ... -14.865 -14.865 -14.865

The *#* character denotes the beginning and the end of the comment. The UID (*A4DB3 ...611F1A*) is CRFReporter generated.

**NB:** CRFReporter checks that the version number of the PartyProfile 
xml matches the CRFReporter version. Each CRFReporter version update requires new
PartyProfile xml from CRFReporter.

## E GHG Scenarios

`ghg-scenario.py` can generate excel file for ghg scenario calculations.
The command line is as follows. The `[]` denotes optional arguments. In `bash` 
the `\` character denotes the command line continues to the next line:

	(lukeghg) prompt% ghg-scenario.py [-h] --files FILES  --scen SCEN \
                          -m M -o O --start START --end END [--GWP GWP] [--noformulas]
     
- -h: python help
- --files: Give scenario csv files (wild card search). The format of
the files is the  same as in ghg inventory. A row consists of optional
but highly recommended comment part, UID of the time series followed by the time series.
- --scen: The template excel in lukeghg for results. It contains three sheets:
  - UIDMatrix: contains  UIDs  identifying times series.
  - LandUse: template for results for land use and land use change.
  - LULUCF: template for collecting LULUCF totals from land use and land use change. 
- -m: The UID mapping file as in run-ghg-master.sh.
- -o: Excel output file
- --start: The start year of the scenario inventory
- --end: The end year of the scenario inventory
- --GWP: Global warming potential for CH4 and N2O, possible values AR4 (GHG inventory) or AR5 (default)
- --noformulas: Sum up summary sheets. Default: Not present, use excel formulas in summary sheets

For the sample command line set your working directory to *GHGInventory* (as in *D GHG inventory to CRFReporter xml file*). 
Then, assuming the scenario result files are under *hiisi* directory type:

	(lukeghg) prompt% ghg-scenario.py --files 'hiisi/wem/crf/LU*.csv' --scen lukeghg/ScenarioTemplate/ScenarioTemplate.xlsx \ 
	          -m lukeghg/300_500_mappings_1.1.csv -o Hiisi_1990_2050.xlsx --start 1990 --end 2050

For further details see [GHG_SCENARIO](GHG_SCENARIO.md).

## F Some other useful programs

lukeghg package contains useful scripts for checks for the inventory 
and to generate some ubiquitous tables to appear in NIR. Standard python -h (help) option
prints short explanation for each command line option.

### ghg-todo.py: 
Compare two inventories and list missing time series and UIDs not
found. This sample command assumes that 2018 inventory is in 2018crf
directory and the output excel file is GHGToDo2019.xlsx.


	(lukeghg) prompt% ghg-todo.py -f1 '2018crf/[KPLU]*.csv' -f2 'crf/[KPLU]*.csv' -x PartyProfile/PartyProfile_FIN_2021_1.xml \
	  -o GHGToDo2019.xlsx -m lukeghg/300_500_mappings_1.1.csv -y 2019

Also, `ghg-todo.py` is a quick fix to help to bring together scenario predictions for
further analysis. Give all scenario result files for argument `-f1` and let 
the `-f2` be a listing that produces no files. For example:

	(lukeghg) prompt% ghg-todo.py -f1 'scen/[KPLU]*.csv' -f2 'scen/[KPLU]*.txt' -x PartyProfile/PartyProfile_FIN_2021_1.xml \
	   -o GHGToDo2019.xlsx -m lukeghg/300_500_mappings_1.1.csv -y 2019

This assumes that the scenario files are in *scen* directory and `-f2 scen/[KPLU]*.txt` produces empty list of files.
Better solution for scenario projects is under construction (E GHG Scenarios).

### checkinventoryvalues.py:
Compare two inventories and check for 1) too large differences in inventory values, 2) changes in notation keys and 
3) missing UID's. These will appear in their respective sections in the output file.

The sample command line assumes 2018 inventory  is in *2018crf* directory and 2019 inventory in *crf* directory.
Output file is *GHGComparison.txt*. Excel file of the same name (*GHGComparison.xlsx*) will also be generated. 

	(lukeghg) prompt% checkinventoryvalues.py -p '2018crf/[KPLU]*.csv' -c crf/[KPLU]*.csv -m crf/lukeghg/300_500_mappings_1.1.csv \
	  -f GHGComparison.txt -t 20
	  
The `-t` option defines that values that disagree 20% or more will be accounted for. More precisely, if two values for some 
inventory year in the same time series from the two inventories differ more than this threshold value, 
the two time series will appear in the result file.  
	

### lulucf-table-612.py:
Produce NIR Table 6-1.2 in LuluTable6-1.2.xlsx. In the command line example inventory files are in *crf* directory. 

	(lukeghg) prompt% lulucf-table-612.py -s 1990 -e 2019 -o LuluTable6-1.2.xlsx -d crf/
	  
Please note you must have set up public private key for `ssh`. `lulucf-table-612.py`  will fetch biomasses 
(the first two rows in the table) from hirsi server for the current inventory year.

### kptable-appendix11b.py:
Produce NIR Table Appendix11b in KPTable_Appendix11b.txt. Read it to excel with *#* as a column separator.
In the command line example inventory files are in *crf* directory. 

	(lukeghg) prompt%  kptable-appendix11b.py -s 1990 -e 2019 -o KPTable_Appendix11b.txt -d crf/

### kptable-appendix11c.py:
Produce NIR Table Appendix11c in KPTable_Appendix11c.txt. Read it to excel with *#* as a column separator
In the command line example inventory files are in 'crf' directory. 

	(lukeghg) prompt%:  kptable-appendix11c.py -s 1990 -e 2019 -o KPTable_Appendix11c.txt -d crf/

## Version control

Currently *lukeghg* is in GitHub. Sample gitgonfig file for git is available
in Git directory. Edit email and your name and install it as *.gitconfig* in your home directory. 

## Notes on hirsi-server

hirsi server will be phased out in the near future (winter, spring 2021).
The parts of the manual refering to hirsi are due to change to reflect  the fact
the GHG inventory will be done in sorvi completely.

## References

+ https://sorvi-int1.ns.luke.fi/sorvi-guides/ug/
+ https://docs.python.org/3/library/venv.html
+ https://docs.python.org/3/distutils/index.html
+ https://docs.python.org/3/distutils/setupscript.html
