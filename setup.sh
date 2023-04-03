# https://zenodo.org/record/6970062
mkdir datasets
cd datasets
wget https://zenodo.org/record/6970062/files/phase1_dataset_final.zip
wget https://zenodo.org/record/6970062/files/phase2_dataset_final_unseen.zip
wget https://zenodo.org/record/6970062/files/phase2_dataset_final_whole.zip

unzip phase1_dataset_final.zip
unzip phase2_dataset_final_unseen.zip
mv phase2_dataset_final phase2_dataset_final_unseen
unzip phase2_dataset_final_whole.zip

cd ../attention_analysis
wget https://zenodo.org/record/6970062/files/attention_analysis.zip
unzip attention_analysis.zip
unzip TNs_attn_weights.zip

cd ../scripts
wget https://zenodo.org/record/6970062/files/data.zip
unzip data.zip

cd ..
wget https://zenodo.org/record/6970062/files/epoch_21_fold_1.h5

