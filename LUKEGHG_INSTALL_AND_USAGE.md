# lukeghg: Installation and usage in sorvi server
The *lukeghg* python package contains command line tools to generate CRFReporter xml file from 
GHG inventory results for CRFReporter import, check missing work, compare results with 
previous year and generate some ubiquitous NIR tables. There are no intentions to make graphical user interface.

The instructions are for `bash` shell in sorvi.  Your default shell
might be for example `tcsh` and you must for instance adjust quotation marks (')
in command lines containing wild cards accordingly.

## Contents

1. Create python virtual environment
2. Install lukeghg python package
3. Update  lukeghg python package
4. GHG inventory to CRFReporter xml file
5. GHG Scenarios
6. Other useful programs
+ Version control
+ Notes on hirsi server
+ Reading


## 1. Create python virtual environment

Create python virtual environment (called e.g. lukeghg) in your home directory
(The *prompt%* denotes your terminal command line prompt):

	prompt% /usr/bin/python3 -m venv lukeghg

Activate the virtual environment:

	prompt% source lukeghg/bin/activate
	(lukeghg) prompt%

Note the *(lukeghg)* appearing in front of your command prompt.

Check you have the latest versions of `pip`, *setuptools* and *wheel* installed:

	(lukeghg) prompt% python3 -m pip install --upgrade pip
	(lukeghg) prompt% python3 -m pip install --upgrade setuptools wheel

**Tips**: Consider creating all python virtual environments under one directory
(*venv* for example).

## 2. Install the lukeghg python package
We assume that the working directory will be in */data/shared/\<user\>* in sorvi
server where *\<user\>* denotes your user name. For GitHub you need to have *.gitconfig* 
in your home directory. See *Version control* at the end.

Create *GHGInventory* directory and clone lukeghg from GitHub:

	(lukeghg) prompt% cd /data/shared/<user>
	(lukeghg) prompt% mkdir GHGInvenory
	(lukeghg) prompt% cd GHGInventory
	(lukeghg) prompt% git clone https://github.com/jariperttunen/lukeghg.git

Create the *wheel package* for lukeghg and install it to your virtual environment:

	(lukeghg) prompt% cd GHGInventory/lukeghg/lukeghg
	(lukeghg) prompt% python3 setup.py sdist bdist_wheel
	(lukeghg) prompt% python3 -m pip install --upgrade dist/lukeghg-1.0-py3-none-any.whl

All the command line programs in lukeghg package are now available in your virtual environment. 
The programs are located in [lukeghg/lukeghg/bin](lukeghg/lukeghg/bin) in *lukeghg* package.

**Tips**: Naturally you can organise your work as you like including directory names. 
But as we will see lukeghg package contains template and configuration files that make 
the use of command line programs easier. So try this schema first and improve later.

## 3. Update lukeghg python package

You need to update lukeghg package from GitHub whenever someone has made changes
and pushed the work there. Otherwise changes will not appear available in the virtual environment,

Remember to activate the virtual environment if needed (check your
prompt). The `~` character refers to your home directory: 

	prompt% source ~/lukeghg/bin/activate
	(lukeghg) prompt%

Update lukeghg package from GitHub. Make sure you are in `/data/shared/<user>/GHGInventory/lukeghg/` directory:

	(lukeghg) prompt% cd /data/shared/<user>/GHGInventory/lukeghg/
	(lukeghg) prompt% git pull

Update your lukeghg virtual environment next. As with the installation
recreate the wheel package, but now first remove the lukeghg package
and then upgrade lukeghg and its dependencies.
Make sure you are in `/data/shared/<user>/GHGInventory/lukeghg/lukeghg`:

	(lukeghg) prompt% cd /data/shared/<user>/GHGInventory/lukeghg/lukeghg
	(lukeghg) prompt% python3 setup.py sdist bdist_wheel
	(lukeghg) prompt% python3 -m pip uninstall lukeghg
	(lukeghg) prompt% python3 -m pip install --upgrade dist/lukeghg-1.0-py3-none-any.whl

The `pip`command line allows other ways to achieve the same result but
this seems to be the most straightforward. 

**Tips**: Note we had to move around a bit inside the lukeghg package. 
In case `pip` requires update, upgrade also *setuptools* and *wheel* (*1. Create python virtual environment*).

## 4. GHG inventory to CRFReporter xml file

[`run-ghg-master.sh`](lukeghg/lukeghg/bin/run-ghg-master.sh) is a shell script that sets directories 
and files for `ghg-master.py` python script to insert GHG inventory results in the CRFReporter PartyProfile xml. 
Edit the following command line options if needed and update lukeghg package as  in *3. Update lukeghg python package*:

- -c Location of the GHG inventory files.
- -n Location of the GHG iventory files for NIR section in CRFReporter.
- -i Location of the GHG inventory comment files for CRFReporter.
- -p Location of the empty (i.e. no inventory data) PartyProfile xml from CRFReporter.
     The naming convention is that it uses the name of the active inventory in CRFReporter
     (see also **NB** at the end of chapter).
- -x Location of the PartyProfile result file to be imported to CRFReporter.
     The naming convention is  that it appends *_result* to the empty PartyProfile file name. 
- -y Inventory year (the last year in CRFReporter).

`ghg-master.py` has also the options -b, -k,-l and -m (not shown here) that 
refer to ubiquitous configuration files and directories that come with the *lukeghg* package. 

#### Produce CRFReporter xml file

Make sure you have activated *lukeghg* python virtual environment and you are in */data/shared/\<user\>/GHGInventory*. 
Then create *crf* and *PartyProfile* directories for GHG Inventory result files and PartyProfile xml files respectively:

	(lukeghg) prompt% cd /data/shared/<user>/GHGInventory/
	(lukeghg) prompt% mkdir crf
	(lukeghg( prompt% mkdir PartyProfile

Copy GHG inventory files to *crf* directory. Be sure the read rights for the files exists, e.g. 2020 inventory:

	(lukeghg) prompt% scp /data/projects/khk/ghg/2020/crf/*.csv crf/

It has been practice that all GHG inventory results are by year in the same *ghg/\<year\>/crf* directory on the server.

Download PartyProfile xml from CRFReporter and copy it to *PartyProfile* directory. 
Rename as denoted by the `-p`  option in `run-ghg-master.sh`. To produce the PartyProfile 
result file filled with the  GHG inventory results type the two commands:

	(lukeghg) prompt% convertutf8.py -f 'crf/*.csv'
	(lukeghg) prompt% run-ghg-master.sh > Import.log 2> Error.log

The GHG inventory result files (csv files) seem to use different encoding systems.
`convertutf8.py` converts them to utf8 if needed (this is why they need to be copied 
with `scp` to *crf* directory first).  The script `run-ghg-master.sh` will run few minutes at most. 
The `>`character redirects standard out terminal output to *Import.log* file 
and `2>` redirects standard error terminal output to *Error.log* file.

The final step is to import the PartyProfile result file to CRFReporter.

For EU529 inventory there is similar [`run-eu529-ghg-master.sh`](lukeghg/lukeghg/bin/run-eu529-ghg-master.sh). 
Note EU529 concerns KPLULUCF files only (LULUCF files are not missing by accident).

**Tips**: Once you have this set-up you can use it also for the future inventories. Always check that
you have the right active inventory in CRFReporter. Each year CRFReporter requires 
[manual work](CRFREPORTER_ANNUAL_CHECK.md) that needs to be done.

**NB:** CRFReporter checks that the version number of the PartyProfile 
xml matches the CRFReporter version. Each CRFReporter version update requires new
PartyProfile xml from CRFReporter, even during the same active inventory. 

#### GHG inventory files
The files are text (csv) files with white space as the delimeter mark. Each line
in the file represent one time series for an emission, some area etc.
in CRFReporter. The line begins with optional comment, then the UID ("unique identifier")
of the time series followed by the time series itself. For example:

       #fl.to.cl# A4DB34A0-1847-401A-92BA-7CCE37611F1A -29.903 -28.157 -26.926 ... -14.865 -14.865 -14.865

The *#* character denotes the beginning and the end of the comment. The UID (*A4DB3 ...611F1A*) is CRFReporter generated.

## 5. GHG Scenarios

`ghg-scenario.py` can generate excel file for ghg scenario calculations.
The command line is as follows. Brackets ([]) denote optional arguments. In `bash` 
the backslash (\\) denotes the command line continues to the next line:

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
- --noformulas: Add up values in summary sheets. Default: Not present, generate excel formulas in summary sheets

For further details see [GHG_SCENARIO](GHG_SCENARIO.md).

## 6. Other useful programs

lukeghg package contains useful scripts for checks for the inventory 
and to generate some ubiquitous tables to appear in NIR. Standard python -h (help) option
prints short explanation for each command line option.

### ghg-todo.py
Compare two inventories and list missing time series and UIDs not
found. This sample command assumes that 2018 inventory is in 2018crf
directory and the output excel file is GHGToDo2019.xlsx:

	(lukeghg) prompt% ghg-todo.py -f1 '2018crf/[KPLU]*.csv' -f2 'crf/[KPLU]*.csv' -x PartyProfile/PartyProfile_FIN_2021_1.xml \
	  -o GHGToDo2019.xlsx -m lukeghg/300_500_mappings_1.1.csv -y 2019

### checkinventoryvalues.py
Compare two inventories and check for 1) too large differences in inventory values, 2) changes in notation keys and 
3) missing UID's. These will appear in their respective sections in the output file.

The sample command line assumes 2018 inventory  is in *2018crf* directory and 2019 inventory in *crf* directory.
Output file is *GHGComparison.txt*. Excel file of the same name (*GHGComparison.xlsx*) will also be generated:

	(lukeghg) prompt% checkinventoryvalues.py -p '2018crf/[KPLU]*.csv' -c crf/[KPLU]*.csv -m crf/lukeghg/300_500_mappings_1.1.csv \
	  -f GHGComparison.txt -t 20
	  
The `-t` option defines that values that disagree 20% or more will be accounted for. More precisely, if two values for some 
inventory year in the same time series from the two inventories differ more than this threshold value, 
the two time series will appear in the result file.  
	

### lulucf-table-612.py
Produce NIR Table 6-1.2 in LuluTable6-1.2.xlsx. In the command line example inventory files are in *crf* directory: 

	(lukeghg) prompt% lulucf-table-612.py -s 1990 -e 2019 -o LuluTable6-1.2.xlsx -d crf/
	  
**Note**: `lulucf-table-612.py`  will fetch biomasses (the first two rows in the table) 
from precalculated files for the current inventory year.

### kptable-appendix11b.py
Produce NIR Table Appendix11b in KPTable_Appendix11b.txt. Read it to excel with *#* as a column separator.
In the command line example inventory files are in *crf* directory: 

	(lukeghg) prompt%  kptable-appendix11b.py -s 1990 -e 2019 -o KPTable_Appendix11b.txt -d crf/

### kptable-appendix11c.py
Produce NIR Table Appendix11c in KPTable_Appendix11c.txt. Read it to excel with *#* as a column separator
In the command line example inventory files are in 'crf' directory: 

	(lukeghg) prompt%:  kptable-appendix11c.py -s 1990 -e 2019 -o KPTable_Appendix11c.txt -d crf/
	
### pretty-print-xml.py
CRFReporter xml files come without line endings. `pretty-print-xml.py` formats xml to more human readable 
form. This is useful when new UIDs must be found for GHG inventory:
	
	(lukeghg) prompt%: pretty-print-xml.py -i xml_input_file.xml -o xml_output_file.xml

## Version control

Currently *lukeghg* package is in GitHub. Sample minimum gitgonfig file for Git is available in [Git](Git) directory. 
Download it, edit your name, email address and install it as *.gitconfig* in your home directory. 

## Notes on hirsi-server

hirsi server will be phased out in the near future (winter, spring 2021).
The parts of the manual refering to hirsi are due to change to reflect  the fact
the GHG inventory will be done in sorvi completely.

## Reading

+ https://sorvi-int1.ns.luke.fi/sorvi-guides/ug/
+ https://docs.python.org/3/library/venv.html
+ https://docs.python.org/3/distutils/index.html
+ https://docs.python.org/3/distutils/setupscript.html
