#!/bin/bash

# and simply output the node's hostname to
# rq1_reproduce.output
#
#SBATCH --mail-type=ALL
#SBATCH --mail-user=kl5sq@virginia.edu
#
#SBATCH --job-name="reproduce_embedding"
#SBATCH --error="reproduce.err"
#SBATCH --output="reproduce.output"
# --- specify the partition (queue) name
#SBATCH --partition="gpu"
#SBATCH --gres=gpu:4
#SBATCH --nodelist=adriatic[01-06]
#source /etc/profile.d/modules.sh
#module load python3
#source seer/bin/activate
cd /u/kl5sq/masters/SEER/embedding_analysis/
python3 embedding_analysis.py --data_path ../datasets/phase1_dataset_final/ --model JointEmbedder --dataset TestOracleInferencePhase1 --gpu_id 0 --fold_number 1 --reload_from 21 --pos_enc True
