#!/bin/bash

# and simply output the node's hostname to
# rq1_reproduce.output
#
#SBATCH --mail-type=ALL
#SBATCH --mail-user=kl5sq@virginia.edu
#
#SBATCH --job-name="phase3"
#SBATCH --error="phase3.err"
#SBATCH --output="phase3.output"
# --- specify the partition (queue) name
#SBATCH --partition="gpu"
cd /u/kl5sq/masters/SEER/learning/
python3 test.py --data_path ../datasets/phase3_dataset/ --model JointEmbedder --dataset TestOracleInferencePhase2 --timestamp 202203201945 --gpu_id 0 --fold 1 --reload_from 29
