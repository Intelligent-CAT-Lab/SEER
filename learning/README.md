# Model Training and Evaluation
In this directory, we introduce all python modules which have been used for model training and evaluation purposes. Please download the datasets and a pretrained model (if you want to continue from a specific epoch) from Zenodo.

## Implementation Details
Please check the following descriptions related to each .py file in this directory:
* `data_loader_phase1.py`: This file is used to read the .h5 files, process them based on the dataset, and bring it into an iterable form. Each instance of this dataset contains the Test, Fixed Code, Buggy Code, Fixed Code Difference, and Negative Code Difference.
* `data_loader_phase2.py`: This file is used to read the .h5 files, process them based on the dataset, and bring it into an iterable form. Each instance of this dataset contains the Test, Code, and its corresponding Label.
* `modules.py`: This file contains some important modules of our implementation. This includes the Transformer, Positional Encoding, Early Stopping , etc.
* `test.py`: This file is used for predicting the labels of test sets using a pretrained model. For testing a pretrained model from phase-2 with model type **JointEmbedder**, dataset type **TestOracleInferencePhase2**, --timestamp **202203201945**, GPU ID **0**, fold number **1**, and epoch number **29**, please execute the following:  
`python3 test.py --data_path phase2_dataset_final/ --model JointEmbedder --dataset TestOracleInferencePhase2 --timestamp 202203201945 --gpu_id 0 --fold 1 --reload_from 29`
* `train_phase1.py`: This file is used for training phase-1 of SEER. For training a model in phase-1 with model type **JointEmbedder**, dataset type **TestOracleInferencePhase1**, fold number **1**, and GPU ID **0**, please execute the following:  
`python3 train_phase1.py --data_path phase1_dataset_final/ --model JointEmbedder --dataset TestOracleInferencePhase1 --fold 1 --gpu_id 0`  
Please check `python3 train_phase1.py --help` for more help, or if you want to load and continue from a specific model checkpoint.
* `train_phase2.py`: This file is used for training phase-2 of SEER. For training a model in phase-2 with model type **JointEmbedder**, dataset type **TestOracleInferencePhase2**, fold number **1**, and GPU ID **0**, loss function weight set to **True**, please execute the following:  
`python3 train_phase2.py --data_path phase2_dataset_final/ --model JointEmbedder --dataset TestOracleInferencePhase2 --fold 1 --gpu_id 0 --weight True`  
Please check `python3 train_phase2.py --help` for more help, or if you want to load and continue from a specific model checkpoint.
