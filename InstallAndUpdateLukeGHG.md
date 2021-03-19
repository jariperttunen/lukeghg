# Install and update lukeghg python package in sorvi server

The *lukeghg* package contains tools to generate CRFReporter xml file from GHG inventory results for CRFReporter import, 
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

## A Setup your working environment

Create python virtual environment (called e.g. lukeghg) in your home directory
(The *prompt%* denotes your terminal command line prompt):

	prompt% /usr/bin/python3 -m venv lukeghg

Activate the virtual environment:

	prompt% source lukeghg/bin/activate
	(lukeghg) prompt%

Note the *(lukeghg)* appearing in front of your command prompt.

Check you have the latest versions of setuptools and wheel:

	(lukeghg) prompt% python3 -m pip install --upgrade setuptools wheel

Create public private keys for ssh login to hirsi:

The manual for the sorvi server has good instructions but in short you do the
following two commands:

	(lukeghg) prompt% ssh-keygen -t rsa -b 4096
	(lukeghg) prompt% ssh-copy-id <username>@hirsi.in.metla.fi

Now you should be able to login to hirsi.in.metla.fi with ssh (without
password). Check that this is possible. You will need this when
generating NIR Table 6.1-2 with `lulucf-table-612.py` (F Some other useful programs):

	(lukeghg) prompt% ssh  hirsi.in.metla.fi

## B Install the lukeghg python package

For GitHub you need to have *.gitconfig* in your home directory.
See item G Version control at the end.

Clone lukeghg from GitHub for example to `/data/shared/<user>`.
`<user>` denotes your user name and `<GHGInventoryDirectory>` the name
of your choice for the working directory.

	(lukeghg) prompt% cd /data/shared/<user>
	(lukeghg) prompt% mkdir <GHGInventoryDirectory>
	(lukeghg) prompt% cd <GHGInventoryDirectory>
	(lukeghg) prompt% git clone https://github.com/jariperttunen/lukeghg.git

Create the wheel package for lukeghg and install it to your virtual environment

	(lukeghg) prompt% cd <GHGInventoryDirectory>/lukeghg/lukeghg
	(lukeghg) prompt% python3 setup.py sdist bdist_wheel
	(lukeghg) prompt% python3 -m pip install --upgrade dist/lukeghg-1.0-py3-none-any.whl

## C Update lukeghg python package

You need to update lukeghg package from GitHub whenever someone has made changes
and pushed the work there. Otherwise changes will not appear available in the virtual environment,

Remember to activate the virtual environment if needed (check your
prompt). The `~` character refers to your home directory. 

	prompt% source ~/lukeghg/bin/activate
	(lukeghg) prompt%

Update lukeghg package from GitHub. Make sure you are in
`<GHGInventoryDirectory>/lukeghg/` directory:

	(lukeghg) prompt% git pull

Update your lukeghg virtual environment next. As with the installation
recreate the wheel package, but now first remove the lukeghg package
and then upgrade lukeghg and its dependencies.
Make sure you are in `<GHGInventoryDirectory>/lukeghg/lukeghg` where you
can see the *setup.py*  file.

	(lukeghg) prompt% python3 setup.py sdist bdist_wheel
	(lukeghg) prompt% python3 -m pip uninstall lukeghg
	(lukeghg) prompt% python3 -m pip install --upgrade dist/lukeghg-1.0-py3-none-any.whl

The `pip`command line allows other ways to achieve the same result but
this seems to be straightforward.

## D. GHG inventory to CRFReporter xml file

Probably the most important part in this manual. `run-ghg-master.sh` is a script that sets directories and files
for the current ghg inventory and inserts inventory results to CRFReporter PartyProfile xml.

The `run-ghg-master.sh`is located in `<GHGInventoryDirectory>/lukeghg/lukeghg/lukeghg/bin`
directory. Edit the following command options if needed:

- -c Location of the GHG inventory files
- -n Location of the GHG iventory files for NIR section in CRFReporter
- -i Location of the GHG inventory comment files for CRFReporter
- -p Location of the empty (i.e. no inventory data) PartyProfile xml from CRFReporter
- -x Location of the PartyProfile result file to be imported to CRFReporter
- -y Inventory year (the last year in CRFReporter)

