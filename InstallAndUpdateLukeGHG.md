Install and update lukeghg python package, sorvi
==================================
Contents
-------
A Setup your working environment
B Install *lukeghg* python package
C Update  *lukeghg* python package
D GHG inventory to CRFReporter xml file: basic workflow
E Some other useful programs
F Version control

The instructions are for bash shell in sorvi.  Your default shell
might be for example *tcsh* and you must e.g. adjust hyphens
in command lines including wild card searches accordingly.

A Setup your working environment
------------------------------
1. Create python virtual environment (called e.g. lukeghg) in your home directory

(The *prompt%* denotes your terminal command line prompt).

prompt% `/usr/bin/python3 -m venv lukeghg`

2. Activate the virtual environment

prompt% `source lukeghg/bin/activate`
(lukeghg) prompt%

Note the *'(lukeghg)'* appearing in front of your command prompt.

3. Check you have the latest versions of setuptools and wheel 

(lukeghg) prompt% `python3 -m pip install --upgrade setuptools wheel`

4. Create public private keys for ssh login to hirsi

The manual for the sorvi server has good instructions but in short you do the
following two commands:

(lukeghg) prompt% `ssh-keygen -t rsa -b 4096`
(lukeghg) prompt% `ssh-copy-id <username>@hirsi.in.metla.fi`

Now you should be able to login to hirsi.in.metla.fi with ssh (without
password). Check that this is possible. You will need this when
generating lulucf-table-612.py:

(lukeghg) prompt% ssh  hirsi.in.metla.fi


B Install 'lukeghg' python package
-----------------------------
For GitHub you need to have ".gitconfig" in your home directory.
See item F Version control at the end.

1. Install lukeghg python package to the virtual environment
*<user>* denotes your user name and *<GHGInventoryDirectory>* the name
of your choice for the working directory.

1.1 Clone lukeghg from GitHub for example to `/data/shared/<user>`
(lukeghg) prompt% `cd /data/shared/<user>`
(lukeghg) prompt% `mkdir <GHGInventoryDirectory>`
(lukeghg) prompt% `cd <GHGInventoryDirectory>`
(lukeghg) prompt% `git clone https://github.com/jariperttunen/lukeghg.git`

1.2 Create the wheel package for lukeghg and install it 

(lukeghg) prompt% `cd <GHGInventoryDirectory>/lukeghg/lukeghg`
(lukeghg) prompt% `python3 setup.py sdist bdist_wheel`
(lukeghg) prompt% `python3 -m pip install --upgrade dist/lukeghg-1.0-py3-none-any.whl`

C Update lukeghg python package
-----------------------------
You need to update lukeghg package from GitHub whenever someone has made changes
and pushed the work the  there. Otherwise changes will not appear available in the virtual environment,

1. Remember to activate the virtual environment (check your prompt). 

prompt% `source ~/lukeghg/bin/activate`
(lukeghg) prompt%

2. Update lukeghg package from GitHub. Make sure you are in <GHGInventoryDirectory>/lukeghg/

(lukeghg) prompt% git pull

3. Update lukeghg virtual environment

As with the first install recreate the wheel package, but now first remove
the lukeghg package and then upgrade lukeghg and its dependencies.
Make sure you are in <GHGInventoryDirectory>/lukeghg/lukeghg where you
can see setup.py file.

(lukeghg) prompt%: `python3 setup.py sdist bdist_wheel`
(lukeghg) prompt%: `python3 -m pip uninstall lukeghg`
(lukeghg) prompt%: `python3 -m pip install --upgrade dist/lukeghg-1.0-py3-none-any.whl`

The `pip`command line allows other ways to achieve the same thing but
this seems to be straightforward.

D. GHG inventory to CRFReporter xml file: basic workflow
------------------------------------------------

`run-ghg-master.sh` is a script that sets directories and files
for the current ghg inventory and inserts inventory results to PartyProfile xml.

The `run-ghg-master.sh`is located in `<GHGInventoryDirectory>/lukeghg/lukeghg/lukeghg/bin`
directory. Edit the following command options if needed:

- -c Location of the GHG inventory files
- -p Location of the empty (i.e. no inventory data) PartyProfile xml from CRFReporter
- -x Location of the PartyProfile result file to be imported to CRFReporter
- -n Location of the specific NIR files
- -i Location of the Comment files
- -y Inventory year (last year in CRFReporter)

\note Note in addition that the options -b, -k,-l and -m refer to ubiquitous configuration
files. They come with the lukeghg package. Thus after downloading
lukeghg from GitHub create `crf` and `PartyProfile` directories in
`<GHGInventoryDirectory>` and run the `run-ghg-master.sh` script 
in <GHGInventoryDirectory>. 

The xml for CRFReporter can be produced as follows. Make sure you are
in <GHGInventoryDirectory>.

1. Copy GHG inventory files to crf directory.
(lukeghg) prompt%: scp <user>@hirsi.in.metla.fi:/hsan2/khk/ghg/2019/crf/*.csv crf/

2. If needed download PartyProfile xml from CRFReporter and copy it to PartyProfile
directory. Rename as denoted by the -p option in run-ghg-master.sh. 

3. To produce xml with inventory results type the two commands 
(lukeghg) prompt%: python3 -m lukeghg.utility.convertutf8 -f crf/'*.csv'
(lukeghg) prompt%: run-ghg-master.sh > Import.log 2> Error.log

The GHG inventory result files (csv files) seem to use different encoding systems.
convertutf8 converts them to utf8 (this is why they need to be copied with scp to crf directory first). 
The script run-ghg-master.sh will run few minutes at most. 
The '>' character redirects 'standard out' terminal output to Import.log file 
and '2>' redirects 'standard error' terminal output to Error.log file.

For EU529 there is similar run-eu529-ghg-master.sh script. Note EU529
concerns KPLULUCF files only (LULUCF files are not missing by accident).

Please note CRFReporter checks that the version number of the PartyProfile 
xml matches the CRFReporter version. Each CRFReporter update requires new
PartyProfile xml from CRFReporter.

E GHG Scenarios
--------------

ghg-scenario.py can generate excel file for ghg scenario calculations.
The command line is as follows

ghg-scenario.py [-h] [--files FILES] [--uid UID] [--scen SCEN] [--keys]
                           [-m M] [-o O] [--start START] [--end END]

--files: Give scenario csv files as wild card search. The format of
the files is the  same as in ghg inventory. A row consists of optional
but highly recommended comment part, UID of the time series followed by the time series.

--uid: The UIDMatrix excel file containing the UID for each
  time series. The file is  ScenarioTemplate/UIDMatrix.xlsx.

--scen: The template excel for results. Using  this template
  ghg-scenario.py generates excel sheet for each land use  and land
  use change classes. The file is ScenarioTemplate/ScenarioTemplate.xlsx.

--keys: Maintain notation keys. This is boolean argument. That is, if
  not given the notation keys are set to number zero.

-m: The UID mapping file as in run-ghg-master.sh.

-o: Excel output file

--start: The start year of the scenario inventory
--end: The end year of the scenario inventory

For the sample command line set your working directory to
<GHGInventoryDirectory>. Then, assuming the scenario result files
are in DGClima directory type the following:

ghg-scenario.py --files 'DGClima/*.csv' --uid lukeghg/ScenarioTemplate/UIDMatrix.xlsx \
      --scen lukeghg/ScenarioTemplate/ScenarioTemplate.xlsx -m lukeghg/300_500_mappings_1.1.csv \
      -o DGClima.xlsx --start 1990 --end 2018 --keys

The first sheet in the Excel result file (DGClima.xlsx) lists UID's in
UIDMatrix excel file but not in the inventory. Following sheets
represent scenario results for each land use and land use change
class. Summation rows are marked yellow. Cells missing data are marked red.

F Some other useful programs
-------------------------
lukeghg package contains useful scripts for checks during the inventory 
and to generate some ubiquitous tables for NIR. Each one has -h (help) option
that should print explanation for each command line option.

1. ghg-todo.py: 
Compare two inventories and list missing time series and UIDs not
found. This sample command assumes that 2018 inventory is in 2018crf
directory and the output excel file is GHGToDo2019.xlsx.


(lukeghg) promt% ghg-todo.py -f1 '2018crf/[KPLU]*.csv' -f2 'crf/[KPLU]*.csv' -x PartyProfile/PartyProfile_FIN_2021_1.xml -o GHGToDo2019.xlsx -m lukeghg/300_500_mappings_1.1.csv -y 2019

Also, ghg-todo.py is a quick fix to help to bring together scenario predictions for
further analysis. Give all scenario result files for argument -f1 and let 
the -f2 be a listing that produces no files. For example:

(lukeghg) promt% ghg-todo.py -f1 'scen/[KPLU]*.csv' -f2 'scen/[KPLU]*.txt' -x PartyProfile/PartyProfile_FIN_2021_1.xml -o GHGToDo2019.xlsx -m lukeghg/300_500_mappings_1.1.csv -y 2019

This assumes that the scenario files are in 'scen' directory and '-f2 scen/[KPLU]*.txt' produces empty list of files.
Better solution for scenario projects is under construction.


2. lulucf-table-612.py:
Produce Table 6-1.2 in LuluTable6-1.2.xlsx. In the command line example inventory files are in 'crf' directory. 

(lukeghg) prompt% lulucf-table-612.py -s 1990 -e 2019 -o LuluTable6-1.2.xlsx -d crf/

Please note you must have set up public private key for
ssh. lulucf-table-612.py  will fetch biomasses (first two rows in the table) from
hirsi for the current inventory year.

3. kptable-appendix11b.py:
Produce Table Appendix11b in KPTable_Appendix11b.txt. Read it to excel with '#' as a column separator.
In the command line example inventory files are in 'crf' directory. 

(lukeghg) prompt%  kptable-appendix11b.py -s 1990 -e 2019 -o KPTable_Appendix11b.txt -d crf/

4. kptable-appendix11c.py:
Produce Table Appendix11c in KPTable_Appendix11c.txt. Read it to excel with '#' as a column separator
In the command line example inventory files are in 'crf' directory. 

(lukeghg) prompt%  kptable-appendix11c.py -s 1990 -e 2019 -o KPTable_Appendix11c.txt -d crf/


G Version control
--------------

Currently lukeghg is in GitHub. Sample gitgonfig for git is available
in Git directory. Edit email and your name and install it as ".gitconfig" in your home directory. 

Notes on hirsi-server
------------------
hirsi server will be phased out in the near future (winter, spring 2021).
The parts of the manual refering to hirsi are due to change to reflect  the fact
the GHG inventory will be done in sorvi completely.

References
--------
https://sorvi-int1.ns.luke.fi/sorvi-guides/ug/
https://docs.python.org/3/library/venv.html
https://docs.python.org/3/distutils/index.html
https://docs.python.org/3/distutils/setupscript.html