#!/bin/bash
#
#SBATCH --mail-type=ALL
#SBATCH --mail-user=kl5sq@virginia.edu
#
#SBATCH --job-name="triplets_phase3_projects"
#SBATCH --error="project_err_phase3.err"
#SBATCH --output="output_phase3_project.output"
# --- specify the partition (queue) name
#SBATCH --partition="main"
cd /u/kl5sq/masters/SEER
python3 ./real_data_gen/main.py project
