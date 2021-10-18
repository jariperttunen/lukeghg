#!/bin/bash
#run-ghg-master.slurm: Run inventory xml import in one step.
#THIS IS A SLURM SCRIPT. 
#To run type in command line: sbatch run-ghg-master.slurm
#CHECK The lukeghg python virtual environment is correctly set below
#Default: source /home/jarip/venv/bin/activate
#CHECK --account 
#Default:  $USER
#CHECK the --mail-user from command line 
#Note the use of double quotes to allow wild card file reading.
#See GitHub https://github.com/jariperttunen/lukeghg InstallAndUpdateLukeGHG.md
#to setup 'lukeghg' python virtual environment and usage. 
#To redirect output type e.g.: run-ghg-master.sh > output.txt 2> errors.txt.
#It assumed that this script is in python virtual environment (lukeghg)
#SBATCH --job-name=lukeghg   # create a short name for your job
#SBATCH --account=$USER         # account
#SBATCH --nodes=1                # node count
#SBATCH --ntasks=1              # total number of tasks across all nodes
#SBATCH --cpus-per-task=1        # cpu-cores per task (>1 if multi-threaded tasks)
#SBATCH --mem-per-cpu=4G         # memory per cpu-core
#SBATCH --partition=normal         # sorvi: normal, big or test
#SBATCH --time=00:10:00          # total run time limit (HH:MM:SS)
#SBATCH --output=output_%j.txt
#SBATCH --error=errors_%j.txt
#SBATCH --mail-type=begin        # send email when job begins
#SBATCH --mail-type=end          # send email when job ends
#run-eu529-ghg-master.slurm: Run  EU529 inventory xml import in one step. 
#Note the use of double quotes to allow wild card file reading.
#See "/hsan2/khk/ghg/lukeghg/InstallAndUpdateLukeGHG.txt" to setup 'lukeghg' python virtual environment. 
ghg-master.py -c "EU529/KP*.csv" -p PartyProfile/PartyProfile_FIN_2021_4.xml\
	      -x PartyProfile/PartyProfile_FIN_2021_4_result.xml\
	      -b lukeghg/KPLULU1990/KP_CM_GM_RV_WDR_UID_notaatioavain.csv\
	      -k lukeghg/KPLULUSummary/KPSummary.csv\
	      -m lukeghg/CRFReporterMappings/300_500_mappings_1.1.csv\
	      -n "EU529/NIR*.csv"\
	      -i "EU529/C*.csv"\
	      -y 2019

