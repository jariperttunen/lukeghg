#!/bin/bash
#THIS IS A SLURM SCRIPT.
#See GitHub https://github.com/jariperttunen/lukeghg InstallAndUpdateLukeGHG.md
#run-ghg-master.slurm: Run inventory xml import in one step.
#To run type in command line: sbatch --mail-user firstname.lastname@luke.fi run-ghg-master.slurm
#CHECK The lukeghg python virtual environment is correctly set
#CHECK --account (Default: $USER) 
#CHECK --mail-user from command line
#It assumed that this script is in python virtual environment (lukeghg)
#SBATCH --job-name=lukeghg   # create a short name for your job
#SBATCH --account=$USER          # account
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
#source /home/jarip/venv/bin/activate
run-ghg-master.sh

