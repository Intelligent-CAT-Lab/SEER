#!/bin/bash
# and simply output the node's hostname to
# rq3_reproduce.output
#
#SBATCH --mail-type=ALL
#SBATCH --mail-user=kl5sq@virginia.edu
#
#SBATCH --job-name="rq3_3_reproduce Job"
#SBATCH --error="rq3_3_reproduce.err"
#SBATCH --output="rq3_3_reproduce.output"
# --- specify the partition (queue) name
#SBATCH --partition="gpu"
cd ~/masters/SEER/scripts
python3 main.py --RQ 3 --subsec embeddings
