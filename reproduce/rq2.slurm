#!/bin/bash
# and simply output the node's hostname to
# rq2_reproduce.output
#
#SBATCH --mail-type=ALL
#SBATCH --mail-user=kl5sq@virginia.edu
#
#SBATCH --job-name="rq2_reproduce Job"
#SBATCH --error="rq2_reproduce.err"
#SBATCH --output="rq2_reproduce.output"
# --- specify the partition (queue) name
#SBATCH --partition="gpu"
cd ~/masters/SEER/scripts
python3 main.py --RQ 2
