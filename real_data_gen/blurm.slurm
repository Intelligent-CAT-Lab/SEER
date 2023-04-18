#!/bin/bash
#
#SBATCH --mail-type=ALL
#SBATCH --mail-user=kl5sq@virginia.edu
#
#SBATCH --job-name="triplets_phase3"
#SBATCH --error="cpu_err_phase3.err"
#SBATCH --output="output_phase3_cpu.output"
# --- specify the partition (queue) name
#SBATCH --partition="main"
cd /u/kl5sq/masters/SEER
python3 ./learning/test.py
