#!/bin/bash

# and simply output the node's hostname to
# rq1_reproduce.output
#
#SBATCH --mail-type=ALL
#SBATCH --mail-user=kl5sq@virginia.edu
#
#SBATCH --job-name="reproduce Job"
#SBATCH --error="reproduce.err"
#SBATCH --output="reproduce.output"
# --- specify the partition (queue) name
#SBATCH --partition="gpu"
#source /etc/profile.d/modules.sh
#module load python3
#source seer/bin/activate
cd /u/kl5sq/masters/SEER/learning/
python3 test.py --data_path ../datasets/phase2_dataset_final/ --model JointEmbedder --dataset TestOracleInferencePhase2 --timestamp 202203201945 --gpu_id 0 --fold 1 --reload_from 29
