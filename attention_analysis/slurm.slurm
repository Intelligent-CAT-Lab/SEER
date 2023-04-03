#!/bin/bash

# and simply output the node's hostname to
# rq1_reproduce.output
#
#SBATCH --mail-type=ALL
#SBATCH --mail-user=kl5sq@virginia.edu
#
#SBATCH --job-name="reproduce-attention_analysis"
#SBATCH --error="reproduce.err"
#SBATCH --output="reproduce.output"
# --- specify the partition (queue) name
#SBATCH --partition="gpu"
#source /etc/profile.d/modules.sh
#module load python3
#source seer/bin/activate
cd /u/kl5sq/masters/SEER/attention_analysis/
python3 attention_analysis.py --model JointEmbedder --dataset TestOracleInferencePhase2 --gpu_id 0 --fold_number 1 --reload_from 29