It has been practice that all GHG inventory files are in the same *crf* directory.

Practical note: the options -b, -k,-l and -m (in `run-ghg-master.sh`, not shown here) 
refer to ubiquitous configuration files that come with the lukeghg package. 
Thus after downloading lukeghg from GitHub create *crf* and *PartyProfile* directories in
`<GHGInventoryDirectory>` and run the `run-ghg-master.sh` script 
in `<GHGInventoryDirectory>`. 

The xml for CRFReporter can be produced as follows. Make sure you are
in `<GHGInventoryDirectory>`. First, copy GHG inventory files to crf directory:

	(lukeghg) prompt% scp <user>@hirsi.in.metla.fi:/hsan2/khk/ghg/2019/crf/*.csv crf/

Be sure the read rights to the files exists. Then, if needed, download PartyProfile xml 
from CRFReporter and copy it to *PartyProfile* directory. Rename as denoted by the `-p` 
option in `run-ghg-master.sh`. To produce the PartyProfile  result file  filled with the 
GHG inventory results (the option `-x`) type the two commands:

	(lukeghg) prompt% convertutf8 -f crf/'*.csv'
	(lukeghg) prompt% run-ghg-master.sh > Import.log 2> Error.log

The GHG inventory result files (csv files) seem to use different encoding systems.
`convertutf8` converts them to utf8 if needed (this is why they need to be copied with `scp` to *crf* directory first). 

The script `run-ghg-master.sh` will run few minutes at most. 
The `>`character redirects standard out terminal output to *Import.log* file 
and `2>` redirects standard error terminal output to *Error.log* file.

The final step is to import the PartyProfile result file from CRFReporter.

For EU529 there is similar `run-eu529-ghg-master.sh` script. Note EU529
concerns KPLULUCF files only (LULUCF files are not missing by accident).

**NB:** CRFReporter checks that the version number of the PartyProfile 
xml matches the CRFReporter version. Each CRFReporter version update requires new
PartyProfile xml from CRFReporter.

## E GHG Scenarios

`ghg-scenario.py` can generate excel file for ghg scenario calculations.
The command line is as follows. The `[]` denotes optional arguments:

	(lukeghg) prompt% ghg-scenario.py [-h] --files FILES --uid UID --scen SCEN \
     [--keys] -m M -o O --start START --end END [--GWP GWP]

- -files: Give scenario csv files as wild card search. The format of
the files is the  same as in ghg inventory. A row consists of optional
but highly recommended comment part, UID of the time series followed by the time series.

- -uid: The UIDMatrix excel file containing the UID for each
  time series. The file is  `<GHGInventoryDirectory>/ScenarioTemplate/UIDMatrix.xlsx`.

- -scen: The template excel for results. Using  this template
   `ghg-scenario.py` generates excel sheet for each land use  and land
  use change classes. The file is `<GHGInventoryDirectory>/ScenarioTemplate/ScenarioTemplate.xlsx`.

- -keys: Maintain notation keys. This is boolean argument. That is, if
  not given the notation keys are set to number zero.

- -m: The UID mapping file as in run-ghg-master.sh.

- -o: Excel output file

- -start: The start year of the scenario inventory
- -end: The end year of the scenario inventory

- -GWP: Global warming potential for CH4 and N2O, possible values AR4 (GHG inventory) or AR5 (default)

For the sample command line set your working directory to
`<GHGInventoryDirectory>`. Then, assuming the scenario result files
are in DGClima directory type the following. In `bash`the `\` character denotes the
command line continues to the next line.:

	(lukeghg) prompt% ghg-scenario.py --files 'DGClima/*.csv' --uid lukeghg/ScenarioTemplate/UIDMatrix.xlsx \
      --scen lukeghg/ScenarioTemplate/ScenarioTemplate.xlsx -m lukeghg/300_500_mappings_1.1.csv \
      -o DGClima.xlsx --start 1990 --end 2018 --keys

The first sheet in the Excel result file *DGClima.xlsx* lists UID's in
UIDMatrix excel file but not found in the inventory. The second sheet shows the GWP's used. Following sheets
represent scenario results for each land use and land use change
class. Summation rows are marked yellow. Cells missing data are marked red.

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
