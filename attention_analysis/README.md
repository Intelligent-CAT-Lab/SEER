# Attention Analysis
In this section, we aim to visualize the Self-Attention (SA) weight vectors of the model for a specific code sequence using heatmaps. SA weights are available in the multi-head attention component of Transformers.

## How to visualize the attention weights?
In order to produce a heatmap for the attention weights of a specific code sequence, please make sure that the following files are available inside this directory.

- `attention_analysis.py`: the script which processes the input, extract its attention weights and create a heatmap for it.
- `epoch_<reload_from>_fold_<fold_number>.h5`: the pretrained model which you would like to use for generating the heatmap. \<reload_from\> and \<fold_number\> correspond to command line arguments. Please download the file `attention_analysis.zip` from Zenodo and use the pretrained model from there.
- `sample_code.txt`: the code sequence you wish to produce its attention weights.
- `vocab_phase2.json`: the vocabulary which was used for training the model. This file is provided by the authors. Please download the file `attention_analysis.zip` from Zenodo and use the vocabulary from there.
- `main.java`: this file is used to analyze attention weights.

Please change your working directory to this folder (attention_analysis) and execute the script as shown below:  
If the type of model is **JointEmbedder**, the dataset name is **TestOracleInferencePhase2**, the GPU ID is **0**, the fold number of the pretrained model is **1**, and the epoch number of the pretrained_model is **29**:

```
python3 attention_analysis.py --model JointEmbedder --dataset TestOracleInferencePhase2 --gpu_id 0 fold_number 1 reload_from 29
```

Please execute `python3 attention_analysis.py --help` for more help.

## How to analyze the attention weights?
Please extract the attention weights for all input code sequences and place them inside a directory called `TNs_attn_weights`. We have prepared a sample directory which contains the attention weights of all True Negatives (TNs) for you. You may download it, extract it, and analyze the attention weights. Please download the `attention_analysis.zip` file from Zenodo.

Please compile and execute `src/main.java` for attention analysis.
