#!/bin/bash

# and simply output the node's hostname to
# rq1_reproduce.output
#
#SBATCH --mail-type=ALL
#SBATCH --mail-user=kl5sq@virginia.edu
#
#SBATCH --job-name="rq1_reproduce Job"
#SBATCH --error="rq1_reproduce.err"
#SBATCH --output="rq1_reproduce.output"
# --- specify the partition (queue) name
#SBATCH --partition="gpu"
#source /etc/profile.d/modules.sh
#module load python3
#source seer/bin/activate
cd ~/masters/SEER/scripts
python3 main.py --RQ 1
