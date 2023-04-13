#!/bin/bash
#
#SBATCH --mail-type=ALL
#SBATCH --mail-user=kl5sq@virginia.edu
#
#SBATCH --job-name="triplets_phase3"
#SBATCH --error="err_phase3.err"
#SBATCH --output="output_phase3.output"
# --- specify the partition (queue) name
#SBATCH --partition="gpu"
#SBATCH --gres=gpu:4
#SBATCH --nodelist=adriatic[01-06]
cd /u/kl5sq/masters/SEER
python3 ./learning/test.py
