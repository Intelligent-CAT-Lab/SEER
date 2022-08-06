# Embedding Analysis
In this section, we aim to visualize the Embedding Layer weights of the model for buggy and fixed versions of the code. More specifically, we achieve this by applying Linear Discriminant Analysis (LDA) on the 200-d embedding vectors.

## How to visualize the Embedding Layer weights?
In order to apply LDA and plot the results, please make sure that the following files are available inside this directory.

- `embedding_analysis.py`: the script which processes the input, extract its embedding weights and apply LDA on it.
- `epoch_<reload_from>_fold_<fold_number>.h5`: the pretrained model which you would like to use for plotting the embedding layer weights. \<reload_from\> and \<fold_number\> correspond to command line arguments. Please download the pretrained model of phase-1 from Zenodo.
- `phase1_dataset_final`: the directory which contains phase-1 dataset. This directory is provided by the authors. Please download the directory (in .zip) from Zenodo.

Please change your working directory to this folder (embedding_analysis) and execute the script as shown below:  
If the dataset directory name is **phase1_dataset_final**, the type of model is **JointEmbedder**, the dataset name is **TestOracleInferencePhase1**, the GPU ID is **0**, the fold number of the pretrained model is **1**, the epoch number of the pretrained_model is **21**, and the positional encoding is set to **True**:

```
python3 embedding_analysis.py --data_path phase1_dataset_final --model JointEmbedder --dataset TestOracleInferencePhase1 --gpu_id 0 --fold_number 1 --reload_from 21 --pos_enc True
```

Please execute `python3 embedding_analysis.py --help` for more help.

## LDA is taking too long?
We understand that applying LDA can take a very long time. In fact, it took us hours to complete it. If you want to skip the LDA part and directly plot it, please use the provided `embeddings.txt` file in this directory.