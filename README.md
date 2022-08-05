# Perfect Is the Enemy of Test Oracle

Artifact repository for the paper _Perfect Is the Enemy of Test Oracle_, accepted at _ESEC/FSE 2022_.
Authors are [Ali Reza Ibrahimzada][ali], [Yiğit Varlı][yigit], [Dilara Tekinoğlu][dilara], and [Reyhaneh Jabbarvand][reyhaneh].

[ali]: https://alibrahimzada.github.io/
[yigit]: https://github.com/yigitv4rli
[dilara]: https://dtekinoglu.github.io/
[reyhaneh]: https://reyhaneh.cs.illinois.edu/index.htm

## Implementation Details
Please check the following descriptions related to each .py file in this directory:
* `configs.py`: This file is used as a configuration when training deep learning models. We control hyperparameters, dataset, etc. from this file.
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
* `utils.py`: This file contains independent functions which are used throughout the project.
  * For creating the vocabulary for both phase-1 and phase-2, please execute the following:  
  `python3 utils.py create_vocabulary all`
  * For creating the .h5 files from JSONs, please execute the following if JSON type is train, fold is 1, and model type is JointEmbedder:  
  `python3 utils.py json_to_h5 train 1 JointEmbedder`
  * For extracting the length of the longest sequence (Code, Test) in phase-1 dataset, please execute the following:  
  `python3 utils.py get_max_len phase1_dataset_final`
  * For splitting the raw dataset in phase-1 into train (90%), valid (5%), and test sets (5%), please execute the following:  
  `python3 utils.py train_valid_test_split phase1_dataset_final 0.05 0.05`
  * For filtering the assert statements in the dataset, please execute the following:  
  `python3 utils.py filter_asserts`

The directory structure of SEER is as follows:

     SEER
       |
       |--- attention_analysis:       The Multi-Head Attention Analysis related to model interpretation
       |
       |--- embedding_analysis:       The Embedding Analysis related to model interpretation
       |
       |--- dataset_generation:       The module which contains all scripts related to dataset generation
       |
       |--- models:                   The module which contains the deep learning models implemented in PyTorch
       |
       |--- mutant_generation:        The module which contains all scripts related to mutant generation
           |
           |--- mutation_operators:   A directory which contains all mutation operators used in Major

## Contact

Please don't hesitate to open issues or pull-requests, or to contact us directly (alirezai@illinois.edu). We are thankful for any questions, constructive criticism, or interest. :blush:
