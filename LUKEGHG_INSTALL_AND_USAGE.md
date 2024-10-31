# lukeghg: Installation and usage in sorvi server
The *lukeghg* Python package contains command line tools to generate CRT json  file (Common Reporting Tables)
from GHG inventory results for CRT json import in ETF Reporting Tool (Enhanced Transparency Framework).

**The instructions are for `bash` shell in sorvi**. Your default shell might be for example `tcsh` 
and you must for instance adjust quotation marks (') in the examples to fit `tcsh` shell's syntax. 

## 1. Create Python virtual environment

Create Python virtual environment (called e.g. *lukeghg*) for example in your home directory.

	/usr/bin/python3 -m venv lukeghg

Activate the virtual environment:

	source lukeghg/bin/activate
	(lukeghg)

Note the name of the virtual environment *(lukeghg)* appearing in front of your command prompt.

Check you have the latest versions of `pip`, *setuptools* and *wheel* installed:

	(lukeghg) python3 -m pip install --upgrade pip
	(lukeghg) python3 -m pip install --upgrade setuptools wheel build

You can now install *lukeghg* Python package. You can quit the virtual environment with the `deactivate` command.

> [!NOTE]
> If you have any problems creating the virtual environment check your `.bashrc` file. For example 
> if you are part of NFI  you may have settings by NFI that  disrupt the `python3`
> environment installed in sorvi.

> [!TIP] 
> One can collect Python virtual environments under one directory (*venv* for example). 

## 2. Install the lukeghg Python package
Choose your working directory. Use `git` to download *lukeghg* package.

	(lukeghg) git clone https://github.com/jariperttunen/lukeghg.git

Create the *wheel package* for *lukeghg* and install it to your virtual environment. 
[`setup.py`](lukeghg/setup.py) is the configuration file with instructions 
for Python package dependencies and virtual environment set-up:

	(lukeghg) cd lukeghg/lukeghg
	(lukeghg) python3 -m build --wheel .
	(lukeghg( python3 -m pip install  dist/lukeghg-1.0-py3-none-any.whl

You should see *setup.py* file where the `python3 -m build --wheel .` command is made.

All the terminal command line programs in *lukeghg* package are now available in your virtual environment
(see *~/lukeghg/bin/* in your home directory). In the *lukeghg* package hierarchy the programs are located
in the [lukeghg/lukeghg/bin](lukeghg/lukeghg/bin) directory.

## 3. Update the lukeghg Python package

You need to update the *lukeghg* package from GitHub whenever you or someone else has made changes
and edits in the package to make the changes to appear in the virtual environment.

Remember to activate the virtual environment if needed (check your
prompt). The tilde (~) character in `bash` expands to your home directory: 

	source ~/lukeghg/bin/activate

Use `git` to update *lukeghg* package from GitHub in case someone has made contributions to the package.

	(lukeghg) cd \<working director\>/lukeghg/
	(lukeghg) git pull
	(lukeghg) cd lukeghg
	(lukeghg) python3 -m build --wheel .
	(lukeghg) python3 -m pip install --force-reinstall dist/lukeghg-1.0-py3-none-any.whl

Note that one has to move a bit in the directory hierarchy. You should see *setup.py* file where the `python3 -m build --wheel .` 
command is made.

## 4 The CRT programs

All CRT utility programs for the GHG inventory have the *-h* command line option for help.

### 4.1 crttool.py

Program creates the CRT json file from GHG inventory results. The command line needs the GHG inventory files and
the CRT json file as command line arguments:

	(lukeghg) crttool.py --crf /data/projects/khk/ghg/2023/crf/'LU*.csv' --json FIN-CRT-2025-V0-3-DataEntry-20241028-082756.json --year 2023  --out FIN-CRT-2025-V0-3-DataEntry-20241028-082756_results.json > output.txt 2> error.txt
	
The set of GHG inventory files (*LU\*.csv*) can be given with wild card search. Note the use of hyphen (') characters.

Download the CRT json file from the ETF Reporting Tool. Before json import the resulting json file 
must be validated in ETF.

The `>` operator redirects standard output to the *output.tx* file and the `2>` operator standard error output (e.g. notifications
about UIDs not found in the CRT json file) to *error.txt*.

>[!IMPORTANT]
>The json file must have been exported from the LULUCF sector for LULUCF results.
>The json file must have been exported from Agriculture sector for Agriculture results. 

> [!NOTE]
> Two UIDs related to *losses* have their UID twice in CL-FL (60EB12FB-2993-433B-81F9-451C56919187) and 
> GL-FL (18C29684-3802-456A-8925-FAC535734216). These UIDs are added together when filling the CRT json with results.

### 4.2 crtcomments.py
Insert notation key comments to CRT json file. Traditionally the comments have been in the *CLU_notation_explanations.csv* file:

	(lukeghg) crttool.py -csv  /data/projects/khk/ghg/2023/crf/CLU_notation_explanations.csv --json FIN-CRT-2025-V0-3-DataEntry-20241028-082756_results.json --begin 1990 --year 2023 --out FIN-CRT-2025-V0-3-DataEntry-20241028-082756_comments_results.json >output.txt 2> error.txt

> [!IMPORTANT]
> ETF Reporting Tool cannot import notation key comments fall 2024. There seems to be a program bug that consumes 
> browser memory even with few new notation key comments.

### 4.3 crtagritool.py
The GHG inventory results from Agriculture sector are in an Excel file. The file has been augmented with a new UID column
for time series:

	crtagritool.py --excel Kopio_LUKEAgri_2023_2025_joulu-ETFtesti.xls --year 2023 --sheets "CH4 manure" "CH4 enteric" --out AgriGHG.csv

The *--sheets* option is a list of Excel sheets for the GHG inventory results. The ouput file *AgriGHG.csv* has the same format as
in other files in GHG inventory and it can be read to the CRT json file with `crttool.py`.

> [!NOTE]
> Importing Agriculture sector is a work in progress. If the Excel file format remains the same 
> new sheets can be read and results extracted
> to the output csv file. 
